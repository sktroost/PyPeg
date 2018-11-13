from pypeg.utils import charrange, runlpeg, runpattern

def test_charrange():
    chars=charrange("a","z")
    assert "a" in chars
    assert "z" in chars
    assert "0" not in chars
    assert "A" not in chars
    assert chr(96) not in chars  # 1 before 'a' in ascii
    assert chr(123) not in chars  # 1 after 'z' in ascii


def test_runpattern():
    bytecode = runpattern("lpeg.P\"a\"", "aaa")
    assert bytecode == runlpeg("temp.lua")
    assert bytecode == runpattern('lpeg.P"a"','aaa')
    assert bytecode == runpattern('lpeg.P"a"','bbb')
