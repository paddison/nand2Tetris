class Parser:

    ARITHMETIC_COMMANDS = [
        'add',
        'sub',
        'neg',
        'eq',
        'gt',
        'lt',
        'and',
        'or',
        'not'
    ]

    # constrctor read all commands in list
    def __init__(self, file):
        self.commands = []

        with open(file + '.vm', 'r') as f:
            for line in f:
                if line.startswith('//') or line[0].isspace():
                    continue
                if line.find('//') is not -1:
                    line = line[:line.find('//')]
                self.commands.append(line.rstrip())

    # Returns the type of the current VM command (only C_ARITHMETIC, C_PUSH, C_POP implemented)
    def commandType(self, command):
        cmdType = command.split()[0]
        if cmdType == 'push':
            return 'C_PUSH'
        elif cmdType == 'pop':
            return 'C_POP'
        elif cmdType in self.ARITHMETIC_COMMANDS:
            return 'C_ARITHMETIC'
        else:
            raise NotImplementedError

    # Returns the first argument of the current command (not if C_RETURN)
    def arg1(self, command):
        if len(command.split()) == 1:
            return command.split()[0]
        else:
            return command.split()[1]
    
    # Returns the second argumend (only if C_PUSH, C_POP, C_FUNCTION or C_CALL)
    def arg2(self, command):
        return command.split()[2]