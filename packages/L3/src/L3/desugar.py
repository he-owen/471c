from .syntax import (
    Abstract,
    Allocate,
    And,
    Apply,
    Begin,
    Bool,
    Branch,
    If,
    Immediate,
    Let,
    LetRec,
    Load,
    Not,
    Or,
    Primitive,
    Print,
    Program,
    Reference,
    Store,
    StringLength,
    StringLiteral,
    Term,
)


def desugar_term(term: Term) -> Term:
    recur = desugar_term

    match term:
        case Bool(value=True):
            return Immediate(value=1)

        case Bool(value=False):
            return Immediate(value=0)

        case And(left=left, right=right):
            return Branch(
                operator="!=",
                left=recur(left),
                right=Immediate(value=0),
                consequent=recur(right),
                otherwise=Immediate(value=0),
            )

        case Or(left=left, right=right):
            return Branch(
                operator="!=",
                left=recur(left),
                right=Immediate(value=0),
                consequent=Immediate(value=1),
                otherwise=recur(right),
            )

        case Not(value=value):
            return Branch(
                operator="!=",
                left=recur(value),
                right=Immediate(value=0),
                consequent=Immediate(value=0),
                otherwise=Immediate(value=1),
            )

        case If(condition=condition, consequent=consequent, otherwise=otherwise):
            return Branch(
                operator="!=",
                left=recur(condition),
                right=Immediate(value=0),
                consequent=recur(consequent),
                otherwise=recur(otherwise),
            )

        case Let(bindings=bindings, body=body):
            return Let(
                bindings=[(name, recur(value)) for name, value in bindings],
                body=recur(body),
            )

        case LetRec(bindings=bindings, body=body):
            return LetRec(
                bindings=[(name, recur(value)) for name, value in bindings],
                body=recur(body),
            )

        case Reference():
            return term

        case Abstract(parameters=parameters, body=body):
            return Abstract(parameters=parameters, body=recur(body))

        case Apply(target=target, arguments=arguments):
            return Apply(
                target=recur(target),
                arguments=[recur(arg) for arg in arguments],
            )

        case Immediate():
            return term

        case Primitive(operator=operator, left=left, right=right):
            return Primitive(operator=operator, left=recur(left), right=recur(right))

        case Branch(operator=operator, left=left, right=right, consequent=consequent, otherwise=otherwise):
            return Branch(
                operator=operator,
                left=recur(left),
                right=recur(right),
                consequent=recur(consequent),
                otherwise=recur(otherwise),
            )

        case Allocate():
            return term

        case Load(base=base, index=index):
            return Load(base=recur(base), index=index)

        case Store(base=base, index=index, value=value):
            return Store(base=recur(base), index=index, value=recur(value))

        case Print(value=value):
            return Print(value=recur(value))

        case StringLiteral():
            return term

        case StringLength(value=value):
            return StringLength(value=recur(value))

        case Begin(effects=effects, value=value):  # pragma: no branch
            return Begin(
                effects=[recur(effect) for effect in effects],
                value=recur(value),
            )


def desugar_program(program: Program) -> Program:
    match program:
        case Program(parameters=parameters, body=body):  # pragma: no branch
            return Program(
                parameters=parameters,
                body=desugar_term(body),
            )
