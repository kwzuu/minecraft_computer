use quartz_nbt::{compound, NbtCompound, NbtList};
use std::ops::Deref;
use std::time::{SystemTime, UNIX_EPOCH};
use varint::VarintArray;

mod varint;

#[macro_use]
extern crate derive_builder;

trait ReinterpretCast<T> {
    fn reinterpret_cast(&self) -> T;
}

impl ReinterpretCast<i16> for u16 {
    fn reinterpret_cast(&self) -> i16 {
        i16::from_ne_bytes(self.to_ne_bytes())
    }
}

#[derive(Clone)]
struct Metadata {
    name: String,
    author: String,
    required_mods: Box<[String]>,
}

impl Metadata {
    fn to_nbt(&self) -> NbtCompound {
        compound! {
            "Name": &self.name,
            "Author": &self.author,
            "Date": SystemTime::now()
                .duration_since(UNIX_EPOCH).unwrap()
                .as_millis() as i64,
            "RequiredMods": NbtList::from(self.required_mods.clone().to_vec())
        }
    }
}
#[derive(Clone)]
struct Blocks {
    palette: Palette,
}

impl Blocks {
    fn data(&self) -> Vec<u8> {
        todo!()
    }

    fn block_entities(&self) -> NbtList {
        todo!()
    }

    fn to_nbt(&self) -> NbtCompound {
        compound! {
            "Palette": self.palette.to_nbt(),
            "Data": self.data(),
            "BlockEntities": self.block_entities(),
        }
    }
}

#[derive(Clone)]
struct Palette {}

impl Palette {
    fn to_nbt(&self) -> NbtCompound {
        todo!()
    }
}

#[derive(Clone)]
struct Biomes {
    palette: Palette,
    data: VarintArray,
}

impl Biomes {
    fn to_nbt(&self) -> NbtCompound {
        compound! {
            "Palette": self.palette.to_nbt(),
            "Data": self.data.to_nbt(),
        }
    }
}

#[derive(Clone)]
struct Entities {}

impl Entities {
    fn to_nbt(&self) -> NbtCompound {
        todo!()
    }
}

#[derive(Builder)]
struct Schematic {
    dims: (u16, u16, u16),
    offset: (i32, i32, i32),
    metadata: Metadata,
    blocks: Blocks,
    biomes: Biomes,
    entities: Entities,
}

impl Schematic {
    pub fn to_nbt(&self) -> NbtCompound {
        compound! {
            "Version": 3i32,
            "DataVersion": 3578i32,
            "Metadata": self.metadata.to_nbt(),
            "Width":  self.dims.0.reinterpret_cast(),
            "Height": self.dims.1.reinterpret_cast(),
            "Length": self.dims.2.reinterpret_cast(),
            "Offset": [self.offset.0, self.offset.1, self.offset.2],
            "Blocks": self.blocks.to_nbt(),
            "Biomes": self.biomes.to_nbt(),
            "Entities": self.entities.to_nbt(),
        }
    }
}
