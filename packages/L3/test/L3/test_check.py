import pytest
from L3.check import Context, check_program, check_term
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

# Let Tests
def test_check_term_let():
    term = Let(
        bindings=[
            ("x", Immediate(value=0)),
        ],
        body=Reference(name="x"),
    )

    context: Context = {}

    check_term(term, context)

def test_check_term_let_scope():
    term = Let(
        bindings=[
            ("x", Immediate(value=0)),
            ("y", Reference(name="x")),
        ],
        body=Reference(name="y"),
    )

    context: Context = {}

    with pytest.raises(ValueError):
        check_term(term, context)

def test_check_term_let_duplicate_binders():
    term = Let(
        bindings=[
            ("x", Immediate(value=0)),
            ("x", Immediate(value=1)),
        ],
        body=Reference(name="x"),
    )

    context: Context = {}

    with pytest.raises(ValueError):
        check_term(term, context)

def test_check_term_let_multiple_bindings():
    term = Let(
        bindings=[
            ("x", Immediate(value=1)),
            ("y", Immediate(value=2)),
            ("z", Immediate(value=3)),
        ],
        body=Reference(name="z"),
    )
    check_term(term, {})

def test_check_term_let_binding_fail_sibling():
    term = Let(
        bindings=[
            ("a", Immediate(value=0)),
            ("b", Reference(name="a")),
        ],
        body=Reference(name="b"),
    )
    with pytest.raises(ValueError):
        check_term(term, {})


def test_check_term_let_body_null_variable():
    term = Let(
        bindings=[("x", Immediate(value=0))],
        body=Reference(name="z"),
    )
    with pytest.raises(ValueError):
        check_term(term, {})

def test_check_term_let_more_duplicate_binders():
    term = Let(
        bindings=[
            ("x", Immediate(value=0)),
            ("x", Immediate(value=1)),
            ("x", Immediate(value=2)),
        ],
        body=Reference(name="x"),
    )
    with pytest.raises(ValueError):
        check_term(term, {})




# Letrec Tests
def test_check_term_letrec():
    term = LetRec(
        bindings=[
            ("x", Immediate(value=0)),
        ],
        body=Reference(name="x"),
    )

    context: Context = {}

    check_term(term, context)


def test_check_term_letrec_scope():
    term = LetRec(
        bindings=[
            ("y", Reference(name="x")),
            ("x", Immediate(value=0)),
        ],
        body=Reference(name="x"),
    )

    context: Context = {}

    check_term(term, context)


def test_check_term_letrec_duplicate_binders():
    term = LetRec(
        bindings=[
            ("x", Immediate(value=0)),
            ("x", Immediate(value=1)),
        ],
        body=Reference(name="x"),
    )

    context: Context = {}

    with pytest.raises(ValueError):
        check_term(term, context)



def test_check_term_letrec_self_reference():
    term = LetRec(
        bindings=[("x", Reference(name="x"))],
        body=Reference(name="x"),
    )

    check_term(term, {})


def test_check_term_letrec_dual_reference():
    term = LetRec(
        bindings=[
            ("x", Reference(name="y")),
            ("y", Reference(name="x")),
        ],
        body=Reference(name="x"),
    )

    check_term(term, {})


def test_check_term_letrec_body_null_variable():
    term = LetRec(
        bindings=[("x", Immediate(value=0))],
        body=Reference(name="z"),
    )

    with pytest.raises(ValueError):
        check_term(term, {})


# Reference Tests
def test_check_term_reference_bound():
    term = Reference(name="x")

    context: Context = {
        "x": None,
    }

    check_term(term, context)


def test_check_term_reference_free():
    term = Reference(name="x")

    context: Context = {}

    with pytest.raises(ValueError):
        check_term(term, context)

def test_check_term_reference_wrong_name():
    term = Reference(name="xx")

    context: Context = {
        "x": None,
    }
    with pytest.raises(ValueError):

        check_term(term, context)


# Abstract Tests
def test_check_term_abstract():
    term = Abstract(
        parameters=["x"],
        body=Immediate(value=0),
    )

    context: Context = {}

    check_term(term, context)

def test_check_term_abstract_duplicate_parameters():
    term = Abstract(
        parameters=["x", "x"],
        body=Immediate(value=0),
    )

    context: Context = {}

    with pytest.raises(ValueError):
        check_term(term, context)


def test_check_term_abstract_outer_context():
    term = Abstract(
        parameters=["x"],
        body=Reference(name="outer")
    )
    check_term(term, {"outer": None})


def test_check_term_abstract_null_variable_in_body():
    term = Abstract(
        parameters=["x"],
        body=Reference(name="y")
    )

    with pytest.raises(ValueError):
        check_term(term, {})


def test_check_term_abstract_no_parameters():
    term = Abstract(
        parameters=[],
        body=Immediate(value=0)
    )

    check_term(term, {})

# Apply Tests
def test_check_term_apply():
    term = Apply(
        target=Reference(name="x"),
        arguments=[Immediate(value=0)],
    )

    context: Context = {
        "x": None,
    }

    check_term(term, context)

def test_check_term_apply_no_arguments():
    term = Apply(
        target=Reference(name="x"),
                 arguments=[]
                 )
    check_term(term, {"x": None})



def test_check_term_apply_null_target():
    term = Apply(
        target=Reference(name="x"),
        arguments=[]
    )

    with pytest.raises(ValueError):
        check_term(term, {})


def test_check_term_apply_null_argument():
    term = Apply(
        target=Immediate(value=0),
        arguments=[Reference(name="missing")],
    )

    with pytest.raises(ValueError):
        check_term(term, {})


