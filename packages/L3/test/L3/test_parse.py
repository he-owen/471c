from L3.parse import parse_program, parse_term
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


# Let
def test_parse_let_empty():
    source = "(let () x)"

    expected = Let(
        bindings=[],
        body=Reference(name="x"),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_let_bindings():
    source = "(let ((x 0)) x)"

    expected = Let(
        bindings=[
            ("x", Immediate(value=0)),
        ],
        body=Reference(name="x"),
    )

    actual = parse_term(source)

    assert actual == expected


# LetRec
def test_parse_letrec_empty():
    source = "(letrec () x)"

    expected = LetRec(
        bindings=[],
        body=Reference(name="x"),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_letrec_bindings():
    source = "(letrec ((x 0)) x)"

    expected = LetRec(
        bindings=[
            ("x", Immediate(value=0)),
        ],
        body=Reference(name="x"),
    )

    actual = parse_term(source)

    assert actual == expected


# Reference
def test_parse_reference():
    source = "x"

    expected = Reference(
        name="x",
    )

    actual = parse_term(source)

    assert actual == expected


# Abstract
def test_parse_abstract():
    source = "(\\ (x) x)"

    expected = Abstract(
        parameters=["x"],
        body=Reference(name="x"),
    )

    actual = parse_term(source)

    assert actual == expected


# Apply
def test_parse_apply_empty():
    source = "(x)"

    expected = Apply(
        target=Reference(name="x"),
        arguments=[],
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_apply_arguments():
    source = "(x y z)"

    expected = Apply(
        target=Reference(name="x"),
        arguments=[Reference(name="y"), Reference(name="z")],
    )

    actual = parse_term(source)

    assert actual == expected


# Immediate
def test_parse_immediate():
    source = "42"

    expected = Immediate(value=42)

    actual = parse_term(source)

    assert actual == expected


# Primitive
def test_parse_add():
    source = "(+ 1 2)"

    expected = Primitive(
        operator="+",
        left=Immediate(value=1),
        right=Immediate(value=2),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_subtract():
    source = "(- 3 2)"

    expected = Primitive(
        operator="-",
        left=Immediate(value=3),
        right=Immediate(value=2),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_multiply():
    source = "(* 2 3)"
    expected = Primitive(
        operator="*",
        left=Immediate(value=2),
        right=Immediate(value=3),
    )
    actual = parse_term(source)
    assert actual == expected


def test_parse_divide():
    source = "(/ 10 3)"
    expected = Primitive(
        operator="/",
        left=Immediate(value=10),
        right=Immediate(value=3),
    )
    actual = parse_term(source)
    assert actual == expected


def test_parse_modulo():
    source = "(% 10 3)"
    expected = Primitive(
        operator="%",
        left=Immediate(value=10),
        right=Immediate(value=3),
    )
    actual = parse_term(source)
    assert actual == expected


# Branch
def test_parse_less_than():
    source = "(if (< 1 2) 1 0)"

    expected = Branch(
        operator="<",
        left=Immediate(value=1),
        right=Immediate(value=2),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_equal_to():
    source = "(if (== 1 1) 1 0)"

    expected = Branch(
        operator="==",
        left=Immediate(value=1),
        right=Immediate(value=1),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_greater_than():
    source = "(if (> 5 3) 1 0)"

    expected = Branch(
        operator=">",
        left=Immediate(value=5),
        right=Immediate(value=3),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_greater_equal():
    source = "(if (>= 5 5) 1 0)"

    expected = Branch(
        operator=">=",
        left=Immediate(value=5),
        right=Immediate(value=5),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_less_equal():
    source = "(if (<= 3 5) 1 0)"

    expected = Branch(
        operator="<=",
        left=Immediate(value=3),
        right=Immediate(value=5),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_not_equal():
    source = "(if (!= 3 5) 1 0)"

    expected = Branch(
        operator="!=",
        left=Immediate(value=3),
        right=Immediate(value=5),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = parse_term(source)

    assert actual == expected


# Booleans
def test_parse_true():
    source = "#t"

    expected = Bool(value=True)

    actual = parse_term(source)

    assert actual == expected


def test_parse_false():
    source = "#f"

    expected = Bool(value=False)

    actual = parse_term(source)

    assert actual == expected


def test_parse_and():
    source = "(and #t #f)"

    expected = And(
        left=Bool(value=True),
        right=Bool(value=False),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_or():
    source = "(or #f #t)"

    expected = Or(
        left=Bool(value=False),
        right=Bool(value=True),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_not():
    source = "(not #t)"

    expected = Not(value=Bool(value=True))

    actual = parse_term(source)

    assert actual == expected


def test_parse_if_term():
    source = "(if #t 1 0)"

    expected = If(
        condition=Bool(value=True),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_if_term_with_variable():
    source = "(if x 1 0)"

    expected = If(
        condition=Reference(name="x"),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    actual = parse_term(source)

    assert actual == expected


# Print
def test_parse_print():
    source = "(print 42)"

    expected = Print(value=Immediate(value=42))

    actual = parse_term(source)

    assert actual == expected


def test_parse_print_variable():
    source = "(print x)"

    expected = Print(value=Reference(name="x"))

    actual = parse_term(source)

    assert actual == expected


# Strings
def test_parse_string_literal():
    source = '"hello world"'

    expected = StringLiteral(value="hello world")

    actual = parse_term(source)

    assert actual == expected


def test_parse_string_length():
    source = '(string-length "hello")'

    expected = StringLength(value=StringLiteral(value="hello"))

    actual = parse_term(source)

    assert actual == expected


def test_parse_string_ref():
    source = '(string-ref "hello" 0)'

    expected = Primitive(
        operator="string-ref",
        left=StringLiteral(value="hello"),
        right=Immediate(value=0),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_string_append():
    source = '(string-append "hello " "world")'

    expected = Primitive(
        operator="string-append",
        left=StringLiteral(value="hello "),
        right=StringLiteral(value="world"),
    )

    actual = parse_term(source)

    assert actual == expected


# Allocate
def test_parse_allocate():
    source = "(allocate 0)"

    expected = Allocate(
        count=0,
    )

    actual = parse_term(source)

    assert actual == expected


# Load
def test_parse_load():
    source = "(load x 0)"

    expected = Load(
        base=Reference(name="x"),
        index=0,
    )

    actual = parse_term(source)

    assert actual == expected


# Store
def test_parse_store():
    source = "(store x 0 1)"

    expected = Store(
        base=Reference(name="x"),
        index=0,
        value=Immediate(value=1),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_begin():
    source = "(begin x)"

    expected = Begin(
        effects=[],
        value=Reference(name="x"),
    )

    actual = parse_term(source)

    assert actual == expected


def test_parse_begin_effects():
    source = "(begin x y z)"

    expected = Begin(
        effects=[
            Reference(name="x"),
            Reference(name="y"),
        ],
        value=Reference(name="z"),
    )

    actual = parse_term(source)

    assert actual == expected


# Program
def test_parse_program_identity():
    source = "(l3 (x) x)"

    expected = Program(
        parameters=["x"],
        body=Reference(name="x"),
    )

    actual = parse_program(source)

    assert actual == expected
