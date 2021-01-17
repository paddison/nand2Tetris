"""
Provides a sybmol table abstraction. 
The symbol table associates the identifier names found in the program with 
identifier properties needed for compilation: type, kind, and running index.

The symbol table has two nested scopes (class/subroutine)
"""

class SymbolTable:

    # Initializes itself at the start of compiling a new class
    def __init__(self):
        self.classScope = {}
        self.subroutineScope = {}
        self.staticCount = 0
        self.fieldCount = 0
        return

    # Starts a new subroutine scope (resets the subroutine Table)
    def startSubroutine(self):
        self.subroutineScope = {}
        self.localCount = 0
        self.argCount = 0

    # Defines a new Table entry, depending on kind
    def define(self, name, varType, kind):

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

    # Returns the number of variables of the given kind already defined in the current scope
    def varCount(self, kind):
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

    # Returns the kind of the named identifier in the current scope, returns -1 if none is found
    def kindOf(self, name):
        try:
            var = self.subroutineScope[name]
            return var['kind']
        except:
            try:
                var = self.classScope[name]
                return var['kind']
            except:
                return 'NONE'

    # Returns the type of the named identifer in the current scope
    def typeOf(self, name):
        try:
            var = self.subroutineScope[name]
            return var['type']
        except:
            try:
                var = self.classScope[name]
                return var['type']
            except:
                return -1

    # Returns the index assigned to the named identifier
    def indexOf(self, name):
        try:
            var = self.subroutineScope[name]
            return var['index']
        except:
            try:
                var = self.classScope[name]
                return var['index']
            except:
                return -1

    # Return the whole Variable
    def getVariable(self, name):
        try:
            return self.subroutineScope[name]
        except:
            try:
                return self.classScope[name]
            except:
                return -1


        


#
#
# FOR TESTING ONLY
"""
st = SymbolTable()

st.startSubroutine()
st.define('testClass', 'int', 'STATIC')
st.define('testSub', 'int', 'VAR')
st.kindOf('testClass')
st.kindOf('testSub')
st.typeOf('testClass')
st.typeOf('testSub')
st.indexOf('testClass')
st.indexOf('testSub')
"""