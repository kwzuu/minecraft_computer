from __future__ import annotations

from computer.codegen.variable import Variable
from computer.codegen.coordinates import Coordinates


class VectorVariable:
    __match_args__ = "x", "y", "z"

    def __init__(self, name: str, *args):
        match args:
            case int(x), int(y), int(z):
                self.name = name
                self.x = Variable(name + "_x", x)
                self.y = Variable(name + "_y", y)
                self.z = Variable(name + "_z", z)
            case Variable() as x, Variable() as y, Variable() as z:
                self.name = name
                self.x = x
                self.y = y
                self.z = z
            case (Coordinates(x, y, z), ):
                self.__init__(name, x, y, z)
            case ():
                self.__init__(name, 0, 0, 0)
            case x:
                raise ValueError(f"invalid arguments: {x}")

    def delete(self):
        self.x.delete()
        self.y.delete()
        self.z.delete()

    def __iadd__(self, other: VectorVariable):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __isub__(self, other: VectorVariable):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self
