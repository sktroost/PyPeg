from utils import runpattern
from parser import parse, relabel
from stackentry import ChoicePoint, ReturnAddress
from stack import Stack, CaptureStack, CaptureList
from captures import Capture
from sys import argv
from flags import Flags

from rpython.rlib import jit


def get_printable_location(pc, prev_pc, fail, instructionlist):
    instr = instructionlist[pc].name
    return "%s (%s)" % (pc, prev_pc) + " " + instr + " FAIL" * fail

driver = jit.JitDriver(reds=["index", "inputstring",
                             "choice_points", "captures"],
                       greens=["pc", "prev_pc", "fail", "instructionlist"],
                       get_printable_location=get_printable_location,
                       is_recursive=True)


class VMOutput():
    def __init__(self, captures, fail, index):
        self.captures = captures
        self.fail = fail
        self.index = index


def runbypattern(pattern, inputstring, index=0, flags=Flags()):
    bytecodestring = runpattern(pattern)
    instructionlist = parse(bytecodestring)
    instructionlist = relabel(instructionlist)
    return run(instructionlist, inputstring, index, flags)


def run(instructionlist, inputstring, index=0, flags=Flags()):
    fail = False
    pc = 0
    prev_pc = 0
    choice_points = None
    captures = CaptureStack()
    #captures = CaptureList()
    #captures_index = captures
    while True:
        driver.jit_merge_point(instructionlist=instructionlist,
                               inputstring=inputstring,
                               index=index,
                               fail=fail,
                               pc=pc,
                               prev_pc=prev_pc,
                               choice_points=choice_points,
                               captures=captures)
        if flags.debug:
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
            if choice_points:  # if choice_points seems to fail
                entry = choice_points  # .pop()
                choice_points = choice_points.prev
                while type(entry) is ReturnAddress:
                    if not choice_points:
                        if flags.debug:
                            print("Choicepointlist empty")
                        return VMOutput(captures, True, index)
                    entry = choice_points
                    choice_points = choice_points.prev
                if type(entry) is ChoicePoint:
                    pc = jit.promote(entry.pc)
                    index = entry.index
                    #captures = entry.captures
                    #if captures is not entry.capturelength:  # capturelist
                    if captures.index != entry.capturelength:
                        #assert isinstance(captures, CaptureList)
                        #assert isinstance(entry.capturelength, CaptureList)
                        #captures = entry.capturelength  # List
                        captures.index = entry.capturelength
                    if flags.debug:
                        print("ChoicePoint Restored!"+str(pc))
                else:
                    raise Exception("Unexpected Entry in choice_points! "
                                    + str(entry))
            else:
                return VMOutput(captures, True, index)
        if not isinstance(pc, int):
            raise Exception("pc is of type "+str(type(pc))
                            + "with value "+str(pc))
        instruction = instructionlist[jit.promote(pc)]
        if flags.debug:
            print instruction
        if instruction.name == "char":
            if flags.optimize_chars:
                n = look_for_chars(instructionlist, pc)
                if index + n <= len(inputstring):
                    if flags.debug:
                        print("advanced char handling engaged")
                    if (n > 1 and
                        match_many_chars(instructionlist, pc, n,
                                         inputstring, index)):
                        pc += n
                        index += n
                        continue
                    else:  # optimized fail case. no need to advance chars
                        fail = True
                        continue
            if index >= len(inputstring):
                fail = True
            elif instruction.character == inputstring[index]:
                pc += 1
                index += 1
            else:
                fail = True
        elif instruction.name == "end":
            if index < len(inputstring):
                if flags.debug:
                    print("Not all Input consumed at End Bytecode")
                return VMOutput(captures, False, index)
            if not fail:
                return VMOutput(captures, False, index)
            else:
                if flags.debug:
                    print("Failed End Bytecode")
                return VMOutput(captures, True, index)
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
                #index += 1
                #testany DOES consume input
                #bug in bytecode for pattern
                #'lpeg.P{ lpeg.C(lpeg.R("09")^1) + 1 * lpeg.V(1)}^0'
                #(because if testany didnt consume input, lpeg.P(-2) code
                #would not make any sense
        elif instruction.name == "fail":
            fail = True
        elif instruction.name == "failtwice":
            fail = True
            top = choice_points
            assert top is not None
            choice_points = choice_points.prev
            #assert isinstance(top, ReturnAddress)
            #assert isinstance(choice_points.pop(), ReturnAddress)
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
        elif instruction.name == "behind":
            pc += 1
            #pass  # todo:make this make sense
        elif instruction.name == "choice":
            pc += 1
            choice_points = ChoicePoint(instruction.goto, index,
                                        captures.index, choice_points)
            #capturestack, fuer list .index entfernen
        elif instruction.name == "commit":
            # commits pop values from the stack
            pc = instruction.goto
            assert choice_points is not None
            choice_points = choice_points.prev
        elif instruction.name == "partial_commit":
            # partial commits modify the stack
            top = choice_points
            assert isinstance(top, ChoicePoint)
            top.index = index
            #top.capturelength = captures  # capturelist
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
            prev_pc = pc
            currentlabel = pc
            choice_points = ReturnAddress(currentlabel+1, choice_points)
            pc = instruction.goto
        elif instruction.name == "ret":
            stacktop = choice_points
            assert choice_points is not None
            choice_points = choice_points.prev
            #stacktop = choice_points.pop(#)
            #assert isinstance(stacktop, ReturnAddress)  # sanity check
            pc = stacktop.pc
        elif instruction.name == "jmp":
            pc = instruction.goto
        elif instruction.name == "fullcapture":
            if instruction.capturetype == "simple":
                #captures.append(("full", "simple", instruction.size, index))
                captures.append(Capture.FULLSTATUS, Capture.SIMPLEKIND,
                                instruction.size, index)
                #assert isinstance(captures, CaptureList)
                #captures = CaptureList(Capture.FULLSTATUS,
                                       #Capture.SIMPLEKIND, instruction.size,
                                       #index, captures)  # capturelist
                #captures_index = captures
            elif instruction.capturetype == "position":
                #captures.append(("full", "position", index))
                captures.append(Capture.FULLSTATUS,
                                Capture.POSITIONKIND, -1, index=index)
                #assert isinstance(captures, CaptureList)
                #captures = CaptureList(Capture.FULLSTATUS,
                                       #Capture.POSITIONKIND,-1,
                                       #index, captures)  # capturelist
                #captures_index = captures
            else:
                raise Exception("Unknown capture type!"
                                + instruction.capturetype)
            pc += 1
        elif instruction.name == "opencapture":
            if instruction.capturetype == "simple":
                #captures.append(("open", "simple", 0, index))
                captures.append(Capture.OPENSTATUS,
                                Capture.SIMPLEKIND, -1, index)
                #assert isinstance(captures, CaptureList)
                #captures = CaptureList(Capture.OPENSTATUS,
                                       #Capture.SIMPLEKIND, -1,
                                       #index, captures)  # capturelist
                #captures_index = captures
            else:
                raise Exception("Unknown capture type!"
                                + instruction.capturetype)
            pc += 1
        elif instruction.name == "closecapture":
            capture = captures.storage[captures.index-1]  # STACK
            #for list remove above line and call capture>s<.stack, etc. below
            #capture = captures.capture  # capturelist
            #previously captures_index
            assert capture is not Capture()  # previously none
            assert capture.status == Capture.OPENSTATUS
            if capture.kind == Capture.SIMPLEKIND:
                size = index - capture.index
                capture.size = size
                capture.index = index
                capture.status = Capture.FULLSTATUS
            else:
                raise Exception("Unknown capture type! "+str(capture.kind))
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


