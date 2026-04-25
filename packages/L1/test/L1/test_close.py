from L0 import syntax as L0
from L1 import syntax as L1
from L1.close import close_program, close_statement, free_variables
from util.sequential_name_generator import SequentialNameGenerator


# free_variables tests


def test_free_variables_copy():
    statement = L1.Copy(destination="x", source="y", then=L1.Halt(value="x"))
    assert free_variables(statement) == {"y"}


def test_free_variables_abstract():
    statement = L1.Abstract(
        destination="f",
        parameters=["x"],
        body=L1.Apply(target="x", arguments=["y"]),
        then=L1.Halt(value="f"),
    )
    assert free_variables(statement) == {"y"}


def test_free_variables_apply():
    statement = L1.Apply(target="f", arguments=["x", "y"])
    assert free_variables(statement) == {"f", "x", "y"}


def test_free_variables_immediate():
    statement = L1.Immediate(destination="x", value=42, then=L1.Halt(value="x"))
    assert free_variables(statement) == set()


def test_free_variables_primitive():
    statement = L1.Primitive(
        destination="z",
        operator="+",
        left="x",
        right="y",
        then=L1.Halt(value="z"),
    )
    assert free_variables(statement) == {"x", "y"}


def test_free_variables_branch():
    statement = L1.Branch(
        operator="<",
        left="a",
        right="b",
        then=L1.Halt(value="c"),
        otherwise=L1.Halt(value="d"),
    )
    assert free_variables(statement) == {"a", "b", "c", "d"}


def test_free_variables_allocate():
    statement = L1.Allocate(destination="x", count=3, then=L1.Halt(value="x"))
    assert free_variables(statement) == set()


def test_free_variables_load():
    statement = L1.Load(destination="x", base="arr", index=0, then=L1.Halt(value="x"))
    assert free_variables(statement) == {"arr"}


def test_free_variables_store():
    statement = L1.Store(base="arr", index=0, value="v", then=L1.Halt(value="arr"))
    assert free_variables(statement) == {"arr", "v"}


def test_free_variables_halt():
    statement = L1.Halt(value="x")
    assert free_variables(statement) == {"x"}


# close_statement tests


def test_close_statement_copy():
    statement = L1.Copy(destination="x", source="y", then=L1.Halt(value="x"))

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Copy(destination="x", source="y", then=L0.Halt(value="x"))
    assert actual == expected


def test_close_statement_immediate():
    statement = L1.Immediate(destination="x", value=42, then=L1.Halt(value="x"))

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Immediate(destination="x", value=42, then=L0.Halt(value="x"))
    assert actual == expected


def test_close_statement_primitive():
    statement = L1.Primitive(
        destination="z",
        operator="+",
        left="x",
        right="y",
        then=L1.Halt(value="z"),
    )

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Primitive(
        destination="z",
        operator="+",
        left="x",
        right="y",
        then=L0.Halt(value="z"),
    )
    assert actual == expected


def test_close_statement_branch():
    statement = L1.Branch(
        operator="<",
        left="x",
        right="y",
        then=L1.Halt(value="a"),
        otherwise=L1.Halt(value="b"),
    )

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Branch(
        operator="<",
        left="x",
        right="y",
        then=L0.Halt(value="a"),
        otherwise=L0.Halt(value="b"),
    )
    assert actual == expected


def test_close_statement_allocate():
    statement = L1.Allocate(destination="x", count=3, then=L1.Halt(value="x"))

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Allocate(destination="x", count=3, then=L0.Halt(value="x"))
    assert actual == expected


def test_close_statement_load():
    statement = L1.Load(destination="x", base="arr", index=0, then=L1.Halt(value="x"))

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Load(destination="x", base="arr", index=0, then=L0.Halt(value="x"))
    assert actual == expected


