from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from computer.codegen.chain_context import command, capture, INIT_CONTEXT
from computer.codegen.command import Command
from computer.codegen.execute import StoreLocation, Condition

registered_names = set()


def find_name(base_name: str) -> str:
    """
    finds a name for a variable, adding numbers to the end if necessary
    :param base_name: the name to try first or append numbers to if it is taken
    :return: the found name
    """
    if base_name in registered_names:
        n = 0
        while True:
            trial = base_name + str(n)
            if trial not in registered_names:
                return trial
            n += 1
    return base_name


@dataclass
class VariableComparison(Condition):
    """
    a comparison between two variables
    """

    left: Variable
    operator: str
    right: Variable

    def condition(self, *args):
        return f"score {self.left.name} vars {self.operator} {self.right.name} vars"


@dataclass
class IntRange:
    """
    an open or closed range over the integers
    """

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
    """
    Condition for checking whether a variable matches a range or integer
    """

    variable: Variable
    int_range: IntRange | int

    def condition(self, *args) -> str:
        return f"score {self.variable.name} vars matches {self.int_range}"


registered_constants: dict[int, Variable] = {}


class Variable(StoreLocation):
    """
    a scoreboard variable for use in runtime computations
    """

    def __init__(self, name: str, value: int = 0):
        name = find_name(name)
        if name in registered_names:
            raise Exception(f"duplicate name: {name}")
        self.name = name
        registered_names.add(name)
        self.set(value)

    def delete(self) -> None:
        """
        removes the variable from the scoreboard and the registered name list
        """
        registered_names.remove(self.name)
        command(f"scoreboard players reset {self.name} vars")

    @staticmethod
    def constant(const: int) -> Variable:
        """
        returns a variable corresponding to a constant
        :param const: the constant
        :return: the variable
        """
        if const not in registered_constants:
            with INIT_CONTEXT:
                var = Variable(str(const), const)
            registered_constants[const] = var
            return var
        return registered_constants[const]

    def operation(self, op: str, src: Variable | int, inplace=True) -> Variable:
        """
        performs a scoreboard operation on either the variable or a clone of the variable, returning the result
        :param op: the operator
        :param src: the variable for the other operand
        :param inplace: whether to perform the operation on this variable or a clone
        :return: the result
        """
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
        """
        sets the variable to a constant or another variable
        :param other: the constant or other variable
        """
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
        """
        returns the minimum of this variable and another
        :param other: the other variable
        :param inplace: whether to perform the operation in place
        :return: the result
        """
        return self.operation("<", other, inplace=inplace)

    def max(self, other, inplace=False):
        """
        returns the maximum of this variable and another
        :param other: the other variable
        :param inplace: whether to perform the operation in place
        :return: the result
        """
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

    def clone(self, base_name="var_") -> Variable:
        """
        returns a copy of the variable with the same value
        :return: the new variable
        """
        var = Variable(find_name(base_name))
        var.set(self)
        return var

    def bitslice(self, skip: int, length: int, last=False, inplace=False):
        """
        returns a slice of the bits in this variable
        :param skip: the number of bits of low significance to skip
        :param length: the number of bits to keep in the result
        :param last: whether there are guaranteed to be no more significant bits set than those in the slice
        :param inplace: whether to perform the operation in place
        :return:
        """
        if inplace:
            dst = self
        else:
            dst = self.clone(self.name)

        if skip > 0:
            dst /= (1 << skip)
        if not last:
            dst %= (1 << length)

        return dst

    def sign_extend(self, width: int) -> None:
        """
        sign extends the current value in place
        :param width: the width to sign extend from
        """
        n = 1 << (width - 1)
        (self >= n).if_true(capture()(self.__isub__(n)))

    def sign_extended(self, width: int) -> Variable:
        """
        sign extends a copy of the current value
        :param width: the width to sign extend from
        :return: the result
        """
        var = self.clone(self.name)
        var.sign_extend(width)
        return var

    def store_location(self) -> str:
        return f"score {self.name} vars"

    def get(self) -> Command:
        """
        returns a command to get the value of the variable
        :return: the command
        """
        return Command(f"scoreboard players get {self.name} vars")

    def matches(self, int_range: IntRange) -> VariableMatches:
        return VariableMatches(self, int_range)
