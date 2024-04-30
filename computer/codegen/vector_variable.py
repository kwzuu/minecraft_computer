from __future__ import annotations
from computer.codegen.variable import Variable
from computer.codegen.coordinates import Coordinates


class VectorVariable:
    def __init__(self, name: str, *args, **kwargs):
        match args:
            case int(x), int(y), int(z):
                self.name = name
                self.x = Variable(name + "_x", x)
                self.y = Variable(name + "_y", y)
                self.z = Variable(name + "_z", z)
            case Variable(x), Variable(y), Variable(z):
                self.name = name
                self.x = x
                self.y = y
                self.z = z
            case Coordinates(coords):
                self.__init__(name, coords.x, coords.y, coords.z)
            case ():
                self.__init__(name,
                              kwargs.get("x") or 0,
                              kwargs.get("y") or 0,
                              kwargs.get("z") or 0)
            case _:
                raise ValueError

    def delete(self):
        self.x.delete()
        self.y.delete()
        self.z.delete()

    def __iadd__(self, other: VectorVariable):
        self.x += other.x
        self.y += other.y
        self.z += other.z

    def __isub__(self, other: VectorVariable):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
