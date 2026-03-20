from L3.syntax import (
    Abstract,
    Allocate,
    Apply,
    Begin,
    Branch,
    Immediate,
    Let,
    LetRec,
    Load,
    Primitive,
    Program,
    Reference,
    Store,
)
from L3.uniqify import Context, uniqify_program, uniqify_term
from util.sequential_name_generator import SequentialNameGenerator


def test_uniqify_term_reference():
    term = Reference(name="x")

    context: Context = {"x": "y"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh=fresh)

    expected = Reference(name="y")

    assert actual == expected


def test_uniqify_immediate():
    term = Immediate(value=42)

    context: Context = dict[str, str]()
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Immediate(value=42)

    assert actual == expected


def test_uniqify_term_let():
    term = Let(
        bindings=[
            ("x", Immediate(value=1)),
            ("y", Reference(name="x")),
        ],
        body=Apply(
            target=Reference(name="x"),
            arguments=[
                Reference(name="y"),
            ],
        ),
    )

    context: Context = {"x": "y"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Let(
        bindings=[
            ("x0", Immediate(value=1)),
            ("y0", Reference(name="y")),
        ],
        body=Apply(
            target=Reference(name="x0"),
            arguments=[
                Reference(name="y0"),
            ],
        ),
    )

    assert actual == expected


# LetRec Tests
def test_uniqify_term_letrec():
    term = LetRec(
        bindings=[
            ("f", Reference(name="f")),
        ],
        body=Reference(name="f"),
    )

    context: Context = {}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = LetRec(
        bindings=[
            ("f0", Reference(name="f0")),
        ],
        body=Reference(name="f0"),
    )

    assert actual == expected


def test_uniqify_term_letrec_mutual_recursion():
    term = LetRec(
        bindings=[
            ("f", Reference(name="g")),
            ("g", Reference(name="f")),
        ],
        body=Reference(name="f"),
    )

    context: Context = {}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = LetRec(
        bindings=[
            ("f0", Reference(name="g0")),
            ("g0", Reference(name="f0")),
        ],
        body=Reference(name="f0"),
    )

    assert actual == expected


def test_uniqify_term_letrec_with_outer_context():
    term = LetRec(
        bindings=[
            ("x", Reference(name="y")),
        ],
        body=Reference(name="x"),
    )

    context: Context = {"y": "z"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = LetRec(
        bindings=[
            ("x0", Reference(name="z")),
        ],
        body=Reference(name="x0"),
    )

    assert actual == expected


# Abstract Tests
def test_uniqify_term_abstract():
    term = Abstract(
        parameters=["x"],
        body=Reference(name="x"),
    )

    context: Context = {}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Abstract(
        parameters=["x0"],
        body=Reference(name="x0"),
    )

    assert actual == expected


def test_uniqify_term_abstract_multiple_parameters():
    term = Abstract(
        parameters=["x", "y"],
        body=Primitive(
            operator="+",
            left=Reference(name="x"),
            right=Reference(name="y"),
        ),
    )

    context: Context = {}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Abstract(
        parameters=["x0", "y0"],
        body=Primitive(
            operator="+",
            left=Reference(name="x0"),
            right=Reference(name="y0"),
        ),
    )

    assert actual == expected


def test_uniqify_term_abstract_shadows_outer():
    term = Abstract(
        parameters=["x"],
        body=Reference(name="x"),
    )

    context: Context = {"x": "outer"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Abstract(
        parameters=["x0"],
        body=Reference(name="x0"),
    )

    assert actual == expected


def test_uniqify_term_abstract_preserves_outer():
    term = Abstract(
        parameters=["x"],
        body=Reference(name="y"),
    )

    context: Context = {"y": "z"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Abstract(
        parameters=["x0"],
        body=Reference(name="z"),
    )

    assert actual == expected


# Apply Tests
def test_uniqify_term_apply():
    term = Apply(
        target=Reference(name="f"),
        arguments=[Reference(name="x")],
    )

    context: Context = {"f": "f0", "x": "x0"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Apply(
        target=Reference(name="f0"),
        arguments=[Reference(name="x0")],
    )

    assert actual == expected


def test_uniqify_term_apply_no_arguments():
    term = Apply(
        target=Reference(name="f"),
        arguments=[],
    )

    context: Context = {"f": "f0"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Apply(
        target=Reference(name="f0"),
        arguments=[],
    )

    assert actual == expected


# Primitive Tests
def test_uniqify_term_primitive():
    term = Primitive(
        operator="+",
        left=Reference(name="x"),
        right=Reference(name="y"),
    )

    context: Context = {"x": "x0", "y": "y0"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Primitive(
        operator="+",
        left=Reference(name="x0"),
        right=Reference(name="y0"),
    )

    assert actual == expected


def test_uniqify_term_primitive_with_immediates():
    term = Primitive(
        operator="*",
        left=Immediate(value=2),
        right=Immediate(value=3),
    )

    context: Context = {}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Primitive(
        operator="*",
        left=Immediate(value=2),
        right=Immediate(value=3),
    )

    assert actual == expected


# Branch Tests
def test_uniqify_term_branch():
    term = Branch(
        operator="<",
        left=Reference(name="x"),
        right=Reference(name="y"),
        consequent=Reference(name="a"),
        otherwise=Reference(name="b"),
    )

    context: Context = {"x": "x0", "y": "y0", "a": "a0", "b": "b0"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Branch(
        operator="<",
        left=Reference(name="x0"),
        right=Reference(name="y0"),
        consequent=Reference(name="a0"),
        otherwise=Reference(name="b0"),
    )

    assert actual == expected


def test_uniqify_term_branch_with_immediates():
    term = Branch(
        operator="==",
        left=Immediate(value=1),
        right=Immediate(value=2),
        consequent=Immediate(value=10),
        otherwise=Immediate(value=20),
    )

    context: Context = {}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Branch(
        operator="==",
        left=Immediate(value=1),
        right=Immediate(value=2),
        consequent=Immediate(value=10),
        otherwise=Immediate(value=20),
    )

    assert actual == expected


# Allocate Tests
def test_uniqify_term_allocate():
    term = Allocate(count=3)

    context: Context = {}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Allocate(count=3)

    assert actual == expected


# Load Tests
def test_uniqify_term_load():
    term = Load(
        base=Reference(name="arr"),
        index=2,
    )

    context: Context = {"arr": "arr0"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Load(
        base=Reference(name="arr0"),
        index=2,
    )

    assert actual == expected


# Store Tests
def test_uniqify_term_store():
    term = Store(
        base=Reference(name="arr"),
        index=0,
        value=Reference(name="x"),
    )

    context: Context = {"arr": "arr0", "x": "x0"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Store(
        base=Reference(name="arr0"),
        index=0,
        value=Reference(name="x0"),
    )

    assert actual == expected


# Begin Tests
def test_uniqify_term_begin():
    term = Begin(
        effects=[Reference(name="x")],
        value=Reference(name="y"),
    )

    context: Context = {"x": "x0", "y": "y0"}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Begin(
        effects=[Reference(name="x0")],
        value=Reference(name="y0"),
    )

    assert actual == expected


def test_uniqify_term_begin_empty_effects():
    term = Begin(
        effects=[],
        value=Immediate(value=5),
    )

    context: Context = {}
    fresh = SequentialNameGenerator()
    actual = uniqify_term(term, context, fresh)

    expected = Begin(
        effects=[],
        value=Immediate(value=5),
    )

    assert actual == expected


# Program Tests
def test_uniqify_program_simple():
    program = Program(
        parameters=["x"],
        body=Reference(name="x"),
    )

    _, actual = uniqify_program(program)

    expected = Program(
        parameters=["x0"],
        body=Reference(name="x0"),
    )

    assert actual == expected


def test_uniqify_program_multiple_parameters():
    program = Program(
        parameters=["x", "y"],
        body=Primitive(
            operator="+",
            left=Reference(name="x"),
            right=Reference(name="y"),
        ),
    )

    _, actual = uniqify_program(program)

    expected = Program(
        parameters=["x0", "y0"],
        body=Primitive(
            operator="+",
            left=Reference(name="x0"),
            right=Reference(name="y0"),
        ),
    )

    assert actual == expected


def test_uniqify_program_no_parameters():
    program = Program(
        parameters=[],
        body=Immediate(value=42),
    )

    _, actual = uniqify_program(program)

    expected = Program(
        parameters=[],
        body=Immediate(value=42),
    )

    assert actual == expected


def test_uniqify_program_nested_let():
    program = Program(
        parameters=["x"],
        body=Let(
            bindings=[("y", Reference(name="x"))],
            body=Reference(name="y"),
        ),
    )

    _, actual = uniqify_program(program)

    expected = Program(
        parameters=["x0"],
        body=Let(
            bindings=[("y0", Reference(name="x0"))],
            body=Reference(name="y0"),
        ),
    )

    assert actual == expected
