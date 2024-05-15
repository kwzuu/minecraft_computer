#!/bin/python3.12

from computer.codegen.chain_context import ChainGroup, INIT_CONTEXT
from computer.codegen.coordinates import Coordinates
from computer.codegen.execute import run_if, run_else
from computer.codegen.output import assemble_schematic
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer import registers
from computer.computer.clone import initialize_indirection, execute_arbitrary_code
from computer.computer.memory import initialize_memory, memory_load
from computer.computer.registers import OPCODE, JUMPED, REGISTER_BANK_POS, load_gpr, store_gpr, LF, LE, EQ, GE, GT, NE


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


def arithmetic_instructions() -> ChainGroup:
    with INIT_CONTEXT:
        a = Variable("a")
        b = Variable("b")

    group = ChainGroup(only_chain=True)

    src_arg: Variable
    dst_arg: Variable

    BINARY_OP_BASE = ARITHMETIC_GROUP_POS + Coordinates(0, 0, 1)
    UNARY_OP_BASE = ARITHMETIC_GROUP_POS + Coordinates(0, 0, 13)

    with (group.new()):  # dispatch
        binary_offset = OPCODE.clone()
        binary_offset /= 64
        binary_offset %= 8

        unary_offset = OPCODE.clone()
        unary_offset -= 1600
        unary_offset /= 8

        src_arg = OPCODE.clone()
        src_arg %= 8

        dst_arg = OPCODE.clone()
        dst_arg /= 8
        dst_arg %= 8

        indirect_x = Variable("arithmetic_indirect_x", ARITHMETIC_GROUP_POS.x)
        indirect_y = Variable("arithmetic_indirect_y", ARITHMETIC_GROUP_POS.y)
        indirect_z = Variable("arithmetic_indirect_z", ARITHMETIC_GROUP_POS.z)

        with run_if(OPCODE < 0o1600):
            # run binary op
            indirect_z.set(BINARY_OP_BASE.z)
            indirect_z += binary_offset
        with run_if(OPCODE >= 0o1600):
            # run unary op
            indirect_z.set(UNARY_OP_BASE.z)
            indirect_z += unary_offset
        indirect = VectorVariable(
            "arithmetic_indirect",
            indirect_x,
            indirect_y,
            indirect_z)

        execute_arbitrary_code(indirect, 50)

    def binary_op(f):
        store_gpr(dst_arg, a)
        store_gpr(src_arg, b)
        f(a, b)
        load_gpr(dst_arg, a)

    def unary_op(f):
        store_gpr(src_arg, a)
        f(a)
        load_gpr(src_arg, a)

    # first eight: simple binary operations
    with group.new():  # move
        binary_op(Variable.set)
    with group.new():  # add
        binary_op(Variable.__iadd__)
    with group.new():  # subtract
        binary_op(Variable.__isub__)
    with group.new():  # multiply
        binary_op(Variable.__imul__)
    with group.new():  # divide
        binary_op(Variable.__itruediv__)
    with group.new():  # modulo
        binary_op(Variable.__imod__)
    with group.new():  # minimum
        binary_op(lambda dst, src: dst.min(src))
    with group.new():  # maximum
        binary_op(lambda dst, src: dst.max(src))

    # next six: complex binary operations
    with group.new():  # split
        def split(dst: Variable, src: Variable):
            dst.set(src)
            dst %= 0o1000
            src /= 0o1000
        binary_op(split)
    with group.new():  # cmp
        def cmp(dst: Variable, src: Variable):
            with run_if(dst < src):
                LF.set(1)
            with run_else():
                LF.set(0)
            with run_if(dst <= src):
                LE.set(1)
            with run_else():
                LE.set(0)
            with run_if(dst == src):
                EQ.set(1)
                NE.set(0)
            with run_else():
                EQ.set(0)
                NE.set(1)
            with run_if(dst >= src):
                GE.set(1)
            with run_else():
                GE.set(0)
            with run_if(dst > src):
                GT.set(1)
            with run_else():
                GT.set(0)
        binary_op(cmp)
    with group.new():  # mov from scratch
        pass
    with group.new():  # mov into scratch
        pass
    with group.new():  # memory load
        pass
    with group.new():  # memory store
        pass

    # next eight: simple unary operations
    with group.new():  # load from cr
        pass
    with group.new():  # increment
        pass
    with group.new():  # decrement
        pass
    with group.new():  # negate
        pass
    with group.new():  # clear
        pass
    with group.new():  # arithmetic shift right 12
        pass
    with group.new():  # arithmetic shift left 12
        pass
    with group.new():  # RESERVED
        pass

    # last eight: complex unary operations
    with group.new():  # compare with 0
        pass
    with group.new():  # push to stack
        pass
    with group.new():  # pop from stack
        pass
    with group.new():  # RESERVED
        pass
    with group.new():  # RESERVED
        pass
    with group.new():  # RESERVED
        pass
    with group.new():  # RESERVED
        pass
    with group.new():  # RESERVED
        pass

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

    arithmetic_instruction_group = arithmetic_instructions()
    arithmetic_instruction_group.write_out(file, ARITHMETIC_GROUP_POS)

    register_group = registers.register_group()
    register_group.write_out(file, REGISTER_BANK_POS)


def generate_computer():
    assemble_schematic(computer, "computer")
