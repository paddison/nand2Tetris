"""
The JackTokenizer module removes all comments and white space from the input stream and 
breaks it into Jack-language tokens, as specified by the Jack grammar.
"""

import re

class JackTokenizer():
    
    # The list containing all the keywords
    keywords = ['class', 'constructor', 'function', 'method',   # subroutines
                'field', 'static', 'var',                       # variable types
                'int', 'char', 'boolean', 'void',               # primitive types  
                'true', 'false', 'null'                         # booleans & null
                'this', 'let', 'do',                            # keywords
                'if', 'else', 'while', 'return']                # program flow control                      

    # The list containing all the symbols
    symbols = ['{', '}', '(', ')', '[', ']', 
              '.', ',', ';', '+', '-', '*', 
              '/', '&', '|', '<', '>', '=', '~']

    # A list containg all binary operators
    operators = ['+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

    # A list containing all unary operators
    unaryOperators = ['-', '~']

    # A list containing all statements
    statements = ['let', 'if', 'while', 'do', 'return']

    # A list containing all keyword constants
    keywordConstants = ['true', 'false', 'null', 'this']

    
    tokenPointer = 0

    # # Regular expressions used for parsing
    matchKeywords = r'(' + r'|'.join(keywords) + r')(?=\W)'
    matchSymbols =  r'' + '\\' + '|\\'.join(symbols)
    matchIntegerConstant = r'[0-9]+((?=[^0-9])|$)'
    matchStringConstant = r'\".*\"'
    matchIdentifier = r'[a-zA-Z]\w*((?=\W)|$)'

    # Opens the input file and tokenizes it
    def __init__(self, fname):
        # Initialize the token list
        self.tokens = []

        # Initialize the pointer for the current token to 0
        self.tokenPointer = 0
        with open(fname) as f:
            # Boolean to help finding multiline comments
            multilineComment = False

            for line in f:

                # Check if this line is part of a multiline comment
                if multilineComment:
                    if line.find('*/') != -1:
                        multilineComment = False
                    continue

                # remove whitespace
                line = line.lstrip()

                # Filter for inline comments
                if line.startswith('//'):
                    continue
                line = line[:line.find('//')]

                # Filter multiline comments
                if line.startswith('/**'):
                    if (line.find('*/') != -1):
                        continue
                    else:
                        multilineComment = True
                        continue
                
                # Match tokens against re
                matches = re.finditer(self.matchKeywords + '|' 
                                          + self.matchIntegerConstant + '|' 
                                          + self.matchIdentifier + '|' 
                                          + self.matchStringConstant + '|'
                                          + self.matchSymbols, line)
                
                for m in matches:
                    self.tokens.append(m.group(0))
                
        # Set the first token to the current token
        self.currentToken = self.tokens[self.tokenPointer]

    # Do we have more tokens in the input?
    def hasMoreTokens(self):
        return self.tokenPointer < len(self.tokens)

    # Get the next token from the input and makes it the current token
    def advance(self):
        self.tokenPointer += 1
        if (self.hasMoreTokens()):  
            self.currentToken = self.tokens[self.tokenPointer]
        return

    # Returns the type of the current token
    def tokenType(self):
        if self.currentToken in self.keywords:
            return 'KEYWORD'
        elif self.currentToken in self.symbols:
            return 'SYMBOL'
        elif re.match(self.matchIdentifier, self.currentToken):
            return 'IDENTIFIER'
        elif re.match(self.matchIntegerConstant, self.currentToken):
            return 'INT_CONST'
        elif re.match(self.matchStringConstant, self.currentToken):
            return 'STRING_CONST'
        else:
            return 'INVALID TOKEN'
    
    # Returns the keyword which is the current token, and advances the input. 
    # Should be called only when tokenType() is KEYWORD.
    def keyWord(self):
        cur = self.currentToken
        self.advance()
        return cur.upper()

    # Returns the character which is the current token, and advances the input.
    # Should be called only when tokenType() is SYMBOL.
    def symbol(self):

        cur = self.currentToken
        self.advance()
        return cur
    
    # Returns the identifier which is the current token, and advances the input. 
    # Should be called only when tokenType() is IDENTIFIER.
    def identifier(self):
        cur = self.currentToken
        self.advance()
        return cur

    # Returns the integer value of the current token, and advances the input. 
    # Should be called only when tokenType() is INT_CONST.
    def intVal(self):
        cur = self.currentToken
        self.advance()
        return int(cur)

    # Returns the string value ofthe current token, without the double quotes, and advances the input.
    # Should be called only when tokenType() is STRING_CONST.
    def stringVal(self):
        cur = self.currentToken[1:-1]
        self.advance()
        return cur

