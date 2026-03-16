from collections.abc import Mapping
from functools import partial

from .syntax import (
    Abstract,
    Allocate,
    Apply,
    Begin,
    Branch,
    Identifier,
    Immediate,
    Let,
    Load,
    Primitive,
    Program,
    Reference,
    Store,
    Term,
)

type Environment = Mapping[Identifier, Immediate | Reference]


def free_variables(term: Term) -> set[str]:
    match term:
        case Immediate() | Allocate():
            return set()

        case Reference(name=name):
            return {name}

        case Let(bindings=bindings, body=body):
            free: set[str] = set()
            bound: set[str] = set()
            for name, value in bindings:
                free |= free_variables(value) - bound
                bound.add(name)
            return free | (free_variables(body) - bound)

        case Abstract(parameters=parameters, body=body):
            return free_variables(body) - set(parameters)

        case Apply(target=target, arguments=arguments):
            result = free_variables(target)
            for arg in arguments:
                result |= free_variables(arg)
            return result

        case Primitive(left=left, right=right):
            return free_variables(left) | free_variables(right)

        case Branch(left=left, right=right, consequent=consequent, otherwise=otherwise):
            return (
                free_variables(left) | free_variables(right) | free_variables(consequent) | free_variables(otherwise)
            )

        case Load(base=base):
            return free_variables(base)

        case Store(base=base, value=value):
            return free_variables(base) | free_variables(value)

        case Begin(effects=effects, value=value):  # pragma: no branch
            result = free_variables(value)
            for effect in effects:
                result |= free_variables(effect)
            return result


def optimize_term(
    term: Term,
    env: Environment,
) -> Term:
    recur = partial(optimize_term, env=env)

    match term:
        case Immediate():
            return term

        case Reference(name=name):
            if name in env:
                return env[name]
            return term

        case Let(bindings=bindings, body=body):
            new_env = dict(env)
            new_bindings: list[tuple[str, Term]] = []

            for name, value in bindings:
                opt_value = optimize_term(value, new_env)
                match opt_value:
                    case Immediate() | Reference():
                        new_env[name] = opt_value
                    case _:
                        pass
                new_bindings.append((name, opt_value))

            opt_body = optimize_term(body, new_env)

            used = free_variables(opt_body)
            kept: list[tuple[str, Term]] = []
            for name, value in reversed(new_bindings):
                if name in used:
                    kept.append((name, value))
                    used |= free_variables(value)
            kept.reverse()

            if not kept:
                return opt_body

            return Let(bindings=kept, body=opt_body)

        case Abstract(parameters=parameters, body=body):
            inner_env = {k: v for k, v in env.items() if k not in set(parameters)}
            return Abstract(
                parameters=parameters,
                body=optimize_term(body, inner_env),
            )

        case Apply(target=target, arguments=arguments):
            return Apply(
                target=recur(target),
                arguments=[recur(arg) for arg in arguments],
            )

        case Primitive(operator=operator, left=left, right=right):
            opt_left = recur(left)
            opt_right = recur(right)

            if isinstance(opt_left, Immediate) and isinstance(opt_right, Immediate):
                match operator:
                    case "+":
                        return Immediate(value=opt_left.value + opt_right.value)
                    case "-":
                        return Immediate(value=opt_left.value - opt_right.value)
                    case "*":  # pragma: no branch
                        return Immediate(value=opt_left.value * opt_right.value)

            return Primitive(operator=operator, left=opt_left, right=opt_right)

        case Branch(operator=operator, left=left, right=right, consequent=consequent, otherwise=otherwise):
            opt_left = recur(left)
            opt_right = recur(right)

            if isinstance(opt_left, Immediate) and isinstance(opt_right, Immediate):
                match operator:
                    case "<":
                        condition = opt_left.value < opt_right.value
                    case "==":  # pragma: no branch
                        condition = opt_left.value == opt_right.value

                if condition:
                    return recur(consequent)
                return recur(otherwise)

            return Branch(
                operator=operator,
                left=opt_left,
                right=opt_right,
                consequent=recur(consequent),
                otherwise=recur(otherwise),
            )

        case Allocate():
            return term

        case Load(base=base, index=index):
            return Load(base=recur(base), index=index)

        case Store(base=base, index=index, value=value):
            return Store(
                base=recur(base),
                index=index,
                value=recur(value),
            )

        case Begin(effects=effects, value=value):  # pragma: no branch
            return Begin(
                effects=[recur(e) for e in effects],
                value=recur(value),
            )


def optimize_program(
    program: Program,
) -> Program:
    previous = program

    while True:
        match previous:
            case Program(parameters=parameters, body=body):  # pragma: no branch
                optimized = Program(
                    parameters=parameters,
                    body=optimize_term(body, {}),
                )

        if optimized == previous:
            return optimized
        previous = optimized
