"""
The analyzer program operates on a given  source, 
where source is either a file name of the form Xxx.jack 
or a directory name containing one or more such files. 
For each source Xxx.jack file, the analyzer goes through the logic
as described below
"""

import JackTokenizer
import CompilationEngine
import sys
import os

if len(sys.argv) != 2:
    print('Usage: python3 JackAnalyzer.py file/directory.')
    exit()

path = sys.argv[1]
files = []
# A single file as input
if (path[-5:] == '.jack'):
    f = path.rsplit('/', 1)[1]
    files.append(f)
    path = path.rsplit('/', 1)[0] + '/'

# Parse whole directory
else:
    if not path.endswith('/'):
        path += '/'
    directory = os.listdir(path)
    
    # Get all .jack files
    for f in directory:
        if f[-5:] == '.jack':
            files.append(f)

    # If no files were found, print an error
    if len(files) == 0:
        print('ERROR: No *jack files found in directory.')
        exit()

for f in files:
    print('Parsing: ' + f)
    # Create a tokenizer from the current Xxx.jack input file
    jt = JackTokenizer.JackTokenizer(path + f)

    # Create the output with the compilation engine
    ce = CompilationEngine.CompilationEngine(jt, path + f[:-5])

    # open a new file from path and filename (without .jack ending)
    out = open(path + f[:-5] + '_out' + '.xml', 'w')
    
    # Write the xml file and take care of indentation
    xmlSpace = ""
    for line in ce.out:
        if line.find('</') == 0:
            xmlSpace = xmlSpace[:-2]
        
        # Write to the output file
        out.write(xmlSpace + line + '\n')
        if not line.startswith('</') and line.find('</') == - 1:
            xmlSpace = xmlSpace + "  "
    
    out.close()

print('\nComplete.')
print('Goodbye!')