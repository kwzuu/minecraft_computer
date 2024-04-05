use quartz_nbt::{NbtCompound, NbtTag};
use quartz_nbt::NbtTag::Int;
use crate::nbt_tag_extensions::NbtTagExtensions;

#[derive(Clone)]
pub struct Palette {
    palette: NbtCompound,
    next: u32,
}

impl Palette {
    fn new() -> Palette {
        Palette {
            palette: Default::default(),
            next: 0,
        }
    }

    fn contains(&self, name: &str) -> bool {
        self.palette.contains_key(name)
    }

    fn get_id(&self, name: &str) -> Option<u32> {
        self.palette.get(name)
            .ok()
            .and_then(NbtTag::int)
            .and_then(|x| x.try_into().ok())
    }
    fn get_id_or_insert(&mut self, name: &str) -> u32 {
        self.get_id(name).unwrap_or_else(|| {
            self.palette.insert(name.to_string(), Int(self.next as i32));
            let tmp = self.next;
            self.next += 1;
            tmp
        })
    }

    fn into_nbt(self) -> NbtCompound {
        self.palette
    }

    pub(crate) fn to_nbt(&self) -> NbtCompound {
        self.palette.clone()
    }
}
