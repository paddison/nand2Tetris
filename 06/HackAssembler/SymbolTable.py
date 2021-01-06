# manages the symbol table


class Table:

    # Initialize all the predefined symbols
    SYMBOLS = {
        'SP': '0',
        'LCL': '1',
        'ARG': '2',
        'THIS': '3',
        'THAT': '4',
        'R0': '0',
        'R1': '1',
        'R2': '2',
        'R3': '3',
        'R4': '4',
        'R5': '5',
        'R6': '6',
        'R7': '7',
        'R8': '8',
        'R9': '9',
        'R10': '10',
        'R11': '11',
        'R12': '12',
        'R13': '13',
        'R14': '14',
        'R15': '15',
        'SCREEN': '16384',
        'KBD': '24576'
    }

    curAddress = 16

    # Adds a new entry to the symbols dictionary, 
    def addEntry(self, symbol, address=None, loop=False):
        if loop: 
            self.SYMBOLS[symbol] = str(address)
        else:
            self.SYMBOLS[symbol] = str(self.curAddress)
            self.curAddress += 1

    def contains(self, symbol):
        return symbol in self.SYMBOLS

    def getAddress(self, symbol):
        return self.SYMBOLS[symbol]