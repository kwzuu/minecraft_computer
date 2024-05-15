### Name
assembler - Convert assembly language into machine code
### Synopsis
assembler <u>FILE</u>
### Description
This is an assembler for the block architecture. Assembly language is read from the input file and machine code is put into the standard output. Instructions in the output are separated by newlines and represented as 12-bit octal integers, e.g. `7024` for the number 3064.

### Assembly Format
Lines of assembly follow this grammar:

```bnf
<line>        ::= <instruction> | <labeldecl> | <comment> | <directive> | <blank>


<instruction> ::= <mnemonic> <arguments>

<mnemonic>    ::= <ident>

<arguments>   ::= "" | <whitespace> <argument> <arguments>
<argument>    ::= <signedint> | <labelref> | <register> | <pointer>

<signedint>   ::= <negative> | <integer>
<negative>    ::= "-" <integer>
<integer>     ::= <decimal> | <hex> | <octal> | <binary> 
<decimal>     ::= /[0-9]+/
<hex>         ::= "0x" /[0-9a-f]+/
<octal>       ::= "0o" /[0-7]+/
<binary>      ::= "0b" /[01]+/

<labelref>    ::= <ident>

<register>    ::= <gpreg> | <scratchreg>
<gpreg>       ::= "%a0" | "%a1" | "%a2" | "%t0" | "%t1" | "%s0" | "%s1" | "%s2"
<scratchreg>  ::= "%x0" | "%x1" | "%x2" | "%x3" | "%y0" | "%y1" | "%y2" | "%y3"

<pointer>     ::= "*" <gpreg>


<labeldecl>   ::= <ident> ":"


<comment>     ::= "#" /.*/


<directive>   ::= "." <ident> <arguments>


<ident>       ::= /[a-z][a-z0-9]*/
<whitespace>  ::= /[ \r\n\t]+/
```

### Instruction Set
Instruction listings can be found in [this spreadsheet](https://github.com/kwzuu/minecraft_computer/blob/main/Instruction%20Set.ods)