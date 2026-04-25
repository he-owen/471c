from collections.abc import Callable
from functools import partial

from L0 import syntax as L0

from .syntax import (
    Abstract,
    Allocate,
    Apply,
    Branch,
    Copy,
    Halt,
    Immediate,
    Load,
    Primitive,
    Program,
    Statement,
    Store,
)


def free_variables(statement: Statement) -> set[str]:
    match statement:
        case Copy(destination=destination, source=source, then=then):
            return {source} | (free_variables(then) - {destination})

        case Abstract(destination=destination, parameters=parameters, body=body, then=then):
            return (free_variables(body) - set(parameters)) | (free_variables(then) - {destination})

        case Apply(target=target, arguments=arguments):
            return {target, *arguments}

        case Immediate(destination=destination, then=then):
            return free_variables(then) - {destination}

        case Primitive(destination=destination, left=left, right=right, then=then):
            return {left, right} | (free_variables(then) - {destination})

        case Branch(left=left, right=right, then=then, otherwise=otherwise):
            return {left, right} | free_variables(then) | free_variables(otherwise)

        case Allocate(destination=destination, then=then):
            return free_variables(then) - {destination}

        case Load(destination=destination, base=base, then=then):
            return {base} | (free_variables(then) - {destination})

        case Store(base=base, value=value, then=then):
            return {base, value} | free_variables(then)

        case Halt(value=value):  # pragma: no branch
            return {value}


def close_statement(
    statement: Statement,
    fresh: Callable[[str], str],
    procedures: list[L0.Procedure],
) -> L0.Statement:
    _statement = partial(close_statement, fresh=fresh, procedures=procedures)

    match statement:
        case Copy(destination=destination, source=source, then=then):
            return L0.Copy(destination=destination, source=source, then=_statement(then))

        case Abstract(destination=destination, parameters=parameters, body=body, then=then):
            fvs = sorted(free_variables(body) - set(parameters))

            proc_name = fresh("f")
            closure_param = fresh("c")

            converted_body = close_statement(body, fresh, procedures)
            for i in reversed(range(len(fvs))):
                converted_body = L0.Load(destination=fvs[i], base=closure_param, index=i + 1, then=converted_body)

            procedures.append(
                L0.Procedure(
                    name=proc_name,
                    parameters=[closure_param, *parameters],
                    body=converted_body,
                )
            )

            converted_then = _statement(then)

            result: L0.Statement = converted_then
            for i in reversed(range(len(fvs))):
                result = L0.Store(base=destination, index=i + 1, value=fvs[i], then=result)
            addr_temp = fresh("t")
            result = L0.Store(base=destination, index=0, value=addr_temp, then=result)
            result = L0.Address(destination=addr_temp, name=proc_name, then=result)
            result = L0.Allocate(destination=destination, count=1 + len(fvs), then=result)

            return result

        case Apply(target=target, arguments=arguments):
            t = fresh("t")
            return L0.Load(
                destination=t,
                base=target,
                index=0,
                then=L0.Call(target=t, arguments=[target, *arguments]),
            )

        case Immediate(destination=destination, value=value, then=then):
            return L0.Immediate(destination=destination, value=value, then=_statement(then))

        case Primitive(destination=destination, operator=operator, left=left, right=right, then=then):
            return L0.Primitive(
                destination=destination, operator=operator, left=left, right=right, then=_statement(then)
            )

        case Branch(operator=operator, left=left, right=right, then=then, otherwise=otherwise):
            return L0.Branch(
                operator=operator,
                left=left,
                right=right,
                then=_statement(then),
                otherwise=_statement(otherwise),
            )

        case Allocate(destination=destination, count=count, then=then):
            return L0.Allocate(destination=destination, count=count, then=_statement(then))

        case Load(destination=destination, base=base, index=index, then=then):
            return L0.Load(destination=destination, base=base, index=index, then=_statement(then))

        case Store(base=base, index=index, value=value, then=then):
            return L0.Store(base=base, index=index, value=value, then=_statement(then))

        case Halt(value=value):  # pragma: no branch
            return L0.Halt(value=value)


def close_program(
    program: Program,
    fresh: Callable[[str], str],
) -> L0.Program:
    match program:
        case Program(parameters=parameters, body=body):  # pragma: no branch
            procedures: list[L0.Procedure] = []
            converted_body = close_statement(body, fresh, procedures)
            procedures.append(
                L0.Procedure(
                    name="l0",
                    parameters=list(parameters),
                    body=converted_body,
                )
            )
            return L0.Program(procedures=procedures)
