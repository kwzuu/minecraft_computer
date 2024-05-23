from computer.codegen.coordinates import Coordinates

# positions for command block groups
MAIN_GROUP_POS = Coordinates(0, 0, 0)
ARITHMETIC_GROUP_POS = Coordinates(0, 1, 0)
JUMP_GROUP_POS = Coordinates(0, 2, 0)
CONST_GROUP_POS = Coordinates(0, 3, 0)
CARD_GROUP_POS = Coordinates(0, 4, 0)
CONSTANT_GROUP_POS = Coordinates(0, 5, 0)
REGISTER_BANK_POS = Coordinates(0, 6, 0)

# positions for specific subsections of the arithmetic group
BINARY_OP_BASE = ARITHMETIC_GROUP_POS + Coordinates(0, 0, 1)
UNARY_OP_BASE = ARITHMETIC_GROUP_POS + Coordinates(0, 0, 13)

# the temporary buffer used by clones
TEMP_BUF_BASE = Coordinates(0, -32, 0)
TEMP_BUF_SIZE = Coordinates(64, 64, 64)
TEMP_BUF_END = TEMP_BUF_BASE + TEMP_BUF_SIZE

# the location of the barrel cube
MEM_BASE = Coordinates(0, 128, 0)
MEM_SIZE = Coordinates(16, 16, 16)
MEM_END = MEM_BASE + MEM_SIZE - Coordinates(1, 1, 1)
