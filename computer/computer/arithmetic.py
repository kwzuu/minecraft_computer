from computer.codegen.chain_context import ChainGroup, INIT_CONTEXT
from computer.codegen.execute import run_if, run_else
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer.clone import execute_arbitrary_code
from computer.computer.layout import ARITHMETIC_GROUP_POS, BINARY_OP_BASE, UNARY_OP_BASE
from computer.computer.memory import memory_load, memory_store
from computer.computer.registers import OPCODE, get_gpr, set_gpr, LF, LE, EQ, NE, GE, GT, get_scratch, set_scratch


def arithmetic_instructions() -> ChainGroup:
    with INIT_CONTEXT:
        a = Variable("a")
        b = Variable("b")

    group = ChainGroup(only_chain=True)

    src_arg: Variable
    dst_arg: Variable

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
        get_gpr(dst_arg, a)
        get_gpr(src_arg, b)
        f(a, b)
        set_gpr(dst_arg, a)

    def unary_op(f):
        get_gpr(src_arg, a)
        f(a)
        set_gpr(src_arg, a)

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
        get_scratch(src_arg, a)
        set_gpr(dst_arg, a)
    with group.new():  # mov into scratch
        get_gpr(src_arg, a)
        set_scratch(dst_arg, a)
    with group.new():  # memory load
        get_gpr(src_arg, a)
        get_gpr(dst_arg, b)

        memory_load(a, b)
    with group.new():  # memory store
        get_gpr(dst_arg, a)
        get_gpr(src_arg, b)

        memory_store(a, b)

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
