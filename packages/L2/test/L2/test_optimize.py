from L2.optimize import Environment, free_variables, optimize_program, optimize_term
from L2.syntax import (
    Abstract,
    Allocate,
    Apply,
    Begin,
    Branch,
    Immediate,
    Let,
    Load,
    Primitive,
    Program,
    Reference,
    Store,
)


# free_variables tests


def test_free_variables_immediate():
    assert free_variables(Immediate(value=1)) == set()


def test_free_variables_allocate():
    assert free_variables(Allocate(count=2)) == set()


def test_free_variables_reference():
    assert free_variables(Reference(name="x")) == {"x"}


def test_free_variables_let():
    term = Let(
        bindings=[("x", Reference(name="a")), ("y", Reference(name="x"))],
        body=Reference(name="y"),
    )
    assert free_variables(term) == {"a"}


def test_free_variables_abstract():
    term = Abstract(parameters=["x"], body=Reference(name="x"))
    assert free_variables(term) == set()


def test_free_variables_apply():
    term = Apply(target=Reference(name="f"), arguments=[Reference(name="a")])
    assert free_variables(term) == {"f", "a"}


def test_free_variables_primitive():
    term = Primitive(operator="+", left=Reference(name="x"), right=Reference(name="y"))
    assert free_variables(term) == {"x", "y"}


def test_free_variables_branch():
    term = Branch(
        operator="<",
        left=Reference(name="a"),
        right=Reference(name="b"),
        consequent=Reference(name="c"),
        otherwise=Reference(name="d"),
    )
    assert free_variables(term) == {"a", "b", "c", "d"}


def test_free_variables_load():
    assert free_variables(Load(base=Reference(name="x"), index=0)) == {"x"}


def test_free_variables_store():
    assert free_variables(Store(base=Reference(name="x"), index=0, value=Reference(name="v"))) == {"x", "v"}


def test_free_variables_begin():
    term = Begin(effects=[Reference(name="x")], value=Reference(name="y"))
    assert free_variables(term) == {"x", "y"}


# optimize_term tests


def test_optimize_term_immediate():
    assert optimize_term(Immediate(value=42), {}) == Immediate(value=42)


def test_optimize_term_reference():
    assert optimize_term(Reference(name="x"), {}) == Reference(name="x")


def test_optimize_term_reference_in_env():
    env: Environment = {"x": Immediate(value=7)}
    assert optimize_term(Reference(name="x"), env) == Immediate(value=7)


def test_optimize_term_copy_propagation():
    env: Environment = {"x": Reference(name="y")}
    assert optimize_term(Reference(name="x"), env) == Reference(name="y")


def test_optimize_term_allocate():
    assert optimize_term(Allocate(count=3), {}) == Allocate(count=3)


def test_optimize_term_apply():
    term = Apply(target=Reference(name="f"), arguments=[Reference(name="x")])
    env: Environment = {"x": Immediate(value=5)}

    actual = optimize_term(term, env)

    expected = Apply(target=Reference(name="f"), arguments=[Immediate(value=5)])
    assert actual == expected


def test_optimize_term_load():
    term = Load(base=Reference(name="x"), index=0)
    env: Environment = {"x": Reference(name="arr")}
    assert optimize_term(term, env) == Load(base=Reference(name="arr"), index=0)


def test_optimize_term_store():
    term = Store(base=Reference(name="x"), index=0, value=Immediate(value=1))
    env: Environment = {"x": Reference(name="arr")}
    assert optimize_term(term, env) == Store(base=Reference(name="arr"), index=0, value=Immediate(value=1))


def test_optimize_term_begin():
    term = Begin(effects=[Reference(name="x")], value=Reference(name="y"))
    env: Environment = {"x": Immediate(value=1)}

    actual = optimize_term(term, env)

    expected = Begin(effects=[Immediate(value=1)], value=Reference(name="y"))
    assert actual == expected


def test_optimize_term_abstract():
    term = Abstract(parameters=["x"], body=Reference(name="y"))
    env: Environment = {"y": Immediate(value=10)}

    actual = optimize_term(term, env)

    assert actual == Abstract(parameters=["x"], body=Immediate(value=10))


def test_optimize_term_abstract_shadows():
    term = Abstract(parameters=["x"], body=Reference(name="x"))
    env: Environment = {"x": Immediate(value=99)}

    actual = optimize_term(term, env)

    assert actual == Abstract(parameters=["x"], body=Reference(name="x"))


# Constant Folding


