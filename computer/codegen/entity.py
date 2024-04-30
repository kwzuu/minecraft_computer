from computer.codegen.chain_context import command
from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates
from computer.codegen.execute import Execute, StoreLocation, Condition
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable

max_tag = 0


def new_tag() -> str:
    global max_tag
    name = "e" + str(max_tag)
    max_tag += 1
    return name


class Entity(StoreLocation, Condition):
    def __init__(self, kind: str):
        self.kind = kind
        self.uid = new_tag()
        self.summon = f"summon {self.kind} ~ ~ ~" + " {Tags:[" + repr(self.uid) + "]}"

    def condition(self, *args) -> str:
        return f"entity {self.selector()}"

    def create(self):
        command(self.summon)

    def create_if_not_exists(self):
        (
            Execute()
            .unless_condition(self)
            .run(Command(self.summon))
        )

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
        else:
            raise ValueError(f"{value}")

    def set_pos(self, coords: VectorVariable | Coordinates):
        match coords:
            case VectorVariable(x, y, z):
                self.set_nbt("Pos[0]", x, "double")
                self.set_nbt("Pos[1]", y, "double")
                self.set_nbt("Pos[2]", z, "double")
            case Coordinates() as c:
                command(f"tp {c.double()}")
            case _:
                raise ValueError(f"{coords}")

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
