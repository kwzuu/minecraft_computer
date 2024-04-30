from computer.codegen.chain_context import INIT_CONTEXT, ChainGroup, command
from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates
from computer.codegen.entity import Entity
from computer.codegen.execute import Execute
from computer.codegen.variable import Variable
from computer.computer.clone import execute_arbitrary_code, TEMP_BUF_BASE

REGISTER_BANK_POS = Coordinates(0, 5, 0)

with INIT_CONTEXT:
    CONSTANT_REGISTER = Variable("cr")
    INSTRUCTION_POINTER = Variable("ip")
    STACK_POINTER = Variable("sp")
    BASE_POINTER = Variable("bp")
    OPCODE = Variable("opcode")
    JUMPED = Variable("jumped")

    # source and destination for micro-ops
    SRC = Variable("src")
    DST = Variable("dst")

    A0 = Variable("a0")
    A1 = Variable("a1")
    A2 = Variable("a2")
    T0 = Variable("t0")
    T1 = Variable("t1")
    S0 = Variable("s0")
    S1 = Variable("s1")
    S2 = Variable("s2")

    X0 = Variable("x0")
    X1 = Variable("x1")
    X2 = Variable("x2")
    X3 = Variable("x3")
    Y0 = Variable("y0")
    Y1 = Variable("y1")
    Y2 = Variable("y2")
    Y3 = Variable("y3")

GP_REGISTERS = [A0, A1, A2, T0, T1, S0, S1, S2]
SCRATCH_REGISTERS = [X0, X1, X2, X3, Y0, Y1, Y2, Y3]


def initialize_registers():
    reset_registers()
    REGISTER_FETCHER.create()


def reset_registers():
    CONSTANT_REGISTER.set(0)
    INSTRUCTION_POINTER.set(0)
    OPCODE.set(0)
    JUMPED.set(0)
    SRC.set(0)
    DST.set(0)
    STACK_POINTER.set(4095)
    BASE_POINTER.set(4095)
    for i in GP_REGISTERS + SCRATCH_REGISTERS:
        i.set(0)


REGISTER_FETCHER = Entity("minecraft:armor_stand")


def gpr_op(kind: int, reg: Variable):
    if not 0 <= kind < 8:
        raise ValueError
    # x: reg
    # y: constant
    # z: kind
    REGISTER_FETCHER.set_pos(REGISTER_BANK_POS + Coordinates(0, 0, kind))
    REGISTER_FETCHER.set_nbt("Pos[0]", reg, "double")
    (
        Execute()
        .at_entity(REGISTER_FETCHER)
        .run(Command(f"clone ~ ~ ~ ~ ~ ~ {TEMP_BUF_BASE}"))
    )
    command(f"clone {TEMP_BUF_BASE} {TEMP_BUF_BASE} ~1 ~ ~")
    command("")


def load_gpr(reg: Variable, src: Variable):
    SRC.set(src)
    gpr_op(0, reg)


def store_gpr(reg: Variable, dst: Variable):
    gpr_op(1, reg)
    dst.set(DST)


def load_scratch(reg: Variable, src: Variable):
    SRC.set(src)
    gpr_op(2, reg)


def store_scratch(reg: Variable, dst: Variable):
    gpr_op(3, reg)
    dst.set(DST)


def generate_register_load(var: Variable, registers: list[Variable]):
    for r in registers:
        var.set(r)


def generate_register_store(var: Variable, registers: list[Variable]):
    for r in registers:
        r.set(var)


def register_group() -> ChainGroup:
    # TODO: make group use chain command blocks only
    group = ChainGroup()
    with group.new():
        generate_register_load(SRC, GP_REGISTERS)
    with group.new():
        generate_register_store(DST, GP_REGISTERS)
    with group.new():
        generate_register_load(SRC, SCRATCH_REGISTERS)
    with group.new():
        generate_register_store(DST, SCRATCH_REGISTERS)

    return group
