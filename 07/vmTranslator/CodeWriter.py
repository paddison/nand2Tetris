class CodeWrite:

    def __init__(self, file):
        self.f = open(file + '.asm', 'w')
        self.eqCount = 0
        self.gtCount = 0
        self.ltCount = 0
        if file.rfind('/') != -1:
            self.fname = file[file.rfind('/') + 1:]
        else:
            self.fname = file

    def close(self):
        self.f.close()

    def writeArithmetic(self, command):

        if command == 'add':
            self.f.write('// add\n')
            for line in self.A_add():
                self.f.write(line + '\n')

        elif command == 'sub':
            self.f.write('// sub\n')
            for line in self.A_sub():
                self.f.write(line + '\n')

        elif command == 'neg':
            self.f.write('// neg\n')
            for line in self.A_neg():
                self.f.write(line + '\n')

        elif command == 'eq':
            self.f.write('// eq\n')
            for line in self.A_eq():
                self.f.write(line + '\n')

        elif command == 'gt':
            self.f.write('// gt\n')
            for line in self.A_gt():    
                self.f.write(line + '\n')

        elif command == 'lt':
            self.f.write('// lt\n')
            for line in self.A_lt():
                self.f.write(line + '\n')

        elif command == 'and':
            self.f.write('// and\n')
            for line in self.A_and():
                self.f.write(line + '\n')

        elif command == 'or':
            self.f.write('// or\n')
            for line in self.A_or():
                self.f.write(line + '\n')

        elif command == 'not':
            self.f.write('// not\n')
            for line in self.A_not():
                self.f.write(line + '\n')

        # increment pointer at end
        for line in self.incrementPointer():
            self.f.write(line + '\n')
    
    def A_add(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.append("M=M+D")
        return assemblyCode

    def A_sub(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.append("M=M-D")
        return assemblyCode

    def A_neg(self):
        assemblyCode = self.prepareUnaryArithemtic()
        assemblyCode.append("M=-M")
        return assemblyCode

    def A_and(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.append("M=D&M")
        return assemblyCode

    def A_or(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.append("M=D|M")
        return assemblyCode

    def A_not(self):
        assemblyCode = self.prepareUnaryArithemtic()
        assemblyCode.append("M=!M")
        return assemblyCode

    def A_eq(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.extend(self.booleanJump('JEQ'))
        self.eqCount += 1

        return assemblyCode

    def A_gt(self):
        assemblyCode = self.prepareBinaryArithmetic()       
        assemblyCode.extend(self.booleanJump('JGT'))
        self.gtCount += 1

        return assemblyCode

    def A_lt(self):
        assemblyCode = self.prepareBinaryArithmetic()     
        assemblyCode.extend(self.booleanJump('JLT'))
        self.ltCount += 1

        return assemblyCode

    def booleanJump(self, jump):
        # value to check
        assemblyCode = ['D=M-D']    

        # what kind of comparison, adjust labels
        if jump == 'JEQ':
            label = 'EQ' + str(self.eqCount)  
        elif jump == 'JGT':
            label = 'GT' + str(self.gtCount)
        elif jump == 'JLT':
            label = 'LT' + str(self.ltCount)

        assemblyCode.append('@' + label)
        # if true jump
        assemblyCode.append('D;' + jump)

        # false and go to end
        assemblyCode.append('D=0')
        assemblyCode.append('@END' + label)
        assemblyCode.append('0;JMP')
        
        # true
        assemblyCode.append('(' + label + ')')
        assemblyCode.append('D=-1')
        assemblyCode.append('(END' + label + ')')

        # load into memory
        assemblyCode.append('@SP')
        assemblyCode.append('A=M')
        assemblyCode.append('M=D')


        return assemblyCode

    def prepareUnaryArithemtic(self):
        return self.decrementPointer()

    def prepareBinaryArithmetic(self):
        assemblyCode = self.decrementPointer()
        assemblyCode.append("D=M")
        assemblyCode.extend(self.decrementPointer())
        return assemblyCode

    def decrementPointer(self):
        assemblyCode = []
        assemblyCode.append("@SP")
        assemblyCode.append("AM=M-1")
        return assemblyCode

    def incrementPointer(self):
        assemblyCode = []
        assemblyCode.append('@SP')
        assemblyCode.append('M=M+1')
        return assemblyCode

    def writePushPop(self, command, segment, index):
        if command == "C_PUSH":
            self.f.write('// push ' + segment + ' ' + index + '\n')
            for line in self.writePush(segment, index):
                self.f.write(line + '\n')
        elif command == "C_POP":
            self.f.write('// pop ' + segment + ' ' + index + '\n')
            for line in self.writePop(segment, index):
                self.f.write(line + '\n')
        
    # get Value for pop and set pointer
    def getPopValue(self):
        assemblyCode = self.decrementPointer()
        assemblyCode.append("D=M")
        return assemblyCode

    def writePush(self, segment, index):
        assemblyCode = []
        if segment == 'constant':
            assemblyCode.append(self.getSymbol(segment, index))
            assemblyCode.append('D=A')
        else:
            if (segment == 'local') or (segment == 'argument') or (segment == 'this') or (segment == 'that'):
                assemblyCode.append('@'+ str(index))
                assemblyCode.append('D=A')
                assemblyCode.append(self.getSymbol(segment, index))
                assemblyCode.append('A=M+D')                    
            elif (segment == 'static') or (segment == 'temp') or (segment == 'pointer'):
                assemblyCode.append(self.getSymbol(segment, index))
            assemblyCode.append('D=M')
        
        assemblyCode.append('@SP')
        assemblyCode.append('A=M')
        assemblyCode.append('M=D')
        assemblyCode.extend(self.incrementPointer())

        return assemblyCode

    def writePop(self, segment, index):
        assemblyCode = []
        if (segment == 'local') or (segment == 'this') or (segment == 'that') or (segment == 'argument'):
            assemblyCode.append('@' + str(index))
            assemblyCode.append('D=A')
            assemblyCode.append(self.getSymbol(segment, index))
            assemblyCode.append('D=D+M')
            assemblyCode.append('@R13') # use general purpose register to store address
            assemblyCode.append('M=D')
            assemblyCode.extend(self.getPopValue())
            assemblyCode.append('@R13') # get address from general purpose register
            assemblyCode.append('A=M')

        else:
            assemblyCode.extend(self.getPopValue())
            assemblyCode.append(self.getSymbol(segment, index))

        assemblyCode.append('M=D')

        return assemblyCode

    # returns string for symbol
    def getSymbol(self, segment, index):

        if segment == 'constant':
            return '@' + index
        elif segment == 'local':
            return '@LCL'
        elif segment == 'static':
            return '@' + self.fname + index
        elif segment == 'argument':
            return '@ARG'
        elif segment == 'this':
            return '@THIS'
        elif segment == 'that':
            return '@THAT'
        elif segment == 'pointer':
            return '@' + str(int(index) + 3)
        elif segment == 'temp':
            return '@' + str(int(index) + 5)