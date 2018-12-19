from utils import runpattern
from parser import parse, relabel
from stackentry import ChoicePoint, ReturnAddress
from stack import Stack
from captures import Capture
from sys import argv

from rpython.rlib import jit


def get_printable_location(pc, fail, instructionlist):
    instr = instructionlist[pc].name
    return str(pc) + " " + instr

driver = jit.JitDriver(reds=["index", "inputstring",
                             "choice_points", "captures"],
                       greens=["pc", "fail", "instructionlist"],
                       get_printable_location=get_printable_location,
                       is_recursive=True)


class VMOutput():
    def __init__(self, captures, fail):
        self.captures = captures
        self.fail = fail


def runbypattern(pattern, inputstring, index=0, debug=False):
    bytecodestring = runpattern(pattern)
    instructionlist = parse(bytecodestring)
    instructionlist = relabel(instructionlist)
    return run(instructionlist, inputstring, index, debug)


def run(instructionlist, inputstring, index=0, debug=False):
    fail = False
    pc = 0
    choice_points = []
    captures = Stack()
    while True:
        driver.jit_merge_point(instructionlist=instructionlist,
                               inputstring=inputstring,
                               index=index,
                               fail=fail,
                               pc=pc,
                               choice_points=choice_points,
                               captures=captures)
        if debug:
            print("-"*10)
            print("Program Counter: "+str(pc))
            print("Index: "+str(index))
            print("Choicepoints "+str(choice_points))
            print("Instruction: "+str(instructionlist[pc]))
            print("Captures: "+str(captures))
            if fail:
                print "FAIL"
        if fail:
            fail = False
            if choice_points != []:
                entry = choice_points.pop()
                while type(entry) is ReturnAddress:
                    if choice_points == []:
                        if debug:
                            print("Choicepointlist empty")
                        return VMOutput(captures, True)
                    entry = choice_points.pop()  # remove pending calls
                if type(entry) is ChoicePoint:
                    pc = jit.promote(entry.pc)
                    index = entry.index
                    #captures = entry.captures
                    if captures.index != entry.capturelength:
                        captures.index = entry.capturelength  # Stack
                     #   del captures[entry.capturelength:]
                        #captures = captures[:entry.capturelength]
                    if debug:
                        print("ChoicePoint Restored!"+str(pc))
                else:
                    raise Exception("Unexpected Entry in choice_points! "
                                    + str(entry))
            else:
                return VMOutput(captures, True)
        if not isinstance(pc, int):
            raise Exception("pc is of type "+str(type(pc))
                            + "with value "+str(pc))
        instruction = instructionlist[jit.promote(pc)]
        if debug:
            print instruction
        if instruction.name == "char":
            if index >= len(inputstring):
                fail = True
            elif instruction.character == inputstring[index]:
                pc += 1
                index += 1
            else:
                fail = True
        elif instruction.name == "end":
            if index < len(inputstring):
                if debug:
                    print("Not all Input consumed at End Bytecode")
                return VMOutput(captures, True)
            if not fail:
                #TODO: remove all not closed captures
                return VMOutput(captures, False)  # previously return True
            else:
                if debug:
                    print("Failed End Bytecode")
                return VMOutput(captures, True)
        elif instruction.name == "testchar":
            if index >= len(inputstring):
                pc = instruction.goto
            elif instruction.character == inputstring[index]:
                pc += 1
                #doesnt consume input
            else:
                pc = instruction.goto
        elif instruction.name == "testany":
            if index >= len(inputstring):
                pc = instruction.goto
            else:
                pc += 1
                index += 1  # must be the case because of 'lpeg.P(-1)'
        elif instruction.name == "fail":
            fail = True
        elif instruction.name == "failtwice":
            fail = True
            assert isinstance(choice_points.pop(), ReturnAddress)
        elif instruction.name == "testset":
            if index >= len(inputstring):
                pc = instruction.goto
            elif instruction.incharlist(inputstring[index]):
                pc += 1
            else:
                pc = instruction.goto
        elif instruction.name == "any":  # assuming any with n=1 (see paper)
            if index >= len(inputstring):
                fail = True
            else:
                pc += 1
                index += 1  # since n=1
        elif "behind" in instruction.name:
            pc += 1
            #pass  # todo:make this make sense
        elif instruction.name == "choice":
            pc += 1
            choicepoint = ChoicePoint(instruction.goto, index, captures.index)
            choice_points.append(choicepoint)
        elif instruction.name == "commit":
            # commits pop values from the stack
            pc = instruction.goto
            choice_points.pop()
        elif instruction.name == "partial_commit":
            # partial commits modify the stack
            top = choice_points[-1]
            top.index = index
            top.capturelength = captures.index
            pc = instruction.goto
        elif instruction.name == "set":
            if index >= len(inputstring):
                fail = True
            elif instruction.incharlist(inputstring[index]):
                pc += 1
                index += 1
            else:
                fail = True
        elif instruction.name == "span":  # can't fail
            index = spanloop(inputstring, index, instruction)
            pc += 1
        elif instruction.name == "call":
            currentlabel = pc
            returnaddress = ReturnAddress(currentlabel+1)
            choice_points.append(returnaddress)
            pc = instruction.goto
        elif instruction.name == "ret":
            stacktop = choice_points.pop()
            #assert isinstance(stacktop, ReturnAddress)  # sanity check
            pc = stacktop.pc
        elif instruction.name == "jmp":
            pc = instruction.goto
        elif instruction.name == "fullcapture":
            if instruction.capturetype == "simple":
                #captures.append(("full", "simple", instruction.size, index))
                captures.append(Capture("full", "simple",
                                        instruction.size, index))
            elif instruction.capturetype == "position":
                #captures.append(("full", "position", index))
                captures.append(Capture("full", "position", index=index))
            else:
                raise Exception("Unknown capture type!"
                                + instruction.capturetype)
            pc += 1
        elif instruction.name == "opencapture":
            if instruction.capturetype == "simple":
                #captures.append(("open", "simple", 0, index))
                captures.append(Capture("open", "simple", index=index))
            else:
                raise Exception("Unknown capture type!"
                                + instruction.capturetype)
            pc += 1
        elif instruction.name == "closecapture":
            capture = captures.pop()
            assert capture is not None  # makes pypy happy
            #assert capture.status == "open"
            if capture.kind == "simple":
                size = index - capture.index
                captures.append(Capture("full", "simple", size, index))
            else:
                raise Exception("Unknown capture type! "+capture.kind)
            pc += 1
        else:
            raise Exception("Unknown instruction! "+instruction.name)


