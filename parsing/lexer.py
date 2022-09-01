"""
    A simple lexer for tokenizing a regex string.

    The tokens are:
        - 'paren'       a parenthesis '(' or ')'
        - 'bracket'     a bracket '[' or ']'

        - 'star'        a star '*'
        - 'plus'        a plus '+'
        - 'question'    a question mark '?'
        - 'pipe'        a pipe '|'
        - 'repeat'      a repeat '{n,m}'

        - 'char'        a character
        - 'class'       a character class '<digit>', '<alpha>', etc.
        - 'dot'         a dot '.'

        - 'caret'       a caret '^'
        - 'dash'        a dash '-'
        - 'eq'          an equals '='
        - 'colon'       a colon ':'

        - 'eof'         end of file
    

    Characters may be escaped with a backslash '\'. 
"""

from dataclasses import dataclass
from typing import Iterator


class LexerError(Exception):
    """Raised when the lexer encounters an error."""

    def __init__(self, msg: str, pos: int) -> None:
        super().__init__(f"LexerError: {msg} at position {pos}")
        self.pos = pos


@dataclass(frozen=True, eq=True)
class Token:
    """A single token produced by the lexer."""

    type: str
    value: str
    pos: int

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value}, {self.pos})"


class Chars(Iterator[str]):
    """An iterator over the characters of a string, parses escaped characters."""

    def __init__(self, s: str) -> None:
        self.s = s
        self.pos = 0
        self.cur = self._next_char()

    def _next_char(self) -> str | None:
        """Return the next character and advance."""
        if self.pos >= len(self.s):
            return None
        c = self.s[self.pos]
        self.pos += 1
        if c == "\\":
            if self.pos >= len(self.s):
                raise LexerError("unexpected end of string", self.pos)
            c = self.s[self.pos]
            self.pos += 1
        return c

    def peek(self) -> str | None:
        """Return the next character without advancing."""
        return self.cur

    def next(self) -> str | None:
        """Return the next character and advance."""
        c = self.cur
        self.cur = self._next_char()
        return c

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        c = self.next()
        if c is None:
            raise StopIteration
        return c
