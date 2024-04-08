use std::cmp::max;
use quartz_nbt::{compound, NbtCompound, NbtList};
use crate::palette::Palette;
use crate::varint::VarintArray;

#[derive(Clone)]
pub struct Blocks {
    palette: Palette,
    data: VarintArray,
    block_entities: NbtList,
}

#[derive(Clone)]
struct BlockEntity {

}

impl Blocks {
    pub fn builder() -> BlocksBuilder {
        BlocksBuilder::new()
    }

    pub fn add_block_entity(&mut self, entity: BlockEntity) {
        todo!()
    }

    pub(crate) fn into_nbt(self) -> NbtCompound {
        compound! {
            "BlockEntities": self.block_entities,
            "Palette": self.palette.into_nbt(),
            "Data": self.data.into_nbt(),
        }
    }

    pub(crate) fn to_nbt(&self) -> NbtCompound {
        self.clone().into_nbt()
    }
}

struct BlocksBuilder {
    palette: Palette,
    blocks: Vec<(Coordinates, u32)>,
}

impl BlocksBuilder {
    fn new() -> Self {
        Self {
            palette: Palette::new(),
            blocks: vec![],
        }
    }

    fn add_block(&mut self, coordinates: Coordinates, id: &str) {
        let id = self.palette.get_id_or_insert(id);
        self.blocks.push((coordinates, id));
    }

    fn build(mut self) -> Blocks {
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
            block_entities: Default::default(),
        }
    }
}

#[derive(Copy, Clone, Eq, PartialEq)]
struct Dimensions {
    width: usize,
    height: usize,
    length: usize,
}

impl Dimensions {
    fn new(width: usize, height: usize, length: usize) -> Self {
        Self {
            width,
            height,
            length,
        }
    }

    pub fn width(&self) -> usize {
        self.width
    }

    pub fn height(&self) -> usize {
        self.height
    }

    pub fn length(&self) -> usize {
        self.length
    }

}

#[derive(Copy, Clone, Eq, PartialEq)]
struct Coordinates {
    pub x: usize,
    pub y: usize,
    pub z: usize,
}

impl Dimensions {
    fn size(&self) -> usize {
        self.height * self.width * self.length
    }
}

impl Dimensions {
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
            + self.y * dimensions.width * dimensions.height
        )
    }
}

#[derive(Clone, PartialEq, Eq)]
pub struct Array3d<T> {
    dimensions: Dimensions,
    items: Box<[T]>
}

impl<T: Copy> Array3d<T> {
    fn new_with(dimensions: Dimensions, item: T) -> Self {
        let size = dimensions.size();

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
    fn from_function<F: FnMut(usize, usize, usize)>(dimensions: Dimensions, mut f: F) {
        let size = dimensions.size();

        let mut v = Vec::with_capacity(size);
        for y in 0..dimensions.height {
            for z in 0..dimensions.width {
                for x in 0..dimensions.length {
                    v.push(f(x, y, z))
                }
            }
        }
    }

    pub fn get(&self, coordinates: &Coordinates) -> Option<&T> {
        coordinates.to_linear_in(&self.dimensions)
            .and_then(|x| self.items.get(x))
    }

    pub fn set(&mut self, coordinates: &Coordinates, item: T) {
        coordinates.to_linear_in(&self.dimensions)
            .map(|x| self.items[x] = item);
    }

    pub fn xzy_contents(&self) -> &[T] {
        &self.items
    }
}