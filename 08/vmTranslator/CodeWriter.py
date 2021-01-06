class CodeWrite:

    def __init__(self, file):
        self.f = open(file + '.asm', 'w')
        self.returnAdress = {}
        self.p = PointerHandler()
        self.a = ArithmeticHandler()
        self.pp = PushPopHandler()
        self.fs = FunctionStateHandler()
        if file.rfind('/') != -1:
            self.fname = file[file.rfind('/') + 1:]
        else:
            self.fname = file

    def close(self):
        self.f.close()

    # set the name of current function
    def setCurrentFunctionName(self, functionName):
        self.currentFunction = functionName
        self.pp.currentFunction = functionName
        self.f.write('//current function: ' + functionName + '\n')

    # initialize SP to 256 and call Sys.init 
    def writeInit(self):
        self.f.write('//initializing SP=256\n'
                    '@256\n'
                    'D=A\n'
                    '@SP\n'
                    'M=D\n')

        self.writeCall('Sys.init', '0')        

    def writeArithmetic(self, command):

        if command == 'add':
            self.f.write('// add\n')
            for line in self.a.add():
                self.f.write(line + '\n')

        elif command == 'sub':
            self.f.write('// sub\n')
            for line in self.a.sub():
                self.f.write(line + '\n')

        elif command == 'neg':
            self.f.write('// neg\n')
            for line in self.a.neg():
                self.f.write(line + '\n')

        elif command == 'eq':
            self.f.write('// eq\n')
            for line in self.a.eq():
                self.f.write(line + '\n')

        elif command == 'gt':
            self.f.write('// gt\n')
            for line in self.a.gt():    
                self.f.write(line + '\n')

        elif command == 'lt':
            self.f.write('// lt\n')
            for line in self.a.lt():
                self.f.write(line + '\n')

        elif command == 'and':
            self.f.write('// and\n')
            for line in self.a.and_a():
                self.f.write(line + '\n')

        elif command == 'or':
            self.f.write('// or\n')
            for line in self.a.or_a():
                self.f.write(line + '\n')

        elif command == 'not':
            self.f.write('// not\n')
            for line in self.a.not_a():
                self.f.write(line + '\n')

        # increment pointer at end
        for line in self.p.incrementPointer():
            self.f.write(line + '\n')

    def writePushPop(self, command, segment, index):
        if command == "C_PUSH":
            self.f.write('//push ' + segment + ' ' + index + '\n')
            for line in self.pp.writePush(segment, index):
                self.f.write(line + '\n')
        elif command == "C_POP":
            self.f.write('//pop ' + segment + ' ' + index + '\n')
            for line in self.pp.writePop(segment, index):
                self.f.write(line + '\n')

    # convention for labeling is functionName$label
    # writing a label is basically identical to writing it in Assembly
    def writeLabel(self, label):
        self.f.write('// label ' + label + '\n')
        self.f.write('(' + self.currentFunction + '$' + label + ')\n')

    # same as unconditional jump in assembly
    def writeGoto(self, label):
        self.f.write('// goto ' + label + '\n')
        self.f.write('@' + self.currentFunction + '$' + label + '\n')
        self.f.write('0;JMP' + '\n')

    # see if recently pushed value is 0 (false) if not, then goto label, same as D;JNE
    def writeIf(self, label):
        self.f.write('// if-goto ' + label + '\n')
        for line in self.pp.getPopValue():
            self.f.write(line + '\n')
        self.f.write('@' + self.currentFunction + '$' + label + '\n')
        self.f.write('D;JNE' + '\n')

    def writeCall(self, functionName, numArgs):
        returnAdress = self.generateReturnAdress(functionName, numArgs)
        # push returnAdress 
        self.f.write('//Call' + functionName + '\n'
                    '//push return-adress\n'
                    '@' + returnAdress + '\n'
                    'D=A\n'
                    '@SP\n'
                    'A=M\n'
                    'M=D\n')

        for line in self.p.incrementPointer():
            self.f.write(line + '\n')
        
        # push LCL
        self.f.write('//push LCL\n')
        for line in self.fs.saveSegment('LCL'):
            self.f.write(line + '\n')
        for line in self.p.incrementPointer():
            self.f.write(line + '\n')

        # push ARG
        self.f.write('//push ARG\n')
        for line in self.fs.saveSegment('ARG'):
            self.f.write(line + '\n')
        for line in self.p.incrementPointer():
            self.f.write(line + '\n')

        # push THIS
        self.f.write('//push THIS\n')
        for line in self.fs.saveSegment('THIS'):
            self.f.write(line + '\n')
        for line in self.p.incrementPointer():
            self.f.write(line + '\n')

        # push THAT
        self.f.write('//push THAT\n')
        for line in self.fs.saveSegment('THAT'):
            self.f.write(line + '\n')
        for line in self.p.incrementPointer():
            self.f.write(line + '\n')

        # set ARG
        self.f.write('//set ARG = SP - n - 5\n')
        self.f.write('@' + str((int(numArgs) + 5)) + '\n'
                    'D=A\n'
                    '@SP\n'
                    'D=M-D\n'
                    '@ARG\n'
                    'M=D\n')

        # set LCL to current SP
        self.f.write('//set LCL = SP\n')
        self.f.write('@SP\n'
                    'D=M\n'
                    '@LCL\n'
                    'M=D\n')

        # goto f
        self.f.write('@FUNCTION$' + functionName + '\n'
                    '0;JMP\n')

        #declare label for return adress
        self.f.write('(' + returnAdress + ')\n')
        
    def writeFunction(self, functionName, numLocals):
        self.f.write('//' + functionName + numLocals + ' initialization\n')
        self.f.write('(FUNCTION$' + functionName + ')\n')
        for _ in range(int(numLocals)):
            for line in self.pp.writePush('constant', '0'):
                self.f.write(line + '\n')

    def writeReturn(self):
        # save current LCL (FRAME)
        self.f.write('//Return\n'
                    '//Save LCL in R14 = FRAME\n'
                    '@LCL\n'
                    'D=M\n'
                    '@14\n'
                    'M=D\n')

        # save return adress(FRAME - 5)
        self.f.write('//Save Return adress (FRAME - 5) in R15\n'
                    '@5\n'
                    'D=A\n'
                    '@14\n'
                    'A=M-D\n'
                    'D=M\n'
                    '@15\n'
                    'M=D\n')
        
        # pop return value into arg0
        self.f.write('//pop return value in ARG0\n')
        for line in self.pp.getPopValue():
            self.f.write(line + '\n')
        self.f.write('@ARG\n'
                    'A=M\n'
                    'M=D\n')

        # restore SP (ARG + 1)
        self.f.write('//reposition pointer to ARG + 1\n'
                    '@ARG\n'
                    'D=M+1\n'
                    '@SP\n'
                    'M=D\n')

        # restore State of segemnts
        #THAT = *(FRAME - 1)
        self.f.write('//restore THAT = *(FRAME - 1)\n')
        for line in self.fs.restoreState('THAT', '1'): 
            self.f.write(line + '\n')
        # THIS = *(FRAME - 2)
        self.f.write('//restore THIS = *(FRAME - 2)\n')
        for line in self.fs.restoreState('THIS', '2'): 
            self.f.write(line + '\n')
        self.f.write('//restore ARG = *(FRAME - 3)\n')
        # ARG = *(FRAME - 3)
        for line in self.fs.restoreState('ARG', '3'): 
            self.f.write(line + '\n')
        # LCL = *(FRAME - 4)
        self.f.write('//restore LCL = *(FRAME - 4)\n')
        for line in self.fs.restoreState('LCL', '4'): 
            self.f.write(line + '\n')

        # goto return adress (stored in R15)
        self.f.write('//goto return adress (stored in R15)\n'
                    '@15\n'
                    'A=M\n'
                    '0;JMP\n')

    # generates a unique return adress for each new function RETURN$functionNamenumArgs_Count
    def generateReturnAdress(self, functionName, numArgs):
        if not (functionName + numArgs) in self.returnAdress:
            self.returnAdress[functionName + numArgs] = 0
        else :
            self.returnAdress[functionName + numArgs] += 1
        
        return 'RETURN$' + functionName + numArgs + '_' + str(self.returnAdress[functionName + numArgs])

