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

    # The token list
    tokens = []

    # # Regular expressions used for parsing
    matchKeywords = r'(' + r'|'.join(keywords) + r')(?=\W)'
    matchSymbols =  r'' + '\\' + '|\\'.join(symbols)
    matchIntegerConstant = r'[0-9]+((?=[^0-9])|$)'
    matchStringConstant = r'\".*\"'
    matchIdentifier = r'[a-zA-Z]\w*((?=\W)|$)'

    # Opens the input file and tokenizes it
    def __init__(self, fname):
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

    # Returns the type of the current token
    def tokentype(self, token):
        if token in self.keywords:
            return 'KEYWORD'
        elif token in self.symbols:
            return 'SYMBOL'
        elif re.match(self.matchIdentifier, token):
            return 'IDENTIFIER'
        elif re.match(self.matchIntegerConstant, token):
            return 'INT_CONST'
        elif re.match(self.matchStringConstant, token):
            return 'STRING_CONST'
        else:
            return 'INVALID TOKEN'
    
    # Returns the keyword which is the current token. 
    # Should be called only when tokenType() is KEYWORD.
    def keyWord(self, token):
        return token.upper()

    # Returns the character which is the current token.
    # Should be called only when tokenType() is SYMBOL.
    def symbol(self, token):
        return token
    
    # Returns the identifier which is the current token. 
    # Should be called only when tokenType() is IDENTIFIER.
    def identifier(self, token):
        return token

    # Returns the integer value of the current token. 
    # Should be called only when tokenType() is INT_CONST.
    def intVal(self, token):
        return int(token)

    # Returns the string value ofthe current token, without the double quotes.
    # Should be called only when tokenType() is STRING_CONST.
    def stringVal(self, token):
        return token[1:-1]

