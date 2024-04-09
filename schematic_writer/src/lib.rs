#![feature(hash_set_entry)]

use quartz_nbt::{compound, NbtCompound, NbtList};
use std::time::{SystemTime, UNIX_EPOCH};
use quartz_nbt::NbtTag::IntArray;
use blocks::Blocks;
use palette::Palette;
use varint::VarintArray;

mod varint;
mod nbt_tag_extensions;
mod palette;
mod blocks;

#[macro_use]
extern crate derive_builder;

/// Trait for reinterpreting the bytes of one integer as another
trait ReinterpretCast<T> {
    /// reinterpret the bytes of `self` as `T`
    fn reinterpret_cast(&self) -> T;
}

impl ReinterpretCast<i16> for u16 {
    fn reinterpret_cast(&self) -> i16 {
        i16::from_ne_bytes(self.to_ne_bytes())
    }
}

/// Schematic metadata
#[derive(Clone)]
struct Metadata {
    name: String,
    author: String,
    required_mods: Box<[String]>,
}

impl Metadata {
    fn into_nbt(self) -> NbtCompound {
        compound! {
            "Name": self.name,
            "Author": self.author,
            "Date": SystemTime::now()
                .duration_since(UNIX_EPOCH).unwrap()
                .as_millis() as i64,
            "RequiredMods": NbtList::from(self.required_mods.to_vec())
        }
    }
}

#[derive(Clone)]
struct Biomes {
    palette: Palette,
    data: VarintArray,
}

impl Biomes {
    fn into_nbt(self) -> NbtCompound {
        compound! {
            "Palette": self.palette.into_nbt(),
            "Data": self.data.clone().into_nbt(),
        }
    }
}

#[derive(Clone)]
struct Entities {}

impl Entities {
    fn into_nbt(self) -> NbtCompound {
        todo!()
    }
}

#[derive(Clone, Builder)]
pub struct Schematic {
    offset: Option<(i32, i32, i32)>,
    metadata: Metadata,
    blocks: Blocks,
    biomes: Option<Biomes>,
    entities: Option<Entities>,
}

impl Schematic {
    pub fn into_nbt(self) -> NbtCompound {
        let mut schematic = compound! {
            "Version": 3i32,
            "DataVersion": 3578i32,
            "Metadata": self.metadata.into_nbt(),
            "Width":  *&self.blocks.dimensions.width as i16,
            "Height": *&self.blocks.dimensions.height as i16,
            "Length": *&self.blocks.dimensions.length as i16,
            "Blocks": self.blocks.into_nbt(),
        };

        match self.offset {
            None => {}
            Some((x, y, z)) => {
                schematic.insert("Offset", IntArray(vec![x, y, z]));
            }
        }

        match self.biomes {
            None => {}
            Some(biomes) => {
                schematic.insert("Biomes", biomes.into_nbt())
            }
        }

        match self.entities {
            None => {}
            Some(entities) => {
                schematic.insert("Entities", entities.into_nbt())
            }
        }

        schematic
    }

    pub fn to_nbt(&self) -> NbtCompound {
        self.clone().into_nbt()
    }
}
