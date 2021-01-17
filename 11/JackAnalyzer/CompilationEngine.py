"""
The Compilation Engine module, which parses the tokens according to the grammar.
I did not implement error checking, so I assume the input is correct.
"""

import SymbolTable
import VMWriter
import CompilationErrors as ce

class CompilationEngine:

    def __init__(self, tokenizer, fname):
        """
        Initialize it with a tokenizer, which will guide the input.

        The output file will be written by calls to the VMWriter.

        Also initialize all label counters to 0, and create a new class level symbol table.
        """
        self.jt = tokenizer
        self.writer = VMWriter.VMWriter(fname)
        # Initialize lables for this class
        self.labels = {
            'WHILE': 0,
            'IF': 0
        }

        # Initialize a new symbol table
        self.st = SymbolTable.SymbolTable()
        self.compileClass()

        return
        
    def compileClass(self):
        """
        Compiles a complete class according to the following grammar:
            'class' className '{' classVarDec* subroutineDec* '}'
        """
        # 'class'
        if self.jt.keyWord() != 'CLASS':
            ce.classDeclarationError(self.jt.getCurrentLine())

        # className identifier
        if self.jt.tokenType() != 'IDENTIFIER':
            ce.classDeclarationError(self.jt.getCurrentLine())

        self.className = self.jt.identifier()

        #'{' 
        if self.jt.symbol() != '{':
            ce.missingBracketError(self.jt.getCurrentLine())

        # classVarDec*
        self.compileClassVarDec()
       
        # subroutineDec*
        self.compileSubroutine()

        # '}'
        if self.jt.symbol() != '}':
            ce.missingBracketError(self.jt.getCurrentLine())
        return

    def compileClassVarDec(self):
        """ 
        Compiles zero or more static or field declarations by adding them to the Symbol Table.
            Grammar: ('static' | 'field') type varName (',' varName)* ';'
        """
        while self.jt.currentToken == 'static' or self.jt.currentToken == 'field':

            # ('static' | 'field')
            varKind = self.jt.keyWord()
            
            # type 
            varType = self.jt.currentToken
            if not self.checkVarType():
                ce.invalidVarTypeError(varType, self.jt.getCurrentLine())
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
                
            # ';'
            if self.jt.symbol() != ';':
                ce.missingTerminationError(self.jt.getCurrentLine())

        # if trying to declare invalid variable kind
        if self.jt.currentToken == 'var':
            ce.invalidVarKindError(self.jt.currentToken, 'class variable space', self.jt.getCurrentLine())

        return

    def compileSubroutine(self):
        """
        Compiles zero or more subroutines according to the following grammar:
            ('constructor' | 'function' | 'method')('void' | type) subroutineName '(' parameterList ')' subroutineBody
        """
        while (self.jt.currentToken == 'constructor' or 
               self.jt.currentToken == 'function' or 
               self.jt.currentToken == 'method'):
            
            # Start a new Symbol table for the subroutine
            self.st.startSubroutine()
            
            # ('constructor' | 'function' | 'method')
            self.currentSubroutineType = self.jt.keyWord()
  
            # ('void' | type) get return type for this subroutine
            if self.jt.tokenType() == 'IDENTIFIER':
                self.returnType = self.jt.identifier()
            else:
                self.returnType = self.jt.keyWord()
            
            # subroutineName
            subroutineName = self.jt.identifier()
            
            # '(' 
            if self.jt.currentToken != '(':
                ce.missingBracketError(self.jt.getCurrentLine())
            self.jt.advance()
            
            # If the current subroutine is a method, the current object MUST be first argument added to the symbol table
            if self.currentSubroutineType == 'METHOD':
                self.st.define('this', self.className, 'ARG')

            # adds arguments to SubroutineTable
            self.compileParameterList() #DONE

            # ')'
            if self.jt.currentToken != ')':
                ce.missingBracketError(self.jt.getCurrentLine())
            self.jt.advance()
            
            # Compile the body of a subroutine
            
            # '{' 
            if self.jt.currentToken != '{':
                ce.missingBracketError(self.jt.getCurrentLine())
            self.jt.advance()
            
            # Add local variables to Subroutine Table
            self.compileVarDec() 

            # Get number of local variables and write function declaration (function Class.subroutineName numLocals) 
            numLocals = self.st.varCount('VAR')
            self.writer.writeFunction(self.className + '.' + subroutineName, numLocals)

            # If the current function is a constructor, allocate space for object and set the pointer segment to point to said obejct
            # The space needed will be the number of field variables
            if self.currentSubroutineType == 'CONSTRUCTOR':
                self.writer.writePush('constant', self.st.varCount('FIELD'))
                self.writer.writeCall('Memory.alloc', 1)
                self.writer.writePop('pointer', 0) # setting 'this'

            # If the current function is a method, we must set the this segment/current object first.
            # In a method call the first argument will ALWAYS be the current object.
            elif self.currentSubroutineType == 'METHOD':
                self.writer.writePush('argument', 0)
                self.writer.writePop('pointer', 0) # setting 'this'

            # statements
            self.compileStatements() 
            
            # '}'
            if self.jt.currentToken != '}':
                ce.missingBracketError(self.jt.getCurrentLine())
            self.jt.advance()

        return

    def compileParameterList(self):
        """
        Adds the ARG variabls of a subroutine declaration to the symbol table, according to the following grammar:
            ((type varName) (',' type varName)*)?
        """
        # Are there any arguments?
        if (self.jt.currentToken == 'int' or self.jt.currentToken == 'char' or
            self.jt.currentToken == 'boolean' or self.jt.tokenType() == 'IDENTIFIER'):
            
            # see if its a primitive type
            if self.jt.tokenType() == 'KEYWORD':    
                varType = self.jt.keyWord()
            else:
                varType = self.jt.identifier()

            # error checking variable type
            if not self.checkVarType():
                ce.invalidVarTypeError(varType, self.jt.getCurrentLine())

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

                # error checking variable type
                if not self.checkVarType():
                    ce.invalidVarTypeError(varType, self.jt.getCurrentLine())

                name = self.jt.identifier()
                
                # add entry to symbol table
                self.st.define(name, varType, 'ARG')

        return

    def compileVarDec(self):
        """
        Compiles zero or more var declarations according to the following grammar:
            'var' type varName (',' varName)* ';'
        """
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

            # error checking variable type
            if not self.checkVarType():
                ce.invalidVarTypeError(varType, self.jt.getCurrentLine())

            #varName
            name = self.jt.identifier()

            # Add to symbol table
            self.st.define(name, varType, kind)

            # see if there are more variable of same type
            while (self.jt.currentToken == ','):
                self.jt.advance()
                name = self.jt.identifier()
                self.st.define(name, varType, kind)

            # ';' 
            if self.jt.currentToken != ';':
                ce.missingTerminationError(self.jt.getCurrentLine())
            self.jt.advance()

        # if trying to declare invalid variable kind
        if self.jt.currentToken == 'static' or self.jt.currentToken == 'field':
            ce.invalidVarKindError(self.jt.currentToken, 'local space', self.jt.getCurrentLine())

        return

    def compileStatements(self):
        """
        Compiles a sequence of statements according to the follwoing grammar:
            statement* (let | if | while | do | return)
        """
        # Are there any statements? 
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
        return


    def compileDo(self):
        """
        Compiles a do statement according to the following grammar:
            'do' subroutineCall ';'
        """
        # subroutineCall
        self.compileSubroutineCall(self.jt.identifier())

        # A do function call will always be void, which by convention return 0
        # They need to be 'dumped' in the temp memory segment
        self.writer.writePop('temp', 0)

        # ';'
        if self.jt.currentToken != ';':
            ce.missingTerminationError(self.jt.getCurrentLine())
        self.jt.advance()
        
        return

    def compileLet(self):
        """
        Compiles a let statement according to the following grammar:
            'let' varName ('[' expression ']')? '=' expression ';'
        """
        # varName, get current variable from symbolTable
        varName = self.jt.identifier()
        var = self.st.getVariable(varName)

        if var == -1:
            ce.variableNotFoundError(varName, self.jt.getCurrentLine())

        # ('[' expression ']')? 
        if self.jt.currentToken == '[':
            # '['
            self.jt.advance()

            # Push array on stack (it is storing the heap adress)
            self.writer.writePush(var['kind'], var['index'])
            
            # expression
            self.compileExpression()

            # Calculate the index (baseAdress + expression) and put it on top of stack
            self.writer.writeArithmetic('ADD')

            # ']' 
            if self.jt.currentToken != ']':
                ce.missingBracketError(self.jt.getCurrentLine())
            self.jt.advance()

            # '=' 
            if self.jt.currentToken != '=':
                ce.missingEqualsError(self.jt.getCurrentLine())
            self.jt.advance()

            # expression
            self.compileExpression()

            # After compiling the expression the top value on stack will be the return value which will be stored in temp 0
            # The next value on the stack is the adress of the index, which will be popped in pointer 1, to set the 'that' segment
            # Afterwards save the value of temp 0 in the adress of that
            self.writer.writePop('temp', 0)
            self.writer.writePop('pointer', 1)
            self.writer.writePush('temp', 0)
            self.writer.writePop('that', 0)

        else:
            # '= '
            if self.jt.currentToken != '=':
                ce.missingEqualsError(self.jt.getCurrentLine())
            self.jt.advance()

            # expression
            self.compileExpression()

            # Pop expression result into variable
            self.writer.writePop(var['kind'], var['index'])

        # ';'
        if self.jt.currentToken != ';':
            ce.missingTerminationError(self.jt.getCurrentLine())
        self.jt.advance()

        return

    def compileWhile(self):     
        """
        Compiles a while statement according to the following grammar:
            'while' '(' expression ')' '{' statements '}'
        
        When writing a while statement we must evaluate the condition first and then negate it.
        If it is true (meaning the actual condition is false) we go to the exit label. 
        Otherwise continue in the loop, go to top, and repeat.

        The general VM code will look like:
            label className_WHILEx
            VM code for computing ~(cond)
            if-goto className_WHILEx_EXIT
            VM code for loop statements
            goto className_WHILEx
            label className_WHILEx_EXIT
        """   
        # 'while' tokenpointer advanced before function call
        
        # Create label for entering while loop
        label = self.createLabel('WHILE')
        # increment label counter
        self.labels['WHILE'] += 1 

        self.writer.writeLabel(label)
        
        # '(' 
        if self.jt.currentToken != '(':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # expression
        self.compileExpression()

        # ')'
        if self.jt.currentToken != ')':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # negate the expression
        self.writer.writeArithmetic('NOT')
        # if true (meaning the condition evaluated to false) goto exit label
        self.writer.writeIf(label + '_EXIT')

        # '{'
        if self.jt.currentToken != '{':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # statements
        self.compileStatements()

        # '}'
        if self.jt.currentToken != '}':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # at the end of statements, go back to beginning
        self.writer.writeGoto(label)

        # label to exit while loop
        self.writer.writeLabel(label + '_EXIT')

        return

    def compileReturn(self):
        """
        compiles a return statement according to the following grammar:
            'return' expression? ';'
        A return statement must always have a value pushed on the stack before executed. 
        If the current function is void, constant 0 will be pushed before return.
        """
        
        # 'return' tokenPointer advanced before function call.

        # expression?
        if self.jt.currentToken != ';':
            self.compileExpression()

        # ';'
        if self.jt.currentToken != ';':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # if current subroutine is of return type 'void', push 0 before return
        if (self.returnType == 'VOID'):
            self.writer.writePush('constant', 0)

        self.writer.writeReturn()
        return

    def compileIf(self):
        """ 
        Compiles an if statement according to the following grammar.
            'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    
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

        # '(' 
        if self.jt.currentToken != '(':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # expression
        self.compileExpression()

        # ')'
        if self.jt.currentToken != ')':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # Negate the expression
        self.writer.writeArithmetic('NOT')

        # write if-goto for else
        self.writer.writeIf(label + '_ELSE')

        # '{'
        if self.jt.currentToken != '{':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # statements for if part
        self.compileStatements()

        # '}'
        if self.jt.currentToken != '}':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # after code execution go to end of if else
        self.writer.writeGoto(label + '_EXIT')

        # write label for else
        self.writer.writeLabel(label + '_ELSE')

        # ('else' '{' statements '}')?
        if self.jt.currentToken == 'else':
            # 'else'
            self.jt.advance()

            # '{'
            if self.jt.currentToken != '{':
                ce.missingBracketError(self.jt.getCurrentLine())
            self.jt.advance()

            # statements
            self.compileStatements()

            # '}'
            if self.jt.currentToken != '}':
                ce.missingBracketError(self.jt.getCurrentLine())
            self.jt.advance()

        # write exit label for if statement
        self.writer.writeLabel(label + '_EXIT')

        return

    def compileExpression(self):
        """
        Compiles an expression according to the following grammar:
            term (op term)*
        Luckily since terms are compiled recursively, we don't need to worry about the order.
        If there is a operator, the arithmetic operation must always be evaluated after the term compilation itself
        (e.g. term1, term2, add)
        """
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

        return

    def compileTerm(self):
        """
        Compiles a term according to the following grammar:
            integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        """

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
                if self.currentSubroutineType == 'FUNCTION':
                    ce.wrongFunctionContext(self.jt.getCurrentLine())
                self.writer.writePush('pointer', 0)
                
        # varName | varName '[' expression ']' | subroutineCall
        elif self.jt.tokenType() == 'IDENTIFIER':
            # Get varName from table, if no result is found, assume it is function
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
                    self.writer.writePush('temp', 0) # Push it on stack for return

                    # ']'
                    if self.jt.currentToken != ']':
                        ce.missingBracketError(self.jt.getCurrentLine())
                    self.jt.advance()

                # if it is a method
                elif self.jt.currentToken == '.':
                    self.compileSubroutineCall(varName)
                else:
                    # Push variable on stack
                    self.writer.writePush(var['kind'], var['index'])
                
            # If it is a function or constructor
            else:
                # subroutineCall
                # '(' expressionList ')' | (className | varName).subroutineName'(' expressionList ')'
                self.compileSubroutineCall(varName)

        # '(' expression ')'
        elif self.jt.currentToken == '(':
            self.jt.advance()
            self.compileExpression()
            if self.jt.currentToken != ')':
                ce.missingBracketError(self.jt.getCurrentLine())
            self.jt.advance()

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
                self.jt.advance()
                # 'expression'
                self.compileExpression()
                numExpressions += 1

        return numExpressions
  
    def compileSubroutineCall(self, subName):
        """
        A helper function to compile a subroutine call, must be called with name of the subroutine
            Grammar: subroutineName '(' expressionList ')' | (className | varName).subroutineName'(' expressionList ')'
        """
        # subroutineName | className | varName
        identifier = subName
        numArgs = 0

        # if there is a dot
        if (self.jt.currentToken == '.'):
            self.jt.advance()
            # see if it is a method call, by checking if identifier is in symbol table
            varName = self.st.getVariable(identifier)

            # If no variable was found it means subroutine is a function, or constructor.
            if varName == -1:
                className = identifier
            else: 
                # If a variable is found it means it is a method
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
        
        # '('
        if self.jt.currentToken != '(':
            ce.missingParameterList(self.jt.getCurrentLine())
        self.jt.advance()

        # expressionList has to return number of expressions, will be number for function call
        numArgs += self.compileExpressionList()

        # ')'
        if self.jt.currentToken != ')':
            ce.missingBracketError(self.jt.getCurrentLine())
        self.jt.advance()

        # write the call with className.subroutineName, numExpressions
        self.writer.writeCall(className + '.' + subroutineName, numArgs)
        
        return

    def createLabel(self, name):
        """
        A helper to create labels. They are created with the following naming convention:
            className_labelNameCounter(_additionalInfo)*
        """
        return self.className + '_' + name + str(self.labels[name])

    def checkVarType(self):
        """
        A helper to check if the variable is of a valid type. (Meaning not 'null' or 'this' etc)    
        """
        if (self.jt.tokenType() != 'KEYWORD' and self.jt.tokenType() != 'IDENTIFIER'):
            return False
        elif (self.jt.tokenType() == 'KEYWORD' and self.jt.currentToken not in self.jt.primitiveTypes):
            return False
        else:
            return True