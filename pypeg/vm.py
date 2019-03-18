from utils import runpattern
from parser import parse, relabel
from stackentry import ChoicePoint, Bottom
from naive_stack import NaiveBottom
from stack import new_capturelist
from captures import Capture, SimpleCapture, PositionCapture, AbstractCapture
from sys import argv
from flags import Flags
from os import environ
from rpython.rlib import rstring

from rpython.rlib import jit

IS_SIMPLE = True


def get_printable_location(pc, prev_pc, fail, instructionlist, flags):
    instr = instructionlist[pc].name
    return "%s (%s)" % (pc, prev_pc) + " " + instr + " FAIL" * fail


driver = jit.JitDriver(reds=["index", "inputstring",
                             "choice_points", "captures"],
                       greens=["pc", "prev_pc", "fail", "instructionlist",
                               "flags"],
                       get_printable_location=get_printable_location,
                       is_recursive=True)
if 0:
    jitoptions = environ.get("jitoptions", None)
    if jitoptions:
        jit.set_user_param(driver, jitoptions)


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
    if flags.optimize_choicepoints:
        choice_points = Bottom()
    else:
        choice_points = NaiveBottom()
    if flags.debug:
        from time import sleep
    captures = new_capturelist()
    while True:
        instruction = instructionlist[jit.promote(pc)]
        if instruction.isjumptarget and flags.jumptargets:
            driver.can_enter_jit(instructionlist=instructionlist,
                                 inputstring=inputstring,
                                 index=index,
                                 fail=fail,
                                 pc=pc,
                                 prev_pc=prev_pc,
                                 choice_points=choice_points,
                                 captures=captures,
                                 flags=flags)
        driver.jit_merge_point(instructionlist=instructionlist,
                               inputstring=inputstring,
                               index=index,
                               fail=fail,
                               pc=pc,
                               prev_pc=prev_pc,
                               choice_points=choice_points,
                               captures=captures,
                               flags=flags)
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
            if choice_points:
                try:
                    entry, choice_points = choice_points.find_choice_point()
                except AttributeError:
                    import pdb; pdb.set_trace()
                if entry is None:
                    if flags.debug:
                        print("Choicepointlist empty")
                    return VMOutput(captures, True, index)
                pc = jit.promote(entry.get_pc())
                index = entry.index
                if captures is not entry.captures:
                    print("RESTORING CAPTURES FROM "+captures)
                    print("TO "+entry.captures)
                    assert isinstance(captures, AbstractCapture)
                    #TODO: TEST THAT BRANCHES INTO THIS CODE
                    assert isinstance(entry.captures,
                                      AbstractCapture)
                    captures = entry.captures  # List
                if flags.debug:
                    print("ChoicePoint Restored!"+str(pc))

            else:
                return VMOutput(captures, True, index)
        if not isinstance(pc, int):
            raise Exception("pc is of type "+str(type(pc))
                            + "with value "+str(pc))
        instruction = instructionlist[jit.promote(pc)]
        if flags.debug:
            print instruction
        if instruction.name == "char":
            if flags.optimize_char:
                n = look_for_chars(instructionlist, pc)
                if index + n <= len(inputstring):
                    if flags.debug:
                        print("advanced char handling engaged")
                    if (n > 0 and
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
                continue
            elif flags.optimize_testchar:
                if flags.debug:
                    print("advanced testchar handling engaged")
                if testchar_check_optimize(instructionlist, pc):
                    index = testchar_optimize(inputstring, index,
                                              instruction.character)
                    pc += 1
                    if index == -1:
                        fail = True
                        pc = instruction.goto + 1
                    continue
            if instruction.character == inputstring[index]:
                pc += 1
                #doesnt consume input
            else:
                pc = instruction.goto
        elif instruction.name == "testany":
            if index >= len(inputstring):
                pc = instruction.goto
            else:
                pc += 1
        elif instruction.name == "fail":
            fail = True
        elif instruction.name == "failtwice":
            fail = True
            top = choice_points
            assert top is not None
            choice_points = choice_points.pop()
        elif instruction.name == "testset":
            if index >= len(inputstring):
                pc = instruction.goto
                continue
            elif flags.optimize_testchar:
                if flags.debug:
                    print("advanced testset handling engaged")
                if testchar_check_optimize(instructionlist, pc):
                    index = testset_optimize(inputstring, index,
                                             instruction)
                    pc += 1
                    if index == -1:
                        fail = True
                        pc = instruction.goto + 1
                    continue
            if instruction.incharlist(inputstring[index]):
                pc += 1
            else:
                pc = instruction.goto
        elif instruction.name == "any":
            if index >= len(inputstring):
                fail = True
            else:
                pc += 1
                index += 1
        elif instruction.name == "behind":
            pc += 1  # currently broken.
            assert False
        elif instruction.name == "choice":
            pc += 1
            choice_points = choice_points.push_choice_point(
                instruction.goto, index, captures)
        elif instruction.name == "commit":
            # commits pop values from the stack
            pc = instruction.goto
            assert choice_points is not None
            choice_points = choice_points.pop()
        elif instruction.name == "partial_commit":
            # partial commits modify the stack
            top = choice_points
            #assert isinstance(top, ChoicePoint)  # commenting this out might break pypy
            top.mod_choice_point(index, captures)
            #re-set index and captures for current CP
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
            choice_points = choice_points.push_return_address(currentlabel + 1)
            pc = instruction.goto
        elif instruction.name == "ret":
            stacktop = choice_points
            assert choice_points is not None
            pc, choice_points = choice_points.pop_return_address()
        elif instruction.name == "jmp":
            pc = instruction.goto
        elif instruction.name == "fullcapture":
            if instruction.capturetype == "simple":
                assert isinstance(captures, AbstractCapture)  # not none
                captures = new_capturelist(True, SimpleCapture.FULLSTATUS,
                                          instruction.size, index, captures)
            elif instruction.capturetype == "position":
                assert isinstance(captures, AbstractCapture)  # not none
                captures = new_capturelist(not IS_SIMPLE, index=index,
                                          prev=captures)
            else:
                raise Exception("Unknown capture type!"
                                + instruction.capturetype)
            pc += 1
        elif instruction.name == "opencapture":
            if instruction.capturetype == "simple":
                assert isinstance(captures, AbstractCapture)
                captures = new_capturelist(IS_SIMPLE,
                                          SimpleCapture.OPENSTATUS,
                                          0, index, captures)
            else:
                raise Exception("Unknown capture type!"
                                + instruction.capturetype)
            pc += 1
        elif instruction.name == "closecapture":
            assert isinstance(captures, SimpleCapture)
            assert captures.get_status() == SimpleCapture.OPENSTATUS
            size = index - captures.index
            captures.set_size(size)
            captures.index = index
            captures.set_status_full()
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


@jit.elidable
def look_for_chars(instructionlist, pc):
    count = 0
    while pc < len(instructionlist) and instructionlist[pc].name == "char":
        count += 1
        pc += 1
    return count  # at least 1 since my own name is "char"


@jit.unroll_safe
def match_many_chars(instructionlist, pc, n, inputstring, index):
    ret = True
    for i in range(n):
        if instructionlist[pc+i].character != inputstring[index+i]:
            ret = False
    return ret


@jit.elidable
def testchar_check_optimize(instructionlist, pc):
    myself = instructionlist[pc]
    if instructionlist[myself.goto].name == "any":
        nextnextinstr = instructionlist[myself.goto+1]
        if (nextnextinstr.name == "jmp"
           and nextnextinstr.goto == myself.label):
            return True
    return False


def get_printable_location3(instruction):
    return "TESTSET" + str(instruction.charlist)

testsetdriver = jit.JitDriver(reds=["index", "inputstring"],
                              greens=["instruction"],
                              get_printable_location=
                              get_printable_location3)


def testset_optimize(inputstring, index, instruction):
    assert index >= 0
    while index < len(inputstring):
        if instruction.incharlist(inputstring[index]):
            return index
        index += 1
        testsetdriver.jit_merge_point(index=index,
                                      inputstring=inputstring,
                                      instruction=instruction)
    return -1


def testchar_optimize(inputstring, index, char):
    assert index >= 0
    return inputstring.find(char, index)


def processcaptures(captures, inputstring, flags=Flags()):
    #returnlist = []
    out = rstring.StringBuilder()
    if flags.debug:
        print captures
    while captures.prev is not None:
        if isinstance(captures, SimpleCapture):
            size = captures.get_size()
            index = captures.index
            newindex = index-size
            assert newindex >= 0
            assert index >= 0
            out.append_slice(inputstring, newindex, index)
            out.append("\n")
        elif isinstance(captures, PositionCapture):
            appendee = "POSITION:"+str(captures.index)
            out.append(appendee + "\n")
        captures = captures.prev  # capturelist
    return out.build()  # returnlist


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
