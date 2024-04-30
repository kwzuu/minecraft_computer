from dataclasses import dataclass
from typing import Tuple, Iterable


@dataclass
class Bitfield:
    width: int
    skip: int

    def get(self, n: int) -> int:
        mask = (1 << self.width) - 1
        return (n >> self.skip) & mask

    def set(self, n: int, val: int) -> int:
        if val >= (1 << self.width):
            raise ValueError(f"value {val} too wide for width {self.width} field")
        mask = ((1 << self.width) - 1) << self.skip
        n ^= (n & mask)
        n |= (val << self.skip)
        return n


GP_REGISTERS = dict(
    a0=0,
    a1=1,
    a2=2,
    t0=3,
    t1=4,
    s0=4,
    s1=6,
    s2=7,
)

SCRATCH_REGISTERS = dict(
    x0=0,
    x1=1,
    x2=2,
    x3=3,
    y0=4,
    y1=5,
    y2=6,
    y3=7
)


def parse_imm(s: str) -> tuple[str, int]:
    return "imm", int(s)


def parse_gpr(s: str) -> tuple[str, int]:
    return "r32", GP_REGISTERS[s]


def parse_pointer(s: str) -> tuple[str, int]:
    reg = s[1:]
    if reg in GP_REGISTERS:
        return "p32", parse_gpr(reg)[1]
    elif reg in SCRATCH_REGISTERS:
        return "ps32", parse_scratch(reg)[1]


def parse_scratch(s: str) -> tuple[str, int]:
    return "s32", SCRATCH_REGISTERS[s]


@dataclass
class Instruction:
    name: str
    opcode: int
    opcode_width: int
    field_types: list[str]
    fields: list[Bitfield]

    def __init__(
            self,
            name: str,
            opcode: int,
            opcode_width: int,
            fields: list[tuple[str, Bitfield]],
    ):
        self.name = name
        self.opcode = opcode
        self.opcode_width = opcode_width
        self.field_types = []
        self.fields = []
        for field_type, field in fields:
            self.field_types.append(field_type)
            self.fields.append(field)

    def encode(self, args: Iterable[int]) -> int:
        i = self.opcode << (12 - self.opcode_width)
        for arg, field in zip(args, self.fields):
            i = field.set(i, arg)
        return i

    def can_encode(self, types: list[str]) -> bool:
        return self.field_types == types


def parse_field(f: str) -> tuple[str, int]:
    if f.startswith("*"):
        return parse_pointer(f)
    elif f in GP_REGISTERS:
        return parse_gpr(f)
    elif f in SCRATCH_REGISTERS:
        return parse_scratch(f)
    else:
        return parse_imm(f)
