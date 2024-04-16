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
- There will be 8 total 32-bit registers
- Supported arithmetic instructions will be:
	- The ones included in the scoreboard command (=, +=, -=, \*=, /=, %=, ><, <, >)
	- Extras for shifting values to store in memory (>>>=12, <<<=12)
	- Memory address calculation (a + b * (1|2|4|8))

### Instruction formats
- 2 bit prefix, 2 bit kind, 8 bit immediate
	- `10kkii iiiiii`
	- used for constant building
	- kinds:
		- set
		- set and sign-extend
		- shift-and-add
		- shift-and-(sign-extend then add) (?)
- 2 bit prefix, 4 bit card, 6 bit immediate
	- `11cccc iiiiii`
	- used for running opcodes from expansion cards -- one card is selected from 16 slots, and it is given 6 bits of space for its own arguments
- 6 bit opcode, 3 bit immediate, 3 bit immediate
	- used for binary arithmetic instructions
- 9 bit opcode, 3 bit immediate
	- used for unary arithmetic instructions
