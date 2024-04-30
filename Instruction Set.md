### Instruction Set

Operand Types:
	- \[name]:r32 -> general-purpose register
	-  \*\[name]:r32 -> general-purpose register to be treated as pointer 
	- \[name]:s32 -> scratch register
	- \[name]:imm*N* -> *N*-bit immediate

| Mnemonic               | Long Name                         | Binary          | Octal      | Behaviour                                                                                                 |
| ---------------------- | --------------------------------- | --------------- | ---------- | --------------------------------------------------------------------------------------------------------- |
| mov a:r32, b:r32       | move                              | `000000 aaabbb` | 0000-0077  | a <- b                                                                                                    |
| add a:r32, b:r32       | add                               | `000001 aaabbb` | 0100-0177  | a <- a + b                                                                                                |
| sub a:r32, b:r32       | subtract                          | `000010 aaabbb` | 0200-0277  | a <- a - b                                                                                                |
| mul a:r32, b:r32       | multiply                          | `000011 aaabbb` | 0300-0377  | a <- a \* b                                                                                               |
| div a:r32, b:r32       | divide                            | `000100 aaabbb` | 0400-0477  | a <- a / b                                                                                                |
| mod a:r32, b:r32       | modulo                            | `000101 aaabbb` | 0500-0577  | a <- a % b                                                                                                |
| min a:r32, b:r32       | minimum                           | `000110 aaabbb` | 0600-0677  | a <- min(a, b)                                                                                            |
| max a:r32, b:r32       | maximum                           | `000111 aaabbb` | 0700-0777  | a <- min(a, b)                                                                                            |
| ord a:r32, b:r32       | order                             | `001000 aaabbb` | 1000-1077  | a, b <- min(a, b), max(a, b)                                                                              |
| mov a:r32, b:s32       | load from scratch                 | `001001 aaabbb` | 1200-1277  | a <- b                                                                                                    |
| mov a:s32, b:r32       | store into scratch                | `001010 aaabbb` | 1300-1377  | a <- b                                                                                                    |
| cmp a:r32, b:r32       | comparison                        | `001011 aaabbb` | 1100-1177  | LT <- a < b<br>LE <- a <= b<br>EQ <- a == b<br>GE <- a > b<br>GE <- a >= b<br>GT <- a > b<br>NE <- a != b |
| mov a:r32, \*b:r32     | memory load                       | `001100 aaabbb` |            | a <- \*b                                                                                                  |
| mov \*a:r32, b:r32     | memory store                      | `001101 aaabbb` |            | \*a <- b                                                                                                  |
| ldc a:r32              | load constant<br>register         | `001110 000aaa` | 1200-1207  | a <- cr                                                                                                   |
| inc a:r32              | increment                         | `001110 001aaa` |            | a <- a + 1                                                                                                |
| dec a:r32              | decrement                         | `001110 010aaa` |            | a <- a - 1                                                                                                |
| neg a:r32              | negation                          | `001110 011aaa` |            | a <- -a                                                                                                   |
| clr a:r32              | clear                             | `001110 100aaa` |            | a <- 0                                                                                                    |
| asr12 a:r32            | arithmetic shift right<br>12 bits | `001110 101aaa` |            | a <- a >>> 12                                                                                             |
| asl12 a:r32            | arithmetic shift left<br>12 bits  | `001110 110aaa` |            | a <- a <<< 12                                                                                             |
|                        |                                   | `001110 111aaa` |            |                                                                                                           |
| RESERVED               |                                   | `001111 000aaa` |            |                                                                                                           |
| RESERVED               |                                   | `001111 001aaa` |            |                                                                                                           |
| RESERVED               |                                   | `001111 010aaa` |            |                                                                                                           |
| RESERVED               |                                   | `001111 011aaa` |            |                                                                                                           |
| RESERVED               |                                   | `001111 100aaa` |            |                                                                                                           |
| RESERVED               |                                   | `001111 101aaa` |            |                                                                                                           |
| RESERVED               |                                   | `001111 110aaa` |            |                                                                                                           |
| RESERVED               |                                   | `001111 111aaa` |            |                                                                                                           |
| const imm:8            | load constant                     | `1000ii iiiiii` | 4000-4377  | cr <- imm                                                                                                 |
| sconst imm:8           | load signed constant              | `1001ii iiiiii` | 4400-4777  | cr <- sign_extend(imm, 8, 32)                                                                             |
| econst imm:8           | extend constant                   | `1010ii iiiiii` | 5000-5377  | cr <- (cr \* 0o400) \| imm                                                                                |
| RESERVED               | TBD                               | `1011ii iiiiii` | 5400-5777  | TBD                                                                                                       |
| constant               | smart constant                    | (multiple)      | (multiple) | creates a 32-bit constant<br>with multiple instructions                                                   |
| ext card:imm4 imm:imm6 | run expansion card                | `11cccc iiiiii` | 6000-7777  | runs the *card*th expansion<br>card with immediate<br>argument *imm*                                      |