def search(instructions, s):
    for index in range(len(s)):
        res = run(instructions, s, index)
        if res:
            return index


def get_printable_location2(instruction):
    return "SPAN" + str(instruction.charlist)

spanloopdriver = jit.JitDriver(reds=["index", "inputstring"],
                               greens=["instruction"],
                               get_printable_location=get_printable_location2)


def spanloop(inputstring, index, instruction):
    while(index < len(inputstring)
          and instruction.incharlist(inputstring[index])):
        index += 1
        spanloopdriver.jit_merge_point(index=index,
                                       inputstring=inputstring,
                                       instruction=instruction)
    return index


def processcaptures(captures, inputstring, debug=False):
    returnlist = []
    if debug:
        print captures
    #for capture in captures:
    while captures.index > 0:  # STACK
        #print captures.index
        capture = captures.pop()  # STACK
        if capture.kind == "simple":
            size = capture.size
            index = capture.index
            newindex = index-size
            assert newindex >= 0
            assert index >= 0
            capturedstring = inputstring[newindex:index]
            returnlist.append(capturedstring)
        elif capture.kind == "position":
            app = "POSITION: "+str(capture.index)
            returnlist.append(app)
            # might need to make this pypy compatible (ints and str in list)
    return returnlist


if __name__ == "__main__":
    patternfilename = argv[1]
    inputfilename = argv[2]
    patternfile = open(patternfilename, "r")
    inputfile = open(inputfilename, "r")
    pattern = patternfile.read()
    patternfile.close()
    inputstring = inputfile.read()
    inputfile.close()
    inputstring = inputstring.strip()
    captures = runbypattern(pattern, inputstring)
    output = processcaptures(captures, inputstring)
    print output
