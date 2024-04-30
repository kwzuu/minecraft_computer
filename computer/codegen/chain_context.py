from typing import Optional, Callable

from computer.codegen.command import Command
from computer.codegen.output import chain
from computer.codegen.coordinates import Coordinates

CHAIN_CONTEXT_STACK: list["ChainContext"] = []


class ChainContext:
    contents: list[Command]

    def __init__(self):
        self.contents = []

    def __enter__(self):
        CHAIN_CONTEXT_STACK.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CHAIN_CONTEXT_STACK.pop()

    def write(self, file, pos: Coordinates):
        chain(file, pos, self.contents)

    def add(self, the_command: Command):
        self.contents.append(the_command)


INIT_CONTEXT: Optional[ChainContext] = ChainContext()


def command(cmd: Command | str):
    if isinstance(cmd, str):
        cmd = Command(cmd)
    CHAIN_CONTEXT_STACK[-1].add(cmd)


def init_command(cmd: Command):
    INIT_CONTEXT.add(cmd)


class ChainGroup:
    chain_contexts: list[ChainContext]

    def __init__(self):
        self.chain_contexts = []

    def new(self) -> ChainContext:
        chain_context = ChainContext()
        self.chain_contexts.append(chain_context)
        return chain_context

    def add(self, ctx: ChainContext):
        self.chain_contexts.append(ctx)

    def write_out(self, file, base: Coordinates):
        for index, chain_context in enumerate(self.chain_contexts):
            chain_context.write(file, base + Coordinates(0, 0, index))


def capture[T]() -> Callable[[T], list[Command]]:
    ctx = ChainContext()
    ctx.__enter__()

    def inner(_: T) -> list[Command]:
        ctx.__exit__(None, None, None)
        return ctx.contents

    return inner
