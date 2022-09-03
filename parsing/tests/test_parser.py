from parsing.parser import *


def types(ast: AST) -> list[type[AST]]:
    """Recursively walk the AST and return the types of each node in pre-order."""
    if isinstance(ast, Or):
        return [Or] + sum((types(expr) for expr in ast.exprs), [])
    elif isinstance(ast, Concat):
        return [Concat] + sum((types(expr) for expr in ast.exprs), [])
    elif isinstance(ast, Repeat):
        return [Repeat] + types(ast.expr)
    elif isinstance(ast, Set):
        return [Set] + sum((types(expr) for expr in ast.exprs), [])
    elif isinstance(ast, Dot):
        return [Dot]
    elif isinstance(ast, Char):
        return [Char]
    elif isinstance(ast, Range):
        return [Range]
    elif isinstance(ast, Class):
        return [Class]
    else:
        raise ValueError(f"Unknown AST node: {ast}")


def test_or():
    ast = parse("a|b")
    assert types(ast) == [Or, Char, Char]


def test_concat():
    ast = parse("abc")
    assert types(ast) == [Concat, Char, Char, Char]


def test_repeat():
    ast = parse("a*b?c+d{2,3}")
    assert types(ast) == [
        Concat,
        Repeat,
        Char,
        Repeat,
        Char,
        Repeat,
        Char,
        Repeat,
        Char,
    ]


def test_set():
    ast = parse("[\\:b-d:alpha:.[^\\]]")
    assert types(ast) == [Set, Char, Range, Class, Dot, Set, Char]


def test_neg_set():
    ast = parse("[^.]")
    assert types(ast) == [Set, Dot]
