use std::io::{BufRead, BufReader, BufWriter};
use std::io;
use std::fs::File;
use std::num::ParseIntError;
use quartz_nbt::{NbtCompound, snbt};
use quartz_nbt::io::{Flavor, write_nbt};
use quartz_nbt::snbt::SnbtError;
use schematic_writer::blocks::{BlockEntity, BlocksBuilder};
use schematic_writer::{Metadata, Schematic, SchematicBuilder};
use crate::LineParseError::{EarlyEnd, IntParseError, NbtParseError};

/// Represents a line of schematic assembly
#[derive(Debug)]
struct Line {
    position: (u16, u16, u16),
    block_id: String,
    nbt: Option<NbtCompound>
}

/// An error in parsing a line
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
    /// parses a string into a line
    fn parse(s: &str) -> Result<Line, LineParseError> {
        let mut split = s.splitn(5, ' ');

        let mut read = || split.next().ok_or(EarlyEnd);

        let position = (
            read()?.parse().map_err(IntParseError)?,
            read()?.parse().map_err(IntParseError)?,
            read()?.parse().map_err(IntParseError)?
        );

        let block_id = read()?;

        let nbt = if let Ok(nbt) = read().map(snbt::parse) {
            Some(nbt?)
        } else {
            None
        };

        Ok(Line {
            position,
            block_id: block_id.to_string(),
            nbt
        })
    }
}

/// reads the headers present at the start of a file
// fn read_headers<I: Iterator<Item=String>>(lines: &mut I) -> HashMap<String, String> {
//     let mut m = HashMap::new();
//
//     while let Some(line) = lines.next() {
//         if line.len() == 0 {
//             break;
//         } else {
//             let index = line.find("=")
//                 .expect("error in reading headers: no `=' present");
//             m.insert(line[..index].to_string(), line[index+1..].to_string());
//         }
//     }
//
//     m
// }

/// creates a schematic from a file
fn make_schematic(lines: Vec<Line>) -> Schematic {
    let mut builder = BlocksBuilder::new();
    for line in lines {
        let coords = line.position.into();
        builder.add_block(coords, &line.block_id);
        if let Some(nbt) = line.nbt {
            builder.add_block_entity(BlockEntity::new(coords, line.block_id, Some(nbt)))
        }
    }
    let blocks = builder.build();

    let metadata = Metadata {
        name: "Schematic".to_string(),
        author: "schematic_assembler".to_string(),
        required_mods: Box::new([]),
    };

    SchematicBuilder::default()
        .blocks(blocks)
        .metadata(metadata)
        .build()
        .unwrap()
}

fn main() -> io::Result<()> {
    let args: Vec<String> = std::env::args().collect();

    let in_filename: String;
    let out_filename: String;

    match &args[1..] {
        [in_name, out_name] => {
            in_filename = in_name.clone();
            out_filename = out_name.clone();
        },
        _ => panic!("usage: schematic_writer <INFILE> <OUTFILE>")
    }

    let file = File::open(in_filename)?;

    let mut lines = vec![];
    for l in BufReader::new(file).lines() {
        let line = l?;
        let parsed = Line::parse(&line);
        lines.push(parsed.unwrap());
    }

    let schematic = make_schematic(lines);
    let nbt = schematic.into_nbt();
    let output= File::create(out_filename)?;

    write_nbt(
        &mut BufWriter::new(output),
        Some(""),
        &nbt,
        Flavor::GzCompressed
    ).unwrap();

    Ok(())
}
