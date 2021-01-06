# Main file, initializes the I/O files and drives the process

import sys
import Parser as p
import Code as c
import SymbolTable as t

# make sure one and only one file is provided

if len(sys.argv) != 2:
    print("Usage: python3 HackAssembler.py file.asm")
    exit()

fname = sys.argv[1]

if fname[-4:] != ".asm":
    print("Only *asm files accepted")
    exit()
    
out = open(fname[:-4] + '.hack', 'w')

table = t.Table()
parser = p.Parser(fname)

# first pass, add loop instructions to table
for instr in parser.instructions:
    cType = parser.commandType(instr)
    if cType == 'L_COMMAND':
        table.addEntry(instr[1:-1], address=parser.curInstr, loop=True)
   
# second pass, add symbols to table, and translate
for instr in parser.instructions:
    cType = parser.commandType(instr)
    if cType == 'A_COMMAND':
        symbol = parser.symbol(instr, cType)
        if not symbol.isnumeric():
            if  not table.contains(symbol):
                table.addEntry(symbol)
                instr = "@" + table.getAddress(symbol)
            else:
                instr = "@" + table.getAddress(symbol)
        mCode = c.convertA(instr)
        out.write(mCode + '\n')
    if cType == 'C_COMMAND':
        mDest = c.convertDest(parser.dest(instr))
        mComp = c.convertComp(parser.comp(instr))
        mJump = c.convertJump(parser.jump(instr))

        mCode = '111' + mComp + mDest + mJump
        out.write(mCode + '\n')

out.close()