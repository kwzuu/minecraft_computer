from dataclasses import dataclass
from typing import Optional, Tuple, Any
import re


def split_lines(source: str) -> list[str]:
    lines = []
    escaped = False
    for line in source.split("\n"):
        escape_current = escaped
        escaped = False
        if line.endswith("\\"):
            line = line[:-1]
            escaped = True
        if escape_current:
            lines[-1] += line
    return lines


@dataclass
class Instruction:
    pass


def parse_instruction(line) -> Optional[Instruction]:
    return Instruction()


@dataclass
class LabelDeclaration:
    pass


def parse_label_declaration(line) -> Optional[LabelDeclaration]:
    return LabelDeclaration()


@dataclass
class Comment:
    pass


def parse_comment(line) -> Optional[Comment]:
    if line.startswith("#"):
        return Comment()
    if ws := parse_whitespace(line) is not None:
        return parse_comment(ws[1])
    return None


@dataclass
class Directive:
    pass


def parse_directive(line) -> Optional[tuple[Directive, str]]:
    return Directive(), ""


@dataclass
class Whitespace:
    pass


@dataclass
class Identifier:
    name: str


IDENTIFIER = re.compile(r"[a-zA-Z_\-][a-zA-Z0-9_\-]+(.*)")


def parse_identifier(s: str) -> Optional[tuple[Identifier, str]]:
    if (m := IDENTIFIER.match(s)) is not None:
        return Identifier(s), m[1]
    return None


WHITESPACE = re.compile(r"^\s+(.*)")


def parse_whitespace(s: str) -> Optional[tuple[Whitespace, str]]:
    if (m := WHITESPACE.match(s)) is not None:
        return Whitespace(), m[1]
    return None


def parse_blank(line: str) -> Optional[Whitespace]:
    if len(line) == 0:
        return Whitespace()
    ws, rest = parse_whitespace(line)
    if rest != "":
        return None
    return ws


def parse_line(line: str) -> Any:
    blank = parse_blank(line)
    if blank is not None:
        return blank

    comment = parse_comment(line)
    if comment is not None:
        return comment

    directive = parse_directive(line)
    if directive is not None:
        return directive

    label_declaration = parse_label_declaration(line)
    if label_declaration is not None:
        return label_declaration

    instruction = parse_instruction(line)
    if instruction is not None:
        return instruction

    raise ValueError(f"parsing error: line `{line}' did not match any line types")
