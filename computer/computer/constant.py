from computer.codegen.chain_context import ChainGroup, command
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer import registers
from computer.computer.clone import execute_arbitrary_code
from computer.computer.layout import CONST_GROUP_POS
from computer.computer.registers import OPCODE


def constant_instructions() -> ChainGroup:
    """
    instructions used for creating and using constants
    :return:
    """
    # group for constant instructions
    group = ChainGroup(only_chain=True)

    with group.new():  # dispatch
        const_pos_x = Variable("const_pos_x", CONST_GROUP_POS.x)
        const_pos_y = Variable("const_pos_y", CONST_GROUP_POS.y)
        const_pos_z = Variable("const_pos_z", CONST_GROUP_POS.z)

        const_pos_z.set(OPCODE)
        const_pos_z.bitslice(8, 2, 0)
        const_pos_z += 1

        const_pos = VectorVariable("const_pos", const_pos_x, const_pos_y, const_pos_z)
        execute_arbitrary_code(const_pos, 16)
    with group.new():  # const
        imm = registers.OPCODE.bitslice(0, 8)
        registers.CONSTANT_REGISTER.set(imm)
    with group.new():  # sconst
        imm = registers.OPCODE.bitslice(0, 8)
        imm.sign_extend(8)
        registers.CONSTANT_REGISTER.set(imm)
    with group.new():  # econst
        imm = registers.OPCODE.bitslice(0, 8)
        registers.CONSTANT_REGISTER *= 256
        registers.CONSTANT_REGISTER += imm
    with group.new():  # RESERVED
        command("say ILLEGAL USAGE OF RESERVED COMMAND")

    return group
