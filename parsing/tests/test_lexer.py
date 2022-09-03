from parsing.lexer import Token, Lexer


def has_types(tokens: list[Token], types: list[str]) -> None:
    """Check whether the tokens have the correct types."""
    assert types == [t.type for t in tokens]


def has_values(tokens: list[Token], values: list[dict[str, str]]) -> None:
    """Check whether the tokens have the correct values."""
    assert values == [t.value for t in tokens]


def test_chars() -> None:
    tokens = list(Lexer("abc"))
    has_types(tokens, ["char", "char", "char"])
    has_values(tokens, [{"val": "a"}, {"val": "b"}, {"val": "c"}])


def test_range() -> None:
    tokens = list(Lexer("aa-b"))
    has_types(tokens, ["char", "range"])
    has_values(tokens, [{"val": "a"}, {"first": "a", "last": "b"}])


def test_repeat() -> None:
    tokens = list(Lexer("a{1,2}"))
    has_types(tokens, ["char", "repeat"])
    has_values(tokens, [{"val": "a"}, {"min": "1", "max": "2"}])


def test_class() -> None:
    tokens = list(Lexer(":alnum:"))
    has_types(tokens, ["class"])
    has_values(tokens, [{"val": "alnum"}])


def test_escaped() -> None:
    tokens = list(Lexer(r"\|"))
    has_types(tokens, ["char"])
    has_values(tokens, [{"val": "|"}])

def test_parens() -> None:
    tokens = list(Lexer("(a)"))
    has_types(tokens, ["l-paren", "char", "r-paren"])
    has_values(tokens, [{}, {"val": "a"}, {}])
