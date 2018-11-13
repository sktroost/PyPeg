#usage: call from commandline python lua_to_instr.py myluafile.lua.
#only works with lua files that only output bytecode
#(no other printlines allowed)
from subprocess import check_output
from sys import argv
from os import chdir
from instruction import Instruction
from utils import runlpeg


def charrange(a, b):
    ret = []
    for i in range(ord(a), ord(b) + 1):
        ret.append(chr(i))
    return ret


def line_to_instruction(line):
    labelsplit = line.split(":")
    label = int(labelsplit[0])
    line = labelsplit[1]
    goto = charlist = idx = size = character = None
    if "->" in line:  # assuming format of "stuff -> int"
        gotosplit = line.split("->")
        goto = int(gotosplit[1])
        line = gotosplit[0]
    if "[" in line and "]" in line:
        #assuming format similar to "labelname [(stuff)(stuff)]"
        cut1 = line.find("[")
        cut2 = line.find("]") + 1
        bracketline = line[cut1:cut2]
        line = line[:cut1] + line[cut2:]
        bracketsplit = bracketline.split(")(")
        charlist = []
        for element in bracketsplit:
            element = (
                element.replace("(", "")
                .replace(")", "")
                .replace("[", "")
                .replace("]", "")
            )
            if "-" in element:  # describes a range of values
                sublist = []
                rangevalues = element.split("-")
                range1 = int("0x"+rangevalues[0], 16)
                range2 = int("0x"+rangevalues[1], 16)
                for i in range(range1, range2 + 1):
                    sublist.append(chr(i))
                charlist.append(sublist)
            else:
                charlist.append(chr(int("0x" + element, 16)))
    if "(" in line:  # assuming format simillar to
        #"labelname (something = int) (somethingelse = int)"
        parensplit = line.split("(")
        line = parensplit[0]
        for element in parensplit:
            number = ""
            for x in element:
                if x.isdigit():
                    number += x
            if "idx" in element:
                idx = int(number)
            elif "size" in element:
                size = int(number)
            elif ")" in element:
                raise Exception("Unexpected bytecode parameter: " + element)

    if "\'" in line:  # assuming format of "labelname 'character'"
        character = line[line.find("\'") + 1]
        line = line.replace("\'"+character+"\'", "")
    name = line
    while name[-1] == " ":
        name = name[:-1]
    while name[0] == " ":
        name = name[1:]
    #didnt use strip() method because some bytecodes
    #have spaces in the middle of them
    return Instruction(name, label, goto, charlist, idx, size, character)


def parse(lines):
    lines = lines.splitlines()
    instructionlist = []
    for line in lines:
        if line.strip():  # if line is not empty
            instruction = line_to_instruction(line)
            instructionlist.append(instruction) 
    return instructionlist


def relabel(instructionlist):
    labeldict = {}
    for i in range(len(instructionlist)):
        #1st loop sets up the dictionary
        currentlabel = instructionlist[i].label
        if currentlabel in labeldict.keys():
            raise Exception("Multiple Bytecodes with Label "
                            + str(currentlabel))
        labeldict[currentlabel] = i
    for instruction in instructionlist:
        #2nd loop relabels the instructions
        currentlabel = instruction.label
        instruction.label = labeldict[currentlabel]
        if instruction.goto is not None:
            currentgoto = instruction.goto
            instruction.goto = labeldict[currentgoto]
    return instructionlist


if __name__ == "__main__":
    bytecodestring = runlpeg(argv[1])
    instructionlist = parse(bytecodestring)
    instructionlist = relabel(instructionlist)
    for instruction in instructionlist:
        print(instruction)
