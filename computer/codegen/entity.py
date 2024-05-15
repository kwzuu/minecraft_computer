from computer.codegen.chain_context import command
from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates
from computer.codegen.execute import Execute, StoreLocation, Condition
from computer.codegen.variable import Variable
from computer.codegen.vector_variable import VectorVariable

max_tag = 0


def new_tag() -> str:
    """
    gets a new unique tag
    :return:
    """
    global max_tag
    name = "e" + str(max_tag)
    max_tag += 1
    return name


class Entity(StoreLocation, Condition):
    """
    representation of a unique minecraft entity
    """
    def __init__(self, kind: str):
        self.kind = kind
        self.uid = new_tag()
        self.summon = f"summon {self.kind} ~ ~ ~" + " {Tags:[" + repr(self.uid) + "]}"
        self._selector = f"@e[tag={self.uid},limit=1]"

    def condition(self, *_) -> str:
        """
        returns a condition for whether the entity exists, to be used by `execute if` and `execute unless`
        :return: the formatted condition
        """
        return f"entity {self.selector()}"

    def create(self) -> None:
        """
        creates the entity if it does not already exist.
        """
        (
            Execute()
            .unless_condition(self)
            .run(Command(self.summon))
        )

    def destroy(self) -> None:
        """
        kills the entity
        """
        command(f"kill {self.selector()}")

    def selector(self) -> str:
        """
        returns a selector identifying the entity uniquely
        :return: the selector
        """
        return self._selector

    def set_nbt(self, path: str, value: Variable | str | int, mc_type="int", scale=1) -> None:
        """
        sets an nbt property of the entity to that of a variable, snbt object, or integer.
        :param path: the path of the nbt property
        :param value: the value to store
        :param mc_type: the type of the value, if using a variable
        :param scale: the amount to multiply the value by, if using a variable
        """
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

    def set_pos(self, coords: VectorVariable | Coordinates) -> None:
        """
        sets the position of the entity to a position known at compile time or runtime
        uses fewer command blocks if the position is known at compile time
        :param coords: the coordinates to use
        """
        match coords:
            case VectorVariable(x, y, z):
                self.set_nbt("Pos[0]", x, "double")
                self.set_nbt("Pos[1]", y, "double")
                self.set_nbt("Pos[2]", z, "double")
            case Coordinates() as c:
                command(f"tp {self.selector()} {c.exact()}")
            case _:
                raise ValueError(f"{coords}")

    def store_location(self, *args) -> str:
        """
        stores a value into the entity's nbt
        :param args: (path: str, mc_type: str = "int", scale: float = 1)
        :return: the formatted store location
        """
        match args:
            case (path, mc_type, scale):
                return f"entity {self.selector()} {path} {mc_type} {scale}"
            case (path, mc_type):
                return f"entity {self.selector()} {path} {mc_type} 1"
            case (path,):
                return f"entity {self.selector()} {path} int 1"
            case _:
                raise ValueError
