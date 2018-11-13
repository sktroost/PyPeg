from pypeg.parser import parse
from pypeg.utils import charrange
def test_char():
    input = "44: char '+'"
    instr, = parse(input)
    assert instr.label == 44
    assert instr.character == "+"
    assert instr.name == "char"

def test_span():
    input="21: span [(30-39)]"
    instr, = parse(input)
    assert instr.label == 21
    assert instr.name == "span"
    assert instr.charlist[0] == charrange("0", "9")
