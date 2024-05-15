## Screen

interface:
```c
// clears the screen
void clear_screen();
// shifts all content on the screen up by a line
void shift_line();
// writes a character at the given position
void write_char(char c, unsigned short row, unsigned short col);
```

## Terminal Emulator

interface:
```c
#define COLUMNS 80
#define LINES 40

// writes a character to the screen
void putchar(char c);
// checks if there is a character to read from the buffer
bool haschar();
// gets a character from the buffer
char getchar();
```

implementation:

```c
int col;
int row;

void carriage_return() {
	col = 0;
}

void line_feed() {
	if (row + 1 == LINES) {
		shift_line();
	} else {
		row++;
	}
}

void putchar(char c) {
	if (c == '\n') {
		carriage_return();
		line_feed();
		return;
	}
	
	if (c == '\r') {
		carriage_return();
		return;
	}
	
	if (col == COLUMNS - 1) {
		carriage_return();
		line_feed();
	}
	
	if (c == '\t') {
		diff = row % 8;

		if (diff == 0) {
			diff = 8;
		}
		
		do {
			write_char(' ', row, col);
			row++;
		} while (--diff);
		return;
	}

	write_char(c, row, col);
	row++;
}
```