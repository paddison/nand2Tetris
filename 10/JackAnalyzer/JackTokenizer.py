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
    matchIntegerConstant = r'[0-9]+(?=[^0-9])'
    matchStringConstant = r'\".*\"'
    matchIdentifier = r'[a-zA-Z]\w*(?=\W)'

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
            
            print(self.tokens)