def test_fold_add():
    term = Primitive(operator="+", left=Immediate(value=3), right=Immediate(value=4))
    assert optimize_term(term, {}) == Immediate(value=7)


def test_fold_sub():
    term = Primitive(operator="-", left=Immediate(value=10), right=Immediate(value=3))
    assert optimize_term(term, {}) == Immediate(value=7)


def test_fold_mul():
    term = Primitive(operator="*", left=Immediate(value=3), right=Immediate(value=5))
    assert optimize_term(term, {}) == Immediate(value=15)


def test_no_fold_primitive():
    term = Primitive(operator="+", left=Reference(name="x"), right=Immediate(value=1))
    assert optimize_term(term, {}) == term


def test_fold_branch_lt_true():
    term = Branch(
        operator="<",
        left=Immediate(value=1),
        right=Immediate(value=5),
        consequent=Immediate(value=10),
        otherwise=Immediate(value=20),
    )
    assert optimize_term(term, {}) == Immediate(value=10)


def test_fold_branch_lt_false():
    term = Branch(
        operator="<",
        left=Immediate(value=5),
        right=Immediate(value=1),
        consequent=Immediate(value=10),
        otherwise=Immediate(value=20),
    )
    assert optimize_term(term, {}) == Immediate(value=20)


def test_fold_branch_eq_true():
    term = Branch(
        operator="==",
        left=Immediate(value=3),
        right=Immediate(value=3),
        consequent=Immediate(value=10),
        otherwise=Immediate(value=20),
    )
    assert optimize_term(term, {}) == Immediate(value=10)


def test_fold_branch_eq_false():
    term = Branch(
        operator="==",
        left=Immediate(value=3),
        right=Immediate(value=4),
        consequent=Immediate(value=10),
        otherwise=Immediate(value=20),
    )
    assert optimize_term(term, {}) == Immediate(value=20)


def test_no_fold_branch():
    term = Branch(
        operator="<",
        left=Reference(name="x"),
        right=Immediate(value=5),
        consequent=Immediate(value=10),
        otherwise=Immediate(value=20),
    )
    assert optimize_term(term, {}) == term


# Constant Propagation


def test_let_propagate_immediate():
    term = Let(
        bindings=[("x", Immediate(value=5))],
        body=Reference(name="x"),
    )
    assert optimize_term(term, {}) == Immediate(value=5)


def test_let_propagate_reference():
    term = Let(
        bindings=[("x", Reference(name="y"))],
        body=Reference(name="x"),
    )
    assert optimize_term(term, {}) == Reference(name="y")


def test_let_no_propagate():
    term = Let(
        bindings=[("x", Primitive(operator="+", left=Reference(name="a"), right=Reference(name="b")))],
        body=Reference(name="x"),
    )
    assert optimize_term(term, {}) == term


def test_let_sequential_propagation():
    term = Let(
        bindings=[("x", Immediate(value=3)), ("y", Reference(name="x"))],
        body=Reference(name="y"),
    )
    assert optimize_term(term, {}) == Immediate(value=3)


# Dead Code Elimination


def test_dce_unused_binding():
    term = Let(
        bindings=[("x", Immediate(value=1)), ("y", Immediate(value=2))],
        body=Reference(name="y"),
    )
    assert optimize_term(term, {}) == Immediate(value=2)


def test_dce_all_dead():
    term = Let(
        bindings=[("x", Immediate(value=1))],
        body=Immediate(value=99),
    )
    assert optimize_term(term, {}) == Immediate(value=99)


def test_dce_keeps_used():
    term = Let(
        bindings=[("x", Apply(target=Reference(name="f"), arguments=[]))],
        body=Reference(name="x"),
    )
    assert optimize_term(term, {}) == term


# optimize_program


def test_optimize_program():
    program = Program(
        parameters=[],
        body=Primitive(
            operator="+",
            left=Immediate(value=1),
            right=Immediate(value=1),
        ),
    )

    expected = Program(
        parameters=[],
        body=Immediate(value=2),
    )

    actual = optimize_program(program)

    assert actual == expected


def test_optimize_program_no_change():
    program = Program(parameters=["x"], body=Reference(name="x"))
    assert optimize_program(program) == program


def test_optimize_program_multiple_passes():
    program = Program(
        parameters=[],
        body=Let(
            bindings=[("x", Immediate(value=2))],
            body=Let(
                bindings=[("y", Reference(name="x"))],
                body=Primitive(operator="+", left=Reference(name="y"), right=Immediate(value=3)),
            ),
        ),
    )

    expected = Program(parameters=[], body=Immediate(value=5))

    assert optimize_program(program) == expected
