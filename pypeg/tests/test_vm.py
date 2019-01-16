from pypeg.vm import run, runbypattern, processcaptures
from pypeg.parser import parse, relabel

def test_any():
    pattern = 'lpeg.P(1)'
    #matches any string of length 1
    assert not runbypattern(pattern, "K").fail
    assert runbypattern(pattern, "").fail 
    assert runbypattern(pattern, "AA").fail 


def test_char_end():
    pattern = 'lpeg.P"a"'
    #matches exactly the string "a"
    assert not runbypattern(pattern, "a").fail
    assert runbypattern(pattern, "b").fail 
    assert runbypattern(pattern, "").fail 


def test_char_end_2():
    pattern = 'lpeg.P"ab"'
    #matches exactly the string "ab"
    assert not runbypattern(pattern, "ab").fail
    assert runbypattern(pattern, "ac").fail 
    assert runbypattern(pattern, "b").fail 
    assert runbypattern(pattern, "").fail 


def test_set():
    pattern = 'lpeg.P"a"+lpeg.P"c"+lpeg.P"z"'
    #matches either of these 3 strings: "a","c","z"
    assert not runbypattern(pattern, "a").fail
    assert not runbypattern(pattern, "c").fail
    assert not runbypattern(pattern, "z").fail
    assert runbypattern(pattern, "b").fail 
    assert runbypattern(pattern, "").fail 


def test_testchar():
    pattern = 'lpeg.P"aa"+lpeg.P"bb"'
    #matches either of these 2 strings: "aa", "bb"
    assert not runbypattern(pattern, "aa").fail
    assert not runbypattern(pattern, "bb").fail
    assert runbypattern(pattern, "ab").fail 
    assert runbypattern(pattern, "ba").fail 
    assert runbypattern(pattern, "banana").fail 
    assert runbypattern(pattern, "").fail 


def test_choice_commit():
    pattern = 'lpeg.P"aa"+lpeg.P"ab"'
    #matches either of these 2 strings: "aa", "ab"
    assert not runbypattern(pattern, 'aa').fail
    assert not runbypattern(pattern, 'ab').fail
    assert runbypattern(pattern, 'aaa').fail 
    assert runbypattern(pattern, '').fail 


def test_testset_partial_commit():  # possible todo: find shorter example
    pattern = '(lpeg.P"aa"+lpeg.P"zz")^0'
    #matches arbitrarily many repetitions
    #of either of these 2 strings: "aa","zz"
    assert not runbypattern(pattern, "").fail
    assert not runbypattern(pattern, "aazzaa").fail
    assert not runbypattern(pattern, "zzaazz").fail
    assert runbypattern(pattern, "azazaz").fail 
    assert runbypattern(pattern, "aaaaaz").fail 
    assert runbypattern(pattern, "banana").fail 


def test_span():
    pattern = '(lpeg.P"a"+lpeg.P"b")^0'
    #matches arbitrarily many repetitions
    #of either of these 2 strings: "a", "b"
    assert not runbypattern(pattern, "").fail
    assert not runbypattern(pattern, "aaaaa").fail
    assert not runbypattern(pattern, "b").fail
    assert runbypattern(pattern, "aaac").fail 
    assert runbypattern(pattern, "abca").fail 


def test_behind():
    pattern = 'lpeg.B(lpeg.P"a")'
    #matches exactly the string "a" without consuming input
    assert runbypattern(pattern, "").fail 
    assert not runbypattern(pattern, "a").fail


def test_behind_2():
    pattern = '#lpeg.P(2)'
    #matches any 2 characters without consuming them
    assert runbypattern(pattern, "").fail 
    assert runbypattern(pattern, "z").fail 
    assert not runbypattern(pattern, "ak").fail
    assert runbypattern(pattern, "lol").fail 


def test_testany_fail():
    pattern = 'lpeg.P(-1)'
    # matches only on empty string
    assert not runbypattern(pattern, "").fail
    assert runbypattern(pattern, "a").fail 
    assert runbypattern(pattern, " ").fail 


def test_failtwice():
    pattern = 'lpeg.P(-2)'
    #Matches any String of length 1 or less
    assert not runbypattern(pattern, "").fail
    assert not runbypattern(pattern, "a", debug=True).fail
    assert runbypattern(pattern, "aa").fail 
    assert runbypattern(pattern, "  ").fail 


def test_slow():
    bignumber = 1*10**4
    longstring = "c"*bignumber+"ab"
    pattern = 'lpeg.P{ lpeg.P"ab" + 1 * lpeg.V(1) }'
    #matches any string that ends with "ab"
    assert not runbypattern(pattern,
                            longstring).fail
    assert runbypattern(pattern,
                        longstring[0:1000]).fail 


def test_grammar_call_jmp_ret():
    grammar = """lpeg.P{
    "a";
    a =     lpeg.V("b") * lpeg.V("c"),
    b = lpeg.P("b"),
    c = lpeg.P("c")}"""
    #matches exactly the string "bc"
    assert not runbypattern(grammar, "bc").fail
    assert runbypattern(grammar, "").fail 
    assert runbypattern(grammar, "b").fail 


def test_fullcapture_simple():
    #fullcapture tests for captures of fixed length
    pattern = 'lpeg.C(lpeg.P("a"))'
    #captures exactly the string "a"
    assert not runbypattern(pattern, "a").fail
    assert runbypattern(pattern, "").fail


def test_fullcapture_simple_2():
    pattern = 'lpeg.C(lpeg.P("ab"))'
    #captures exactly the string "ab"
    assert runbypattern(pattern, "").fail 
    assert runbypattern(pattern, "a").fail 
    assert not runbypattern(pattern, "ab").fail
    assert runbypattern(pattern, "banana").fail 


def test_fullcapture_position():
    pattern = 'lpeg.P"a"^0*lpeg.Cp()'
    #captures the position of the end of a string of "a"s
    assert not runbypattern(pattern, "a").fail
    assert runbypattern(pattern, "b").fail 
    assert not runbypattern(pattern, "").fail


def test_opencapture_simple_closecapture():
    pattern = 'lpeg.C(lpeg.R("09")^0)'
    #captures a number
    captures = runbypattern(pattern, "123").captures
    assert captures is not None
    assert processcaptures(captures, "123") == ["123"]
    #TODO: more tests, figure out how to write this elegantly


def test_opencapture_simple_closecapture_search():  # needs more debugging.
    #current hypothesis is that the bytecode generated for this pattern is bugged
    pattern = 'lpeg.P{ lpeg.C(lpeg.R("09")^1) + 1 * lpeg.V(1)}^0'
    #searches text for numbers
    input = "1h12h999x"
    captures = runbypattern(pattern, input,debug=False).captures
    #print captures
    assert captures is not None
    assert processcaptures(captures, input) == ["999","12","1"]

def test_processcapture_open_simple():
    pattern = 'lpeg.R("09")^0 *  lpeg.C( lpeg.R("az")) * lpeg.R("09")^0'
    #captures a number
    #followed by a letter
    #followed by a number
    inputstring = "123a567"
    captures = runbypattern(pattern, inputstring).captures
    assert processcaptures(captures, inputstring) == ["a"]
    #TODO: more tests, figure out how to write this elegantly


def test_processcapture_full_position():
    pattern = 'lpeg.P"a"^0*lpeg.Cp()'
    #captures the position of the end of a string of "a"s
    inputstring = "aaaa"
    captures = runbypattern(pattern, inputstring).captures
    assert processcaptures(captures, inputstring) == ["POSITION: 4"]
