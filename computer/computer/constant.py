from computer.codegen.chain_context import ChainGroup
from computer.computer import registers


def constant_instructions() -> ChainGroup:
    """
    instructions used for creating and using constants
    :return:
    """
    # group for constant instructions
    group = ChainGroup()

    const_context = group.new()
    with const_context:
        imm = registers.OPCODE.bitslice(0, 8)
        registers.CONSTANT_REGISTER.set(imm)

    sconst_context = group.new()
    with sconst_context:
        imm = registers.OPCODE.bitslice(0, 8)
        imm.sign_extend(8)
        registers.CONSTANT_REGISTER.set(imm)

    econst_context = group.new()
    with econst_context:
        imm = registers.OPCODE.bitslice(0, 8)
        registers.CONSTANT_REGISTER *= 256
        registers.CONSTANT_REGISTER += imm

    return group
