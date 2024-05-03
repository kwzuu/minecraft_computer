from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from computer.codegen.chain_context import command, capture, init_command, INIT_CONTEXT
from computer.codegen.command import Command
from computer.codegen.execute import StoreLocation, Condition

registered_names = set()


def find_name(name: str) -> str:
    if name in registered_names:
        n = 0
        while True:
            trial = name + str(n)
            if trial not in registered_names:
                return trial
            n += 1
    return name


@dataclass
class VariableComparison(Condition):
    left: Variable
    operator: str
    right: Variable

    def condition(self, *args) -> str:
        return f"score {self.left.name} vars {self.operator} {self.right.name} vars"


@dataclass
class IntRange:
    left: Optional[int]
    right: Optional[int]

    def __format__(self, format_spec):
        if self.left is None:
            if self.right is None:
                raise ValueError
            else:
                return f"..{self.right}"
        else:
            if self.right is None:
                return f"{self.left}.."
            else:
                return f"{self.left}..{self.right}"


@dataclass
class VariableMatches(Condition):
    variable: Variable
    int_range: IntRange | int

    def condition(self, *args) -> str:
        return f"score {self.variable.name} vars matches {self.int_range}"


registered_constants = {}


class Variable(StoreLocation):
    def __init__(self, name: str, value: int = 0):
        if name in registered_names:
            raise Exception(f"duplicate name: {name}")
        self.name = name
        registered_names.add(name)
        self.initialize(value)

    def delete(self):
        registered_names.remove(self.name)
        command(f"scoreboard players reset {self.name} vars")

    def initialize(self, val: int):
        command(f"scoreboard players set {self.name} vars {val}")

    @staticmethod
    def constant(val: int) -> Variable:
        if val not in registered_constants:
            with INIT_CONTEXT:
                var = Variable(str(val), val)
            registered_constants[val] = var
            return var
        return registered_constants[val]

    def operation(self, op, src: Variable | int, inplace=True):
        if inplace:
            if isinstance(src, int):
                Variable.constant(src)
                src_name = str(src)
            else:
                src_name = src.name
            command(f"scoreboard players operation {self.name} vars {op} {src_name} vars")
            return self
        else:
            var = self.clone()
            var.operation(op, src)
            return var

    def set(self, other: Variable | int) -> None:
        if isinstance(other, Variable):
            self.operation("=", other)
        else:
            command(f"scoreboard players set {self.name} vars {other}")

    def __add__(self, other):
        if isinstance(other, Variable):
            return self.operation("+=", other, inplace=False)
        var = self.clone()
        var += other
        return var

    def __iadd__(self, other):
        if isinstance(other, Variable):
            return self.operation("+=", other)
        command(f"scoreboard players add {self.name} vars {other}")
        return self

    def __sub__(self, other):
        if isinstance(other, Variable):
            return self.operation("-=", other, inplace=False)
        var = self.clone()
        var -= other
        return var

    def __isub__(self, other):
        if isinstance(other, Variable):
            return self.operation("-=", other)
        command(f"scoreboard players remove {self.name} vars {other}")
        return self

    def __mul__(self, other):
        return self.operation("*=", other, inplace=False)

    def __imul__(self, other):
        return self.operation("*=", other)

    def __truediv__(self, other):
        return self.operation("/=", other, inplace=False)

    def __itruediv__(self, other):
        return self.operation("/=", other)

    def __mod__(self, other):
        return self.operation("%=", other, inplace=False)

    def __imod__(self, other):
        return self.operation("%=", other)

    def min(self, other, inplace=False):
        return self.operation("<", other, inplace=inplace)

    def max(self, other, inplace=False):
        return self.operation(">", other, inplace=inplace)

    def __lt__(self, other) -> Condition:
        if isinstance(other, Variable):
            return VariableComparison(self, "<", other)
        else:
            return VariableMatches(self, other - 1)

    def __le__(self, other) -> Condition:
        if isinstance(other, Variable):
            return VariableComparison(self, "<=", other)
        else:
            return VariableMatches(self, IntRange(None, other))

    def __eq__(self, other: Variable | int) -> Condition:
        if isinstance(other, Variable):
            return VariableComparison(self, "=", other)
        else:
            return VariableMatches(self, other)

    def equals(self, other: Variable | int) -> Condition:
        return self == other

    def __ge__(self, other) -> Condition:
        if isinstance(other, Variable):
            return VariableComparison(self, ">=", other)
        else:
            return VariableMatches(self, IntRange(other, None))

    def __gt__(self, other) -> Condition:
        if isinstance(other, Variable):
            return VariableComparison(self, ">", other)
        else:
            return VariableMatches(self, IntRange(other + 1, None))

    def clone(self) -> Variable:
        var = Variable(find_name("var_"))
        var.set(self)
        return var

    def bitslice(self, skip: int, length: int, last=False, inplace=False):
        if inplace:
            dst = self
        else:
            dst = self.clone()

        if skip > 0:
            dst /= (1 << skip)
        if not last:
            dst %= (1 << length)

        return dst

    def sign_extend(self, width: int):
        n = 1 << (width - 1)
        (self >= n).if_true(capture()(self.__isub__(n)))

    def sign_extended(self, width: int) -> Variable:
        var = self.clone()
        var.sign_extend(width)
        return var

    def store_location(self) -> str:
        return f"score {self.name} vars"

    def get(self) -> Command:
        return Command(f"scoreboard players get {self.name} vars")
