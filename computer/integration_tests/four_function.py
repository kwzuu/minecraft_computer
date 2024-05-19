from computer.codegen.chain_context import ChainGroup, command
from computer.codegen.coordinates import Coordinates
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer.clone import execute_arbitrary_code, initialize_cloning


def four_function(file) -> None:
    """
    integration test for a four-function calculator using indirection
    :param file: the file to write out to
    """
    main_group = ChainGroup()
    with main_group.new():
        # initialization
        command("scoreboard objectives add vars dummy")
        command("scoreboard objectives setdisplay sidebar vars")
        a = Variable("a")
        b = Variable("b")
        op = Variable("op")
        initialize_cloning()

    operation_group = ChainGroup(only_chain=True)
    with operation_group.new():
        # add
        a += b
    with operation_group.new():
        # sub
        a -= b
    with operation_group.new():
        # mul
        a *= b
    with operation_group.new():
        # div
        a /= b

    numbers_group = ChainGroup()
    for i in range(10):
        with numbers_group.new():
            b *= 10
            b += i

    control_group = ChainGroup()
    with control_group.new():
        # =
        indirect = VectorVariable("indirect", 0, 0, 0)
        indirect.z.set(op)
        execute_arbitrary_code(indirect, 1)
        b.set(0)
    with control_group.new():
        # Clear
        b.set(0)
    with control_group.new():
        # Clear Everything
        a.set(0)
        b.set(0)
        op.set(-1)
    with control_group.new():
        # +
        op.set(0)
        a.set(b)
        b.set(0)
    with control_group.new():
        # -
        op.set(1)
        a.set(b)
        b.set(0)
    with control_group.new():
        # *
        op.set(2)
        a.set(b)
        b.set(0)
    with control_group.new():
        # /
        op.set(3)
        a.set(b)
        b.set(0)

    operation_group.write_out(file, Coordinates(0, 0, 0))
    main_group.write_out(file, Coordinates(0, 1, 0))
    numbers_group.write_out(file, Coordinates(0, 5, 0))
    control_group.write_out(file, Coordinates(0, 7, 0))
