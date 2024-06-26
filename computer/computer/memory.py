from computer.codegen import coordinates
from computer.codegen.block import Block
from computer.codegen.chain_context import command
from computer.codegen.command import Command
from computer.codegen.entity import Entity
from computer.codegen.execute import Execute
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable
from computer.computer.layout import MEM_END, MEM_BASE


MEMORY_GETTER = Entity("minecraft:armor_stand")


high_half: Variable
low_half: Variable


def initialize_memory():
    command(f"fill {MEM_BASE} {MEM_END} air")
    command(
        f"fill {MEM_BASE} {MEM_END} minecraft:barrel"
        '{Items:['
        '{Slot:0b,id:"minecraft:stone",Count:1b},'
        '{Slot:1b,id:"minecraft:stone",Count:1b}'
        ']}')
    MEMORY_GETTER.create()
    global high_half, low_half
    high_half = Variable("high_half", 0)
    low_half = Variable("low_half", 0)


def reset_memory():
    initialize_memory()


def move_getter_to_index(index: Variable):
    mem_index = VectorVariable("mem_index", MEM_BASE)

    mem_offset = VectorVariable(
        "mem_offset",
        index.bitslice(0, 4),
        index.bitslice(8, 4, last=True),
        index.bitslice(4, 4)
    )

    mem_index += mem_offset

    MEMORY_GETTER.set_pos(mem_index)


def memory_load(index: Variable, dest: Variable):
    memory_load_high_half = Variable("high_half")

    move_getter_to_index(index)

    (
        Execute()
        .at_entity(MEMORY_GETTER)
        .store_result(memory_load_high_half)
        .run(Command("data get block ~ ~ ~ Items[0].Count"))
    )

    (
        Execute()
        .at_entity(MEMORY_GETTER)
        .store_result(dest)
        .run(Command("data get block ~ ~ ~ Items[1].Count"))
    )

    dest -= 1
    memory_load_high_half -= 1
    memory_load_high_half *= 64
    dest += memory_load_high_half


def memory_store(index: Variable, src: Variable):
    global high_half, low_half
    move_getter_to_index(index)

    barrel = Block(coordinates.CURRENT)

    high_half.set(src)
    high_half /= 64
    high_half += 1
    low_half.set(src)
    low_half %= 64
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
    from computer.computer.registers import STACK_POINTER
    memory_store(STACK_POINTER, src)
    STACK_POINTER -= 1


def pop(dst: Variable):
    from computer.computer.registers import STACK_POINTER
    STACK_POINTER += 1
    memory_load(STACK_POINTER, dst)


def call(ptr: Variable):
    from computer.computer.registers import INSTRUCTION_POINTER
    push(INSTRUCTION_POINTER + 1)
    INSTRUCTION_POINTER.set(ptr)


def ret():
    from computer.computer.registers import INSTRUCTION_POINTER
    pop(INSTRUCTION_POINTER)
