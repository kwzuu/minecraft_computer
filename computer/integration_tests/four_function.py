from computer.codegen.chain_context import ChainGroup, command
from computer.codegen.coordinates import Coordinates
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer.clone import execute_arbitrary_code, initialize_indirection


def four_function(file):
    main_group = ChainGroup()
    with main_group.new():
        # initialization
        command("scoreboard objectives new vars dummy")
        command("scoreboard objectives setdisplay sidebar vars")
        a = Variable("a")
        b = Variable("b")
        op = Variable("op")
        dst = Variable("dst")
        initialize_indirection()
    with main_group.new():
        # main logic
        indirect = VectorVariable("indirect", 0, 0, 0)
        indirect.z.set(op)
        execute_arbitrary_code(indirect, 1)

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

    operation_group.write_out(file, Coordinates(0, 0, 0))
    main_group.write_out(file, Coordinates(0, 1, 0))
