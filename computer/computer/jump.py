from computer.codegen.chain_context import ChainGroup
from computer.codegen.execute import run_if
from computer.codegen.variable import IntRange, Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer import memory
from computer.computer.clone import execute_arbitrary_code
from computer.computer.layout import JUMP_GROUP_POS
from computer.computer.registers import OPCODE, INSTRUCTION_POINTER, CONSTANT_REGISTER, LF, LE, EQ, GE, GT, NE
from computer.computer.logging import log


def jump_instructions() -> ChainGroup:
    group = ChainGroup(only_chain=True)

    with group.new():  # dispatch
        log("dispatching jump")
        address = Variable("address")
        x_coord = Variable("jump_position_x", JUMP_GROUP_POS.x)
        y_coord = Variable("jump_position_y", JUMP_GROUP_POS.y)
        z_coord = Variable("jump_position_z", JUMP_GROUP_POS.z)

        with run_if(OPCODE < 0o3600):
            log("running offset jump")
            # jump by offset
            offset = Variable("offset")
            offset.set(OPCODE)
            offset %= 128
            offset.sign_extend(7)
            address.set(INSTRUCTION_POINTER)
            address += offset
            z_coord.set(OPCODE)
            z_coord.bitslice(7, 3)
            z_coord += 1
        with run_if(OPCODE > 0o3777):
            log("running absolute jump")
            # absolute jump
            high = Variable("high_part")
            high.set(OPCODE)
            high %= 16
            high *= 256
            address.set(high)
            address += CONSTANT_REGISTER
            z_coord.set(OPCODE)
            z_coord.bitslice(4, 3)
            z_coord += 1

        position = VectorVariable("target", x_coord, y_coord, z_coord)
        execute_arbitrary_code(position, 16)

    with group.new():  # jump if less than
        with run_if(LF > 0):
            INSTRUCTION_POINTER.set(address)
    with group.new():  # jump if less than or equal
        with run_if(LE > 0):
            INSTRUCTION_POINTER.set(address)
    with group.new():  # jump if equal
        with run_if(EQ > 0):
            INSTRUCTION_POINTER.set(address)
    with group.new():  # jump if greater than or equal
        with run_if(GE > 0):
            INSTRUCTION_POINTER.set(address)
    with group.new():  # jump if greater than
        with run_if(GT > 0):
            INSTRUCTION_POINTER.set(address)
    with group.new():  # jump if not equal
        with run_if(NE > 0):
            INSTRUCTION_POINTER.set(address)
    with group.new():  # jump
        INSTRUCTION_POINTER.set(address)
    with group.new():  # call
        memory.push(INSTRUCTION_POINTER)
        INSTRUCTION_POINTER.set(address)

    return group
