from computer.codegen.chain_context import command
from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates, RelativeCoordinates, CURRENT
from computer.codegen.entity import Entity
from computer.codegen.execute import Execute
from computer.codegen.vector_variable import VectorVariable

TEMP_BUF_BASE = Coordinates(0, -128, 0)
TEMP_BUF_SIZE = Coordinates(64, 64, 64)
TEMP_BUF_END = TEMP_BUF_BASE + TEMP_BUF_SIZE
INDIRECT = Entity("minecraft:armor_stand")


def initialize_indirection():
    INDIRECT.create()


def smart_clone(
        src: VectorVariable | Coordinates | RelativeCoordinates,
        dst: VectorVariable | Coordinates | RelativeCoordinates,
        buf: Coordinates,
        size: Coordinates,
        mode="replace"
):
    # offset size because /clone's borders are inclusive
    size += Coordinates(-1, -1, -1)
    # copy from source to buffer
    INDIRECT.set_pos(src)
    (
        Execute()
        .at_entity(INDIRECT)
        .run(Command(f"clone {CURRENT} {CURRENT + size} {buf}"))
    )
    # copy from buffer to destination
    INDIRECT.set_pos(dst)
    (
        Execute()
        .at_entity(INDIRECT)
        .run(Command(f"clone {buf} {buf + size} {CURRENT} {mode}"))
    )


def execute_arbitrary_code(src: VectorVariable, length: int):
    smart_clone(
        src,
        RelativeCoordinates("~2", "~", "~"),
        TEMP_BUF_BASE,
        Coordinates(length, 1, 1),
        mode="masked"
    )
    for i in range(length):
        command("")
    command(f"fill ~-1 ~ ~ ~-{length} ~ ~ minecraft:chain_command_block[facing=east]")
