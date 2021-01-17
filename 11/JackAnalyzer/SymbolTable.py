"""
Provides a sybmol table abstraction. 
The symbol table associates the identifier names found in the program with 
identifier properties needed for compilation: type, kind, and running index.

The symbol table has two nested scopes (class/subroutine)
"""

class SymbolTable:
 
    def __init__(self):
        """
        Initializes itself at the start of compiling a new class.
        """
        self.classScope = {}
        self.subroutineScope = {}
        self.staticCount = 0
        self.fieldCount = 0
        return

    def startSubroutine(self):
        """
        Starts a new subroutine scope (resets the subroutine Table).
        """
        self.subroutineScope = {}
        self.localCount = 0
        self.argCount = 0

    def define(self, name, varType, kind):
        """
        Defines a new Table entry, depending on kind.
        """
        if (kind == 'STATIC'):
            self.classScope[name] = {
            'type': varType,
            'kind': kind,
            'index': self.staticCount
            }
            self.staticCount += 1
        elif (kind == 'FIELD'):
            self.classScope[name] = {
            'type': varType,
            'kind': kind,
            'index': self.fieldCount
            }
            self.fieldCount += 1
        elif (kind == 'ARG'):
            self.subroutineScope[name] = {
            'type': varType,
            'kind': kind,
            'index': self.argCount
            }
            self.argCount += 1
        elif (kind == 'VAR'):
            self.subroutineScope[name] = {
            'type': varType,
            'kind': kind,
            'index': self.localCount
            }
            self.localCount += 1
        else:
            return -1
        
        return

    def varCount(self, kind):
        """
        Returns the number of variables of the given kind already defined in the current scope/
        """
        if (kind == 'STATIC'):
            return self.staticCount
        elif (kind == 'FIELD'):
            return self.fieldCount
        elif (kind == 'ARG'):
            return self.argCount
        elif (kind == 'VAR'):
            return self.localCount
        else:
            return -1

    def kindOf(self, name):
        """
        Returns the kind of the named identifier in the current scope, returns -1 if none is found.
        """
        try:
            var = self.subroutineScope[name]
            return var['kind']
        except:
            try:
                var = self.classScope[name]
                return var['kind']
            except:
                return 'NONE'

    def typeOf(self, name):
        """
        Returns the type of the named identifer in the current scope.
        """
        
        try:
            var = self.subroutineScope[name]
            return var['type']
        except:
            try:
                var = self.classScope[name]
                return var['type']
            except:
                return -1

    def indexOf(self, name):
        """
        Returns the index assigned to the named identifier.
        """
        try:
            var = self.subroutineScope[name]
            return var['index']
        except:
            try:
                var = self.classScope[name]
                return var['index']
            except:
                return -1

    def getVariable(self, name):
        """
        Return the whole Variable.
        """
        try:
            return self.subroutineScope[name]
        except:
            try:
                return self.classScope[name]
            except:
                return -1