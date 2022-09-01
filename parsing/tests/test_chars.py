from parsing.lexer import Chars, LexerError
from pytest import raises

def test_chars() -> None:
    chars = list(Chars(r"a\bc"))
    assert chars == ["a", "b", "c"]


def test_chars_fail() -> None:
    chars = Chars("a\\")
    with raises(LexerError):
        list(chars)

def test_chars_initial() -> None:
    chars = Chars("\\ab")
    assert chars.peek() == "a"