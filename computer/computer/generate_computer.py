#!/bin/python3.12

from computer.codegen.chain_context import ChainGroup, INIT_CONTEXT
from computer.codegen.execute import run_if
from computer.codegen.output import assemble_schematic
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer import registers
from computer.computer.arithmetic import arithmetic_instructions
from computer.computer.clone import initialize_cloning, execute_arbitrary_code
from computer.computer.constant import constant_instructions
from computer.computer.layout import MAIN_GROUP_POS, CONST_GROUP_POS, ARITHMETIC_GROUP_POS, REGISTER_BANK_POS
from computer.computer.memory import initialize_memory, memory_load
from computer.computer.registers import OPCODE, JUMPED


def initialize_computer():
    initialize_memory()
    initialize_cloning()


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

    arithmetic_instruction_group = arithmetic_instructions()
    arithmetic_instruction_group.write_out(file, ARITHMETIC_GROUP_POS)

    register_group = registers.register_group()
    register_group.write_out(file, REGISTER_BANK_POS)


def generate_computer():
    assemble_schematic(computer, "computer")
