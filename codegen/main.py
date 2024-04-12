import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Coordinates:
    x: int
    y: int
    z: int

    def __add__(self, other):
        return Coordinates(self.x + other.x, self.y + other.y, self.z + other.z)


Coordinates.EAST = Coordinates(1, 0, 0)
Coordinates.WEST = Coordinates(-1, 0, 0)
Coordinates.UP = Coordinates(0, 1, 0)
Coordinates.DOWN = Coordinates(0, -1, 0)
Coordinates.SOUTH = Coordinates(0, 0, 1)
Coordinates.NORTH = Coordinates(0, 0, -1)


def emit(file, pos: Coordinates, block_id: str, snbt=None):
    file.write(f"{pos.x} {pos.y} {pos.z} " + (block_id if snbt is None else (block_id + " " + snbt)) + "\n")


def command_block(file, pos: Coordinates, command: str, data="", kind="minecraft:command_block"):
    emit(file, pos, kind + data, snbt='{Command:%s}' % repr(command))


def chain(
        file,
        pos: Coordinates,
        commands: list[str],
        grow=Coordinates.EAST,
        start_block="minecraft:command_block",
        facing="east"
):
    if len(commands) == 0:
        raise ValueError("chains must have at least one command")
    it = iter(commands)
    command_block(file, pos, next(it), kind=start_block + f"[facing={facing}]")
    for command in it:
        pos += grow
        command_block(file, pos, command, kind=f"minecraft:chain_command_block[facing={facing}]")


def computer(file):
    chain(file, Coordinates(0, 0, 1), [
        "say hello world",
        "say meow"
    ])


def run_schematic_assembler(src, dst):
    process = subprocess.Popen(["../schematic_assembler/target/release/schematic_assembler", src, dst])


def assemble_schematic(function, name: str):
    Path("generated").mkdir(exist_ok=True)
    with open(f"generated/{name}.blk", "w") as file:
        computer(file)
        run_schematic_assembler(f"generated/{name}.blk", f"../schematics/{name}.schematic")


def main():
    assemble_schematic(computer, "computer")


if __name__ == "__main__":
    main()
