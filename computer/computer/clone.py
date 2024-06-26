from computer.codegen.chain_context import command
from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates, RelativeCoordinates, CURRENT
from computer.codegen.entity import Entity
from computer.codegen.execute import Execute
from computer.codegen.vector_variable import VectorVariable
from computer.computer.layout import TEMP_BUF_BASE



# the entity used by clones
CLONER = Entity("minecraft:armor_stand")


def initialize_cloning():
    """
    does setup work needed for cloning
    """
    CLONER.create()


def smart_clone(
        src: VectorVariable | Coordinates | RelativeCoordinates,
        dst: VectorVariable | Coordinates | RelativeCoordinates,
        buf: Coordinates,
        size: Coordinates,
        mode="replace"
) -> None:
    """
    clones a world region from one place to another
    :param src: the base position clone from
    :param dst: the base position to clone to
    :param buf: the base position of a temporary buffer, with enough space to fit the cloned region.
    :param size: the size of the world region to clone, maximum of 32767 blocks.
    :param mode: the mode to use for the clone command (supported: "replace", "masked")
    """
    # offset size because /clone's borders are inclusive
    size += Coordinates(-1, -1, -1)
    if size.x < 0 or size.y < 0 or size.z < 0:
        raise ValueError("clone command size must be nonzero")
    # copy from source to buffer
    CLONER.set_pos(src)
    (
        Execute()
        .at_entity(CLONER)
        .run(Command(f"clone {CURRENT} {CURRENT + size} {buf}"))
    )
    # copy from buffer to destination
    CLONER.set_pos(dst)
    (
        Execute()
        .at_entity(CLONER)
        .run(Command(f"clone {buf} {buf + size} {CURRENT} {mode}"))
    )


def execute_arbitrary_code(src: VectorVariable, length: int) -> None:
    """
    runs a command block chain of length `length` in the current tick
    :param src: the position of the chain to run
    :param length: the length of the chain to run
    """
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
