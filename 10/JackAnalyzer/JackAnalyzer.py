"""
The analyzer program operates on a given  source, 
where source is either a file name of the form Xxx.jack 
or a directory name containing one or more such files. 
For each source Xxx.jack file, the analyzer goes through the logic
as described below
"""

import JackTokenizer
# Create a tokenizer from the Xxx.jack input file
jt = JackTokenizer.JackTokenizer("/home/padder/Documents/nand2tetris/projects/10/ArrayTest/Main.jack")