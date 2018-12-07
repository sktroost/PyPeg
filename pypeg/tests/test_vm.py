from pypeg.vm import run, runbypattern, processcaptures
from pypeg.parser import parse, relabel


def test_any():
    pattern = 'lpeg.P(1)'
    #matches any string of length 1
    assert runbypattern(pattern, "K") is not None
    assert runbypattern(pattern, "") is None
    assert runbypattern(pattern, "AA") is None


def test_char_end():
    pattern = 'lpeg.P"a"'
    #matches exactly the string "a"
    assert runbypattern(pattern, "a") is not None
    assert runbypattern(pattern, "b") is None
    assert runbypattern(pattern, "") is None


def test_char_end_2():
    pattern = 'lpeg.P"ab"'
    #matches exactly the string "ab"
    assert runbypattern(pattern, "ab") is not None
    assert runbypattern(pattern, "ac") is None
    assert runbypattern(pattern, "b") is None
    assert runbypattern(pattern, "") is None


def test_set():
    pattern = 'lpeg.P"a"+lpeg.P"c"+lpeg.P"z"'
    #matches either of these 3 strings: "a","c","z"
    assert runbypattern(pattern, "a") is not None
    assert runbypattern(pattern, "c") is not None
    assert runbypattern(pattern, "z") is not None
    assert runbypattern(pattern, "b") is None
    assert runbypattern(pattern, "") is None


def test_testchar():
    pattern = 'lpeg.P"aa"+lpeg.P"bb"'
    #matches either of these 2 strings: "aa", "bb"
    assert runbypattern(pattern, "aa") is not None
    assert runbypattern(pattern, "bb") is not None
    assert runbypattern(pattern, "ab") is None
    assert runbypattern(pattern, "ba") is None
    assert runbypattern(pattern, "banana") is None
    assert runbypattern(pattern, "") is None


def test_choice_commit():
    pattern = 'lpeg.P"aa"+lpeg.P"ab"'
    #matches either of these 2 strings: "aa", "ab"
    assert runbypattern(pattern, 'aa') is not None
    assert runbypattern(pattern, 'ab') is not None
    assert runbypattern(pattern, 'aaa') is None
    assert runbypattern(pattern, '') is None


def test_testset_partial_commit():  # possible todo: find shorter example
    pattern = '(lpeg.P"aa"+lpeg.P"zz")^0'
    #matches arbitrarily many repetitions
    #of either of these 2 strings: "aa","zz"
    assert runbypattern(pattern, "") is not None
    assert runbypattern(pattern, "aazzaa") is not None
    assert runbypattern(pattern, "zzaazz") is not None
    assert runbypattern(pattern, "azazaz") is None
    assert runbypattern(pattern, "aaaaaz") is None
    assert runbypattern(pattern, "banana") is None


def test_span():
    pattern = '(lpeg.P"a"+lpeg.P"b")^0'
    #matches arbitrarily many repetitions
    #of either of these 2 strings: "a", "b"
    assert runbypattern(pattern, "") is not None
    assert runbypattern(pattern, "aaaaa") is not None
    assert runbypattern(pattern, "b") is not None
    assert runbypattern(pattern, "aaac") is None
    assert runbypattern(pattern, "abca") is None


def test_behind():
    pattern = 'lpeg.B(lpeg.P"a")'
    #matches exactly the string "a" without consuming input
    assert runbypattern(pattern, "") is None
    assert runbypattern(pattern, "a") is not None


def test_behind_2():
    pattern = '#lpeg.P(2)'
    #matches any 2 characters without consuming them
    assert runbypattern(pattern, "") is None
    assert runbypattern(pattern, "z") is None
    assert runbypattern(pattern, "ak") is not None
    assert runbypattern(pattern, "lol") is None


def test_testany_fail():
    pattern = 'lpeg.P(-1)'
    # matches only on empty string
    assert runbypattern(pattern, "") is not None
    assert runbypattern(pattern, "a") is None
    assert runbypattern(pattern, " ") is None


def test_failtwice():
    pattern = 'lpeg.P(-2)'
    #Matches any String of length 1 or less
    assert runbypattern(pattern, "") is not None
    assert runbypattern(pattern, "a") is not None
    assert runbypattern(pattern, "aa") is None
    assert runbypattern(pattern, "  ") is None


def test_slow():
    bignumber = 1*10**4
    longstring = "c"*bignumber+"ab"
    pattern = 'lpeg.P{ lpeg.P"ab" + 1 * lpeg.V(1) }'
    #matches any string that ends with "ab"
    assert runbypattern(pattern,
                        longstring) is not None
    assert runbypattern(pattern,
                        longstring[0:1000]) is None


def test_grammar_call_jmp_ret():
    grammar = """lpeg.P{
    "a";
    a =     lpeg.V("b") * lpeg.V("c"),
    b = lpeg.P("b"),
    c = lpeg.P("c")}"""
    #matches exactly the string "bc"
    assert runbypattern(grammar, "bc") is not None
    assert runbypattern(grammar, "") is None
    assert runbypattern(grammar, "b") is None


def test_fullcapture_simple():
    #fullcapture tests for captures of fixed length
    pattern = 'lpeg.C(lpeg.P("a"))'
    #captures exactly the string "a"
    assert runbypattern(pattern, "a") is not None
    assert runbypattern(pattern, "") is None


def test_fullcapture_simple_2():
    pattern = 'lpeg.C(lpeg.P("ab"))'
    #captures exactly the string "ab"
    assert runbypattern(pattern, "") is None
    assert runbypattern(pattern, "a") is None
    assert runbypattern(pattern, "ab") is not None
    assert runbypattern(pattern, "banana") is None


def test_opencapture_simple_closecapture():
    pattern = 'lpeg.C(lpeg.R("09")^0)'
    #captures a number
    captures = runbypattern(pattern, "123")
    assert captures is not None
    assert processcaptures(captures, "123") == ["123"]
    #TODO: more tests, figure out how to write this elegantly


def test_processcapture():
    pattern = 'lpeg.R("09")^0 *  lpeg.C( lpeg.R("az")) * lpeg.R("09")^0'
    #captures a number
    #followed by a letter
    #followed by a number
    inputstring = "123a567"
    captures = runbypattern(pattern, inputstring)
    assert processcaptures(captures, inputstring) == ["a"]
    #TODO: more tests, figure out how to write this elegantly
