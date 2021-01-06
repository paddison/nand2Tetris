// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

@0 // set R2 to zero
D=A
@R2
M=D

@R0 // load first number into data
D=M
@R1 // load 2nd num into data and compare to first (R0 - R1)
D=D-M
@JLT // if result is negative, R1 > R0, use R0 as multiplicant
D;JLT
@ELSE
0;JMP

(JLT) // R0 is multiplicant, R1 is num
@R0
D=M
@multiplicant
M=D
@R1
D=M
@num
M=D
@LOOP // jump to loop to execute the multiplication loop
0;JMP

(ELSE) // R1 is multiplicant, R0 is num
@R1
D=M
@multiplicant
M=D
@R0
D=M
@num
M=D // no jum necessary

(LOOP) // the multiplication loop,
@num
D=M
@R2
M=D+M
@multiplicant
M=M-1 // decrement multiplicant by 1
D=M
@END
D;JEQ // if multiplicant == 0 multiplication is finished
@LOOP
0;JMP

(END)
@END
0;JMP



