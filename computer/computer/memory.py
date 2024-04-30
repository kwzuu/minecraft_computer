from computer.codegen import coordinates
from computer.codegen.block import Block
from computer.codegen.chain_context import command
from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates, RelativeCoordinates
from computer.codegen.entity import Entity
from computer.codegen.execute import Execute
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable

MEM_BASE = Coordinates(0, 128, 0)
MEM_SIZE = Coordinates(16, 16, 16)
MEM_END = MEM_BASE + MEM_SIZE
MEMORY_GETTER = Entity("minecraft:armor_stand")


def initialize_memory():
    command(
        f"fill {MEM_BASE} {MEM_END} minecraft:barrel"
        '{Items:['
        '{Slot:0b,id:"minecraft:stone",Count:1b},'
        '{Slot:1b,id:"minecraft:stone",Count:1b}'
        ']}')
    MEMORY_GETTER.create()


def reset_memory():
    initialize_memory()


def move_getter_to_index(index: Variable):
    mem_index = VectorVariable("mem_index", MEM_BASE)

    mem_offset = VectorVariable(
        "mem_offset",
        index.bitslice(0, 4),
        index.bitslice(4, 4),
        index.bitslice(8, 4, last=True)
    )

    mem_index += mem_offset

    MEMORY_GETTER.set_pos(mem_index)


def memory_load(index: Variable, dest: Variable):
    move_getter_to_index(index)

    high_half = Variable("high_half", 0)

    (
        Execute()
        .at_entity(MEMORY_GETTER)
        .store_result(high_half)
        .run(Command("data get block ~ ~ ~ Items[0].Count"))
    )

    (
        Execute()
        .at_entity(MEMORY_GETTER)
        .store_result(dest)
        .run(Command("data get block ~ ~ ~ Items[1].Count"))
    )

    dest -= 1
    high_half -= 1
    high_half *= 64
    dest += high_half


def memory_store(index: Variable, src: Variable):
    move_getter_to_index(index)

    barrel = Block(coordinates.CURRENT)

    high_half = src // 64
    high_half += 1
    low_half = src % 64
    low_half += 1

    (
        Execute()
        .at_entity(MEMORY_GETTER)
        .store_result(barrel.slot(0))
        .run(high_half.get())
    )

    (
        Execute()
        .at_entity(MEMORY_GETTER)
        .store_result(barrel.slot(1))
        .run(low_half.get())
    )


def push(src: Variable):
    from registers import STACK_POINTER
    memory_store(STACK_POINTER, src)
    STACK_POINTER -= 1


def pop(dst: Variable):
    from registers import STACK_POINTER
    STACK_POINTER += 1
    memory_load(STACK_POINTER, dst)


def call(ptr: Variable):
    from registers import INSTRUCTION_POINTER
    push(INSTRUCTION_POINTER + 1)
    INSTRUCTION_POINTER.set(ptr)


def ret(ptr: Variable):
    from registers import INSTRUCTION_POINTER
    pop(INSTRUCTION_POINTER)
