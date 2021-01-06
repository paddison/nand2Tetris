
class JackTokenizer():
    
    

    # Opens the input file and tokenizes it
    def __init__(self, fname):
        tokens = []
        with open(fname) as f:
            multilineComment = False
            
            # No for loop because it's easier to remove multiline comments that way
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
                
                # Split the line into single words
                words = line.split(" ")

                # A boolean to help with parsing string constants
                stringConstant = False
                for word in words:
                    if word == 'class':
                        tokens.append(word)
                    word = word.lstrip()
                    print(word)
                
                # print(line,"")