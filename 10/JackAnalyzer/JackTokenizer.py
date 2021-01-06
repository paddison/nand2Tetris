
class JackTokenizer():
    
    tokens = []

    # Opens the input file and tokenizes it
    def __init__(self, fname):
        with open(fname) as f:
            for line in f:
                # Look for inline comments
                line = line.lstrip('//')
                print(line)