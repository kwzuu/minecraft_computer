from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterable

from computer.codegen.chain_context import command, ChainContext
from computer.codegen.command import Command


class StoreLocation(ABC):
    def store_location(self, *args) -> str:
        pass


class Condition(ABC):
    def condition(self, *args) -> str:
        pass

    def if_true(self, cmd: Command | list[Command]) -> Condition:
        execute = Execute().if_condition(self)
        if isinstance(cmd, Command):
            execute.run(cmd)
        else:
            execute.run_all(cmd)
        return self

    def if_false(self, cmd: Command | list[Command]) -> Condition:
        execute = Execute().unless_condition(self)
        if isinstance(cmd, Command):
            execute.run(cmd)
        else:
            execute.run_all(cmd)
        return self


class Execute:
    def __init__(self):
        self.parts = []

    def at_entity(self, entity: "Entity") -> Execute:
        self.parts.append(f"at {entity.selector()}")
        return self

    def as_entity(self, entity: "Entity") -> Execute:
        self.parts.append(f"as {entity.selector()}")
        return self

    def if_condition(self, condition: Condition) -> Execute:
        self.parts.append(f"if {condition.condition()}")
        return self

    def unless_condition(self, condition: Condition) -> Execute:
        self.parts.append(f"unless {condition.condition()}")
        return self

    def store_result(self, store_location: StoreLocation, *args) -> Execute:
        self.parts.append(f"store result {store_location.store_location(*args)}")
        return self

    def store_success(self, store_location: StoreLocation, *args) -> Execute:
        self.parts.append(f"store success {store_location.store_location(*args)}")
        return self

    def run(self, *args):
        match args:
            case Command(cmd),:
                self.parts.append(f"run {cmd}")
                command("execute " + " ".join(self.parts))
            case ():
                return Run(self)
            case _:
                raise ValueError

    def run_all(self, cmds: Iterable[Command]):
        for cmd in cmds:
            command("execute " + " ".join(self.parts) + f" run {cmd.command}")


@dataclass
class Run:
    execute: Execute

    def __enter__(self):
        self.ctx = ChainContext().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctx.__exit__(None, None, None)
        self.execute.run_all(self.ctx.contents)


def run_if(condition: Condition) -> Run:
    return Execute().if_condition(condition).run()


def run_unless(condition: Condition) -> Run:
    return Execute().unless_condition(condition).run()
