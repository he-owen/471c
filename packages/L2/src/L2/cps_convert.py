from collections.abc import Callable, Sequence
from functools import partial

from L1 import syntax as L1

from L2 import syntax as L2


def cps_convert_term(
    term: L2.Term,
    k: Callable[[L1.Identifier], L1.Statement],
    fresh: Callable[[str], str],
) -> L1.Statement:
    _term = partial(cps_convert_term, fresh=fresh)
    _terms = partial(cps_convert_terms, fresh=fresh)

    match term:
        case L2.Let(bindings=bindings, body=body):
            match list(bindings):
                case []:
                    return _term(body, k)
                case [(name, value), *rest]:  # pragma: no branch
                    return _term(
                        value,
                        lambda v, name=name, rest=rest: L1.Copy(
                            destination=name,
                            source=v,
                            then=cps_convert_term(L2.Let(bindings=rest, body=body), k, fresh),
                        ),
                    )

        case L2.Reference(name=name):
            return k(name)

        case L2.Abstract(parameters=parameters, body=body):
            t = fresh("t")
            k_param = fresh("k")
            return L1.Abstract(
                destination=t,
                parameters=[*parameters, k_param],
                body=_term(body, lambda v: L1.Apply(target=k_param, arguments=[v])),
                then=k(t),
            )

        case L2.Apply(target=target, arguments=arguments):
            k_name = fresh("k")
            t = fresh("t")
            return _term(
                target,
                lambda tid: _terms(
                    arguments,
                    lambda aids: L1.Abstract(
                        destination=k_name,
                        parameters=[t],
                        body=k(t),
                        then=L1.Apply(target=tid, arguments=[*aids, k_name]),
                    ),
                ),
            )

        case L2.Immediate(value=value):
            t = fresh("t")
            return L1.Immediate(destination=t, value=value, then=k(t))

        case L2.Primitive(operator=operator, left=left, right=right):
            t = fresh("t")
            return _terms(
                [left, right],
                lambda ids: L1.Primitive(
                    destination=t,
                    operator=operator,
                    left=ids[0],
                    right=ids[1],
                    then=k(t),
                ),
            )

        case L2.Branch(operator=operator, left=left, right=right, consequent=consequent, otherwise=otherwise):
            j = fresh("j")
            t = fresh("t")

            def join_k(v: L1.Identifier) -> L1.Statement:
                return L1.Apply(target=j, arguments=[v])

            return _terms(
                [left, right],
                lambda ids: L1.Abstract(
                    destination=j,
                    parameters=[t],
                    body=k(t),
                    then=L1.Branch(
                        operator=operator,
                        left=ids[0],
                        right=ids[1],
                        then=_term(consequent, join_k),
                        otherwise=_term(otherwise, join_k),
                    ),
                ),
            )

        case L2.Allocate(count=count):
            t = fresh("t")
            return L1.Allocate(destination=t, count=count, then=k(t))

        case L2.Load(base=base, index=index):
            t = fresh("t")
            return _term(
                base,
                lambda bid: L1.Load(destination=t, base=bid, index=index, then=k(t)),
            )

        case L2.Store(base=base, index=index, value=value):
            t = fresh("t")
            return _terms(
                [base, value],
                lambda ids: L1.Store(
                    base=ids[0],
                    index=index,
                    value=ids[1],
                    then=L1.Immediate(destination=t, value=0, then=k(t)),
                ),
            )

        case L2.Begin(effects=effects, value=value):  # pragma: no branch
            return _terms([*effects, value], lambda ids: k(ids[-1]))


def cps_convert_terms(
    terms: Sequence[L2.Term],
    k: Callable[[Sequence[L1.Identifier]], L1.Statement],
    fresh: Callable[[str], str],
) -> L1.Statement:
    _term = partial(cps_convert_term, fresh=fresh)
    _terms = partial(cps_convert_terms, fresh=fresh)

    match terms:
        case []:
            return k([])

        case [first, *rest]:
            return _term(first, lambda first: _terms(rest, lambda rest: k([first, *rest])))

        case _:  # pragma: no cover
            raise ValueError(terms)


def cps_convert_program(
    program: L2.Program,
    fresh: Callable[[str], str],
) -> L1.Program:
    _term = partial(cps_convert_term, fresh=fresh)

    match program:
        case L2.Program(parameters=parameters, body=body):  # pragma: no branch
            return L1.Program(
                parameters=parameters,
                body=_term(body, lambda value: L1.Halt(value=value)),
            )
