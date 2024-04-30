from computer.codegen.chain_context import command
from computer.codegen.coordinates import Coordinates
from computer.codegen.execute import Execute, StoreLocation
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable

max_tag = 0


def new_tag() -> str:
    global max_tag
    name = "e" + str(max_tag)
    max_tag += 1
    return name


class Entity(StoreLocation):
    def __init__(self, kind: str):
        self.kind = kind
        self.uid = new_tag()

    def create(self):
        command(f"summon {self.kind}" + " {Tags:[" + repr(self.uid) + "]}")

    def destroy(self):
        command(f"kill {self.selector()}")

    def selector(self) -> str:
        return f"@e[tag={self.uid},limit=1]"

    def set_nbt(self, path: str, value: Variable | str | int, mc_type="int", scale=1):
        if isinstance(value, str) or isinstance(value, int):
            command(f"data modify"
                    f" entity {self.selector()}"
                    f" set {path} {value}")
        elif isinstance(value, Variable):
            (
                Execute()
                .store_result(self, path, mc_type, scale)
                .run(value.get())
            )

    def set_pos(self, coords: VectorVariable | Coordinates):
        match coords:
            case VectorVariable(v):
                self.set_nbt("Pos[0]", v.x, "double")
                self.set_nbt("Pos[1]", v.y, "double")
                self.set_nbt("Pos[2]", v.z, "double")
            case Coordinates(c):
                command(f"tp {c.double()}")

    def store_location(self, *args) -> str:
        match args:
            case (path, mc_type, scale):
                return f"entity {self.selector()} {path} {mc_type} {scale}"
            case (path, mc_type):
                return f"entity {self.selector()} {path} {mc_type} 1"
            case (path,):
                return f"entity {self.selector()} {path} int 1"
            case _:
                raise ValueError
