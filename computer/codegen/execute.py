from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterable, Optional

from computer.codegen.chain_context import command, ChainContext
from computer.codegen.command import Command


class StoreLocation(ABC):
    """
    base class for constructs that can function as an argument to `execute store`
    """

    def store_location(self, *args) -> str:
        """
        gets a string that can be used as an argument to `execute store` in order to put a value into `self`
        :param args: additional arguments needed to specify the location to store to
        :return: a string that can be used with `execute store`
        """
        pass


class Condition(ABC):
    """
    base class for constructs that can function as an argument to `execute if` and `execute unless`
    """

    def condition(self, *args) -> str:
        """
        gets a string that can be used as an argument to `execute if` and `execute unless`
        :param args: additional arguments needed to specify the condition
        :return: a string that can be used with `execute if` and execute unless``
        """
        pass

    def if_true(self, cmd: Command | list[Command]) -> Condition:
        """
        runs the command or list of commands if the condition is true, returning it after to enable chaining of methods
        :param cmd: the command or list of commands to run
        :return: the condition
        """
        execute = Execute().if_condition(self)
        if isinstance(cmd, Command):
            execute.run(cmd)
        else:
            execute.run_all(cmd)
        return self

    def if_false(self, cmd: Command | list[Command]) -> Condition:
        """
        runs the command or list of commands if the condition is false, returning it after to enable chaining of methods
        :param cmd: the command or list of commands to run
        :return: the condition
        """
        execute = Execute().unless_condition(self)
        if isinstance(cmd, Command):
            execute.run(cmd)
        else:
            execute.run_all(cmd)
        return self


class Execute:
    """
    builder for `execute` commands
    """

    def __init__(self):
        self.parts = []

    def at_entity(self, entity: "Entity") -> Execute:
        """
        runs the command at the feet of an entity
        :param entity: the entity to execute at
        :return: the builder
        """
        self.parts.append(f"at {entity.selector()}")
        return self

    def as_entity(self, entity: "Entity") -> Execute:
        """
        runs the command as an entity
        :param entity: the entity to execute as
        :return: the builder
        """
        self.parts.append(f"as {entity.selector()}")
        return self

    def if_condition(self, condition: Condition) -> Execute:
        """
        runs the command only if a condition is true
        :param condition: the condition to check
        :return: the builder
        """
        self.parts.append(f"if {condition.condition()}")
        return self

    def unless_condition(self, condition: Condition) -> Execute:
        """
        runs the command only if a condition is false
        :param condition: the condition to check
        :return: the builder
        """
        self.parts.append(f"unless {condition.condition()}")
        return self

    def store_result(self, store_location: StoreLocation, *args) -> Execute:
        """
        stores the result of the command in a construct that can support storing
        :param store_location: the location to store to
        :param args: additional arguments needed to specify where to store to
        :return: the builder
        """
        self.parts.append(f"store result {store_location.store_location(*args)}")
        return self

    def store_success(self, store_location: StoreLocation, *args) -> Execute:
        """
        stores the success of the command in a construct that can support storing
        :param store_location: the location to store to
        :param args: additional arguments needed to specify where to store to
        :return: the builder
        """
        self.parts.append(f"store success {store_location.store_location(*args)}")
        return self

    def run(self, cmd: Command = None) -> Optional[Run]:
        """
        runs a command if one is present, or returns a context manager that accumulates commands if one is not.
        :param cmd: the command to run
        :return: returns a `Run` instance if no command is specified.
        """
        if cmd is not None:
            self.parts.append(f"run {cmd.command}")
            command("execute " + " ".join(self.parts))
        else:
            return Run(self)

    def run_all(self, cmds: Iterable[Command]) -> None:
        """
        runs a series of commands, using multiple command blocks if necessary.
        warning: evaluates all parts of the execute command for each command to run.
        :param cmds: the commands to run
        """
        for cmd in cmds:
            command("execute " + " ".join(self.parts) + f" run {cmd.command}")


@dataclass
class Run:
    """
    a context manager that captures commands within and runs them with the `Execute` instance provided upon exiting
    """

    execute: Execute

    def __enter__(self):
        self.ctx = ChainContext().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctx.__exit__(None, None, None)
        self.execute.run_all(self.ctx.contents)


last_cond: Optional[Condition] = None
last_negated: Optional[Condition] = None


def run_if(condition: Condition) -> Run:
    """
    returns a `Run` instance that executes commands it captures if the condition is true
    :param condition: the condition to check
    :return: a `Run` instance
    """
    global last_negated, last_cond
    last_negated = False
    last_cond = condition
    return Execute().if_condition(condition).run()


def run_unless(condition: Condition) -> Run:
    """
    returns a `Run` instance that executes commands it captures if the condition is false
    :param condition: the condition to check
    :return: a `Run` instance
    """
    global last_negated, last_cond
    last_negated = True
    last_cond = condition
    return Execute().unless_condition(condition).run()


def run_else() -> Run:
    """
    returns a `Run` instance that executes commands it captures if the previous call to `run_if` or `run_unless`
    did not run anything.
    :return: a `Run` instance
    """
    return (run_unless if last_negated else run_if)(last_cond)
