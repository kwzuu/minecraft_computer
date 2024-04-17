### Word Size
- 12 bit data, instruction, and address word size
- 32 bit 
- Addresses will be physical for ease of implementation

### Memory layout
- Memory will be:
	- Linearly addressed by a 12-bit value that uniquely identifies a single word
	- Stored in a 16x16x16 cube of barrels for a total of 4096 words of memory

### Arithmetic and Registers
- Arithmetic will be done with signed 32 bit integers, as is supported by the Minecraft scoreboard
- There will be 2 total 12-bit pointer registers, with special behaviour
	- stack pointer
	- instruction pointer
	- base pointer
- There will be 8 total 32-bit general purpose registers, along with a special register for constant-building instructions

| name | calling convention            | id  |
| ---- | ----------------------------- | --- |
| a0   | argument register, clobbered  | 0   |
| a1   | argument register, clobbered  | 1   |
| a2   | argument register, clobbered  | 2   |
| t0   | temporary register, clobbered | 3   |
| t1   | temporary register, clobbered | 4   |
| s0   | saved register, preserved     | 5   |
| s1   | saved register, preserved     | 6   |
| s2   | saved register, preserved     | 7   |

- There will be 8 additional scratch registers, which have limited use

| name | calling convention          | id  |
| ---- | --------------------------- | --- |
| x0   | scratch register, clobbered | 0   |
| x1   | scratch register, clobbered | 1   |
| x2   | scratch register, clobbered | 2   |
| x3   | scratch register, clobbered | 3   |
| y0   | scratch register, preserved | 4   |
| y1   | scratch register, preserved | 5   |
| y2   | scratch register, preserved | 6   |
| y3   | scratch register, preserved | 7   |

- There will be 8 flag bits, which have limited use. all are clobbered.

| binary name | binary description    | unary description | id  |
| ----------- | --------------------- | ----------------- | --- |
| LT          | less than             | negative flag     | 0   |
| LE          | less than or equal    | not positive      | 1   |
| EQ          | equal                 | equal to zero     | 2   |
| GE          | greater than or equal | not negative      | 3   |
| GT          | greater than          | positive flag     | 4   |
| NE          | not equal             | not zero          | 5   |
|             |                       |                   |     |
|             |                       |                   |     |


- Supported arithmetic instructions will be:
	- The ones included in the scoreboard command (=, +=, -=, \*=, /=, %=, ><, <, >)
	- Extras for shifting values to store in memory (>>>=12, <<<=12)
	- Memory address calculation (a + b * (1|2|4|8)) ?

### Instruction formats
- 2 bit prefix, 2 bit kind, 8 bit immediate
	- `10kkii iiiiii`, b?
	- used for constant building
	- kinds:
		- set
		- set and sign-extend
		- arithmetic-shift-and-add
		- (arithmetic-shift-and-?)(sign-extend then add?)
- 2 bit prefix, 4 bit card, 6 bit immediate
	- `11cccc iiiiii`
	- used for running opcodes from expansion cards -- one card is selected from 16 slots, and it is given 6 bits of space for its own arguments
- 2 bit prefix
	- `00xxxx xxxxxx`
	- used for arithmetic
	- (1 bit prefix, 3 bit opcode OR 2 bit prefix, 2 bit opcode), 3 bit register id, 3 bit register id
		- `000ooo aaabbb
		- `0010oo aaabbb
		- used for binary arithmetic instructions
- 4 bit prefix (clashing with previous), 5 bit opcode, 3 bit immediate
	- `0111oo oooiii`
	- used for unary arithmetic instructions
- 4 bit opcode, 6 bit immediate 
	- `00oooo iiiiii`
	- used for jumps and some immediate math

basic parse tree:
- 0
	- 0: arithmetic
	- 1: jump / arithmetic with immediates
- 1
	- 0: constant building instruction
	- 1: expansion card
