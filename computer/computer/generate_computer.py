#!/bin/python3.12
from computer.codegen import chain_context
from computer.codegen.chain_context import ChainGroup, ChainContext, INIT_CONTEXT
from computer.codegen.execute import Execute, run_if
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.codegen.coordinates import Coordinates
from computer.computer import registers
from computer.computer.clone import initialize_indirection, execute_arbitrary_code
from computer.computer.memory import initialize_memory, memory_load
from computer.codegen.output import assemble_schematic
from computer.computer.registers import OPCODE, JUMPED


def initialize_computer():
    initialize_memory()
    initialize_indirection()


MAIN_GROUP_POS = Coordinates(0, 0, 0)
ARITHMETIC_GROUP_POS = Coordinates(0, 1, 0)
JUMP_GROUP_POS = Coordinates(0, 2, 0)
CONST_GROUP_POS = Coordinates(0, 3, 0)
CARD_GROUP_POS = Coordinates(0, 4, 0)


def primary_chain():
    from computer.computer.registers import INSTRUCTION_POINTER

    memory_load(INSTRUCTION_POINTER, OPCODE)

    secondary_opcode = Variable("secondary_opcode")
    secondary_opcode.set(OPCODE)

    high_bits = OPCODE.bitslice(10, 2, True)
    group_y = high_bits + 1

    with run_if(high_bits == 0):  # arithmetic
        secondary_opcode.bitslice(6, 4)
    with run_if(high_bits == 1):  # jump
        pass
    with run_if(high_bits == 2):  # const.asm
        secondary_opcode.bitslice(8, 2)
    with run_if(high_bits == 3):  # card
        secondary_opcode.bitslice(6, 4)

    # high_bits.equals(0).if_true(do_arithmetic.contents)
    # high_bits.equals(1).if_true(do_jump.contents)
    # high_bits.equals(2).if_true(do_const.contents)
    # high_bits.equals(3).if_true(do_card.contents)

    position = VectorVariable(
        "position",
        Variable.constant(0),
        group_y,
        secondary_opcode,
    )

    execute_arbitrary_code(position, 32)

    with run_if(JUMPED == 0):
        INSTRUCTION_POINTER += 1
    with run_if(JUMPED == 1):
        JUMPED.set(0)


def constant_instructions() -> ChainGroup:
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


def computer(file):
    main_group = ChainGroup()

    main_group.add(INIT_CONTEXT)

    with INIT_CONTEXT:
        initialize_computer()

    primary_context = main_group.new()
    with primary_context:
        primary_chain()

    main_group.write_out(file, MAIN_GROUP_POS)

    const_instruction_group = constant_instructions()
    const_instruction_group.write_out(file, CONST_GROUP_POS)


def generate_computer():
    assemble_schematic(computer, "computer")
