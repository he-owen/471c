from .syntax import (
    Abstract,
    Allocate,
    Apply,
    Branch,
    Copy,
    Halt,
    Immediate,
    Load,
    Primitive,
    Print,
    Program,
    Statement,
    Store,
    StringLength,
)


def pretty_program(program: Program) -> str:
    params = " ".join(program.parameters)
    body = pretty_statement(program.body, indent=2)
    return f"(l1 ({params})\n{body})"


def pretty_statement(stmt: Statement, indent: int = 0) -> str:
    pad = " " * indent
    match stmt:
        case Halt(value=value):
            return f"{pad}(halt {value})"

        case Copy(destination=dest, source=src, then=then):
            rest = pretty_statement(then, indent)
            return f"{pad}(copy {dest} {src})\n{rest}"

        case Immediate(destination=dest, value=value, then=then):
            if isinstance(value, str):
                v = f'"{value}"'
            else:
                v = str(value)
            rest = pretty_statement(then, indent)
            return f"{pad}(immediate {dest} {v})\n{rest}"

        case Primitive(destination=dest, operator=op, left=left, right=right, then=then):
            rest = pretty_statement(then, indent)
            return f"{pad}(primitive {dest} ({op} {left} {right}))\n{rest}"

        case Branch(operator=op, left=left, right=right, then=then, otherwise=otherwise):
            t = pretty_statement(then, indent + 2)
            o = pretty_statement(otherwise, indent + 2)
            return f"{pad}(branch ({op} {left} {right})\n{t}\n{o})"

        case Abstract(destination=dest, parameters=params, body=body, then=then):
            p = " ".join(params)
            b = pretty_statement(body, indent + 2)
            rest = pretty_statement(then, indent)
            return f"{pad}(abstract {dest} ({p})\n{b})\n{rest}"

        case Apply(target=target, arguments=args):
            a = " ".join(args)
            return f"{pad}(apply {target} {a})"

        case Allocate(destination=dest, count=count, then=then):
            rest = pretty_statement(then, indent)
            return f"{pad}(allocate {dest} {count})\n{rest}"

        case Load(destination=dest, base=base, index=index, then=then):
            rest = pretty_statement(then, indent)
            return f"{pad}(load {dest} {base} {index})\n{rest}"

        case Store(base=base, index=index, value=value, then=then):
            rest = pretty_statement(then, indent)
            return f"{pad}(store {base} {index} {value})\n{rest}"

        case Print(destination=dest, value=value, then=then):
            rest = pretty_statement(then, indent)
            return f"{pad}(print {dest} {value})\n{rest}"

        case StringLength(destination=dest, value=value, then=then):
            rest = pretty_statement(then, indent)
            return f"{pad}(string-length {dest} {value})\n{rest}"

        case _:
            return f"{pad}<unknown>"
