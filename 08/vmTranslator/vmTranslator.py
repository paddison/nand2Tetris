import sys
import Parser
import CodeWriter
import os
files = [fname for fname in os.listdir(sys.argv[1]) if fname[-3:] == '.vm']


if len(sys.argv) != 2:
    print('Usage: python3 vmTranslator.py directory_containing_*vm_files')
    exit()

path = sys.argv[1] + '/'
output = sys.argv[1][sys.argv[1].rfind('/') + 1:]
print(path)
print(output)
cw = CodeWriter.CodeWrite(path + output)
cw.writeInit()
for function in files:
    cw.setCurrentFunctionName(function[:-3])
    p = Parser.Parser(path + function[:-3])

    for command in p.commands:
        cmdType = p.commandType(command)
        
        # get command parts
        if cmdType != 'C_RETURN':
            arg1 = p.arg1(command)

        if (cmdType == 'C_PUSH') or (cmdType ==  'C_POP') or (cmdType == 'C_FUNCTION') or (cmdType == 'C_CALL'):
            arg2 = p.arg2(command)
        
        # write according to command
        if cmdType == 'C_ARITHMETIC':
            cw.writeArithmetic(arg1)

        elif (cmdType == 'C_PUSH') or (cmdType == 'C_POP'):
            cw.writePushPop(cmdType, arg1, arg2)
        elif cmdType == 'C_LABEL':
            cw.writeLabel(arg1)
        elif cmdType == 'C_GOTO':
            cw.writeGoto(arg1)
        elif cmdType == 'C_IF':
            cw.writeIf(arg1)
        elif cmdType == 'C_FUNCTION':
            cw.writeFunction(arg1, arg2)
        elif cmdType == 'C_RETURN':
            cw.writeReturn()
        elif cmdType == 'C_CALL':
            cw.writeCall(arg1, arg2)

print('Finished writing ' + output + '.asm.')
cw.close()