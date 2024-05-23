from computer.codegen.chain_context import INIT_CONTEXT, ChainGroup, command
from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates
from computer.codegen.entity import Entity
from computer.codegen.execute import Execute
from computer.codegen.variable import Variable
from computer.computer.layout import TEMP_BUF_BASE, REGISTER_BANK_POS

with INIT_CONTEXT:
    # register used for building constants
    CONSTANT_REGISTER = Variable("cr")
    # register that points to the next instruction to execute
    INSTRUCTION_POINTER = Variable("ip")
    # register that points to the top of the stack
    STACK_POINTER = Variable("sp", 4095)
    # register that points to the bottom of the current stack frame
    BASE_POINTER = Variable("bp", 4095)
    # variable that contains the current opcode
    OPCODE = Variable("opcode")
    # variable that says whether a jump occurred this cycle
    JUMPED = Variable("jumped")

    # source and destination for micro-ops
    SRC = Variable("src")
    DST = Variable("dst")

    # general-purpose registers
    A0 = Variable("a0")
    A1 = Variable("a1")
    A2 = Variable("a2")
    T0 = Variable("t0")
    T1 = Variable("t1")
    S0 = Variable("s0")
    S1 = Variable("s1")
    S2 = Variable("s2")

    # scratch registers
    X0 = Variable("x0")
    X1 = Variable("x1")
    X2 = Variable("x2")
    X3 = Variable("x3")
    Y0 = Variable("y0")
    Y1 = Variable("y1")
    Y2 = Variable("y2")
    Y3 = Variable("y3")

    # comparison flags
    LF = Variable("LF")
    LE = Variable("LE")
    EQ = Variable("EQ")
    GE = Variable("GE")
    GT = Variable("GT")
    NE = Variable("NE")


GP_REGISTERS = [A0, A1, A2, T0, T1, S0, S1, S2]
SCRATCH_REGISTERS = [X0, X1, X2, X3, Y0, Y1, Y2, Y3]


def initialize_registers() -> None:
    """
    initializes the registers
    """
    REGISTER_FETCHER.create()


def reset_registers() -> None:
    """
    resets the registers to their value at startup
    """
    CONSTANT_REGISTER.set(0)
    INSTRUCTION_POINTER.set(0)
    OPCODE.set(0)
    JUMPED.set(0)

    SRC.set(0)
    DST.set(0)

    LF.set(0)
    LE.set(0)
    EQ.set(0)
    GE.set(0)
    GT.set(0)
    NE.set(0)

    STACK_POINTER.set(4095)
    BASE_POINTER.set(4095)

    for i in GP_REGISTERS + SCRATCH_REGISTERS:
        i.set(0)


# entity that performs register loads and stores
REGISTER_FETCHER = Entity("minecraft:armor_stand")


def register_op(kind: int, reg_id: Variable) -> None:
    """
    generates an operation to load or store a register
    for internal use
    :param kind: the kind of operation to perform
    :param reg_id: the index of the register to load from or store into
    """
    if not 0 <= kind < 8:
        raise ValueError
    # x: reg
    # y: constant
    # z: kind
    REGISTER_FETCHER.set_pos(REGISTER_BANK_POS + Coordinates(0, 0, kind))
    REGISTER_FETCHER.set_nbt("Pos[0]", reg_id, "double")
    (
        Execute()
        .at_entity(REGISTER_FETCHER)
        .run(Command(f"clone ~ ~ ~ ~ ~ ~ {TEMP_BUF_BASE}"))
    )
    command(f"clone {TEMP_BUF_BASE} {TEMP_BUF_BASE} ~1 ~ ~")
    command("")


def set_gpr(reg_id: Variable, src: Variable) -> None:
    """
    loads a variable into a general-purpose register
    :param reg_id: the register id to use
    :param src: the variable to load from
    """
    SRC.set(src)
    register_op(0, reg_id)


def get_gpr(reg_id: Variable, dst: Variable) -> None:
    """
    stores a general-purpose register into a variable
    :param reg_id: the register id to use
    :param dst: the variable to store to
    """
    register_op(1, reg_id)
    dst.set(DST)


def set_scratch(reg_id: Variable, src: Variable):
    """
    loads a variable into a scratch register
    :param reg_id: the register id to use
    :param src: the variable to load from
    """
    SRC.set(src)
    register_op(2, reg_id)


def get_scratch(reg_id: Variable, dst: Variable):
    """
    stores a scratch register into a variable
    :param reg_id: the register id to use
    :param dst: the variable to store to
    """
    register_op(3, reg_id)
    dst.set(DST)


def generate_register_loads(var: Variable, registers: list[Variable]) -> None:
    """
    generates a command block to load from each of the registers provided
    :param var: the variable to store into
    :param registers: the list of registers to generate loads for
    """
    for r in registers:
        var.set(r)


def generate_register_stores(var: Variable, registers: list[Variable]) -> None:
    """
    generates a command block to store into each of the registers provided
    :param var: the variable to load from
    :param registers: the list of registers to generate stores for
    """
    for r in registers:
        r.set(var)


def register_group() -> ChainGroup:
    """
    creates the group that contains commands to load and store each register
    :return: the group
    """
    group = ChainGroup()
    with group.new(only_chain=True):
        generate_register_loads(SRC, GP_REGISTERS)
    with group.new(only_chain=True):
        generate_register_stores(DST, GP_REGISTERS)
    with group.new(only_chain=True):
        generate_register_loads(SRC, SCRATCH_REGISTERS)
    with group.new(only_chain=True):
        generate_register_stores(DST, SCRATCH_REGISTERS)

    return group
