# unpacks each instruction into its underlying fields

import Code

class Parser:

    # initialize with file and store instructions in list
    def __init__(self, file):

        self.instructions = [] 
        self.curInstr = 0

        with open(file, 'r') as f:
            for line in f:
                if (line[0:2] == "//") or (line[0].isspace()):
                    continue
                if (line.find('//') != -1):
                    line = line[:line.find('//')]
                self.instructions.append(line.rstrip())

    # find out if current instruction is a or c or loop instruction            
    def commandType(self, instr):
        if (instr[0] == '@'):
            self.curInstr += 1
            return 'A_COMMAND'
        elif (instr[0] == '(' and instr[-1] == ')'):
            return 'L_COMMAND'
        else:
            self.curInstr += 1
            return 'C_COMMAND'

    def symbol(self, instr, cType):
        if cType == 'L_COMMAND':
            return instr[1:-1]
        elif cType == 'A_COMMAND':
            return instr[1:]

    def dest(self, instr):
        iDest = instr.find('=')
        if iDest != -1:
            return instr[:iDest]
        else:
            return ''
    
    def jump(self, instr):
        iJump = instr.find(';')
        if iJump != -1:
            return instr[iJump + 1:]
        else:
            return ''
    
    def comp(self, instr):
        iDest = instr.find('=')
        iJump = instr.find(';')
        if iJump == -1:
            return instr[iDest + 1:]
        else:
            return instr[iDest + 1:iJump]

    def instruction(self, instr):
        if (instr[0] == '@'):
            mCode = Code.convertA(instr)
        else:
            # if c split into comp, dest and jump instructions
            iDest = instr.find("=")

            if (iDest == -1):
                dest = ''
            else:
                dest = instr[:iDest]

            iJump = instr.find(";")

            if (iJump == -1):
                jump = ''
                comp = instr[iDest + 1:]
            else:
                jump = instr[iJump + 1:]
                comp = instr[iDest + 1:iJump]

            mComp = Code.convertComp(comp)
            mDest = Code.convertDest(dest)
            mJump = Code.convertJump(jump)

            mCode = '111' + mComp + mDest + mJump

        return mCode