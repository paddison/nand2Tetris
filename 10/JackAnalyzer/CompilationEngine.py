"""
The Compilation Engine module, which parses the tokens according to the grammar.
I did not implement error checking, so I assume the input is correct.
"""

class CompilationEngine:

    # Initialize it with a tokenizer, who will guide the input, where each line will first be stored in a list called out.
    def __init__(self, tokenizer):
        self.jt = tokenizer
        self.out = []
        self.compileClass()

    # Compiles a complete class according to the following grammar:
    # 'class' className '{' classVarDec* subroutineDec* '}'
    def compileClass(self):
        
        # first keyword must be a class
        self.out.append('<class>')

        # 'class'
        self.out.append(self.jt.keyWord())

        # className identifier
        self.out.append(self.jt.identifier())

        #'{'
        self.out.append(self.jt.symbol())

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
        while self.jt.currentToken == 'static' or self.jt.currentToken == 'field':
            self.out.append('<classVarDec>')
            # ('static' | 'field')
            self.out.append(self.jt.keyWord())
            
            # type varName
            self.compileTypeVarName()

            # (',' varName)*
            self.compileAdditionalDeclarations()
            
            # ';'
            self.out.append(self.jt.symbol())
            self.out.append('</classVarDec>')

        return

    # Compiles zero or more subroutines according to the following grammar:
    # ('constructor' | 'function' | 'method')('void' | type) subroutineName '(' parameterList ')' subroutineBody
    def compileSubroutine(self):
        while (self.jt.currentToken == 'constructor' or 
               self.jt.currentToken == 'function' or 
               self.jt.currentToken == 'method'):
            
            self.out.append('<subroutineDec>')

            # ('constructor' | 'function' | 'method')
            self.out.append(self.jt.keyWord())
            
            # ('void' | type)
            if self.jt.tokenType() == 'IDENTIFIER':
                self.out.append(self.jt.identifier())
            else:
                self.out.append(self.jt.keyWord())
            
            # subroutineName
            self.out.append(self.jt.identifier())
            
            # '('
            self.out.append(self.jt.symbol())
            
            # parameterList
            self.compileParameterList()
            
            # ')'
            self.out.append(self.jt.symbol())
            
            # subroutine Body 
            # '{' varDec* statements '}'
            self.out.append("<subroutineBody>")
            
            # '{'
            self.out.append(self.jt.symbol())
            
            # varDec*
            self.compileVarDec()
            
            # statements
            self.compileStatements()
            
            # '}'
            self.out.append(self.jt.symbol())

            self.out.append('</subroutineBody>')
            self.out.append('</subroutineDec>')
        return

    # Compiles a (possibly empty) parameter list, not including the enclosing '()' according to the following grammar:
    # ((type varName) (',' type varName)*)?
    def compileParameterList(self):
        self.out.append('<parameterList>')

        # Are there any parameters?
        if (self.jt.currentToken == 'int' or self.jt.currentToken == 'char' or
            self.jt.currentToken == 'boolean' or self.jt.tokenType() == 'IDENTIFIER'):

            # type varName
            self.compileTypeVarName()

            # (',' type varName)*
            self.compileAdditionalDeclarationsWithType()
        self.out.append('</parameterList>')
        return

    # Compiles zero or more var declarations according to the following grammar:
    # 'var' type varName (',' varName)* ';'
    def compileVarDec(self):

        # Are there any var tokens left?
        while (self.jt.currentToken == 'var'):
            self.out.append('<varDec>')

            # 'var'
            self.out.append(self.jt.keyWord())
            
            # type varName
            self.compileTypeVarName()
            
            # (',' type varName)*
            self.compileAdditionalDeclarations()

            # ';'
            self.out.append(self.jt.symbol())
            self.out.append('</varDec>')
        return

    # Compiles a sequence of statements according to the follwoing grammar:
    # statement* (let | if | while | do | return)
    def compileStatements(self):
        self.out.append('<statements>')

        # Are there any statements?
        while self.jt.currentToken in self.jt.statements:
            if self.jt.currentToken == 'let':
                self.compileLet()
            elif self.jt.currentToken == 'if':
                self.compileIf()
            elif self.jt.currentToken == 'while':
                self.compileWhile()
            elif self.jt.currentToken == 'do':
                self.compileDo()
            elif self.jt.currentToken == 'return':
                self.compileReturn()
        self.out.append('</statements>')
        return

    # Compiles a do statement according to the following grammar:
    # 'do' subroutineCall ';'
    def compileDo(self):
        self.out.append('<doStatement>')

        # 'do'
        self.out.append(self.jt.keyWord())

        # subroutineCall
        self.compileSubroutineCall()

        # ';'
        self.out.append(self.jt.symbol())
        self.out.append('</doStatement>')
        return

    # Compiles a let statement according to the following grammar:
    # 'let' varName ('[' expression ']')? '=' expression ';'
    def compileLet(self):
        self.out.append('<letStatement>')
        # 'let'
        self.out.append(self.jt.keyWord())
        
        # varName
        self.out.append(self.jt.identifier())

        # ('[' expression ']')?
        if self.jt.currentToken == '[':
            # '['
            self.out.append(self.jt.symbol())

            # expression
            self.compileExpression()

            # ']'
            self.out.append(self.jt.symbol())
        
        # = 
        self.out.append(self.jt.symbol())

        # expression
        self.compileExpression()

        # ';'
        self.out.append(self.jt.symbol())

        self.out.append('</letStatement>')
        return

    # Compiles a while statement according to the following grammar:
    # 'while' '(' expression ')' '{' statements '}'
    def compileWhile(self):
        self.out.append('<whileStatement>')
        
        # 'while'
        self.out.append(self.jt.keyWord())
        
        # '('
        self.out.append(self.jt.symbol())

        # expression
        self.compileExpression()

        # ')'
        self.out.append(self.jt.symbol())

        # '{'
        self.out.append(self.jt.symbol())

        # statements
        self.compileStatements()

        # '}'
        self.out.append(self.jt.symbol())

        self.out.append('</whileStatement>')

        return

    # compiles a return statement according to the following grammar:
    # 'return' expression? ';'
    def compileReturn(self):
        self.out.append('<returnStatement>')
        
        # 'return'
        self.out.append(self.jt.keyWord())

        # expression?
        if self.jt.currentToken != ';':
            self.compileExpression()

        # ';'
        self.out.append(self.jt.symbol())
        self.out.append('</returnStatement>')

        return

    # compiles an if statement according to the following grammar:
    # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compileIf(self):
        self.out.append('<ifStatement>')

        # 'if'
        self.out.append(self.jt.keyWord())

        # '('
        self.out.append(self.jt.symbol())

        # expression
        self.compileExpression()

        # ')'
        self.out.append(self.jt.symbol())

        # '{'
        self.out.append(self.jt.symbol())

        # statements
        self.compileStatements()

        # '}'
        self.out.append(self.jt.symbol())

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

        self.out.append('</ifStatement>')
        return

    # Compiles an expression according to the following grammar:
    # term (op term)*
    def compileExpression(self):
        self.out.append('<expression>')
        
        # term
        self.compileTerm()
        
        # (op term)*
        if self.jt.currentToken in self.jt.operators:
            # op
            self.out.append(self.jt.symbol())
            
            # term
            self.compileTerm()

        self.out.append('</expression>')
        return

    # Compiles a term according to the following grammar:
    # integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
    def compileTerm(self):
        self.out.append('<term>')

        # integerConstant
        if self.jt.tokenType() == 'INT_CONST':
            self.out.append(self.jt.intVal())

        # stringConstant
        elif self.jt.tokenType() == 'STRING_CONST':
            self.out.append(self.jt.stringVal())
        
        # keywordConstant
        elif self.jt.currentToken in self.jt.keywordConstants:
            self.out.append(self.jt.keyWord())

        # varName | varName '[' expression ']' | subroutineCall
        elif self.jt.tokenType() == 'IDENTIFIER':
            self.out.append(self.jt.identifier())

            # '[' expression ']'
            if self.jt.currentToken == '[':
                self.out.append(self.jt.symbol())
                self.compileExpression()
                self.out.append(self.jt.symbol())

            # subroutineCall
            # '(' expressionList ')' | (className | varName).subroutineName'(' expressionList ')'
            elif self.jt.currentToken == '.' or self.jt.currentToken == '(':
                
                # if it was not a subroutine
                if (self.jt.currentToken == '.'):
                    
                    # .
                    self.out.append(self.jt.symbol())
                    
                    # subroutineName
                    self.out.append(self.jt.identifier())
                
                # '('
                self.out.append(self.jt.symbol())

                # expressionList
                self.compileExpressionList()

                # ')'
                self.out.append(self.jt.symbol())

        # '(' expression ')'
        elif self.jt.currentToken == '(':
            self.out.append(self.jt.symbol())
            self.compileExpression()
            self.out.append(self.jt.symbol())

        # unaryOp term
        elif self.jt.currentToken in self.jt.unaryOperators:
            self.out.append(self.jt.symbol())
            self.compileTerm()

        self.out.append('</term>')

        return

    # Compiles a (possibly empty) comma-separated list of expressions, according to the following grammar:
    # (expression (',' expression)*)?
    def compileExpressionList(self):
        self.out.append('<expressionList>')

        # Are there any expressions?
        if (self.jt.tokenType() == 'IDENTIFIER' or self.jt.tokenType() == 'INT_CONST' or self.jt.tokenType() == 'STRING_CONST' or
            self.jt.currentToken in self.jt.keywordConstants or self.jt.currentToken in self.jt.unaryOperators or self.jt.currentToken == '(' ):
            
            # expression
            self.compileExpression()

            # (',' expression)*
            while self.jt.currentToken == ',':
                
                # ','
                self.out.append(self.jt.symbol())
                
                # 'expression'
                self.compileExpression()
        
        self.out.append('</expressionList>')

        return

    # A small helper to write the following grammar:
    # type varName (used in compileParameterList, compileClassVarDec & compileVarDec)
    def compileTypeVarName(self):
        # type
        if self.jt.tokenType() == 'KEYWORD':
            self.out.append(self.jt.keyWord())
        else:
            self.out.append(self.jt.identifier())

        #varName
        self.out.append(self.jt.identifier())

        return

    # Two small helpers to write the following grammar:
    # (',' type, varName)? (used in compileParameterList)
    def compileAdditionalDeclarationsWithType(self):
        while (self.jt.currentToken == ','):
            self.out.append(self.jt.symbol())
            self.out.append(self.jt.keyWord())
            self.out.append(self.jt.identifier())
        return

    # (',' varName)? (used in compileVarDec & compileClassVarDec)
    def compileAdditionalDeclarations(self):
        while (self.jt.currentToken == ','):
            self.out.append(self.jt.symbol())
            self.out.append(self.jt.identifier())
        return

    # compiles a subroutineCall
    # subroutineName '(' expressionList ')' | (className | varName).subroutineName'(' expressionList ')'
    def compileSubroutineCall(self):
        # subroutineName | className | varName
        self.out.append(self.jt.identifier())

        # if it was not a subroutine
        if (self.jt.currentToken == '.'):
            
            # .
            self.out.append(self.jt.symbol())
            
            # subroutineName
            self.out.append(self.jt.identifier())
        
        # '('
        self.out.append(self.jt.symbol())

        # expressionList
        self.compileExpressionList()

        # ')'
        self.out.append(self.jt.symbol())
        
        return