# Immediate Tests
def test_check_term_immediate():
    term = Immediate(value=0)

    context: Context = {}

    check_term(term, context)

# Primitive Tests
def test_check_term_primitive():
    term = Primitive(
        operator="+",
        left=Immediate(value=1),
        right=Immediate(value=2),
    )

    context: Context = {}

    check_term(term, context)

def test_check_term_primitive_subtraction():
    term = Primitive(
        operator="-",
        left=Immediate(value=3),
        right=Immediate(value=2)
    )

    context: Context = {}

    check_term(term, context)


def test_check_term_primitive_multiplication():
    term = Primitive(
        operator="*",
        left=Immediate(value=2),
        right=Immediate(value=3)
    )

    context: Context = {}

    check_term(term, context)


def test_check_term_primitive_null_left():
    term = Primitive(
        operator="+",
        left=Reference(name="x"),
        right=Immediate(value=1)
    )

    context: Context = {}

    with pytest.raises(ValueError):
        check_term(term, context)


def test_check_term_primitive_null_right():
    term = Primitive(
        operator="+",
        left=Immediate(value=1),
        right=Reference(name="x")
    )

    context: Context = {}

    with pytest.raises(ValueError):
        check_term(term, context)


def test_check_term_primitive_nested():
    term = Primitive(
        operator="+",
        left=Primitive(
            operator="*",
            left=Immediate(value=2),
            right=Immediate(value=3)
        ),
        right=Immediate(value=1),
    )
    check_term(term, {})


# Branch Tests
def test_check_term_branch():
    term = Branch(
        operator="<",
        left=Immediate(value=1),
        right=Immediate(value=2),
        consequent=Immediate(value=0),
        otherwise=Immediate(value=1),
    )

    context: Context = {}

    check_term(term, context)

def test_check_term_branch_not_less():
    term = Branch(
        operator="<",
        left=Immediate(value=2),
        right=Immediate(value=1),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    context: Context = {}

    check_term(term, context)

def test_check_term_branch_equal():
    term = Branch(
        operator="==",
        left=Immediate(value=1),
        right=Immediate(value=1),
        consequent=Immediate(value=0),
        otherwise=Immediate(value=1),
    )

    context: Context = {}

    check_term(term, context)

def test_check_term_branch_not_equal():
    term = Branch(
        operator="==",
        left=Immediate(value=1),
        right=Immediate(value=2),
        consequent=Immediate(value=1),
        otherwise=Immediate(value=0),
    )

    context: Context = {}

    check_term(term, context)

def test_check_term_branch_null_right():
    term = Branch(
        operator="<",
        left=Immediate(value=1),
        right=Reference(name="x"),
        consequent=Immediate(value=0),
        otherwise=Immediate(value=1),
    )
    with pytest.raises(ValueError):
        check_term(term, {})

# Allocate Tests
def test_check_term_allocate():
    term = Allocate(count=0)

    context: Context = {}

    check_term(term, context)

def test_check_term_allocate_with_context():
    term = Allocate(count=0)

    context: Context = {
        "x": None
    }
    check_term(term, context)


# Load Tests
def test_check_term_load():
    term = Load(
        base=Reference(name="x"),
        index=0,
    )

    context: Context = {
        "x": None,
    }

    check_term(term, context)


def test_check_term_load_free_base():
    term = Load(
        base=Reference(name="missing"),
        index=0
    )

    context: Context = {}

    with pytest.raises(ValueError):
        check_term(term, context)


# Store Tests
def test_check_term_store():
    term = Store(
        base=Reference(name="x"),
        index=0,
        value=Immediate(value=0),
    )

    context: Context = {
        "x": None,
    }

    check_term(term, context)

def test_check_term_store_invalid_context():
    term = Store(
        base=Reference(name="y"),
        index=0,
        value=Immediate(value=0),
    )

    context: Context = {
        "x": None,
    }

    with pytest.raises(ValueError):
        check_term(term, context)


# Begin Tests
def test_check_term_begin():
    term = Begin(
        effects=[Immediate(value=0)],
        value=Immediate(value=0),
    )

    context: Context = {}

    check_term(term, context)

def test_check_term_begin_empty_effects():
    term = Begin(
        effects=[], value=Immediate(value=0)
    )
    check_term(term, {})


def test_check_term_begin_null_effect():
    term = Begin(
        effects=[Reference(name="missing")],
        value=Immediate(value=0),
    )
    with pytest.raises(ValueError):
        check_term(term, {})


def test_check_term_begin_null_value():
    term = Begin(
        effects=[Immediate(value=0)],
        value=Reference(name="missing"),
    )
    with pytest.raises(ValueError):
        check_term(term, {})

# Program Tests
def test_check_program():
    program = Program(
        parameters=[],
        body=Immediate(value=0),
    )

    check_program(program)


def test_check_program_duplicate_parameters():
    program = Program(
        parameters=["x", "x"],
        body=Immediate(value=0),
    )

    with pytest.raises(ValueError):
        check_program(program)



def test_check_program_one_parameter():
    program = Program(
        parameters=["x"], body=Reference(name="x")
    )

    check_program(program)



def test_check_program_null_variable_in_body():
    program = Program(
        parameters=["x"], body=Reference(name="null")
    )

    with pytest.raises(ValueError):
        check_program(program)

def test_check_program_empty_parameters():
    program = Program(
        parameters=[], body=Immediate(value=0)
    )

    check_program(program)