def test_close_statement_store():
    statement = L1.Store(base="arr", index=0, value="v", then=L1.Halt(value="arr"))

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Store(base="arr", index=0, value="v", then=L0.Halt(value="arr"))
    assert actual == expected


def test_close_statement_halt():
    statement = L1.Halt(value="x")

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Halt(value="x")
    assert actual == expected


def test_close_statement_apply():
    statement = L1.Apply(target="f", arguments=["x", "y"])

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Load(
        destination="t0",
        base="f",
        index=0,
        then=L0.Call(target="t0", arguments=["f", "x", "y"]),
    )
    assert actual == expected


def test_close_statement_abstract_no_free_vars():
    statement = L1.Abstract(
        destination="f",
        parameters=["x"],
        body=L1.Halt(value="x"),
        then=L1.Halt(value="f"),
    )

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Allocate(
        destination="f",
        count=1,
        then=L0.Address(
            destination="t0",
            name="f0",
            then=L0.Store(
                base="f",
                index=0,
                value="t0",
                then=L0.Halt(value="f"),
            ),
        ),
    )
    assert actual == expected

    assert procedures == [
        L0.Procedure(
            name="f0",
            parameters=["c0", "x"],
            body=L0.Halt(value="x"),
        )
    ]


def test_close_statement_abstract_with_free_vars():
    statement = L1.Abstract(
        destination="f",
        parameters=["x"],
        body=L1.Primitive(
            destination="z",
            operator="+",
            left="x",
            right="y",
            then=L1.Halt(value="z"),
        ),
        then=L1.Halt(value="f"),
    )

    fresh = SequentialNameGenerator()
    procedures: list[L0.Procedure] = []
    actual = close_statement(statement, fresh, procedures)

    expected = L0.Allocate(
        destination="f",
        count=2,
        then=L0.Address(
            destination="t0",
            name="f0",
            then=L0.Store(
                base="f",
                index=0,
                value="t0",
                then=L0.Store(
                    base="f",
                    index=1,
                    value="y",
                    then=L0.Halt(value="f"),
                ),
            ),
        ),
    )
    assert actual == expected

    assert procedures == [
        L0.Procedure(
            name="f0",
            parameters=["c0", "x"],
            body=L0.Load(
                destination="y",
                base="c0",
                index=1,
                then=L0.Primitive(
                    destination="z",
                    operator="+",
                    left="x",
                    right="y",
                    then=L0.Halt(value="z"),
                ),
            ),
        )
    ]


# close_program tests


def test_close_program():
    program = L1.Program(
        parameters=["x"],
        body=L1.Halt(value="x"),
    )

    fresh = SequentialNameGenerator()
    actual = close_program(program, fresh)

    expected = L0.Program(
        procedures=[
            L0.Procedure(
                name="l0",
                parameters=["x"],
                body=L0.Halt(value="x"),
            ),
        ],
    )
    assert actual == expected


def test_close_program_with_abstract():
    program = L1.Program(
        parameters=["x"],
        body=L1.Abstract(
            destination="f",
            parameters=["y"],
            body=L1.Halt(value="y"),
            then=L1.Apply(target="f", arguments=["x"]),
        ),
    )

    fresh = SequentialNameGenerator()
    actual = close_program(program, fresh)

    expected = L0.Program(
        procedures=[
            L0.Procedure(
                name="f0",
                parameters=["c0", "y"],
                body=L0.Halt(value="y"),
            ),
            L0.Procedure(
                name="l0",
                parameters=["x"],
                body=L0.Allocate(
                    destination="f",
                    count=1,
                    then=L0.Address(
                        destination="t1",
                        name="f0",
                        then=L0.Store(
                            base="f",
                            index=0,
                            value="t1",
                            then=L0.Load(
                                destination="t0",
                                base="f",
                                index=0,
                                then=L0.Call(target="t0", arguments=["f", "x"]),
                            ),
                        ),
                    ),
                ),
            ),
        ],
    )
    assert actual == expected
