"""
The Compilation Engine module
"""

class CompilationEngine:

    out = []

    def __init__(self, tokenizer):
        self.jt = tokenizer
        self.compileClass()

    # Compiles a complete class according to the following grammar:
    # 'class' className '{' classVarDec* subroutineDec* '}'
    def compileClass(self):
        
        # first keyword must be a class
        if self.jt.currentToken != 'class':
            return
        self.out.append('<class>')
        if self.jt.tokenType() != 'KEYWORD':
            return
        self.out.append(self.jt.keyWord())

        # className identifier
        self.jt.advance()
        if self.jt.tokenType() != 'IDENTIFIER':
            return
        self.out.append(self.jt.identifier())

        #'{'
        self.jt.advance()
        if self.jt.tokenType() != 'SYMBOL' and self.jt.currentToken != '}':
            return
        self.out.append(self.jt.symbol())

        # classVarDec*
        self.jt.advance()
        while self.jt.currentToken == 'static' or self.jt.currentToken == 'field':
            self.compileClassVarDec()

        while (self.jt.currentToken == 'constructor' or 
               self.jt.currentToken == 'function' or 
               self.jt.currentToken == 'method'):
               break
               #self.compileSubroutine()
        return



    # Compiles zero or more static or field declarations according to the following grammar:
    # ('static' | 'field') type varName (',' varName)* ';'
    def compileClassVarDec(self):
        self.out.append('<classVarDec>')
        # ('static' | 'field')
        self.out.append(self.jt.keyWord())
        self.jt.advance()
        
        # type
        if (self.jt.tokenType == 'KEYWORD'):
            self.out.append(self.jt.keyWord())
        elif (self.jt.tokenType == 'IDENTIFIER'):
            self.out.append(self.jt.identifier())
        self.jt.advance()

        # varName
        self.out.append(self.jt.identifier())
        self.jt.advance()

        # (',' varName)*
        while self.jt.currentToken == ',':
            self.out.append(self.jt.symbol())
            self.jt.advance()
            self.out.append(self.jt.identifier())
            self.jt.advance()
        
        self.out.append(self.jt.symbol())
        self.jt.advance()
        self.out.append('</classVarDec>')

        return


    # Compiles zero or more subroutines according to the following grammar:
    # ('constructor' | 'function' | 'method')('void' | type) subroutineName '(' parameterList ')' subroutineBody
    def compileSubroutine(self):
        self.out.append('<subroutineDec>')
        self.out.append(self.jt.keyWord())
        return

    def compileParameterList(self):
        pass

    def compileVarDec(self):
        pass

    def compileStatements(self):
        pass

    def compileDo(self):
        pass

    def compileLet(self):
        pass

    def compileWhile(self):
        pass

    def compileReturn(self):
        pass

    def compileIf(self):
        pass

    def compileExpression(self):
        pass

    def compileTerm(self):
        pass

    def compileExpressionList(self):
        pass
