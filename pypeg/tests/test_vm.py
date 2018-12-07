from pypeg.vm import run, runbypattern, processcaptures
from pypeg.parser import parse, relabel


def test_any():
    assert runbypattern('lpeg.P(1)', "K") is not None
    assert runbypattern('lpeg.P(1)', "") is None
    assert runbypattern('lpeg.P(1)', "AA") is None


def test_char_end():
    assert runbypattern('lpeg.P"a"', "a") is not None
    assert runbypattern('lpeg.P"a"', "b") is None
    assert runbypattern('lpeg.P"a"', "") is None


def test_char_end_2():
    assert runbypattern('lpeg.P"ab"', "ab") is not None
    assert runbypattern('lpeg.P"ab"', "ac") is None
    assert runbypattern('lpeg.P"ab"', "b") is None
    assert runbypattern('lpeg.P"ab"', "") is None


def test_set():
    assert runbypattern('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "a") is not None
    assert runbypattern('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "c") is not None
    assert runbypattern('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "z") is not None
    assert runbypattern('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "b") is None
    assert runbypattern('lpeg.P"a"+lpeg.P"c"+lpeg.P"z"', "") is None


def test_testchar():
    assert runbypattern('lpeg.P"aa"+lpeg.P"bb"', "aa") is not None
    assert runbypattern('lpeg.P"aa"+lpeg.P"bb"', "bb") is not None
    assert runbypattern('lpeg.P"aa"+lpeg.P"bb"', "ab") is None
    assert runbypattern('lpeg.P"aa"+lpeg.P"bb"', "ba") is None
    assert runbypattern('lpeg.P"aa"+lpeg.P"bb"', "banana") is None
    assert runbypattern('lpeg.P"aa"+lpeg.P"bb"', "") is None


def test_choice_commit():
    assert runbypattern('lpeg.P"aa"+lpeg.P"ab"', 'aa') is not None
    assert runbypattern('lpeg.P"aa"+lpeg.P"ab"', 'ab') is not None
    assert runbypattern('lpeg.P"aa"+lpeg.P"ab"', 'aaa') is None
    assert runbypattern('lpeg.P"aa"+lpeg.P"ab"', '') is None


def test_testset_partial_commit():  # possible todo: find shorter example
    assert runbypattern('(lpeg.P"aa"+lpeg.P"zz")^0', "") is not None
    assert runbypattern('(lpeg.P"aa"+lpeg.P"zz")^0', "aazzaa") is not None
    assert runbypattern('(lpeg.P"aa"+lpeg.P"zz")^0', "zzaazz") is not None
    assert runbypattern('(lpeg.P"aa"+lpeg.P"zz")^0', "azazaz") is None
    assert runbypattern('(lpeg.P"aa"+lpeg.P"zz")^0', "aaaaaz") is None
    assert runbypattern('(lpeg.P"aa"+lpeg.P"zz")^0', "banana") is None


def test_span():
    assert runbypattern('(lpeg.P"a"+lpeg.P"b")^0', "") is not None
    assert runbypattern('(lpeg.P"a"+lpeg.P"b")^0', "aaaaa") is not None
    assert runbypattern('(lpeg.P"a"+lpeg.P"b")^0', "b") is not None
    assert runbypattern('(lpeg.P"a"+lpeg.P"b")^0', "aaac") is None
    assert runbypattern('(lpeg.P"a"+lpeg.P"b")^0', "abca") is None


def test_behind():
    assert runbypattern('lpeg.B(lpeg.P"a")', "") is None
    assert runbypattern('lpeg.B(lpeg.P"a")', "a") is not None


def test_behind_2():  # matches any 2 characters without consuming them
    assert runbypattern('#lpeg.P(2)', "") is None
    assert runbypattern('#lpeg.P(2)', "z") is None
    assert runbypattern('#lpeg.P(2)', "ak") is not None
    assert runbypattern('#lpeg.P(2)', "lol") is None


def test_testany_fail():  # matches only on empty string
    assert runbypattern('lpeg.P(-1)', "") is not None
    assert runbypattern('lpeg.P(-1)', "a") is None
    assert runbypattern('lpeg.P(-1)', " ") is None


def test_failtwice():  # Matches any String of length 1 or less
    assert runbypattern('lpeg.P(-2)', "") is not None
    assert runbypattern('lpeg.P(-2)', "a") is not None
    assert runbypattern('lpeg.P(-2)', "aa") is None
    assert runbypattern('lpeg.P(-2)', "  ") is None


def test_slow():
    bignumber = 1*10**4
    longstring = "c"*bignumber+"ab"
    assert runbypattern('lpeg.P{ lpeg.P"ab" + 1 * lpeg.V(1) }',
                        longstring) is not None
    assert runbypattern('lpeg.P{ lpeg.P"ab" + 1 * lpeg.V(1) }',
                        longstring[0:1000]) is None


def test_grammar_call_jmp_ret():
    grammar = """lpeg.P{
    "a";
    a =     lpeg.V("b") * lpeg.V("c"),
    b = lpeg.P("b"),
    c = lpeg.P("c")}"""
    assert runbypattern(grammar, "bc") is not None
    assert runbypattern(grammar, "") is None
    assert runbypattern(grammar, "b") is None


def test_fullcapture_simple():
    #fullcapture tests for captures of fixed length
    assert runbypattern('lpeg.C(lpeg.P("a"))', "a") is not None
    assert runbypattern('lpeg.C(lpeg.P("a"))', "") is None
    assert runbypattern('lpeg.C(lpeg.P("ab"))', "") is None
    assert runbypattern('lpeg.C(lpeg.P("ab"))', "a") is None
    assert runbypattern('lpeg.C(lpeg.P("ab"))', "ab") is not None
    assert runbypattern('lpeg.C(lpeg.P("ab"))', "banana") is None


def test_opencapture_simple_closecapture():
    #open and close capture are used for captures of variable length
    pattern = 'lpeg.C(lpeg.R("09")^0)'
    captures = runbypattern(pattern, "123")
    assert captures is not None
    assert processcaptures(captures, "123") == ["123"]
    #TODO: more tests, figure out how to write this elegantly


def test_processcapture():
    pattern = 'lpeg.R("09")^0 *  lpeg.C( lpeg.R("az")) * lpeg.R("09")^0'
    inputstring = "123a567"
    captures = runbypattern(pattern, inputstring)
    assert processcaptures(captures, inputstring) == ["a"]
    #TODO: more tests, figure out how to write this elegantly
