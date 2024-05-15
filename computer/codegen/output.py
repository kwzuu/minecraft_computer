import subprocess
from pathlib import Path
from typing import Callable, TextIO

from computer.codegen import coordinates
from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates


def emit(file, pos: Coordinates, block_id: str, snbt=None):
    """
    writes a line of schematic assembly to a file
    :param file: the file to write to
    :param pos: the position to put the block at
    :param block_id: the id of the block
    :param snbt: nbt data in snbt form for if the block is a block entity
    """
    file.write(f"{pos.x} {pos.y} {pos.z} " + (block_id if snbt is None else (block_id + " " + snbt)) + "\n")


def command_block(file, pos: Coordinates, command: str, kind="minecraft:command_block", auto=False) -> None:
    """
    writes a command block to a file
    :param file: the file to write to
    :param pos: the position to put the command block at
    :param command: the command executed by the command block
    :param kind: the type of command block to use
    :param auto: False if the command block is "Needs Redstone", True if it is "Always"
    """
    snbt_parts = [f"Command:{repr(command)}"]
    if auto:
        snbt_parts.append(f"auto:1b")
    snbt = "{" + ",".join(snbt_parts) + "}"
    emit(file, pos, kind, snbt=snbt)


def chain(
        file,
        pos: Coordinates,
        commands: list[Command],
        start_block="minecraft:command_block",
        only_chain=False,
) -> None:
    """
    writes a chain of command blocks to a file
    :param file: the file to write to
    :param pos: the position to start the chain at
    :param commands: the commands to put in the chain
    :param start_block: the block to start at
    :param only_chain: whether the first command block should be a chain command block
    """
    if len(commands) == 0 and not only_chain:
        raise ValueError("chains must have at least one command")
    it = iter(commands)
    if not only_chain:
        command_block(file, pos, next(it).command, kind=start_block + "[facing=east]")
        pos += coordinates.EAST
    for command in it:
        command_block(file, pos, command.command, kind="minecraft:chain_command_block[facing=east]", auto=True)
        pos += coordinates.EAST


def run_schematic_assembler(src: str, dst: str) -> None:
    """
    invokes the schematic assembler program
    :param src: source file
    :param dst: destination file
    """
    subprocess.Popen(["bin/schematic_assembler", src, dst])


def assemble_schematic(function: Callable[[TextIO], None], name: str = None) -> None:
    """
    assembles a schematic with a function
    :param function: the function to use
    :param name: the name of the schematic, defaults to function name
    """

    if name is None:
        name = function.__name__

    Path("generated").mkdir(exist_ok=True)
    with open(f"generated/{name}.blk", "w") as file:
        function(file)
        run_schematic_assembler(f"generated/{name}.blk", f"schematics/{name}.schematic")
