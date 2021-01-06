// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

@SCREEN // Select the first screen memory
D=A
@curPoint   // make a pointer that points to the current screen location
M=D

// 4 states, empty, clearing, full, or filling, start with empty

(EMPTY)     // wait for input
@KBD
D=M
@FILL
D;JGT
@EMPTY
0;JMP

(FULL)      // wait until no input
@KBD
D=M
@CLEAR
D;JEQ
@FULL
0;JMP

(CLEAR)
@KBD        // check for input change
D=M
@FILL
D;JGT         
@curPoint   // color screen point white
D=M
A=M
M=0
@SCREEN     // if it's first screen point, jump to empty, else decrement
D=D-A
@EMPTY
D;JEQ
@curPoint   // go to next screen point and repeat
M=M-1
@CLEAR      
0;JMP


(FILL)
@KBD        // check for input change
D=M
@CLEAR
D;JEQ
@curPoint   // color screen point black
D=M
A=M
M=-1
@24575     // if it's last screen point, jump to full, else increment
D=D-A
@FULL
D;JEQ
@curPoint   // go to next screen point and repeat
M=M+1
@CLEAR      
0;JMP