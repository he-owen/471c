from L3.desugar import desugar_program, desugar_term
from L3.syntax import (
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
)


def test_desugar_bool_true():
    term = Bool(value=True)

    actual = desugar_term(term)

    expected = Immediate(value=1)

    assert actual == expected


def test_desugar_bool_false():
    term = Bool(value=False)

    actual = desugar_term(term)

    expected = Immediate(value=0)

    assert actual == expected


def test_desugar_and():
    term = And(
        left=Bool(value=True),
        right=Bool(value=False),
    )

    actual = desugar_term(term)

    expected = Branch(
        operator="!=",
        left=Immediate(value=1),
        right=Immediate(value=0),
        consequent=Immediate(value=0),
        otherwise=Immediate(value=0),
    )

    assert actual == expected


def test_desugar_or():
    term = Or(
        left=Bool(value=False),
        right=Bool(value=True),
    )

    actual = desugar_term(term)

    expected = Branch(
        operator="!=",
        left=Immediate(value=0),
        right=Immediate(value=0),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=1),
    )

    assert actual == expected


def test_desugar_not():
    term = Not(value=Bool(value=True))

    actual = desugar_term(term)

    expected = Branch(
        operator="!=",
        left=Immediate(value=1),
        right=Immediate(value=0),
        consequent=Immediate(value=0),
        otherwise=Immediate(value=1),
    )

    assert actual == expected


def test_desugar_if_term():
    term = If(
        condition=Bool(value=True),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = desugar_term(term)

    expected = Branch(
        operator="!=",
        left=Immediate(value=1),
        right=Immediate(value=0),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    assert actual == expected


def test_desugar_if_term_with_reference():
    term = If(
        condition=Reference(name="x"),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = desugar_term(term)

    expected = Branch(
        operator="!=",
        left=Reference(name="x"),
        right=Immediate(value=0),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    assert actual == expected


def test_desugar_nested_and_or():
    term = And(
        left=Or(
            left=Bool(value=True),
            right=Bool(value=False),
        ),
        right=Bool(value=True),
    )

    actual = desugar_term(term)

    expected = Branch(
        operator="!=",
        left=Branch(
            operator="!=",
            left=Immediate(value=1),
            right=Immediate(value=0),
            consequent=Immediate(value=1),
            otherwise=Immediate(value=0),
        ),
        right=Immediate(value=0),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    assert actual == expected


def test_desugar_let_with_bool():
    term = Let(
        bindings=[("x", Bool(value=True))],
        body=Reference(name="x"),
    )

    actual = desugar_term(term)

    expected = Let(
        bindings=[("x", Immediate(value=1))],
        body=Reference(name="x"),
    )

    assert actual == expected


def test_desugar_letrec_with_bool():
    term = LetRec(
        bindings=[("x", Bool(value=True))],
        body=Reference(name="x"),
    )

    actual = desugar_term(term)

    expected = LetRec(
        bindings=[("x", Immediate(value=1))],
        body=Reference(name="x"),
    )

    assert actual == expected


def test_desugar_abstract_with_bool():
    term = Abstract(
        parameters=["x"],
        body=Not(value=Reference(name="x")),
    )

    actual = desugar_term(term)

    expected = Abstract(
        parameters=["x"],
        body=Branch(
            operator="!=",
            left=Reference(name="x"),
            right=Immediate(value=0),
            consequent=Immediate(value=0),
            otherwise=Immediate(value=1),
        ),
    )

    assert actual == expected


def test_desugar_apply_with_bool():
    term = Apply(
        target=Reference(name="f"),
        arguments=[Bool(value=True)],
    )

    actual = desugar_term(term)

    expected = Apply(
        target=Reference(name="f"),
        arguments=[Immediate(value=1)],
    )

    assert actual == expected


def test_desugar_reference():
    term = Reference(name="x")

    actual = desugar_term(term)

    assert actual == term


def test_desugar_immediate():
    term = Immediate(value=42)

    actual = desugar_term(term)

    assert actual == term


def test_desugar_primitive():
    term = Primitive(
        operator="+",
        left=Bool(value=True),
        right=Immediate(value=1),
    )

    actual = desugar_term(term)

    expected = Primitive(
        operator="+",
        left=Immediate(value=1),
        right=Immediate(value=1),
    )

    assert actual == expected


def test_desugar_branch():
    term = Branch(
        operator="<",
        left=Immediate(value=1),
        right=Immediate(value=2),
        consequent=Bool(value=True),
        otherwise=Bool(value=False),
    )

    actual = desugar_term(term)

    expected = Branch(
        operator="<",
        left=Immediate(value=1),
        right=Immediate(value=2),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    assert actual == expected


def test_desugar_allocate():
    term = Allocate(count=3)

    actual = desugar_term(term)

    assert actual == term


def test_desugar_load():
    term = Load(base=Bool(value=True), index=0)

    actual = desugar_term(term)

    expected = Load(base=Immediate(value=1), index=0)

    assert actual == expected


def test_desugar_store():
    term = Store(base=Reference(name="x"), index=0, value=Bool(value=True))

    actual = desugar_term(term)

    expected = Store(base=Reference(name="x"), index=0, value=Immediate(value=1))

    assert actual == expected


def test_desugar_print():
    term = Print(value=Bool(value=True))

    actual = desugar_term(term)

    expected = Print(value=Immediate(value=1))

    assert actual == expected


def test_desugar_string_literal():
    term = StringLiteral(value="hello")

    actual = desugar_term(term)

    assert actual == term


def test_desugar_string_length():
    term = StringLength(value=StringLiteral(value="hello"))

    actual = desugar_term(term)

    assert actual == term


def test_desugar_begin():
    term = Begin(
        effects=[Bool(value=True)],
        value=Bool(value=False),
    )

    actual = desugar_term(term)

    expected = Begin(
        effects=[Immediate(value=1)],
        value=Immediate(value=0),
    )

    assert actual == expected


def test_desugar_program():
    program = Program(
        parameters=["x"],
        body=If(
            condition=Reference(name="x"),
            consequent=Bool(value=True),
            otherwise=Bool(value=False),
        ),
    )

    actual = desugar_program(program)

    expected = Program(
        parameters=["x"],
        body=Branch(
            operator="!=",
            left=Reference(name="x"),
            right=Immediate(value=0),
            consequent=Immediate(value=1),
            otherwise=Immediate(value=0),
        ),
    )

    assert actual == expected
