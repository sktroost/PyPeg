from pypeg.utils import charrange, runlpeg, runpattern
from pypeg.instruction import Instruction

def test_charrange():
    chars=charrange("a","z")
    assert "a" in chars
    assert "z" in chars
    assert "0" not in chars
    assert "A" not in chars
    assert chr(96) not in chars  # 1 before 'a' in ascii
    assert chr(123) not in chars  # 1 after 'z' in ascii


def test_runpattern():
    bytecode = runpattern("lpeg.P\"a\"")
    assert bytecode == "00: char 'a'\n01: end \n"