class FunctionStateHandler:

    def saveSegment(self, segment):
        assemblyCode = ['@' + segment]
        assemblyCode.append('D=M')
        assemblyCode.append('@SP')
        assemblyCode.append('A=M')
        assemblyCode.append('M=D')
        return assemblyCode

    def restoreState(self, segment, framePos):
        assemblyCode = ['@14'] # @FRAME
        assemblyCode.append('D=M') 
        assemblyCode.append('@' + framePos)
        assemblyCode.append('A=D-A')
        assemblyCode.append('D=M')
        assemblyCode.append('@' + segment)
        assemblyCode.append('M=D')
        return assemblyCode 

class ArithmeticHandler:

    def __init__(self):
        self.eqCount = 0
        self.gtCount = 0
        self.ltCount = 0
        self.p = PointerHandler()

    def add(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.append("M=M+D")
        return assemblyCode

    def sub(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.append("M=M-D")
        return assemblyCode

    def neg(self):
        assemblyCode = self.prepareUnaryArithemtic()
        assemblyCode.append("M=-M")
        return assemblyCode

    def and_a(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.append("M=D&M")
        return assemblyCode

    def or_a(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.append("M=D|M")
        return assemblyCode

    def not_a(self):
        assemblyCode = self.prepareUnaryArithemtic()
        assemblyCode.append("M=!M")
        return assemblyCode

    def eq(self):
        assemblyCode = self.prepareBinaryArithmetic()
        assemblyCode.extend(self.booleanJump('JEQ'))
        self.eqCount += 1

        return assemblyCode

    def gt(self):
        assemblyCode = self.prepareBinaryArithmetic()       
        assemblyCode.extend(self.booleanJump('JGT'))
        self.gtCount += 1

        return assemblyCode

    def lt(self):
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
        return self.p.decrementPointer()

    def prepareBinaryArithmetic(self):
        assemblyCode = self.p.decrementPointer()
        assemblyCode.append("D=M")
        assemblyCode.extend(self.p.decrementPointer())
        return assemblyCode

class PointerHandler:

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

class PushPopHandler:
    
    def __init__(self):
        self.p = PointerHandler()
        self.currentFunction = ''

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
                assemblyCode.append('A=D+M')                    
            elif (segment == 'static') or (segment == 'temp') or (segment == 'pointer'):
                assemblyCode.append(self.getSymbol(segment, index))
            assemblyCode.append('D=M')
        
        assemblyCode.append('@SP')
        assemblyCode.append('A=M')
        assemblyCode.append('M=D')
        assemblyCode.extend(self.p.incrementPointer())

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
    
    # get Value for pop and set pointer
    def getPopValue(self):
        assemblyCode = self.p.decrementPointer()
        assemblyCode.append("D=M")
        return assemblyCode

        # returns string for symbol
    
    def getSymbol(self, segment, index):

        if segment == 'constant':
            return '@' + index
        elif segment == 'local':
            return '@LCL'
        elif segment == 'static':
            return '@' + self.currentFunction + '_' + index
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
