use quartz_nbt::NbtTag;
use quartz_nbt::NbtTag::Int;

// Extension methods for nbt tags

pub(crate) trait NbtTagExtensions {
    fn int(&self) -> Option<i32>;
}

impl NbtTagExtensions for NbtTag {
    fn int(&self) -> Option<i32> {
        match self {
            Int(i) => Some(*i),
            _ => None,
        }
    }
}
