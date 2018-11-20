from utils import runpattern
from parser import parse, relabel


def run(pattern, inputstring, debug=False):
    bytecodestring = runpattern(pattern)
    instructionlist = parse(bytecodestring)
    instructionlist = relabel(instructionlist)
    #The state of the VM is realized by 4 values p, i, e and c.
    #Their definitions are found in the paper.
    PC = 0  # probably the index of the instructionlist (program counter)
    index = 0  # probably the index of the inputstring (index)
    e = []  # TODO: find out what that is
    c = "something"  # TODO: find out what that is
    while True:  # Iterating over every instruction once is impractical
        if debug:
            print("-"*10)
            print("Program Counter: "+str(p))
            print("Index: "+str(i))
            print("Backstrackstack: "+str(e))
            if PC != "FAIL":
                print("Instruction: "+str(instructionlist[PC]))
        if PC == "FAIL":  # NOTE: THIS BREAKS AFTER NON TUPLE OBJECTS GO
        #ON THE STACK. SEE PAPER, PAGE 15, FAIL CASE BEHAVIOR ("any")
            if len(e):  # if backtrackstack isnt empty (i love that word)
                ret = e.pop()
                PC = ret[0]
                index = ret[1]
                c = ret[2]
            else:
                return None
        if PC != "FAIL":
            instruction = instructionlist[PC]
        if instruction.name == "char":
            if index >= len(inputstring):
                PC = "FAIL"
            elif instruction.character == inputstring[index]:
                PC += 1
                index += 1
            else:
                PC = "FAIL"
        elif instruction.name == "end":
            if index < len(inputstring):  # not all input consumed
                return None
            elif PC != "FAIL":
                return True
            else:
                return None
        elif instruction.name == "testchar":
            if index >= len(inputstring):
                PC = instruction.goto
            elif instruction.character == inputstring[index]:
                PC += 1
                #i += 1  # is paper page 21 wrong?
            else:
                PC = instruction.goto
        elif instruction.name == "testset":
            if index >= len(inputstring):
                PC = instruction.goto
            elif inputstring[index] in instruction.charlist:
                PC += 1
            else:
                PC = instruction.goto
        elif instruction.name == "any":  # assuming this is any with n=1
            if index >= len(inputstring):
                PC = "FAIL"
            else:
                PC += 1
                index += 1  # since n=1
        elif instruction.name == "choice":
            PC += 1
            e.append((instruction.goto, index, c))
        elif instruction.name == "commit":
            # commits pop values from the stack
            PC = instruction.goto
            e.pop()
        elif instruction.name == "partial_commit":
            # partial commits modify the stack
            PC = instruction.goto
            tripel = e.pop()
            e.append((tripel[0], index, c))  # see paper, p.16
        elif instruction.name == "set":
            if index >= len(inputstring):
                PC = "FAIL"
            elif inputstring[index] in instruction.charlist:
                PC += 1
                index += 1
            else:
                PC = "FAIL"
        else:
            raise Exception("Unknown instruction! "+instruction.name)
