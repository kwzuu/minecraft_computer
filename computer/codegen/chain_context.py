from typing import Optional, Callable

from computer.codegen.command import Command
from computer.codegen.output import chain
from computer.codegen.coordinates import Coordinates

"""
A LIFO stack of all the chain contexts.

The top element is one that is used to put new commands in.
To temporarily push a ChainContext to this stack, use a context manager.
The ChainContext will be removed from the stack when the context manager ends.
"""
CHAIN_CONTEXT_STACK: list["ChainContext"] = []


class ChainContext:
    """
    A context manager that puts together a chain of command blocks.
    intended for use with `ChainGroup`.
    """

    contents: list[Command]
    only_chain: bool

    def __init__(self, only_chain: bool = False):
        self.contents = []
        self.only_chain = only_chain

    def __enter__(self):
        CHAIN_CONTEXT_STACK.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CHAIN_CONTEXT_STACK.pop()

    def write(self, file, pos: Coordinates, **kwargs) -> None:
        """
        writes schematic assembly for the chain out to a file.
        keyword arguments are passed on to `chain`.
        :param file: the file to write to
        :param pos: the position at which to start the chain
        """
        chain(file, pos, self.contents, only_chain=self.only_chain, **kwargs)

    def add(self, the_command: Command) -> None:
        """
        adds a command to the chain
        :param the_command: the command to add
        """
        self.contents.append(the_command)


"""
The context used for commands to be run at initialize-time.
"""
INIT_CONTEXT: Optional[ChainContext] = ChainContext()


def command(cmd: Command | str) -> None:
    """
    runs a command in the current chain context
    :param cmd: the command to run
    """
    if isinstance(cmd, str):
        cmd = Command(cmd)
    # CHAIN_CONTEXT_STACK[-1].add(Command("say DEBUG: " + cmd.command))
    CHAIN_CONTEXT_STACK[-1].add(cmd)


def init_command(cmd: Command) -> None:
    """
    runs a command at initialize-time
    :param cmd: the command to run
    """
    INIT_CONTEXT.add(cmd)


class ChainGroup:
    """
    A group of command block chains, placed at positions increasing on the Z-axis.
    """

    # a list of chain contexts owned by this group
    chain_contexts: list[ChainContext]

    def __init__(self, *args, **kwargs):
        self.chain_contexts = []
        self.args = args
        self.kwargs = kwargs

    def new(self, *args, **kwargs) -> ChainContext:
        """
        Creates a new chain context in the group, returning it.
        :param args: positional arguments to pass on to ChainContext
        :param kwargs: keyword arguments to pass on to ChainContext
        :return: the newly-created context
        """
        chain_context = ChainContext(*(self.args + args), **(self.kwargs | kwargs))
        self.chain_contexts.append(chain_context)
        return chain_context

    def add(self, ctx: ChainContext) -> None:
        """
        adds an externally-created chain context to the group.
        :param ctx: the context to add
        """
        self.chain_contexts.append(ctx)

    def write_out(self, file, start_pos: Coordinates) -> None:
        """
        Writes the chain context out to a schematic assembly file at the given location
        :param file: the file to write out to
        :param start_pos: the world location to start from
        """
        for index, chain_context in enumerate(self.chain_contexts):
            chain_context.write(file, start_pos + Coordinates(0, 0, index))


def capture[T]() -> Callable[[T], list[Command]]:
    """
    Captures the command blocks produced by an expression, returning them in a list.

    example:
    ```
    commands_to_add_variables: list[Command] = capture()(my_variable.__iadd__(my_other_variable))
    ```
    :return: a function to be called on the expression
    """
    ctx = ChainContext()
    ctx.__enter__()

    def inner(_: T) -> list[Command]:
        ctx.__exit__(None, None, None)
        return ctx.contents

    return inner
