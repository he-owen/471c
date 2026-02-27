import pytest
from L2 import syntax as L2
from L3 import syntax as L3
from L3.eliminate_letrec import Context, eliminate_letrec_program, eliminate_letrec_term


@pytest.mark.skip
def test_check_term_let():
    term = L3.Let(
        bindings=[
            ("x", L3.Immediate(value=0)),
        ],
        body=L3.Reference(name="x"),
    )

    context: Context = {}

    expected = L2.Let(
        bindings=[
            ("x", L2.Immediate(value=0)),
        ],
        body=L2.Reference(name="x"),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected


@pytest.mark.skip
def test_eliminate_letrec_program():
    program = L3.Program(
        parameters=[],
        body=L3.Immediate(value=0),
    )

    expected = L2.Program(
        parameters=[],
        body=L2.Immediate(value=0),
    )

    actual = eliminate_letrec_program(program)

    assert actual == expected


# Let Tests
def test_eliminate_letrec_term_let():
    term = L3.Let(
        bindings=[
            ("x", L3.Immediate(value=0)),
        ],
        body=L3.Reference(name="x"),
    )

    context: Context = {}

    expected = L2.Let(
        bindings=[
            ("x", L2.Immediate(value=0)),
        ],
        body=L2.Reference(name="x"),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected

def test_eliminate_letrec_term_let_multiple_bindings():
    term = L3.Let(
        bindings=[
            ("x", L3.Immediate(value=1)),
            ("y", L3.Immediate(value=2)),
        ],
        body=L3.Primitive(operator="+", left=L3.Reference(name="x"), right=L3.Reference(name="y")),
    )

    context: Context = {}

    expected = L2.Let(
        bindings=[
            ("x", L2.Immediate(value=1)),
            ("y", L2.Immediate(value=2)),
        ],
        body=L2.Primitive(operator="+", left=L2.Reference(name="x"), right=L2.Reference(name="y")),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected

def test_eliminate_letrec_term_let_shadows_letrec_context():
    term = L3.Let(
        bindings=[("x", L3.Immediate(value=5))],
        body=L3.Reference(name="x"),
    )

    context: Context = {"x": None}

    expected = L2.Let(
        bindings=[("x", L2.Immediate(value=5))],
        body=L2.Reference(name="x"),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected


# LetRec Tests
def test_eliminate_letrec_term_letrec():
    term = L3.LetRec(
        bindings=[("f", L3.Immediate(value=42))],
        body=L3.Reference(name="f"),
    )

    context: Context = {}

    expected = L2.Let(
        bindings=[("f", L2.Allocate(count=1))],
        body=L2.Begin(
            effects=[
                L2.Store(base=L2.Reference(name="f"), index=0, value=L2.Immediate(value=42)),
            ],
            value=L2.Load(base=L2.Reference(name="f"), index=0),
        ),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected

def test_eliminate_letrec_term_letrec_self_reference():
    term = L3.LetRec(
        bindings=[
            ("f", L3.Abstract(
                parameters=["x"],
                body=L3.Apply(
                    target=L3.Reference(name="f"),
                    arguments=[L3.Reference(name="x")],
                ),
            )),
        ],
        body=L3.Apply(target=L3.Reference(name="f"), arguments=[L3.Immediate(value=0)]),
    )

    context: Context = {}

    expected = L2.Let(
        bindings=[("f", L2.Allocate(count=1))],
        body=L2.Begin(
            effects=[
                L2.Store(
                    base=L2.Reference(name="f"),
                    index=0,
                    value=L2.Abstract(
                        parameters=["x"],
                        body=L2.Apply(
                            target=L2.Load(base=L2.Reference(name="f"), index=0),
                            arguments=[L2.Reference(name="x")],
                        ),
                    ),
                ),
            ],
            value=L2.Apply(
                target=L2.Load(base=L2.Reference(name="f"), index=0),
                arguments=[L2.Immediate(value=0)],
            ),
        ),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected

# Reference Tests
def test_eliminate_letrec_term_reference():
    term = L3.Reference(name="x")

    context: Context = {}

    actual = eliminate_letrec_term(term, context)

    assert actual == L2.Reference(name="x")

def test_eliminate_letrec_term_reference_recursive():
    term = L3.Reference(name="x")

    context: Context = {"x": None}

    actual = eliminate_letrec_term(term, context)

    assert actual == L2.Load(base=L2.Reference(name="x"), index=0)


# Abstract Tests
def test_eliminate_letrec_term_abstract():
    term = L3.Abstract(
        parameters=["x"],
        body=L3.Reference(name="x"),
    )

    context: Context = {}

    expected = L2.Abstract(
        parameters=["x"],
        body=L2.Reference(name="x"),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected

def test_eliminate_letrec_term_abstract_shadows_context():
    term = L3.Abstract(
        parameters=["x"],
        body=L3.Reference(name="x"),
    )

    context: Context = {"x": None}

    expected = L2.Abstract(
        parameters=["x"],
        body=L2.Reference(name="x"),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected

def test_eliminate_letrec_term_abstract_preserves_outer_context():
    term = L3.Abstract(
        parameters=["x"],
        body=L3.Reference(name="f"),
    )

    context: Context = {"f": None}

    expected = L2.Abstract(
        parameters=["x"],
        body=L2.Load(base=L2.Reference(name="f"), index=0),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected


# Apply Tests
def test_eliminate_letrec_term_apply():
    term = L3.Apply(
        target=L3.Reference(name="f"),
        arguments=[L3.Immediate(value=1), L3.Immediate(value=2)],
    )

    context: Context = {"f": None}

    expected = L2.Apply(
        target=L2.Load(base=L2.Reference(name="f"), index=0),
        arguments=[L2.Immediate(value=1), L2.Immediate(value=2)],
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected

def test_eliminate_letrec_term_apply_no_arguments():
    term = L3.Apply(
        target=L3.Reference(name="f"),
        arguments=[],
    )

    context: Context = {}

    expected = L2.Apply(
        target=L2.Reference(name="f"),
        arguments=[],
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected


# Immediate Tests
def test_eliminate_letrec_term_immediate():
    term = L3.Immediate(value=42)

    context: Context = {}

    actual = eliminate_letrec_term(term, context)

    assert actual == L2.Immediate(value=42)


# Primitive Tests
def test_eliminate_letrec_term_primitive():
    term = L3.Primitive(
        operator="+",
        left=L3.Immediate(value=1),
        right=L3.Immediate(value=2),
    )

    context: Context = {}

    expected = L2.Primitive(
        operator="+",
        left=L2.Immediate(value=1),
        right=L2.Immediate(value=2),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected

def test_eliminate_letrec_term_primitive_with_recursive_ref():
    term = L3.Primitive(
        operator="*",
        left=L3.Reference(name="x"),
        right=L3.Reference(name="y"),
    )

    context: Context = {"x": None}

    expected = L2.Primitive(
        operator="*",
        left=L2.Load(base=L2.Reference(name="x"), index=0),
        right=L2.Reference(name="y"),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected


# Branch Tests
def test_eliminate_letrec_term_branch():
    term = L3.Branch(
        operator="<",
        left=L3.Immediate(value=1),
        right=L3.Immediate(value=2),
        consequent=L3.Immediate(value=10),
        otherwise=L3.Immediate(value=20),
    )

    context: Context = {}

    expected = L2.Branch(
        operator="<",
        left=L2.Immediate(value=1),
        right=L2.Immediate(value=2),
        consequent=L2.Immediate(value=10),
        otherwise=L2.Immediate(value=20),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected


# Allocate Tests
def test_eliminate_letrec_term_allocate():
    term = L3.Allocate(count=3)

    context: Context = {}

    actual = eliminate_letrec_term(term, context)

    assert actual == L2.Allocate(count=3)


# Load Tests
def test_eliminate_letrec_term_load():
    term = L3.Load(
        base=L3.Reference(name="arr"),
        index=2,
    )

    context: Context = {}

    expected = L2.Load(
        base=L2.Reference(name="arr"),
        index=2,
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected


# Store Tests
def test_eliminate_letrec_term_store():
    term = L3.Store(
        base=L3.Reference(name="arr"),
        index=0,
        value=L3.Immediate(value=99),
    )

    context: Context = {}

    expected = L2.Store(
        base=L2.Reference(name="arr"),
        index=0,
        value=L2.Immediate(value=99),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected


# Begin Tests
def test_eliminate_letrec_term_begin():
    term = L3.Begin(
        effects=[L3.Immediate(value=0)],
        value=L3.Immediate(value=1),
    )

    context: Context = {}

    expected = L2.Begin(
        effects=[L2.Immediate(value=0)],
        value=L2.Immediate(value=1),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected

def test_eliminate_letrec_term_begin_empty_effects():
    term = L3.Begin(
        effects=[],
        value=L3.Immediate(value=5),
    )

    context: Context = {}

    expected = L2.Begin(
        effects=[],
        value=L2.Immediate(value=5),
    )

    actual = eliminate_letrec_term(term, context)

    assert actual == expected


# Program Tests
def test_eliminate_letrec_program_immediate():
    program = L3.Program(
        parameters=[],
        body=L3.Immediate(value=0),
    )

    expected = L2.Program(
        parameters=[],
        body=L2.Immediate(value=0),
    )

    actual = eliminate_letrec_program(program)

    assert actual == expected

def test_eliminate_letrec_program_with_params():
    program = L3.Program(
        parameters=["x", "y"],
        body=L3.Primitive(operator="+", left=L3.Reference(name="x"), right=L3.Reference(name="y")),
    )

    expected = L2.Program(
        parameters=["x", "y"],
        body=L2.Primitive(operator="+", left=L2.Reference(name="x"), right=L2.Reference(name="y")),
    )

    actual = eliminate_letrec_program(program)

    assert actual == expected
