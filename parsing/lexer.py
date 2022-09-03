"""
    A simple lexer for tokenizing a regex string.

    The tokens are:
        - 'l-paren'     a left parenthesis
        - 'r-paren'     a right parenthesis
        - 'l-bracket'   a left bracket
        - 'r-bracket'   a right bracket
        
        - 'or'          the or operator
        - 'star'        the star operator
        - 'plus'        the plus operator
        - 'question'    the question operator

        - 'char'        a single character
        - 'class'       a character class ':digit:', ':alpha:', etc.
        - 'range'       a range of characters 'a-z'
        - 'dot'         a dot '.'

        - 'caret'       a caret '^'
    

    Characters may be escaped with a backslash '\'. 
"""

from dataclasses import dataclass
from typing import Callable, Iterator


class LexerError(Exception):
    """Raised when the lexer encounters an error."""

    def __init__(self, msg: str, pos: int) -> None:
        super().__init__(f"LexerError: {msg} at position {pos}")
        self.pos = pos


@dataclass(frozen=True, eq=True)
class Token:
    """A single token produced by the lexer."""

    type: str
    value: dict[str, str]
    pos: int

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value}, {self.pos})"


class Chars:
    """An iterator over the characters of a string"""

    def __init__(self, text: str) -> None:
        """Initialize the iterator at position 0 of text."""
        self.text = text
        self.pos = 0

    def next(self) -> str | None:
        """Return the next character in the string or None if at the end."""
        if self.pos >= len(self.text):
            return None
        char = self.text[self.pos]
        self.pos += 1
        return char

    def peek(self, ahead: int = 0) -> str | None:
        """Return the next character in the string or None if at the end."""
        if self.pos + ahead >= len(self.text):
            return None
        return self.text[self.pos + ahead]

    def next_if(self, pred: Callable[[str], bool]) -> str | None:
        """Return the next character if it satisfies the predicate or None."""
        char = self.peek()
        if char is not None and pred(char):
            return self.next()
        return None

    def next_while(self, pred: Callable[[str], bool]) -> str:
        """Consume characters of the string while the predicate is true."""
        start = self.pos
        while (char := self.peek()) is not None and pred(char):
            self.next()
        return self.text[start : self.pos]

    def peek_if(self, pred: Callable[[str], bool]) -> str | None:
        """Return the next character if it satisfies the predicate or None."""
        char = self.peek()
        if char is not None and pred(char):
            return char
        return None

    def peek_while(self, pred: Callable[[str], bool]) -> str:
        """Consume characters of the string while the predicate is true."""
        start = self.pos
        while (char := self.peek()) is not None and pred(char):
            self.next()
        self.pos = start
        return self.text[start : self.pos]


class Lexer(Iterator[Token]):
    """Iterator over the tokens of a regular expression."""

    singles: dict[str, str] = {
        "(": "l-paren",
        ")": "r-paren",
        "[": "l-bracket",
        "]": "r-bracket",
        "|": "or",
        "*": "star",
        "+": "plus",
        "?": "question",
        ".": "dot",
        "^": "caret",
    }

    def __init__(self, re: str) -> None:
        self.chars: Chars = Chars(re)
        self.current: Token | None = self._next()

    def peek(self) -> Token | None:
        """Return the next Token without consuming it"""
        return self.current

    def next(self) -> Token | None:
        """Return the next Token and consume it"""
        token = self.current
        self.current = self._next()
        return token

    def next_if(self, pred: Callable[[Token], bool]) -> Token | None:
        """Return the next token if it satisfies the predicate or None."""
        token: Token | None = self.peek()
        if token is not None and pred(token):
            return self.next()
        return None

    def next_while(self, pred: Callable[[Token], bool]) -> list[Token]:
        """Consume tokens while the predicate is true."""
        tokens: list[Token] = []
        while (token := self.peek()) is not None and pred(token):
            tokens.append(token)
            self.next()
        return tokens

    def __iter__(self) -> Iterator[Token]:
        return self

    def __next__(self) -> Token:
        """Return the next Token or raise StopIteration"""
        token = self.next()
        if token is None:
            raise StopIteration
        return token

    @property
    def pos(self) -> int:
        """Return the current position of the lexer."""
        return self.chars.pos

    def _next(self) -> Token | None:
        """Return the next Token or None if the end has been reached"""
        self.chars.next_while(str.isspace)

        char = self.chars.next()
        if char is None:
            return None

        if char in Lexer.singles:
            return Token(Lexer.singles[char], {}, self.pos - 1)
        if char == "{":
            return self._parse_repeat()
        if char == ":":
            return self._parse_class()
        if char == "\\":
            return self._parse_escape()
        if self.chars.peek() == "-":
            return self._parse_range(char)
        return Token("char", {"val": char}, self.pos - 1)

    def _parse_repeat(self) -> Token:
        """Parse a repeat token of the form {n,m}"""
        start: int = self.pos - 1
        min: str = self.chars.next_while(str.isdigit)
        if not self.chars.next_if(lambda c: c == ","):
            raise LexerError("Expected ','", self.pos)

        max: str = self.chars.next_while(str.isdigit)
        if not self.chars.next_if(lambda c: c == "}"):
            raise LexerError("Expected '}'", self.pos)

        return Token("repeat", {"min": min, "max": max}, start)

    def _parse_class(self) -> Token:
        """Parse a class token of the form :class:"""
        start: int = self.pos - 1
        name: str = self.chars.next_while(lambda c: c.isalnum())
        if not self.chars.next_if(lambda c: c == ":"):
            raise LexerError("Expected ':'", self.pos)

        return Token("class", {"val": name}, start)

    def _parse_escape(self) -> Token:
        """Parse an escaped character"""
        start: int = self.pos - 1
        char: str | None = self.chars.next()
        if char is None:
            raise LexerError("Expected character after '\\'", self.pos)
        return Token("char", {"val": char}, start)

    def _parse_range(self, first: str) -> Token:
        """Parse a range token of the form a-z"""
        start: int = self.pos - 1
        self.chars.next()  # consume the '-'
        last: str | None = self.chars.next()
        if last is None:
            raise LexerError("Expected character after '-'.", self.pos)
        return Token("range", {"first": first, "last": last}, start)
