from utils import runpattern
from parser import parse, relabel


def run(pattern, inputstring, debug=False):
    bytecodestring = runpattern(pattern)
    instructionlist = parse(bytecodestring)
    instructionlist = relabel(instructionlist)
    fail = False
    pc = 0
    index = 0
    choice_points = []
    captures = []
    while True:
        if debug:
            print("-"*10)
            print("Program Counter: "+str(pc))
            print("Index: "+str(index))
            print("Backstrackstack: "+str(choice_points))
            print("Instruction: "+str(instructionlist[pc]))
            if fail:
                print "FAIL"
        if fail:  # NOTE: THIS BREAKS AFTER NON TUPLE OBJECTS GO
        #ON THE STACK. SEE PAPER, PAGE 15, FAIL CASE BEHAVIOR ("any")
            fail = False
            if len(choice_points):
                value = choice_points.pop()
                if type(value) == type(5):  # if int
                    index = value
                else:  # type touple
                    pc, index, c = value
            else:
                return None
        instruction = instructionlist[pc]
        if instruction.name == "char":
            if index >= len(inputstring):
                fail = True
            elif instruction.character == inputstring[index]:
                pc += 1
                index += 1
            else:
                fail = True
        elif instruction.name == "end":
            if index < len(inputstring):  # not all input consumed
                return None
            elif not fail:
                return True
            else:
                return None
        elif instruction.name == "testchar":
            if index >= len(inputstring):
                pc = instruction.goto
            elif instruction.character == inputstring[index]:
                pc += 1
                #i += 1  # is paper page 21 wrong?
            else:
                pc = instruction.goto
        elif instruction.name == "testset":
            if index >= len(inputstring):
                pc = instruction.goto
            elif inputstring[index] in instruction.charlist:
                pc += 1
            else:
                pc = instruction.goto
        elif instruction.name == "any":  # assuming this is any with n=1
            if index >= len(inputstring):
                fail = True
            else:
                pc += 1
                index += 1  # since n=1
        elif instruction.name == "choice":
            pc += 1
            choice_points.append((instruction.goto, index, c))
        elif instruction.name == "commit":
            # commits pop values from the stack
            pc = instruction.goto
            choice_points.pop()
        elif instruction.name == "partial_commit":
            # partial commits modify the stack
            pc = instruction.goto
            tripel = choice_points.pop()
            choice_points.append((tripel[0], index, c))  # see paper, p.16
        elif instruction.name == "set":
            if index >= len(inputstring):
                fail = True
            elif inputstring[index] in instruction.charlist:
                pc += 1
                index += 1
            else:
                fail = True
        elif instruction.name == "span":  # can't fail
            while (index < len(inputstring)
                   and inputstring[index] in instruction.charlist):
                index += 1
            pc += 1
        elif instruction.name == "call":
            currentlabel = pc
            choice_points.append(currentlabel+1)
            pc = instruction.goto
        elif instruction.name == "ret":
            pc = choice_points.pop()
        elif instruction.name == "jmp":
            pc = instruction.goto
        else:
            raise Exception("Unknown instruction! "+instruction.name)
