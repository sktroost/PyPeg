from utils import runpattern
from parser import parse, relabel
def run(pattern, inputstring):
    
    bytecodestring = runpattern(pattern)
    instructionlist = parse(bytecodestring)
    instructionlist = relabel(instructionlist)
    #The state of the VM is realized by 4 values p, i, e and c.
    #Their definitions are found in the paper.
    p = 0  # probably the index of the instructionlist (program counter)
    i = 0  # probably the index of the inputstring (index)
    e = []  # TODO: find out what that is
    c = "something"  # TODO: find out what that is
    while True:  # Iterating over every instruction once is impractical
        #if p == "FAIL":  # todo: pretend python is statically typed
            #return None  # TODO: backtracking instead of returning false
        if p == "FAIL":  # NOTE: THIS BREAKS AFTER NON TUPLE OBJECTS GO
        #ON THE STACK. SEE PAPER, PAGE 15, FAIL CASE BEHAVIOR ("any")
            if len(e):  # if backtrackstack isnt empty (i love that word)
                ret = e.pop()
                p = ret[0]
                i = ret[1]
                c = ret[2]
            else:
                return None
        if p != "FAIL":
            instruction = instructionlist[p]
        if instruction.name == "char":
            if i >= len(inputstring):
                p = "FAIL"
            elif instruction.character == inputstring[i]:
                p += 1
                i+= 1
            else:
                p = "FAIL"
        elif instruction.name == "end":
            if p != "FAIL":
                return True  # currently only outputs that we matched, not where
            else:
                return None
        elif instruction.name == "testchar":
            if i >= len(inputstring):
                p = "FAIL"
            elif instruction.character == inputstring[i]:
                p += 1
                #NO i += 1 because input isnt consumed
            else:
                p = instruction.goto
        elif instruction.name == "any":  # assuming this is any with n=1
            if i >= len(inputstring):
                p = "FAIL"
            else:
                p += 1
                i += 1  # since n=1
        elif instruction.name == "choice":
            p += 1
            e.append((instruction.goto,i,c))
        elif instruction.name == "commit":
            p = instruction.goto
            e.pop()
        elif instruction.name == "set":
            if i >= len(inputstring):
                p = "FAIL"
            elif inputstring[i] in instruction.charlist:
                p += 1
                i += 1
            else:
                p = "FAIL"
        else:
            raise Exception("Unknown instruction! "+instruction.name)
