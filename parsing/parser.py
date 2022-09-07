"""
    A recursive descent parser for regular expressions.

    The grammar is:
        or ::= concat { '|' concat }
        concat :: = { repeat }
        repeat ::= atom [ 'star' | 'plus' | 'question' | 'repeat' ]
        atom ::= 'l-paren' or 'r-paren' | set | 'dot' | 'char'
        set ::= 'l-bracket' { 'char' | 'range' | 'class' | 'dot' | set } 'r-bracket'
    
    These are represented by the ast nodes:
        Or: {exprs: list[ast]}
        Concat: {exprs: list[ast]}
        Repeat: {expr: ast, min: int, max: int} (represents all repeat operators)
        Set: {negated: bool, exprs: list[ast]}
        Dot: {}
        Char: {char: str}
        Range: {start: str, end: str}
        Class: {name: str}
"""

from dataclasses import dataclass
from parsing.lexer import Lexer


class AST:
    """Abstract syntax tree for regular expressions."""

    pass


@dataclass(frozen=True, eq=True)
class Or(AST):
    exprs: list[AST]


@dataclass(frozen=True, eq=True)
class Concat(AST):
    exprs: list[AST]


@dataclass(frozen=True, eq=True)
class Repeat(AST):
    expr: AST
    min: int
    max: int  # -1 means infinity


@dataclass(frozen=True, eq=True)
class Set(AST):
    negated: bool
    exprs: list[AST]


@dataclass(frozen=True, eq=True)
class Dot(AST):
    pass


@dataclass(frozen=True, eq=True)
class Char(AST):
    char: str


@dataclass(frozen=True, eq=True)
class Range(AST):
    start: str
    end: str


@dataclass(frozen=True, eq=True)
class Class(AST):
    name: str


class ParserError(Exception):
    """Raised when the parser encounters an error."""

    def __init__(self, msg: str, pos: int) -> None:
        super().__init__(f"ParserError: {msg} at position {pos}")
        self.pos = pos



def _set(lexer: Lexer) -> AST:
    """Parse a set expression."""
    negated: bool = False
    if (tok := lexer.peek()) and tok.type == "caret":
        lexer.next()
        negated: bool = True
    
    exprs: list[AST] = []
    while (tok := lexer.next()) and tok.type != "r-bracket":
        if tok.type == "char":
            exprs.append(Char(tok.value["val"]))
        elif tok.type == "range":
            exprs.append(Range(tok.value["first"], tok.value["last"]))
        elif tok.type == "class":
            exprs.append(Class(tok.value["val"]))
        elif tok.type == "dot":
            exprs.append(Dot())
        elif tok.type == "l-bracket":
            exprs.append(_set(lexer))
        else:
            raise ParserError(f"Unexpected token {tok.type}", lexer.pos)
    return Set(negated, exprs)


def _atom(lexer: Lexer) -> AST:
    """Parse an atom."""
    tok = lexer.next()
    if not tok:
        raise ParserError("Unexpected end of input", lexer.pos)

    if tok.type == "char":
        return Char(tok.value["val"])
    if tok.type == "dot":
        return Dot()
    if tok.type == "l-paren":
        expr = _or(lexer)
        if not (tok := lexer.next()) or tok.type != "r-paren":
            raise ParserError("Expected ')'", lexer.pos)
        return expr
    if tok.type == "l-bracket":
        return _set(lexer)
    else:
        raise ParserError(f"Unexpected token {tok.type}", lexer.pos)


def _repeat(lexer: Lexer) -> AST:
    """Parse a repeat expression."""
    expr = _atom(lexer)
    tok = lexer.peek()
    if tok and tok.type == "star":
        lexer.next()
        return Repeat(expr, 0, -1)
    elif tok and tok.type == "plus":
        lexer.next()
        return Repeat(expr, 1, -1)
    elif tok and tok.type == "question":
        lexer.next()
        return Repeat(expr, 0, 1)
    elif tok and tok.type == "repeat":
        lexer.next()
        min = int(tok.value["min"]) if tok.value["min"] else 0
        max = int(tok.value["max"]) if tok.value["max"] else -1
        return Repeat(expr, min, max)
    return expr


def _concat(lexer: Lexer) -> AST:
    """Parse a concat expression."""
    exprs = [_repeat(lexer)]
    while (tok := lexer.peek()) and tok.type not in ("or", "r-paren"):
        exprs.append(_repeat(lexer))
    if len(exprs) == 1:
        return exprs[0]
    return Concat(exprs)


def _or(lexer: Lexer) -> AST:
    """Parse an or expression."""
    exprs = [_concat(lexer)]
    while (tok := lexer.peek()) and tok.type == "or":
        lexer.next()
        exprs.append(_concat(lexer))

    if len(exprs) == 1:
        return exprs[0]
    return Or(exprs)


def parse(text: str) -> AST:
    """Parse a regular expression."""
    lexer = Lexer(text)
    expr = _or(lexer)
    if lexer.peek():
        raise ParserError(f"Unexpected token {lexer.next()}", lexer.pos)
    return expr
