from pypeg.utils import charrange, runlpeg, runpattern
from pypeg.instruction import Instruction
from os import getcwd


def test_charrange():
    chars = charrange("a", "z")
    assert "a" in chars
    assert "z" in chars
    assert "0" not in chars
    assert "A" not in chars
    assert chr(96) not in chars  # 1 before 'a' in ascii
    assert chr(123) not in chars  # 1 after 'z' in ascii


def test_runlpeg():
    path = getcwd()
    runlpeg("INVALID FILENAME LOL")
    assert path == getcwd()
    assert runlpeg("notarealfile.lua") is None


def test_runpattern():
    bytecode = runpattern("lpeg.P'a'")
    assert bytecode == "00: char '61'\n01: end \n"


def test_runpattern_2():
    path = getcwd()
    runpattern("INVALID PATTERN LOL")
    assert path == getcwd()
