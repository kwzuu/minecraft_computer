from __future__ import annotations

from dataclasses import dataclass

from computer.codegen.command import Command
from computer.codegen.coordinates import Coordinates
from computer.codegen.execute import StoreLocation


@dataclass
class ItemSlot(StoreLocation):
    """
    an item slot in an inventory
    """

    block: Block
    slot: int

    def store_location(self, *args):
        if len(args):
            scale = args[0]
        else:
            scale = 1
        self.block.store_location(f"Items[{self.slot}].Count", "byte", scale)

    def get(self) -> Command:
        return Command(f"data get block {self.block.position}")


@dataclass
class Block(StoreLocation):
    """
    representation of a block entity
    """

    position: Coordinates

    def store_location(self, *args) -> str:
        match args:
            case path, mc_type, scale:
                return f"block {self.position} {path} {mc_type} {scale}"
            case path, mc_type:
                return f"block {self.position} {path} {mc_type} 1"
            case (path,):
                return f"block {self.position} {path} int 1"
            case _:
                raise ValueError

    def slot(self, slot: int) -> ItemSlot:
        """
        returns a representation for a slot in this block entity's inventory
        :param slot: the index of the slot to use
        :return: the representation for the slot
        """
        return ItemSlot(self, slot)
