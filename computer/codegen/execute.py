from __future__ import annotations

from abc import ABC
from typing import Iterable

from computer.codegen.chain_context import command
from computer.codegen.command import Command
from computer.codegen.entity import Entity


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

    def at_entity(self, entity: Entity) -> Execute:
        self.parts.append(f"at {entity.selector()}")
        return self

    def as_entity(self, entity: Entity) -> Execute:
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

    def run(self, cmd: Command):
        self.parts.append(f"run {cmd.command}")
        command("execute " + " ".join(self.parts))

    def run_all(self, cmds: Iterable[Command]):
        for cmd in cmds:
            command("execute " + " ".join(self.parts) + f" run {cmd.command}")
