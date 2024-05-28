from computer.codegen.chain_context import ChainGroup
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer.clone import execute_arbitrary_code
from computer.computer.layout import CARD_GROUP_POS
from computer.computer.registers import OPCODE


def card_instructions() -> ChainGroup:
    group = ChainGroup(only_chain=True)

    with group.new():  # dispatch
        card_pos_x = Variable("card_pos_x", CARD_GROUP_POS.x)
        card_pos_y = Variable("card_pos_y", CARD_GROUP_POS.y)
        card_pos_z = Variable("card_pos_z", CARD_GROUP_POS.z)

        card_pos_z.set(OPCODE)
        card_pos_z.bitslice(6, 4)
        card_pos_z += 1

        const_pos = VectorVariable("const_pos", card_pos_x, card_pos_y, card_pos_z)
        execute_arbitrary_code(const_pos, 16)

    return group
