"""
    Compile an AST into a list of instructions.
"""

from typing import Callable
from parsing import parser


class Instruction:
    """Base class for instructions"""

    pass


class Match(Instruction):
    """Base class for character matchers"""

    def match(self, char: str) -> bool:
        """Return True if the character matches"""
        raise NotImplementedError


class Char(Match):
    """Match a single character"""

    def __init__(self, char: str) -> None:
        self.char = char

    def match(self, char: str) -> bool:
        return char == self.char


class Range(Match):
    """Match a range of characters"""

    def __init__(self, start: str, end: str) -> None:
        self.start = start
        self.end = end

    def match(self, char: str) -> bool:
        return self.start <= char <= self.end


class Any(Match):
    """Match any character"""

    def match(self, char: str) -> bool:
        return True


class Class(Match):
    """Match a character class"""

    classes: dict[str, Callable[[str], bool]] = {
        "digit": str.isdigit,
        "alpha": str.isalpha,
        "alnum": str.isalnum,
        "word": lambda c: c.isalnum() or c == "_",
        "space": str.isspace,
    }

    def __init__(self, name: str) -> None:
        if name not in Class.classes:
            raise ValueError(f"Unknown class '{name}'")
        self.matcher = Class.classes[name]

    def match(self, char: str) -> bool:
        return self.matcher(char)


class Compiler:
    def __init__(self, ast: parser.AST) -> None:
        self.ast = ast
        self.instructions: list[Instruction] = []
