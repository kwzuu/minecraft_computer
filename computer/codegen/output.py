import subprocess
from pathlib import Path

from computer.codegen import coordinates
from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates


def emit(file, pos: Coordinates, block_id: str, snbt=None):
    file.write(f"{pos.x} {pos.y} {pos.z} " + (block_id if snbt is None else (block_id + " " + snbt)) + "\n")


def command_block(file, pos: Coordinates, command: str, data="", kind="minecraft:command_block", auto=False):
    snbt_parts = [f"Command:{repr(command)}"]
    if auto:
        snbt_parts.append(f"auto:1b")
    snbt = "{" + ",".join(snbt_parts) + "}"
    emit(file, pos, kind + data, snbt=snbt)


def chain(
        file,
        pos: Coordinates,
        commands: list[Command],
        grow=coordinates.EAST,
        start_block="minecraft:command_block",
        facing="east",
        only_chain=False,
):
    if len(commands) == 0 and not only_chain:
        raise ValueError("chains must have at least one command")
    it = iter(commands)
    if not only_chain:
        command_block(file, pos, next(it).command, kind=start_block + f"[facing={facing}]")
    for command in it:
        pos += grow
        command_block(file, pos, command.command, kind=f"minecraft:chain_command_block[facing={facing}]", auto=True)


def run_schematic_assembler(src, dst):
    subprocess.Popen(["bin/schematic_assembler", src, dst])


def assemble_schematic(function, name: str):
    Path("generated").mkdir(exist_ok=True)
    with open(f"generated/{name}.blk", "w") as file:
        function(file)
        run_schematic_assembler(f"generated/{name}.blk", f"schematics/{name}.schematic")
