use std::ops::Deref;
use std::time::{Instant, SystemTime, UNIX_EPOCH};
use quartz_nbt::{compound, NbtCompound, NbtList};

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
struct Palette {

}

impl Palette {
    fn to_nbt(&self) -> NbtCompound {
        todo!()
    }
}

#[derive(Clone)]
pub struct VarintArray {
    bytes: Vec<u8>
}

impl VarintArray {
    fn take(self) -> Vec<u8> {
        self.bytes
    }

    fn bytes(&self) -> &[u8] {
        &self.bytes
    }

    pub fn new() -> Self {
        Self {
            bytes: vec![],
        }
    }

    fn push_byte(&mut self, byte: u8) {
        self.bytes.push(byte)
    }
    fn push_u32(&mut self, mut value: u32) {
        const SEGMENT_BITS: u32 = 0x7f;
        const CONTINUE_BIT: u32 = 0x80;

        loop {
            if value & !SEGMENT_BITS == 0 {
                self.push_byte(value as u8);
                return
            }

            self.push_byte((value & SEGMENT_BITS | CONTINUE_BIT) as u8);
            value >>= 7;
        }
    }

    fn push_u64(&mut self, mut value: u64) {
        const SEGMENT_BITS: u64 = 0x7f;
        const CONTINUE_BIT: u64 = 0x80;

        loop {
            if value & !SEGMENT_BITS == 0 {
                self.push_byte(value as u8);
                return
            }

            self.push_byte((value & SEGMENT_BITS | CONTINUE_BIT) as u8);
            value >>= 7;
        }
    }

    pub fn push_int(&mut self, value: i32) {
        self.push_u32(u32::from_ne_bytes(value.to_ne_bytes()));
    }

    pub fn push_long(&mut self, value: i64) {
        self.push_u64(u64::from_ne_bytes(value.to_ne_bytes()));
    }

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
struct Entities {

}

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