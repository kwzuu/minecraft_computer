use quartz_nbt::{NbtTag};

/// An array of variable-length integers
/// conforms to https://wiki.vg/VarInt_And_VarLong
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct VarintArray {
    bytes: Vec<i8>,
}

impl VarintArray {
    /// take the buffer
    pub fn take(self) -> Vec<i8> {
        self.bytes
    }

    /// retrieve a reference to the buffer
    pub fn bytes(&self) -> &[i8] {
        &self.bytes
    }

    /// create a new array
    pub fn new() -> Self {
        Self { bytes: vec![] }
    }

    fn push_byte(&mut self, byte: u8) {
        self.bytes.push(i8::from_ne_bytes(byte.to_ne_bytes()))
    }
    pub(crate) fn push_u32(&mut self, mut value: u32) {
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

    /// push an integer to the array
    pub fn push_int(&mut self, value: i32) {
        self.push_u32(u32::from_ne_bytes(value.to_ne_bytes()));
    }

    /// push a long to the array
    pub fn push_long(&mut self, value: i64) {
        self.push_u64(u64::from_ne_bytes(value.to_ne_bytes()));
    }

    pub fn into_nbt(self) -> NbtTag {
        NbtTag::ByteArray(self.bytes)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn varlong(i: i64) -> Vec<i8> {
        let mut a = VarintArray::new();
        a.push_long(i);
        a.take()
    }
    fn varint(i: i32) -> Vec<i8> {
        let mut a = VarintArray::new();
        a.push_int(i);
        a.take()
    }

    #[test]
    fn test_varint() {
        assert_eq!(varint(0), vec![0x00,]);
        assert_eq!(varint(1), vec![0x01,]);
        assert_eq!(varint(2), vec![0x02,]);
        assert_eq!(varint(127), vec![0x7f,]);
        assert_eq!(varint(128), vec![-0x80, 0x01]);
        assert_eq!(varint(255), vec![-0x01, 0x01]);
        assert_eq!(varint(25565), vec![-35, -57, 0x01]);
        assert_eq!(varint(2097151), vec![-0x01, -0x01, 0x7f]);
        assert_eq!(varint(2147483647), vec![-0x01, -0x01, -0x01, -0x01, 0x07]);
        assert_eq!(varint(-1), vec![-0x01, -0x01, -0x01, -0x01, 0x0f]);
        assert_eq!(varint(-2147483648), vec![-0x80, -0x80, -0x80, -0x80, 0x08]);
    }

    #[test]
    fn test_varlong() {
        assert_eq!(varlong(0), vec![0x00]);
        assert_eq!(varlong(1), vec![0x01]);
        assert_eq!(varlong(2), vec![0x02]);
        assert_eq!(varlong(127), vec![0x7f]);
        assert_eq!(varlong(128), vec![-0x80, 0x01]);
        assert_eq!(varlong(255), vec![-0x01, 0x01]);
        assert_eq!(varlong(2147483647), vec![-0x01, -0x01, -0x01, -0x01, 0x07]);
        assert_eq!(varlong(9223372036854775807), vec![-0x01, -0x01, -0x01, -0x01, -0x01, -0x01, -0x01, -0x01, 0x7f,]);
        assert_eq!(varlong(-1), vec![-0x01, -0x01, -0x01, -0x01, -0x01, -0x01, -0x01, -0x01, -0x01, 0x01]);
        assert_eq!(varlong(-2147483648), vec![-0x80, -0x80, -0x80, -0x80, -0x08, -0x01, -0x01, -0x01, -0x01, 0x01]);
        assert_eq!(varlong(-9223372036854775808), vec![-0x80, -0x80, -0x80, -0x80, -0x80, -0x80, -0x80, -0x80, -0x80, 0x01]);
    }

    #[test]
    fn test_bytes() {
        let mut v = VarintArray::new();
        assert_eq!(v.bytes(), &[]);
        v.push_int(128);
        assert_eq!(v.bytes(), &[-0x80, 0x01]);
        v.push_int(2);
        assert_eq!(v.bytes(), &[-0x80, 0x01, 0x02]);
    }
}
