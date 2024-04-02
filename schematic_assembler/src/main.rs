use std::collections::HashMap;
use std::io::{BufRead, BufReader, Read};
use std::io;
use std::fs::File;
use std::num::ParseIntError;
use quartz_nbt::{NbtCompound, snbt};
use quartz_nbt::snbt::SnbtError;
use crate::LineParseError::{EarlyEnd, IntParseError, NbtParseError};

#[derive(Debug)]
struct BlockRegistry {
    names: Vec<String>,
    map: HashMap<String, usize>,
}

impl BlockRegistry {
    pub fn new() -> Self {
        Self {
            names: vec![],
            map: Default::default(),
        }
    }

    pub fn get_id(&mut self, name: &str) -> usize {
        match self.map.get(name) {
            None => {
                let new_id = self.names.len();
                self.map.insert(name.to_string(), new_id);
                self.names.push(name.to_string());
                new_id
            }
            Some(x) => *x
        }
    }
}

#[derive(Debug)]
struct Line {
    position: (u16, u16, u16),
    block_id: u32,
    nbt: Option<NbtCompound>
}

#[derive(Debug)]
enum LineParseError {
    EarlyEnd,
    NbtParseError(SnbtError),
    IntParseError(ParseIntError)
}

impl From<SnbtError> for LineParseError {
    fn from(value: SnbtError) -> Self {
        NbtParseError(value)
    }
}

impl Line {
    fn parse(s: &str, registry: &mut BlockRegistry) -> Result<Line, LineParseError> {
        let mut split = s.splitn(5, ' ');

        let mut read = || split.next().ok_or(EarlyEnd);

        let position = (
            read()?.parse().map_err(IntParseError)?,
            read()?.parse().map_err(IntParseError)?,
            read()?.parse().map_err(IntParseError)?
        );

        let block = read()?;
        let block_id = registry.get_id(block) as u32;
        let block_state = read();

        let nbt = if let Ok(nbt) = read().map(snbt::parse) {
            Some(nbt?)
        } else {
            None
        };

        Ok(Line {
            position,
            block_id,
            nbt
        })
    }
}

fn read_headers<I: Iterator<Item=String>>(lines: &mut I) -> HashMap<String, String> {
    let mut m = HashMap::new();

    while let Some(line) = lines.next() {
        if line.len() == 0 {
            break;
        } else {

        }
    }

    m
}

fn main() -> io::Result<()> {
    let args: Vec<String> = std::env::args().collect();

    let filename: String;

    match args.get(1) {
        Some(name) => {
            filename = name.clone();
        },
        _ => panic!("please specify a filename!")
    }

    let file = File::open(filename)?;

    let mut registry = BlockRegistry::new();
    let mut lines = vec![];
    for l in BufReader::new(file).lines() {
        let line = l?;
        let parsed = Line::parse(&line, &mut registry);
        lines.push(parsed);
    }

    dbg!(lines);

    Ok(())
}