def spanloop(inputstring, index, instruction):  # span optimization
    while(index < len(inputstring)
          and instruction.incharlist(inputstring[index])):
        index += 1
        spanloopdriver.jit_merge_point(index=index,
                                       inputstring=inputstring,
                                       instruction=instruction)
    return index


def look_for_chars(instructionlist, pc):
    count = 0
    while pc < len(instructionlist) and instructionlist[pc].name == "char":
        count += 1
        pc += 1
    return count  # at least 1 since my own name is "char"


def match_many_chars(instructionlist, pc, n, inputstring, index):
    ret = True
    for i in range(n):
        if instructionlist[pc+i].character != inputstring[index+i]:
            ret = False
    return ret


def processcaptures(captures, inputstring, flags=Flags()):
    #print captures
    returnlist = []
    if flags.debug:
        print captures
    #for capture in captures:
    while captures.index > 0:  # STACK
    #while captures is not None:  # capturelist
        #print captures.index
        capture = captures.pop()  # STACK
        #for list write capture = captures or access capture>s<.kind etc
        #capture = captures.capture  # capturelist
        if capture.kind == Capture.SIMPLEKIND:
            size = capture.size
            index = capture.index
            newindex = index-size
            assert newindex >= 0
            assert index >= 0
            capturedstring = inputstring[newindex:index]
            returnlist.append(capturedstring)
        elif capture.kind == Capture.POSITIONKIND:
            appendee = "POSITION: "+str(capture.index)
            returnlist.append(appendee)
        #captures = captures.prev  # capturelist
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
    captures = runbypattern(pattern, inputstring).captures
    output = processcaptures(captures, inputstring)
    print output
