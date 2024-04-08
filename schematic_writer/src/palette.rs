use quartz_nbt::{NbtCompound, NbtTag};
use quartz_nbt::NbtTag::Int;
use crate::nbt_tag_extensions::NbtTagExtensions;

/// A representation of the Palette object from the Sponge schematic format
/// Maps string keys to integer values, always returning the same value for the same key
#[derive(Clone)]
pub struct Palette {
    palette: NbtCompound,
    next: u32,
}

impl Palette {
    pub fn new() -> Palette {
        Palette {
            palette: Default::default(),
            next: 0,
        }
    }

    pub fn contains(&self, name: &str) -> bool {
        self.palette.contains_key(name)
    }

    pub fn get_id(&self, name: &str) -> Option<u32> {
        self.palette.get(name)
            .ok()
            .and_then(NbtTag::int)
            .and_then(|x| x.try_into().ok())
    }
    pub fn get_id_or_insert(&mut self, name: &str) -> u32 {
        self.get_id(name).unwrap_or_else(|| {
            self.palette.insert(name.to_string(), Int(self.next as i32));
            let tmp = self.next;
            self.next += 1;
            tmp
        })
    }

    pub(crate) fn into_nbt(self) -> NbtCompound {
        self.palette
    }

    pub(crate) fn to_nbt(&self) -> NbtCompound {
        self.palette.clone()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_palette() {
        let mut p = Palette::new();
        assert_eq!(p.get_id("minecraft:stone"), None);
        assert_eq!(p.get_id_or_insert("minecraft:stone"), 0);
    }
}