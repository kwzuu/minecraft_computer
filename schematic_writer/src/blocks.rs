use std::cmp::max;
use quartz_nbt::{compound, NbtCompound, NbtList, NbtTag, NbtTagKind};
use crate::palette::Palette;
use crate::varint::VarintArray;

#[derive(Debug, Clone)]
pub struct Blocks {
    palette: Palette,
    data: VarintArray,
    block_entities: NbtList,
    pub(crate) dimensions: Dimensions,
}

#[derive(Debug, Clone)]
pub struct BlockEntity {
    pos: Coordinates,
    id: String,
    data: Option<NbtCompound>
}

impl BlockEntity {
    pub fn new(pos: Coordinates, id: String, data: Option<NbtCompound>) -> BlockEntity {
        Self {
            pos,
            id,
            data,
        }
    }

    pub fn into_nbt(self) -> NbtCompound {
        let mut nbt = NbtCompound::new();
        nbt.insert("Pos", self.pos.to_nbt());
        nbt.insert("Id", self.id);

        if let Some(data) = self.data {
            nbt.insert("Data", data)
        }

        nbt
    }
}

impl Blocks {
    pub fn builder() -> BlocksBuilder {
        BlocksBuilder::new()
    }

    pub(crate) fn into_nbt(self) -> NbtCompound {
        let mut nbt = compound! {

            "Palette": self.palette.into_nbt(),
            "Data": self.data.into_nbt(),
        };

        if self.block_entities.len() != 0 {
            nbt.insert("BlockEntities", self.block_entities)
        } else {
            nbt.insert("BlockEntities", NbtList::new_with_tag_kind_if_empty(NbtTagKind::Compound))
        }

        nbt
    }

    // pub(crate) fn to_nbt(&self) -> NbtCompound {
    //     self.clone().into_nbt()
    // }
}

#[derive(Debug)]
pub struct BlocksBuilder {
    palette: Palette,
    blocks: Vec<(Coordinates, u32)>,
    block_entities: NbtList
}

impl BlocksBuilder {
    pub fn new() -> Self {
        Self {
            palette: Palette::new(),
            blocks: vec![],
            block_entities: NbtList::new(),
        }
    }

    pub fn add_block_entity(&mut self, block_entity: BlockEntity) {
        self.block_entities.push(block_entity.into_nbt());
    }

    pub fn add_block(&mut self, coordinates: Coordinates, id: &str) {
        let id = self.palette.get_id_or_insert(id);
        self.blocks.push((coordinates, id));
    }

    pub fn build(mut self) -> Blocks {
        let mut max_x = 0;
        let mut max_y = 0;
        let mut max_z = 0;

        for (coords, _) in &self.blocks {
            max_x = max(max_x, coords.x);
            max_y = max(max_y, coords.y);
            max_z = max(max_z, coords.z);
        }

        let dimensions = Dimensions {
            width: max_x + 1,
            height: max_y + 1,
            length: max_z + 1,
        };

        let air_id = self.palette.get_id_or_insert("minecraft:air");

        let mut array = Array3d::new_with(dimensions, air_id);

        for (coords, id) in &self.blocks {
            array.set(coords, *id)
        }

        let mut varints = VarintArray::new();

        for i in array.xzy_contents() {
            varints.push_u32(*i)
        }

        Blocks {
            data: varints,
            palette: self.palette,
            block_entities: self.block_entities,
            dimensions,
        }
    }
}

#[derive(Debug, Copy, Clone, Eq, PartialEq)]
pub(crate) struct Dimensions {
    pub(crate) width: usize,
    pub(crate) height: usize,
    pub(crate) length: usize,
}

#[derive(Debug, Copy, Clone, Eq, PartialEq)]
pub struct Coordinates {
    pub x: usize,
    pub y: usize,
    pub z: usize,
}

impl Dimensions {
    fn volume(&self) -> usize {
        self.height * self.width * self.length
    }

    fn contains(&self, coordinates: &Coordinates) -> bool {
        coordinates.x < self.width
            && coordinates.y < self.height
            && coordinates.z < self.length
    }
}

impl Coordinates {
    fn to_linear_in(&self, dimensions: &Dimensions) -> Option<usize> {
        dimensions.contains(self).then(||
              self.x
            + self.z * dimensions.width
            + self.y * dimensions.width * dimensions.length
        )
    }

    fn to_nbt(&self) -> NbtTag {
        NbtTag::IntArray(vec![self.x as i32, self.y as i32, self.z as i32])
    }
}

impl From<(u16, u16, u16)> for Coordinates {
    fn from(value: (u16, u16, u16)) -> Self {
        Self {
            x: value.0 as usize,
            y: value.1 as usize,
            z: value.2 as usize,
        }
    }
}

#[derive(Clone, PartialEq, Eq)]
struct Array3d<T> {
    dimensions: Dimensions,
    items: Box<[T]>
}

impl<T: Copy> Array3d<T> {
    fn new_with(dimensions: Dimensions, item: T) -> Self {
        let size = dimensions.volume();

        let mut v = Vec::with_capacity(size);
        for _ in 0..size {
            v.push(item)
        }

        Self {
            dimensions,
            items: v.into_boxed_slice(),
        }
    }
}

impl<T> Array3d<T> {
    pub fn set(&mut self, coordinates: &Coordinates, item: T) {
        coordinates.to_linear_in(&self.dimensions)
            .map(|x| self.items[x] = item);
    }

    pub fn xzy_contents(&self) -> &[T] {
        &self.items
    }
}

#[cfg(test)]
mod tests {
    use quartz_nbt::NbtTag::IntArray;
    use super::*;

    #[test]
    fn test_block_builder() {
        let mut builder = BlocksBuilder::new();

        let stone = "minecraft:stone";
        let chest = "minecraft:chest";

        builder.add_block((0, 0, 0).into(), stone);
        builder.add_block((0, 0, 1).into(), stone);
        builder.add_block((1, 0, 0).into(), stone);
        builder.add_block((1, 0, 1).into(), chest);
        builder.add_block_entity(BlockEntity::new(
            (1, 0, 1).into(),
            chest.to_string(),
            None
        ));

        let mut blocks = builder.build();

        let stone_id = blocks.palette.get_id_or_insert(stone);
        let chest_id = blocks.palette.get_id_or_insert(chest);

        let mut data_target = VarintArray::new();

        data_target.push_u32(stone_id);
        data_target.push_u32(stone_id);
        data_target.push_u32(stone_id);
        data_target.push_u32(chest_id);

        assert_eq!(&data_target, &blocks.data);

        let mut block_entities_target = NbtList::new();

        block_entities_target.push(compound! {
            "Pos": IntArray(vec![1, 0, 1]),
            "Id": "minecraft:chest"
        });

        assert_eq!(&block_entities_target, &blocks.block_entities);
    }

    #[test]
    fn test_coordinates() {
        let coords: Coordinates = (1, 2, 3).into();

        assert_eq!(coords.x, 1);
        assert_eq!(coords.y, 2);
        assert_eq!(coords.z, 3);

        assert_eq!(coords.to_nbt(), IntArray(vec![1, 2, 3]));

        let dimensions = Dimensions {
            width: 3,
            height: 8,
            length: 4,
        };

        assert_eq!(coords.to_linear_in(&dimensions), Some(34));

        let empty = Dimensions {
            width: 0,
            height: 0,
            length: 0,
        };

        assert_eq!(coords.to_linear_in(&empty), None);

    }
}