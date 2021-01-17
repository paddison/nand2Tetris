class VMWriter:
    def __init__(self, fname):
        self.f = open(fname + '.vm', 'w')

    def writePush(self, segment, index):
        segment = self.getSegment(segment)
        self.f.write('push ' + segment + ' ' + str(index) + '\n')

    def writePop(self, segment, index):
        segment = self.getSegment(segment)
        self.f.write('pop ' + segment + ' ' + str(index) + '\n')

    def writeArithmetic(self, command):
        self.f.write(command.lower() + '\n')

    def writeLabel(self, label):
        self.f.write('label ' + label + '\n')

    def writeGoto(self, label):
        self.f.write('goto ' + label + '\n')

    def writeIf(self, label):
        self.f.write('if-goto ' + label + '\n')

    def writeCall(self, name, nArgs):
        self.f.write('call ' + name + ' ' + str(nArgs) + '\n')

    def writeFunction(self, name, nLocals):
        self.f.write('function ' + name + ' ' + str(nLocals) + '\n')

    def writeReturn(self):
        self.f.write('return\n')

    def getSegment(self, segment):
        if segment == 'VAR':
            return 'local'
        elif segment == 'STATIC':
            return 'static'
        elif segment == 'ARG':
            return 'argument'
        elif segment == 'FIELD':
            return 'this'
        else:
            return segment
        