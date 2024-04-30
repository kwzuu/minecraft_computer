from computer.codegen.chain_context import init_command
from computer.codegen.command import Command

registered_constants = set()


def constant(val: int):
    if val not in registered_constants:
        registered_constants.add(val)
        init_command(Command(f"scoreboard players set {val} vars {val}"))
