from pypeg.vm import run


def test_char_end():
    assert run('lpeg.P"a"', "a") is not None
    assert run('lpeg.P"a"', "b") is None
    assert run('lpeg.P"a"', "") is None

def test_char_end_2():
    assert run('lpeg.P"ab"', "ab") is not None
    assert run('lpeg.P"ab"', "ac") is None
    assert run('lpeg.P"ab"', "b") is None
    assert run('lpeg.P"ab"', "") is None

def test_set():
    assert run('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "a") is not None
    assert run('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "c") is not None
    assert run('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "z") is not None
    assert run('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "b") is None
    assert run('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "") is None

def test_testchar():
    assert run('lpeg.P"aa"+lpeg.P"bb"', "aa") is not None
    assert run('lpeg.P"aa"+lpeg.P"bb"', "bb") is not None
    assert run('lpeg.P"aa"+lpeg.P"bb"', "ab") is None
    assert run('lpeg.P"aa"+lpeg.P"bb"', "ba") is None
    assert run('lpeg.P"aa"+lpeg.P"bb"', "banana") is None
    assert run('lpeg.P"aa"+lpeg.P"bb"', "") is None

def test_choice_commit():
    assert run('lpeg.P"aa"+lpeg.P"ab"', 'aa') is not None
    assert run('lpeg.P"aa"+lpeg.P"ab"', 'ab') is not None
    #TODO: figure out if the thing below should be true or not
    assert run('lpeg.P"aa"+lpeg.P"ab"', 'aaa') is not None
    assert run('lpeg.P"aa"+lpeg.P"ab"', '') is None
