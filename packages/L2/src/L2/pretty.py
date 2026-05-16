from .syntax import (
    Abstract,
    Allocate,
    Apply,
    Begin,
    Branch,
    Immediate,
    Let,
    Load,
    Primitive,
    Print,
    Program,
    Reference,
    Store,
    StringLength,
    StringLiteral,
    Term,
)


def pretty_program(program: Program) -> str:
    params = " ".join(program.parameters)
    body = pretty_term(program.body, indent=2)
    return f"(l2 ({params})\n{body})"


def pretty_term(term: Term, indent: int = 0) -> str:
    pad = " " * indent
    match term:
        case Reference(name=name):
            return f"{pad}{name}"

        case Immediate(value=value):
            return f"{pad}{value}"

        case StringLiteral(value=value):
            return f'{pad}"{value}"'

        case Primitive(operator=op, left=left, right=right):
            l = pretty_term(left, 0)
            r = pretty_term(right, 0)
            return f"{pad}({op} {l} {r})"

        case Branch(operator=op, left=left, right=right, consequent=con, otherwise=alt):
            l = pretty_term(left, 0)
            r = pretty_term(right, 0)
            c = pretty_term(con, indent + 2)
            a = pretty_term(alt, indent + 2)
            return f"{pad}(if ({op} {l} {r})\n{c}\n{a})"

        case Let(bindings=bindings, body=body):
            parts = []
            for name, val in bindings:
                v = pretty_term(val, 0)
                parts.append(f"({name} {v})")
            binds = " ".join(parts)
            b = pretty_term(body, indent + 2)
            return f"{pad}(let ({binds})\n{b})"

        case Abstract(parameters=params, body=body):
            p = " ".join(params)
            b = pretty_term(body, indent + 2)
            return f"{pad}(\\ ({p})\n{b})"

        case Apply(target=target, arguments=args):
            t = pretty_term(target, 0)
            a = " ".join(pretty_term(arg, 0) for arg in args)
            if a:
                return f"{pad}({t} {a})"
            return f"{pad}({t})"

        case Allocate(count=count):
            return f"{pad}(allocate {count})"

        case Load(base=base, index=index):
            b = pretty_term(base, 0)
            return f"{pad}(load {b} {index})"

        case Store(base=base, index=index, value=value):
            b = pretty_term(base, 0)
            v = pretty_term(value, 0)
            return f"{pad}(store {b} {index} {v})"

        case Print(value=value):
            v = pretty_term(value, 0)
            return f"{pad}(print {v})"

        case StringLength(value=value):
            v = pretty_term(value, 0)
            return f"{pad}(string-length {v})"

        case Begin(effects=effects, value=value):
            parts = [pretty_term(e, indent + 2) for e in effects]
            parts.append(pretty_term(value, indent + 2))
            body = "\n".join(parts)
            return f"{pad}(begin\n{body})"

        case _:
            return f"{pad}<unknown>"
