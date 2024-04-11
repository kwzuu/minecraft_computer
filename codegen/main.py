from dataclasses import dataclass


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


def emit(pos: Coordinates, block_id: str, snbt=None):
    print(pos.x, pos.y, pos.z, block_id if snbt is None else block_id + " " + snbt)


def command_block(pos: Coordinates, command: str, data="", kind="minecraft:command_block"):
    emit(pos, kind + data, snbt='{Command:%s}' % repr(command))


def chain(pos: Coordinates, commands: list[str], grow=Coordinates.EAST):
    if len(commands) == 0:
        raise ValueError("chains must have at least one command")
    it = iter(commands)
    command_block(pos, next(it))
    for i in it:
        pos += grow
        command_block(pos, i, kind="minecraft:chain_command_block")


chain(Coordinates(0, 0, 0), [
    "say hello world",
    "say meow"
])
