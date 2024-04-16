from main import chain, Coordinates, assemble_schematic


def computer(file):
    chain(file, Coordinates(0, 0, 1), [
        "say hello world",
        "say meow"
    ])


if __name__ == "__main__":
    assemble_schematic(computer, "computer")
