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

def test_complex() -> None:
    re: str= "a([:alnum:\\.]+)b"
    tokens: list[Token] = list(Lexer(re))
    has_types(tokens, ["char", "paren", "bracket", "class", "char", "bracket", "op", "paren", "char"])
    assert tokens[3].value["val"] == "alnum"
    assert tokens[6].value["val"] == "+"

def test_complex2() -> None:
    re: str = "a{,4}:alpha:[^bc]"
    tokens: list[Token] = list(Lexer(re))
    has_types(tokens, ["char", "repeat", "class", "bracket", "caret", "char", "char", "bracket"])
    assert tokens[1].value["min"] == ""
    assert tokens[1].value["max"] == "4"
    assert tokens[2].value["val"] == "alpha"