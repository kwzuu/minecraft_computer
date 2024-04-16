#!/bin/python3.12
from main import chain, Coordinates, assemble_schematic


def variable_initialize(dst: str, val: int) -> list[str]:
    return [f"scoreboard players set {dst} vars {val}"]


def variable_operation(dst: str, op: str, src: str) -> list[str]:
    return [f"scoreboard players operation {dst} vars {op} {src} vars"]


def create_tagged_entity(tags: list[str], kind="minecraft:armor_stand") -> list[str]:
    return [f"summon " + kind + " {Tags:" + repr(tags) + "}"]


MEM_BASE = Coordinates(0, 128, 0)
MEM_SIZE = Coordinates(16, 16, 16)
MEM_END = MEM_BASE + MEM_SIZE


def initialize_memory() -> list[str]:
    xs = []
    xs += create_tagged_entity(["memory_getter"])
    xs.append(
        f"fill {MEM_BASE} {MEM_SIZE} minecraft:barrel"
        '{Items:['
        '{Slot:0b,id:"minecraft:stone",Count:1b},'
        '{Slot:1b,id:"minecraft:stone",Count:1b}'
        ']}')
    xs += variable_initialize("16", 16)
    xs += variable_initialize("256", 256)
    return xs


MEM_GETTER = "@e[tag=memory_getter,limit=1]"


def memory_load(index: str, dest: str) -> list[str]:
    xs = []

    xs += variable_initialize("mem_index_x", MEM_BASE.x)
    xs += variable_initialize("mem_index_y", MEM_BASE.y)
    xs += variable_initialize("mem_index_z", MEM_BASE.z)

    xs += variable_operation("mem_offset_x", "=", index)
    xs += variable_operation("mem_offset_y", "=", index)
    xs += variable_operation("mem_offset_z", "=", index)

    xs += variable_operation("mem_offset_x", "%=", str(MEM_SIZE.x))

    xs += variable_operation("mem_offset_z", "/=", str(MEM_SIZE.x))
    xs += variable_operation("mem_offset_z", "%=", str(MEM_SIZE.x))

    xs += variable_operation("mem_offset_y", "/=", str(MEM_SIZE.x * MEM_SIZE.z))

    xs += variable_operation("mem_index_x", "+=", "mem_offset_x")
    xs += variable_operation("mem_index_y", "+=", "mem_offset_y")
    xs += variable_operation("mem_index_z", "+=", "mem_offset_z")

    for i, j in [("Pos[0]", "mem_index_x"), ("Pos[1]", "mem_index_y"), ("Pos[2]", "mem_index_z")]:
        xs.append("execute"
                  f" store result entity {MEM_GETTER} {i} double 1"
                  f" run scoreboard players get {j} vars")

    xs.append("execute"
              f" at {MEM_GETTER}"
              " store result score high_half vars"
              " run data get block ~ ~ ~ Items[0].Count")
    xs.append("execute"
              f" at {MEM_GETTER}"
              f" store result score {dest} vars"
              " run data get block ~ ~ ~ Items[1].Count")

    xs += variable_operation(dest, "-=", "1")
    xs += variable_operation("high_half", "-=", "1")
    xs += variable_operation("high_half", "*=", "64")
    xs += variable_operation(dest, "+=", "high_half")

    return xs


def computer(file):
    chain(file, Coordinates(0, 0, 1), [
        "say hello world",
        "say meow"
    ])


if __name__ == "__main__":
    assemble_schematic(computer, "computer")
