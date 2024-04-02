use quartz_nbt::NbtCompound;

// https://wiki.vg/VarInt_And_VarLong

#[derive(Clone)]
pub struct VarintArray {
    bytes: Vec<u8>,
}

impl VarintArray {
    fn take(self) -> Vec<u8> {
        self.bytes
    }

    fn bytes(&self) -> &[u8] {
        &self.bytes
    }

    pub fn new() -> Self {
        Self { bytes: vec![] }
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
                return;
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
                return;
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

    pub(crate) fn to_nbt(&self) -> NbtCompound {
        todo!()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn varlong(i: i64) -> Vec<u8> {
        let mut a = VarintArray::new();
        a.push_long(i);
        a.take()
    }
    fn varint(i: i32) -> Vec<u8> {
        let mut a = VarintArray::new();
        a.push_int(i);
        a.take()
    }

    #[test]
    fn test_varint() {
        assert_eq!(varint(0), vec![0x00]);

        assert_eq!(varint(0), vec![0x00,]);
        assert_eq!(varint(1), vec![0x01,]);
        assert_eq!(varint(2), vec![0x02,]);
        assert_eq!(varint(127), vec![0x7f,]);
        assert_eq!(varint(128), vec![0x80, 0x01]);
        assert_eq!(varint(255), vec![0xff, 0x01]);
        assert_eq!(varint(25565), vec![0xdd, 0xc7, 0x01]);
        assert_eq!(varint(2097151), vec![0xff, 0xff, 0x7f]);
        assert_eq!(varint(2147483647), vec![0xff, 0xff, 0xff, 0xff, 0x07]);
        assert_eq!(varint(-1), vec![0xff, 0xff, 0xff, 0xff, 0x0f]);
        assert_eq!(varint(-2147483648), vec![0x80, 0x80, 0x80, 0x80, 0x08]);
    }
}
