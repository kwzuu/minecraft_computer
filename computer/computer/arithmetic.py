from computer.codegen.chain_context import ChainGroup, INIT_CONTEXT, command
from computer.codegen.execute import run_if, run_else
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer import memory
from computer.computer.clone import execute_arbitrary_code
from computer.computer.layout import ARITHMETIC_GROUP_POS, BINARY_OP_BASE, UNARY_OP_BASE
from computer.computer.memory import memory_load, memory_store
from computer.computer.registers import OPCODE, get_gpr, set_gpr, LF, LE, EQ, NE, GE, GT, get_scratch, set_scratch, \
    CONSTANT_REGISTER


def arithmetic_instructions() -> ChainGroup:
    with INIT_CONTEXT:
        a = Variable("a")
        b = Variable("b")

    group = ChainGroup(only_chain=True)

    first_argument: Variable
    second_argument: Variable

    with (group.new()):  # dispatch
        binary_offset = OPCODE.clone()
        binary_offset /= 64
        binary_offset %= 8

        unary_offset = OPCODE.clone()
        unary_offset -= 1600
        unary_offset /= 8

        first_argument = OPCODE.clone()
        first_argument %= 8

        second_argument = OPCODE.clone()
        second_argument /= 8
        second_argument %= 8

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
        get_gpr(second_argument, a)
        get_gpr(first_argument, b)
        f(a, b)
        set_gpr(second_argument, a)

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
        def cmp(dst: Variable, src: Variable | int):
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
        get_scratch(first_argument, a)
        set_gpr(second_argument, a)
    with group.new():  # mov into scratch
        get_gpr(first_argument, a)
        set_scratch(second_argument, a)
    with group.new():  # memory load
        get_gpr(first_argument, a)
        get_gpr(second_argument, b)

        memory_load(a, b)
    with group.new():  # memory store
        get_gpr(second_argument, a)
        get_gpr(first_argument, b)

        memory_store(a, b)

    # next eight: simple unary operations
    with group.new():  # load from cr
        set_gpr(second_argument, CONSTANT_REGISTER)
    with group.new():  # increment
        get_gpr(second_argument, a)
        a += 1
        set_gpr(second_argument, a)
    with group.new():  # decrement
        get_gpr(second_argument, a)
        a += 1
        set_gpr(second_argument, a)
    with group.new():  # negate
        get_gpr(second_argument, a)
        a *= -1
        set_gpr(second_argument, a)
    with group.new():  # clear
        set_gpr(second_argument, Variable.constant(0))
    with group.new():  # arithmetic shift right 12
        second_argument /= Variable.constant(4096)
    with group.new():  # arithmetic shift left 12
        second_argument *= Variable.constant(4096)
    with group.new():  # RESERVED
        command("say ILLEGAL CALL OF RESERVED INSTRUCTION")

    # last eight: complex unary operations
    with group.new():  # compare with 0
        get_gpr(second_argument, a)
        cmp(a, 0)
    with group.new():  # push to stack
        get_gpr(second_argument, a)
        memory.push(a)
    with group.new():  # pop from stack
        memory.pop(a)
        set_gpr(second_argument, a)
    with group.new():  # RESERVED
        command("say ILLEGAL CALL OF RESERVED INSTRUCTION")
    with group.new():  # RESERVED
        command("say ILLEGAL CALL OF RESERVED INSTRUCTION")
    with group.new():  # RESERVED
        command("say ILLEGAL CALL OF RESERVED INSTRUCTION")
    with group.new():  # RESERVED
        command("say ILLEGAL CALL OF RESERVED INSTRUCTION")
    with group.new():  # RESERVED
        command("say ILLEGAL CALL OF RESERVED INSTRUCTION")

    return group
