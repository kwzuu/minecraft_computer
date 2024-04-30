from dataclasses import dataclass


@dataclass
class Coordinates:
    x: int
    y: int
    z: int

    def __add__(self, other):
        return Coordinates(self.x + other.x, self.y + other.y, self.z + other.z)

    def __format__(self, format_spec) -> str:
        return f"{self.x} {self.y} {self.z}"

    def double(self) -> str:
        return f"{self.x}.0 {self.y}.0 {self.z}.0"


EAST = Coordinates(1, 0, 0)
WEST = Coordinates(-1, 0, 0)
UP = Coordinates(0, 1, 0)
DOWN = Coordinates(0, -1, 0)
SOUTH = Coordinates(0, 0, 1)
NORTH = Coordinates(0, 0, -1)


def parse_arg(arg: str | int) -> tuple[int, bool]:
    if isinstance(arg, int):
        return arg, False
    if len(arg) == 0:
        raise ValueError
    if arg[0] == "~":
        return int(arg[1:]), True
    else:
        return int(arg), False


def show_coord(value: int, is_relative: bool = False) -> str:
    if is_relative:
        return f"~{value}"
    else:
        return str(value)


@dataclass
class RelativeCoordinates(Coordinates):
    x_relative: bool
    y_relative: bool
    z_relative: bool

    def __init__(self, x: int | str, y: int | str, z: int | str):
        x, self.x_relative = parse_arg(x)
        y, self.y_relative = parse_arg(y)
        z, self.z_relative = parse_arg(z)
        super().__init__(x, y, z)

    def __format__(self, format_spec) -> str:
        x = show_coord(self.x, self.x_relative)
        y = show_coord(self.y, self.y_relative)
        z = show_coord(self.z, self.z_relative)

        return f"{x} {y} {z}"


CURRENT = RelativeCoordinates("~", "~", "~")
