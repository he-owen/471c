from collections.abc import Sequence
from typing import Annotated, Literal

from pydantic import BaseModel, Field

type Identifier = Annotated[str, Field(min_length=1)]

type Nat = Annotated[int, Field(ge=0)]


class Program(BaseModel, frozen=True):
    tag: Literal["l3"] = "l3"
    parameters: Sequence[Identifier]
    body: Term


type Term = Annotated[
    Let
    | Reference
    | Abstract
    | Apply
    | Immediate
    | Primitive
    | Branch
    | Allocate
    | Load
    | Store
    | Begin
    | LetRec
    | Print
    | StringLiteral
    | StringLength
    | Bool
    | And
    | Or
    | Not
    | If,
    Field(discriminator="tag"),
]


class Let(BaseModel, frozen=True):
    tag: Literal["let"] = "let"
    bindings: Sequence[tuple[Identifier, Term]]
    body: Term


class LetRec(BaseModel, frozen=True):
    tag: Literal["letrec"] = "letrec"
    bindings: Sequence[tuple[Identifier, Term]]
    body: Term


class Reference(BaseModel, frozen=True):
    tag: Literal["reference"] = "reference"
    name: Identifier


class Abstract(BaseModel, frozen=True):
    tag: Literal["abstract"] = "abstract"
    parameters: Sequence[Identifier]
    body: Term


class Apply(BaseModel, frozen=True):
    tag: Literal["apply"] = "apply"
    target: Term
    arguments: Sequence[Term]


class Immediate(BaseModel, frozen=True):
    tag: Literal["immediate"] = "immediate"
    value: int


class Primitive(BaseModel, frozen=True):
    tag: Literal["primitive"] = "primitive"
    operator: Literal["+", "-", "*", "/", "%", "string-ref", "string-append"]
    left: Term
    right: Term


class Branch(BaseModel, frozen=True):
    tag: Literal["branch"] = "branch"
    operator: Literal["<", "==", ">", ">=", "<=", "!="]
    left: Term
    right: Term
    consequent: Term
    otherwise: Term


class Allocate(BaseModel, frozen=True):
    tag: Literal["allocate"] = "allocate"
    count: Nat


class Load(BaseModel, frozen=True):
    tag: Literal["load"] = "load"
    base: Term
    index: Nat


class Store(BaseModel, frozen=True):
    tag: Literal["store"] = "store"
    base: Term
    index: Nat
    value: Term


class Print(BaseModel, frozen=True):
    tag: Literal["print"] = "print"
    value: Term


class StringLiteral(BaseModel, frozen=True):
    tag: Literal["string_literal"] = "string_literal"
    value: str


class StringLength(BaseModel, frozen=True):
    tag: Literal["string_length"] = "string_length"
    value: Term


class Bool(BaseModel, frozen=True):
    tag: Literal["bool"] = "bool"
    value: bool


class And(BaseModel, frozen=True):
    tag: Literal["and"] = "and"
    left: Term
    right: Term


class Or(BaseModel, frozen=True):
    tag: Literal["or"] = "or"
    left: Term
    right: Term


class Not(BaseModel, frozen=True):
    tag: Literal["not"] = "not"
    value: Term


class If(BaseModel, frozen=True):
    tag: Literal["if_term"] = "if_term"
    condition: Term
    consequent: Term
    otherwise: Term


class Begin(BaseModel, frozen=True):
    tag: Literal["begin"] = "begin"
    effects: Sequence[Term]
    value: Term
