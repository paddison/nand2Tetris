import sys
import Parser
import CodeWriter


if len(sys.argv) != 2:
    print('Usage: python3 vmTranslator.py file.vm')
    exit()

if sys.argv[1][-3:] != '.vm':
    print('Only .vm files allowed')
    exit()

fname = sys.argv[1][:-3]

p = Parser.Parser(fname)
cw = CodeWriter.CodeWrite(fname)

for command in p.commands:
    cmdType = p.commandType(command)
    if cmdType != 'C_RETURN':
        arg1 = p.arg1(command)

    if (cmdType == 'C_PUSH') or (cmdType ==  'C_POP') or (cmdType == 'C_FUNCTION') or (cmdType == 'C_CALL'):
        arg2 = p.arg2(command)
    
    if cmdType == 'C_ARITHMETIC':
        cw.writeArithmetic(arg1)

    if (cmdType == 'C_PUSH') or (cmdType == 'C_POP'):
        cw.writePushPop(cmdType, arg1, arg2)

print('Finished writing ' + fname[fname.rfind('/') + 1:] + '.asm.')
cw.close()