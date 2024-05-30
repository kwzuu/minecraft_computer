from computer.codegen.chain_context import command


def log(s: str):
    command("say LOG: " + s)