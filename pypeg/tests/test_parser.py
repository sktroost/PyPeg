from pypeg.parser import parse, relabel
from pypeg.utils import charrange
from pypeg.instruction import Instruction
from pypeg.charlistelement import SingleChar, CharRange


def test_char():
    input = "44: char '2b'"
    instr, = parse(input)
    assert instr.label == 44
    assert instr.character == "+"
    assert instr.name == "char"


def test_behind():
    input = "00: behind 2"
    instr, = parse(input)
    assert instr.label == 0
    assert instr.name == "behind"
    assert instr.behindvalue == 2


def test_span():
    input = "21: span [(30-39)]"
    instr, = parse(input)
    assert instr.label == 21
    assert instr.name == "span"
    assert instr.charlist == [CharRange("0","9")]

def test_set():
    input = "27: set [(30)(33)(35)]"
    instr, = parse(input)
    assert instr.label == 27
    assert instr.name == "set"
    assert instr.charlist == [
    SingleChar("0"),
    SingleChar("3"),
    SingleChar("5")]


def test_opencapture():
    input = "00: opencapture simple (idx = 0)"
    instr, = parse(input)
    assert instr.label == 0
    assert instr.name == "opencapture"
    assert instr.capturetype == "simple"
    assert instr.idx == 0


def test_relabel():
    input = "01: char '2f'\n13: span [(30-39)]\n37: testcode [(1)(3)(39)] -> 13"
    instructionlist = parse(input)
    output = relabel(instructionlist)
    assert output[0] == Instruction(label=0, name="char", character="/")
    assert output[1] == Instruction(label=1, name="span",
                                    charlist=[CharRange("0", "9")])
    assert output[2] == Instruction(label=2, name="testcode",
                                    charlist=[
                                    SingleChar(chr(0x1)),
                                    SingleChar(chr(0x3)),
                                    SingleChar(chr(0x39))],
                                    goto=1)


def test_jumptargets():
    input = "01: char '2f'\n13: span [(30-39)]\n37: testcode [(1)(3)(39)] -> 13\n42: jmp -> 37"
    instructionlist = relabel(parse(input))
    assert not instructionlist[0].isjumptarget
    assert instructionlist[1].isjumptarget
    assert instructionlist[2].isjumptarget
    assert not instructionlist[3].isjumptarget
