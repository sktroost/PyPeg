from pypeg.parser import parse, relabel
from pypeg.utils import charrange
from pypeg.instruction import Instruction


def test_char():
    input = "44: char '+'"
    instr, = parse(input)
    assert instr.label == 44
    assert instr.character == "+"
    assert instr.name == "char"


def test_span():
    input = "21: span [(30-39)]"
    instr, = parse(input)
    assert instr.label == 21
    assert instr.name == "span"
    assert instr.charlist[0] == charrange("0", "9")


def test_set():
    input = "27: set [(30)(33)(35)]"
    instr, = parse(input)
    assert instr.label == 27
    assert instr.name == "set"
    assert instr.charlist == ["0", "3", "5"]


def test_opencapture():
    input = "00: opencapture simple (idx = 0)"
    instr, = parse(input)
    assert instr.label == 0
    assert instr.name == "opencapture simple"
    assert instr.idx == 0


def test_relabel():
    input = "01: char '/'\n13: span [(30-39)]\n37: testcode [(1)(3)(39)] -> 13"
    instructionlist = parse(input)
    output = relabel(instructionlist)
    assert output[0] == Instruction(label=0, name="char", character="/")
    assert output[1] == Instruction(label=1, name="span",
                                    charlist=[charrange("0", "9")])
    assert output[2] == Instruction(label=2, name="testcode",
                                    charlist=[chr(0x1), chr(0x3), chr(0x39)],
                                    goto=1)
