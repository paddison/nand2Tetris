def classDeclarationError(line):
    """
    Throws error if class declaration is missing.
    """
    print('Missing or invalid \'class\' statement or className in line ' + str(line))
    exit()

def missingBracketError(line):
    """
    Throws error if '{', '}', '(', or ')' ']' brackets are missing. 
    """
    print('Missing \'{\', \'}\', \'(\', or \')\' \']\' bracket in line ' + str(line))
    exit()

def missingTerminationError(line):
    """
    Throws error if ';' is missing at end of statement or declaration.
    """
    print('Missing \';\' at line ' + str(line))
    exit()

def wrongClassVarDeclaration(line):
    """
    Throws error if classVars are declared not directly after class definition.
    """
    print('Detected wrong static of field variable declaration in line ' + str(line)) 
    exit()

def invalidVarTypeError(varType, line):
    """
    Throws an error if using a invalid varType (like 'null' or 'INT_CONST' etc.).
    """
    print('Detected invalid variable type \'' + varType + '\' in line ' + str(line))
    exit()

def invalidVarKindError(varKind, segment, line):
    """
    Throws an error if trying to declare a class Variable in local space or vice versa.
    """
    print('Trying to declare ' + varKind + ' variable in ' + segment + ' in line ' + str(line))
    exit()

def variableNotFoundError(varName, line):
    """
    Throws an error if a variable is not found.
    """
    print('Cannot find variable ' + varName + ' in line ' + str(line))
    exit()

def missingEqualsError(line):
    """
    Throws an error if the = sign is missing in a let assignemt.
    """
    print('Missing \'=\' in \'let\' statement in line ' + str(line))
    exit()

def wrongFunctionContext(line):
    """
    Throws an error if trying to use the this keyword outside of a method or constructor.
    """
    print('Trying to use this in function type subroutine in line ' + str(line))
    exit()

def missingParameterList(line):
    """
    Throws an error if the parameter list is missing in a subroutine call
    """
    print('Missing parameters for subroutine call in line ' + str(line))
    exit()