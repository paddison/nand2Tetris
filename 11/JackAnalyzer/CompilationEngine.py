"""
The Compilation Engine module, which parses the tokens according to the grammar.
I did not implement error checking, so I assume the input is correct.
"""

import SymbolTable
import VMWriter

class CompilationEngine:

    # Initialize it with a tokenizer, who will guide the input, where each line will first be stored in a list called out.
    def __init__(self, tokenizer, fname):
        self.jt = tokenizer
        self.out = []
        self.writer = VMWriter.VMWriter(fname)
        # Initialize lables for this class
        self.labels = {
            'WHILE': 0,
            'IF': 0
        }

        # initialize a new symbol table
        self.st = SymbolTable.SymbolTable()
        self.compileClass()
        

    # Compiles a complete class according to the following grammar:
    # 'class' className '{' classVarDec* subroutineDec* '}'
    def compileClass(self):

        # 'class' TODO errorChecking
        self.jt.keyWord()

        # className identifier
        self.className = self.jt.identifier()

        #'{' TODO errorChecking
        self.jt.symbol()

        # classVarDec*
        self.compileClassVarDec()
       
        # subroutineDec*
        self.compileSubroutine()

        # '}'
        self.out.append(self.jt.symbol())
        self.out.append('</class>')
        return

    # Compiles zero or more static or field declarations according to the following grammar:
    # ('static' | 'field') type varName (',' varName)* ';'
    def compileClassVarDec(self):
        """ Compiles zero or more static or field declarations by adding them to the Symbol Table.

            Grammar: ('static' | 'field') type varName (',' varName)* ';'
           
        """


        while self.jt.currentToken == 'static' or self.jt.currentToken == 'field':

            # ('static' | 'field')
            varKind = self.jt.keyWord()
            
            # type 
            varType = self.jt.currentToken
            self.jt.advance()
            
            # varName
            varName = self.jt.identifier()

            # Add it to the Symbol Table
            self.st.define(varName, varType, varKind)

            # (',' varName)*
            while self.jt.currentToken == ',':
                self.jt.advance()
                varName = self.jt.identifier()

                # Add it to the Symbol Table
                self.st.define(varName, varType, varKind)
                
            # ';' TODO errorChecking
            self.out.append(self.jt.symbol())

        return

    # Compiles zero or more subroutines according to the following grammar:
    # ('constructor' | 'function' | 'method')('void' | type) subroutineName '(' parameterList ')' subroutineBody
    def compileSubroutine(self):
        
        

        while (self.jt.currentToken == 'constructor' or 
               self.jt.currentToken == 'function' or 
               self.jt.currentToken == 'method'):
            
            # Start a new Symbol table for the subroutine
            self.st.startSubroutine()
            
            # ('constructor' | 'function' | 'method')
            subroutineType = self.jt.keyWord()

            
            # ('void' | type) get return type for this subroutine
            if self.jt.tokenType() == 'IDENTIFIER':
                self.returnType = self.jt.identifier()
            else:
                self.returnType = self.jt.keyWord()
            
            # subroutineName
            subroutineName = self.jt.identifier()
            
            # '(' TODO errorcheck Parameter
            self.jt.symbol()
            
            # If the current subroutine is a method, the current object MUST be first argument added to the symbol table
            if subroutineType == 'METHOD':
                self.st.define('this', self.className, 'ARG')

            # adds arguments to SubroutineTable
            self.compileParameterList() #DONE

            # ')' TODO errorChecking
            self.jt.symbol()
            
            # Compile the body of a subroutine
            
            # '{' TODO errorChecking
            self.jt.symbol()
            
            # Add local variables to Subroutine Table
            self.compileVarDec() #DONE

            # Get number of local variables and write function declaration (function Class.subroutineName numLocals) 
            numLocals = self.st.varCount('VAR')
            self.writer.writeFunction(self.className + '.' + subroutineName, numLocals)

            # If the current function is a constructor, allocate space for it and set the pointer segment to point to said space
            # The space needed will be the number of field variables
            if subroutineType == 'CONSTRUCTOR':
                self.writer.writePush('constant', self.st.varCount('FIELD'))
                self.writer.writeCall('Memory.alloc', 1)
                self.writer.writePop('pointer', 0)
            # If the current function is a method, we must set the this segment/current object first.
            # In a method call the first argument will ALWAYS be the current object. Which we need to set the this segment to.
            elif subroutineType == 'METHOD':
                self.writer.writePush('argument', 0)
                self.writer.writePop('pointer', 0)

            # statements
            self.compileStatements() 
            
            # '}'
            self.out.append(self.jt.symbol())

            self.out.append('</subroutineBody>')
            self.out.append('</subroutineDec>')
        return

    # Adds the ARG variabls of a subroutine declaration to the symbol table
    def compileParameterList(self):

        # Are there any arguments?
        if (self.jt.currentToken == 'int' or self.jt.currentToken == 'char' or
            self.jt.currentToken == 'boolean' or self.jt.tokenType() == 'IDENTIFIER'):
            
            # see if its a primitive type
            if self.jt.tokenType() == 'KEYWORD':    
                varType = self.jt.keyWord()
            else:
                varType = self.jt.identifier()

            name = self.jt.identifier()
            
            # add entry to symbol table
            self.st.define(name, varType, 'ARG')

            # see if there are additional ARG
            while (self.jt.currentToken == ','):
                self.jt.advance()
                # see if its a primitive type
                if self.jt.tokenType() == 'KEYWORD':    
                    varType = self.jt.keyWord()
                else:
                    varType = self.jt.identifier()

                name = self.jt.identifier()
                
                # add entry to symbol table
                self.st.define(name, varType, 'ARG')

        return

    # Compiles zero or more var declarations according to the following grammar:
    # 'var' type varName (',' varName)* ';'
    def compileVarDec(self):

        # Are there any var tokens left?
        while (self.jt.currentToken == 'var'):

            # kind of variable (should be VAR)
            kind = self.jt.keyWord()
            
            # type
            varType = self.jt.currentToken
            if self.jt.tokenType() == 'KEYWORD':    
                varType = self.jt.keyWord()
            else:
                varType = self.jt.identifier()

            #varName
            name = self.jt.identifier()

            # Add to symbol table
            self.st.define(name, varType, kind)

            # see if there are more variable of same type
            while (self.jt.currentToken == ','):
                self.jt.advance()
                name = self.jt.identifier()
                self.st.define(name, varType, kind)

            # ';' TODO errorChecking
            self.jt.symbol()
        return

    # Compiles a sequence of statements according to the follwoing grammar:
    # statement* (let | if | while | do | return)
    def compileStatements(self):
        self.out.append('<statements>')

        # Are there any statements? #NONE DONE SO FAR #TODO errorChecking
        while self.jt.currentToken in self.jt.statements:
            if self.jt.currentToken == 'let':
                self.jt.advance()
                self.compileLet()
            elif self.jt.currentToken == 'if':
                self.jt.advance()
                self.compileIf()
            elif self.jt.currentToken == 'while':
                self.jt.advance()
                self.compileWhile()
            elif self.jt.currentToken == 'do':
                self.jt.advance()
                self.compileDo() 
            elif self.jt.currentToken == 'return': 
                self.jt.advance()
                self.compileReturn()
        self.out.append('</statements>')
        return

    # Compiles a do statement according to the following grammar:
    # 'do' subroutineCall ';'
    def compileDo(self):

        # subroutineCall
        self.compileSubroutineCall(self.jt.identifier())

        # A function call with do will always be void, which by convention return 0
        # They need to be 'dumped' in the temp memory segment

        self.writer.writePop('temp', 0)

        # ';' #TODO errorChecking
        self.jt.symbol()
        return

    # Compiles a let statement according to the following grammar:
    # 'let' varName ('[' expression ']')? '=' expression ';'
    def compileLet(self):
        
        # varName, get current variable from symbolTable
        var = self.st.getVariable(self.jt.identifier())
        


        # ('[' expression ']')? 
        if self.jt.currentToken == '[':
            # '['
            self.jt.advance()

            # Push array on stack (it is storing the heap adress)
            self.writer.writePush(var['kind'], var['index'])
            
            # expression
            self.compileExpression()

            # Calculate the index (baseAdress + expression)
            self.writer.writeArithmetic('ADD')

            # ']' TODO errorChecking
            self.out.append(self.jt.symbol())

            # = TODO errorChecking
            self.out.append(self.jt.symbol())

            # expression
            self.compileExpression()

            self.writer.writePop('temp', 0)
            self.writer.writePop('pointer', 1)
            self.writer.writePush('temp', 0)
            self.writer.writePop('that', 0)

        else:
            # = TODO errorChecking
            self.out.append(self.jt.symbol())

            # expression
            self.compileExpression()

            # Pop expression result into variable
            self.writer.writePop(var['kind'], var['index'])

        # ';' #TODO errorChecking
        self.out.append(self.jt.symbol())

        return

    # Compiles a while statement according to the following grammar:
    # 'while' '(' expression ')' '{' statements '}'
    def compileWhile(self):        
        
        # 'while' Done before function call
        
        # Create label for entering while loop
        label = self.createLabel('WHILE')
        # increment label counter
        self.labels['WHILE'] += 1 

        self.writer.writeLabel(label)
        
        # '(' TODO errorChecking
        self.out.append(self.jt.symbol())

        # expression
        self.compileExpression()

        # ')' TODO errorChecking
        self.out.append(self.jt.symbol())

        # negate the expression
        self.writer.writeArithmetic('NOT')
        # if true (meaning the condition evaluated to false) goto exit label
        self.writer.writeIf(label + '_EXIT')

        # '{' TODO errorChecking
        self.out.append(self.jt.symbol())

        # statements
        self.compileStatements()

        # '}' TODO errorChecking
        self.out.append(self.jt.symbol())

        # at the end of statements, go back to beginning
        self.writer.writeGoto(label)

        # label to exit while loop
        self.writer.writeLabel(label + '_EXIT')

        return

    # compiles a return statement according to the following grammar:
    # 'return' expression? ';'
    def compileReturn(self):
        
        # 'return' Done before function Call

        # expression?
        if self.jt.currentToken != ';':
            self.compileExpression()

        # ';'
        self.out.append(self.jt.symbol())
        self.out.append('</returnStatement>')

        # if current subroutine is of return type 'void', push 0 before return
        if (self.returnType == 'VOID'):
            self.writer.writePush('constant', 0)

        self.writer.writeReturn()
        return


    def compileIf(self):
        """ Compiles an if statement.

            Grammar: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        
            When compiling an if statement, we must first evaluate the condition, and negate it.
            If it is true, it means the if was false and we goto the else part of it otherwise continue with the flow of the code, 
            and jump to the exit label.

            The general VM-Code will look like:
                VM code for computing ~(cond)    
                if-goto className_IFCount    
                VM code for executing the 'if' part   
                goto className_IFCount_EXIT
                label className_IFCount    
                VM code for executing the 'else' part  
                label className_IFCount_EXIT
        """

        # 'if' handled before function call
        label = self.createLabel('IF')
        
        # increment if label counter
        self.labels['IF'] += 1

        # '(' TODO errorChecking
        self.out.append(self.jt.symbol())

        # expression
        self.compileExpression()

        # ')' TODO errorChecking
        self.out.append(self.jt.symbol())

        # Negate the expression
        self.writer.writeArithmetic('NOT')

        # write if-goto for else
        self.writer.writeIf(label + '_ELSE')

        # '{' TODO errorChecking
        self.out.append(self.jt.symbol())

        # statements for if part
        self.compileStatements()

        # '}' TODO errorChecking
        self.out.append(self.jt.symbol())

        # after code execution go to end of if else
        self.writer.writeGoto(label + '_EXIT')

        # write label for else
        self.writer.writeLabel(label + '_ELSE')

        # ('else' '{' statements '}')?
        if self.jt.currentToken == 'else':
            # 'else'
            self.out.append(self.jt.keyWord())

            # '{'
            self.out.append(self.jt.symbol())

            # statements
            self.compileStatements()

            # '}'
            self.out.append(self.jt.symbol())

        # write exit label for if
        self.writer.writeLabel(label + '_EXIT')

        return

    # Compiles an expression according to the following grammar:
    # term (op term)*
    def compileExpression(self):
        
        # term
        self.compileTerm()
        
        # (op term)*
        while self.jt.currentToken in self.jt.operators:
            
            # get the operator for later
            op = self.jt.symbol()
            
            # term
            self.compileTerm()

            # Always write the arithmetic at the end of each expression
            # if its multiplication or division call respective function
            if (op == '*'):
                self.writer.writeCall('Math.multiply', 2)
            elif (op == '/'):
                self.writer.writeCall('Math.divide', 2)
            elif (op == '+'):
                self.writer.writeArithmetic('ADD')
            elif (op == '-'):
                self.writer.writeArithmetic('SUB')
            elif (op == '='):
                self.writer.writeArithmetic('EQ')
            elif (op == '>'):
                self.writer.writeArithmetic('GT')
            elif (op == '<'):
                self.writer.writeArithmetic('LT')
            elif (op == '&'):
                self.writer.writeArithmetic('AND')
            elif (op == '|'):
                self.writer.writeArithmetic('OR')
            else:
                pass#TODO errorChecking

        return

    # Compiles a term according to the following grammar:
    # integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
    def compileTerm(self):
        self.out.append('<term>')

        # push constant
        if self.jt.tokenType() == 'INT_CONST':
            self.writer.writePush('constant', self.jt.intVal())

        # stringConstant
        elif self.jt.tokenType() == 'STRING_CONST':
            string = self.jt.stringVal()
            self.writer.writePush('constant', len(string)) # Store string in temp 1 while it is created
            self.writer.writeCall('String.new', 1)
            for char in string: # Append each character to temporary string
                self.writer.writePush('constant', ord(char))
                self.writer.writeCall('String.appendChar', 2)
        
        # keywordConstant
        elif self.jt.currentToken in self.jt.keywordConstants:
            keyWord = self.jt.keyWord()
            if keyWord == 'TRUE':
                self.writer.writePush('constant', 1)
                self.writer.writeArithmetic('NEG')
            if keyWord == 'FALSE' or keyWord == 'NULL':
                self.writer.writePush('constant', 0)
            else:
                # 'this' is always pointer 0, since it stores the adress of the object in the heap
                self.writer.writePush('pointer', 0)
                

        # varName | varName '[' expression ']' | subroutineCall
        elif self.jt.tokenType() == 'IDENTIFIER':
            # Get varName from table, if no result is found, assume it is subroutine
            varName = self.jt.identifier()
            var = self.st.getVariable(varName)
            
            if var != - 1:
                
                # '[' expression ']'
                if self.jt.currentToken == '[':
                    self.jt.advance()
                    self.writer.writePush(var['kind'], var['index'])
                    self.compileExpression()
                    self.writer.writeArithmetic('ADD') # Calculate adress of a[i]
                    self.writer.writePop('pointer', 1) # Set pointer to point to that adress
                    self.writer.writePush('that', 0) # Push the value at adress a[i] on stack
                    self.writer.writePop('temp', 0) # Temporarily store it in temp 0
                    self.writer.writePush('temp', 0) # Push it on stack

                    # TODO errorChecking
                    self.out.append(self.jt.symbol())

                elif self.jt.currentToken == '.':
                    self.compileSubroutineCall(varName)
                else:
                    # Push variable on stack
                    self.writer.writePush(var['kind'], var['index'])
                

            # Handle it like a normal subroutine
            else:
                # subroutineCall
                # '(' expressionList ')' | (className | varName).subroutineName'(' expressionList ')'
                self.compileSubroutineCall(varName)

        # '(' expression ')'
        elif self.jt.currentToken == '(':
            self.jt.advance()
            self.compileExpression()
            self.jt.symbol() # TODO errorChecking

        # unaryOp term
        elif self.jt.currentToken in self.jt.unaryOperators:
            # Get the operator
            op = self.jt.currentToken
            self.jt.advance()
            self.compileTerm()
            if op == '-':
                self.writer.writeArithmetic('NEG')
            else:
                self.writer.writeArithmetic('NOT')

        return

    # Compiles a (possibly empty) comma-separated list of expressions, according to the following grammar:
    # (expression (',' expression)*)?
    def compileExpressionList(self):

        # Keep counter to see how many expressions were compile for function call
        numExpressions = 0
        # Are there any expressions?
        if (self.jt.tokenType() == 'IDENTIFIER' or self.jt.tokenType() == 'INT_CONST' or self.jt.tokenType() == 'STRING_CONST' or
            self.jt.currentToken in self.jt.keywordConstants or self.jt.currentToken in self.jt.unaryOperators or self.jt.currentToken == '(' ):
            
            # expression
            self.compileExpression()
            numExpressions += 1
            # (',' expression)*
            while self.jt.currentToken == ',':
                self.jt.symbol() #TODO errorChecking
                # 'expression'
                self.compileExpression()
                numExpressions += 1

        return numExpressions

    # A small helper to write the following grammar:
    # type varName (used in compileParameterList, compileClassVarDec & compileVarDec)
    def compileTypeVarName(self):
        # type
        varType = self.jt.currentToken
        if self.jt.tokenType() == 'KEYWORD':    
            self.out.append(self.jt.keyWord())
        else:
            self.out.append(self.jt.identifier())

        #varName
        name = self.jt.currentToken
        self.out.append(self.jt.identifier())

        return [varType, name]

    # compiles a subroutineCall
    # subroutineName '(' expressionList ')' | (className | varName).subroutineName'(' expressionList ')'
    def compileSubroutineCall(self, subName):
        # subroutineName | className | varName
        identifier = subName
        numArgs = 0

        # if there is a dot
        if (self.jt.currentToken == '.'):
            self.jt.advance()
            # see if it is a method call, by checking if identifier is in symbol table
            varName = self.st.getVariable(identifier)

            # If no variable was found, identifier is the name of a class, otherwise get class (type) of variable
            if varName == -1:
                className = identifier
            else: #TODO errorChecking
                className = varName['type']
                # For method calls, the current variable needs to pushed before arguments, and numArgs = numArgs + 1
                numArgs += 1
                self.writer.writePush(varName['kind'], varName['index'])
            
            # subroutineName
            subroutineName = self.jt.identifier()

        else:
            # If it is just the name of the subroutine, it must be a method AND it is called on the current Object (this)
            className = self.className
            subroutineName = identifier
            numArgs += 1
            self.writer.writePush('pointer', 0) # the adress of the current object
        
        # '(' TODO errorChecking
        self.out.append(self.jt.symbol())

        # expressionList has to return number of expressions, will be number for function call
        numArgs += self.compileExpressionList()

        # ')' TODO errorChecking
        self.out.append(self.jt.symbol())

        # write the call with className.subroutineName, numExpressions
        self.writer.writeCall(className + '.' + subroutineName, numArgs)
        
        return


    # Labels are created like this className_labelNameCount
    def createLabel(self, name):
        return self.className + '_' + name + str(self.labels[name])