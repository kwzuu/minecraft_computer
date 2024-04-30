from computer.assembler.instruction import Instruction, Bitfield, parse_field

imm8 = [
    ("imm", Bitfield(8, 0))
]

imm7 = [
    ("imm", Bitfield(7, 0))
]

imm4 = [
    ("imm", Bitfield(4, 0))
]

imm4_imm6 = [
    ("imm", Bitfield(4, 6)),
    ("imm", Bitfield(6, 0))
]

r32 = [
    ("r32", Bitfield(3, 0))
]


def binary_op(a, b):
    return [
        (a, Bitfield(3, 3)),
        (b, Bitfield(3, 0)),
    ]


r32_r32 = binary_op("r32", "r32")
s32_r32 = binary_op("s32", "r32")
r32_s32 = binary_op("r32", "s32")
p32_r32 = binary_op("p32", "r32")
r32_p32 = binary_op("r32", "p32")

instructions = [
    Instruction("mov", 0b000000, 6, r32_r32),
    Instruction("add", 0b000001, 6, r32_r32),
    Instruction("sub", 0b000010, 6, r32_r32),
    Instruction("mul", 0b000011, 6, r32_r32),
    Instruction("div", 0b000100, 6, r32_r32),
    Instruction("mod", 0b000101, 6, r32_r32),
    Instruction("min", 0b000110, 6, r32_r32),
    Instruction("max", 0b000111, 6, r32_r32),

    Instruction("split", 0b001000, 6, r32_r32),
    Instruction("cmp", 0b001001, 6, r32_r32),
    Instruction("mov", 0b001010, 6, r32_s32),
    Instruction("mov", 0b001011, 6, s32_r32),
    Instruction("mov", 0b001100, 6, r32_p32),
    Instruction("mov", 0b001101, 6, p32_r32),

    Instruction("ldc", 0b001110_000, 9, r32),
    Instruction("inc", 0b001110_001, 9, r32),
    Instruction("dec", 0b001110_010, 9, r32),
    Instruction("neg", 0b001110_011, 9, r32),
    Instruction("clr", 0b001110_100, 9, r32),
    Instruction("asr12", 0b001110_101, 9, r32),
    Instruction("asl12", 0b001110_110, 9, r32),
    Instruction("RES0", 0b001110_111, 9, r32),

    Instruction("cmp", 0b001111_000, 9, r32),
    Instruction("push", 0b001111_001, 9, r32),
    Instruction("pop", 0b001111_010, 9, r32),
    Instruction("RES1", 0b001111_011, 9, r32),
    Instruction("RES2", 0b001111_100, 9, r32),
    Instruction("RES3", 0b001111_101, 9, r32),

    Instruction("ret",  0b001111_110000, 12, []),
    Instruction("RES4", 0b001111_110001, 12, []),
    Instruction("RES5", 0b001111_110010, 12, []),
    Instruction("RES6", 0b001111_110011, 12, []),
    Instruction("RES7", 0b001111_110100, 12, []),
    Instruction("RES8", 0b001111_110101, 12, []),
    Instruction("RES9", 0b001111_110110, 12, []),
    Instruction("RES10", 0b001111_110111, 12, []),

    Instruction("RES11", 0b001111_111000, 12, []),
    Instruction("RES12", 0b001111_111001, 12, []),
    Instruction("RES13", 0b001111_111010, 12, []),
    Instruction("RES14", 0b001111_111011, 12, []),
    Instruction("RES15", 0b001111_111100, 12, []),
    Instruction("RES16", 0b001111_111101, 12, []),
    Instruction("RES17", 0b001111_111110, 12, []),
    Instruction("RES18", 0b001111_111111, 12, []),


    Instruction("jlt", 0b01000, 5, imm7),
    Instruction("jle", 0b01001, 5, imm7),
    Instruction("jeq", 0b01010, 5, imm7),
    Instruction("jge", 0b01011, 5, imm7),
    Instruction("jgt", 0b01100, 5, imm7),
    Instruction("jne", 0b01101, 5, imm7),
    Instruction("jmp", 0b01110, 5, imm7),

    Instruction("jlta", 0b01111000, 8, imm4),
    Instruction("jlea", 0b01111001, 8, imm4),
    Instruction("jeqa", 0b01111010, 8, imm4),
    Instruction("jgea", 0b01111011, 8, imm4),
    Instruction("jgta", 0b01111100, 8, imm4),
    Instruction("jnea", 0b01111101, 8, imm4),
    Instruction("jmpa", 0b01111110, 8, imm4),
    Instruction("call", 0b01111111, 8, imm4),

    Instruction("const", 0b1000, 4, imm8),
    Instruction("sconst", 0b1001, 4, imm8),
    Instruction("econst", 0b1010, 4, imm8),
    Instruction("RES19", 0b1011, 4, imm8),

    Instruction("card", 0b11, 2, imm4_imm6)
]

by_name: dict[str, list[Instruction]] = {}

for i in instructions:
    if i.name in by_name:
        by_name[i.name].append(i)
    else:
        by_name[i.name] = [i]


def encode(line: str) -> int:
    parts = line.split()

    mnemonic = parts[0]

    raw_args = parts[1:]
    arg_types = []
    arg_values = []
    for arg in raw_args:
        arg_type, arg_value = parse_field(arg)
        arg_types.append(arg_type)
        arg_values.append(arg_value)

    possible_instructions = by_name[mnemonic]
    for inst in possible_instructions:
        if inst.can_encode(arg_types):
            return inst.encode(arg_values)
    raise ValueError(f"no encodings found for mnemonic {mnemonic} and types {arg_types} "
                     f"[possible instructions: {possible_instructions}]")
