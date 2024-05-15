from dataclasses import dataclass


@dataclass
class Coordinates:
    """
    World coordinates, known at compile time
    """

    x: int
    y: int
    z: int

    def __add__(self, other):
        return Coordinates(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Coordinates(self.x - other.x, self.y - other.y, self.z - other.z)

    def __format__(self, format_spec) -> str:
        return f"{self.x} {self.y} {self.z}"

    def exact(self) -> str:
        """
        coordinates for teleporting to the corner of the block, rather than the middle.
        :return: string representing the coordinates
        """
        return f"{self.x}.0 {self.y}.0 {self.z}.0"


# unit vectors
EAST = Coordinates(1, 0, 0)
WEST = Coordinates(-1, 0, 0)
UP = Coordinates(0, 1, 0)
DOWN = Coordinates(0, -1, 0)
SOUTH = Coordinates(0, 0, 1)
NORTH = Coordinates(0, 0, -1)


def parse_relative_coordinate(arg: str | int) -> tuple[int, bool]:
    """
    parses a coordinate that may be relative, inverse to `show_relative_coordinate`
    :param arg: the coordinate to parse
    :return: tuple of the number and whether the coordinate is relative
    """
    if isinstance(arg, int):
        return arg, False
    if len(arg) == 0:
        raise ValueError
    if arg[0] == "~":
        i = arg[1:]
        if len(i):
            return int(arg[1:]), True
        else:
            return 0, True
    else:
        return int(arg), False


def show_relative_coordinate(value: int, is_relative: bool = False) -> str:
    """
    stringifies a coordinate that may be relative, inverse to `parse_relative_coordinate`
    :param value: the coordinate
    :param is_relative: whether the coordinate is relative
    :return: the stringified coordinate
    """
    if is_relative:
        return f"~{value}"
    else:
        return str(value)


@dataclass
class RelativeCoordinates(Coordinates):
    """
    World coordinates, known at compile time, that may be offsets from the position at which the command is executing.
    """

    x_relative: bool
    y_relative: bool
    z_relative: bool

    _x: int
    _y: int
    _z: int

    @property
    def x(self):
        if self.x_relative:
            return f"~{self._x}"
        else:
            return self._x

    @property
    def y(self):
        if self.z_relative:
            return f"~{self._z}"
        else:
            return self._z

    @property
    def z(self):
        if self.z_relative:
            return f"~{self._z}"
        else:
            return self._z

    def __init__(self, x: int | str, y: int | str, z: int | str, x_relative=None, y_relative=None, z_relative=None):
        self._x, self.x_relative = parse_relative_coordinate(x)
        self._y, self.y_relative = parse_relative_coordinate(y)
        self._z, self.z_relative = parse_relative_coordinate(z)

        if x_relative is not None:
            self.x_relative = x_relative
        if y_relative is not None:
            self.y_relative = y_relative
        if z_relative is not None:
            self.z_relative = z_relative

    def __format__(self, format_spec) -> str:
        return f"{self.x} {self.y} {self.z}"

    def __add__(self, other):
        return RelativeCoordinates(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
            self.x_relative,
            self.y_relative,
            self.z_relative
        )

    def __sub__(self, other):
        return RelativeCoordinates(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
            self.x_relative,
            self.y_relative,
            self.z_relative
        )

    def exact(self) -> str:
        """
        coordinates for teleporting to the corner of the block, rather than the middle.
        :return: string representing the coordinates
        """
        return f"{self.x}.0 {self.y}.0 {self.z}.0"


# coordinates for the position at which the enclosing command is being executed
CURRENT = RelativeCoordinates("~", "~", "~")
