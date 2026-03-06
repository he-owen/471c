from collections.abc import Sequence
from pathlib import Path

from lark import Lark, Token, Transformer
from lark.visitors import v_args  # pyright: ignore[reportUnknownVariableType]

from .syntax import (
    Abstract,
    Allocate,
    Apply,
    Begin,
    Branch,
    Identifier,
    Immediate,
    Let,
    LetRec,
    Load,
    Primitive,
    Program,
    Reference,
    Store,
    Term,
)


class AstTransformer(Transformer[Token, Program | Term]):
    @v_args(inline=True)
    def program(
        self,
        _program: Token,
        parameters: Sequence[Identifier],
        body: Term,
    ) -> Program:
        return Program(
            parameters=parameters,
            body=body,
        )

    def parameters(
        self,
        children: Sequence[Token],
    ) -> Sequence[Identifier]:
        return [c.value for c in children]

    @v_args(inline=True)
    def term(
        self,
        term: Term,
    ) -> Term:
        return term

    @v_args(inline=True)
    def let(
        self,
        _let: Token,
        bindings: Sequence[tuple[Identifier, Term]],
        body: Term,
    ) -> Term:
        return Let(
            bindings=bindings,
            body=body,
        )

    @v_args(inline=True)
    def letrec(
        self,
        _letrec: Token,
        bindings: Sequence[tuple[Identifier, Term]],
        body: Term,
    ) -> Term:
        return LetRec(
            bindings=bindings,
            body=body,
        )

    def bindings(
        self,
        bindings: Sequence[tuple[Identifier, Term]],
    ) -> Sequence[tuple[Identifier, Term]]:
        return bindings

    @v_args(inline=True)
    def binding(
        self,
        name: Token,
        value: Term,
    ) -> tuple[Identifier, Term]:
        return name.value, value

    def reference(self, children: Sequence[Token]) -> Reference:
        return Reference(name=children[0].value)

    def immediate(self, children: Sequence[Token]) -> Immediate:
        return Immediate(value=int(children[0].value))

    @v_args(inline=True)
    def abstract(
        self,
        _lambda: Token,
        parameters: Sequence[Identifier],
        body: Term,
    ) -> Abstract:
        return Abstract(parameters=parameters, body=body)

    def apply(self, children: Sequence[Term]) -> Apply:
        target, *arguments = children
        return Apply(target=target, arguments=arguments)

    @v_args(inline=True)
    def primitive(
        self,
        operator: Token,
        left: Term,
        right: Term,
    ) -> Primitive:
        return Primitive(operator=operator.value, left=left, right=right)

    @v_args(inline=True)
    def branch(
        self,
        _if: Token,
        operator: Token,
        left: Term,
        right: Term,
        consequent: Term,
        otherwise: Term,
    ) -> Branch:
        return Branch(
            operator=operator.value,
            left=left,
            right=right,
            consequent=consequent,
            otherwise=otherwise,
        )

    @v_args(inline=True)
    def allocate(self, _allocate: Token, count_term: Term) -> Allocate:
        return Allocate(count=count_term.value)

    @v_args(inline=True)
    def load(self, _load: Token, base: Term, index_term: Term) -> Load:
        return Load(base=base, index=index_term.value)

    @v_args(inline=True)
    def store(
        self,
        _store: Token,
        base: Term,
        index_term: Term,
        value: Term,
    ) -> Store:
        return Store(base=base, index=index_term.value, value=value)

    def begin(self, children: Sequence[Term | Token]) -> Begin:
        terms = [c for c in children if not isinstance(c, Token)]
        *effects, value = terms
        return Begin(effects=effects, value=value)


def parse_term(source: str) -> Term:
    grammar = Path(__file__).with_name("L3.lark").read_text()
    parser = Lark(grammar, start="term", parser="lalr")
    tree = parser.parse(source)  # pyright: ignore[reportUnknownMemberType]
    return AstTransformer().transform(tree)  # pyright: ignore[reportReturnType]


def parse_program(source: str) -> Program:
    grammar = Path(__file__).with_name("L3.lark").read_text()
    parser = Lark(grammar, start="program", parser="lalr")
    tree = parser.parse(source)  # pyright: ignore[reportUnknownMemberType]
    return AstTransformer().transform(tree)  # pyright: ignore[reportReturnType]
