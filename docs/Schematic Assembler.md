### Name
schematic_assembler -- convert a textual representation of minecraft schematics to the [Sponge Format Version 3](https://github.com/SpongePowered/Schematic-Specification/blob/master/versions/schematic-3.md)

### Synopsis
schematic_assembler <u>SOURCE_FILE</u> <u>DESTINATION_FILE</u>

### Assembly Format
```
<line>        ::= <coordinates> " " <blockid> <snbt_part>

<coordinates> ::= <number> " " <number> " " <number>

<number>      ::= /[0-9]+/
<blockid>     ::= /[a-zA-Z:_\[\]=]+/

<snbt_part>   ::= " " <snbt> | ""
<snbt>        ::= /.+/
```

Example:
```
0 0 0 minecraft:stone
0 1 0 minecraft:redstone_torch
1 0 0 minecraft:barrel {Items: [{Slot: 0b, Count: 24, Id: "minecraft:stone"}]}
```