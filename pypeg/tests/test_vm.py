from pypeg.vm import run, processcaptures
from pypeg.vm import runbypattern as pypeg_runbypattern
from pypeg.parser import parse, relabel
from pypeg.utils import checklpegoutput, runpattern
from pypeg.flags import Flags

def runbypattern(pattern, input, flags=Flags()):
    #from pypeg.vm import runbypattern
    result1 = pypeg_runbypattern(pattern, input, flags=flags)
    result2 = checklpegoutput(pattern, input)
    if result2 == "nil":
        assert result1.fail
    elif "lpeg.C" not in pattern:  # output is different in capture case
        assert result1.index +1  == int(result2)
    return result1

def test_any(flags=Flags()):
    pattern = 'lpeg.P(1)'
    #matches any string of length 1
    runbypattern(pattern, "K",flags=flags)
    runbypattern(pattern, "",flags=flags)
    runbypattern(pattern, "AA",flags=flags)


def test_char_end(flags=Flags()):
    pattern = 'lpeg.P"a"'
    #matches exactly the string "a"
    runbypattern(pattern, "a",flags=flags)
    runbypattern(pattern, "b",flags=flags)
    runbypattern(pattern, "",flags=flags)


def test_char_end_2(flags=Flags()):
    pattern = 'lpeg.P"ab"'
    #matches exactly the string "ab"
    runbypattern(pattern, "ab",flags=flags)
    runbypattern(pattern, "ac",flags=flags)
    runbypattern(pattern, "b",flags=flags)
    runbypattern(pattern, "",flags=flags)


def test_set(flags=Flags()):
    pattern = 'lpeg.P"a"+lpeg.P"c"+lpeg.P"z"'
    #matches either of these 3 strings: "a","c","z"
    runbypattern(pattern, "a",flags=flags)
    runbypattern(pattern, "c",flags=flags)
    runbypattern(pattern, "z",flags=flags)
    runbypattern(pattern, "b",flags=flags)
    runbypattern(pattern, "",flags=flags)


def test_testchar(flags=Flags()):
    pattern = 'lpeg.P"aa"+lpeg.P"bb"'
    #matches either of these 2 strings: "aa", "bb"
    runbypattern(pattern, "aa",flags=flags)
    runbypattern(pattern, "bb",flags=flags)
    runbypattern(pattern, "ab",flags=flags)
    runbypattern(pattern, "ba",flags=flags)
    runbypattern(pattern, "banana",flags=flags)
    runbypattern(pattern, "",flags=flags)


def test_choice_commit(flags=Flags()):
    pattern = 'lpeg.P"aa"+lpeg.P"ab"'
    #matches either of these 2 strings: "aa", "ab"
    runbypattern(pattern, 'aa',flags=flags)
    runbypattern(pattern, 'ab',flags=flags)
    runbypattern(pattern, 'aaa',flags=flags) 
    runbypattern(pattern, '',flags=Flags(debug=True)) 


def test_testset_partial_commit(flags=Flags()):  # possible todo: find shorter example
    pattern = '(lpeg.P"aa"+lpeg.P"zz")^0'
    #matches arbitrarily many repetitions
    #of either of these 2 strings: "aa","zz"
    runbypattern(pattern, "",flags=flags)
    runbypattern(pattern, "aazzaa",flags=Flags(debug=True))
    runbypattern(pattern, "zzaazz",flags=flags)
    runbypattern(pattern, "azazaz",flags=flags)
    runbypattern(pattern, "aaaaaz",flags=flags)
    runbypattern(pattern, "banana",flags=flags)


def test_span(flags=Flags()):
    pattern = '(lpeg.P"a"+lpeg.P"b")^0'
    #matches arbitrarily many repetitions
    #of either of these 2 strings: "a", "b"
    runbypattern(pattern, "",flags=flags)
    runbypattern(pattern, "aaaaa",flags=flags)
    runbypattern(pattern, "b",flags=flags)
    runbypattern(pattern, "aaac",flags=flags)
    runbypattern(pattern, "abca",flags=flags)


#def test_behind(flags=Flags()):
 #   pattern = 'lpeg.B(lpeg.P"a")'
  #  #matches exactly the string "a" without consuming input
   # runbypattern(pattern, "") 
    #runbypattern(pattern, "a",flags=flags)


#def test_behind_2(flags=Flags()):
 #   pattern = '#lpeg.P(2)'
  #  #matches any 2 characters without consuming them
   # runbypattern(pattern, "") 
    #runbypattern(pattern, "z") 
    #runbypattern(pattern, "ak",flags=flags)
    #runbypattern(pattern, "lol") 


def test_testany_fail(flags=Flags()):
    pattern = 'lpeg.P(-1)'
    # matches only on empty string
    runbypattern(pattern, "",flags=flags)
    runbypattern(pattern, "a",flags=flags)
    runbypattern(pattern, " ",flags=flags)


def test_failtwice(flags=Flags()):
    pattern = 'lpeg.P(-2)'
    #Matches any String of length 1 or less
    runbypattern(pattern, "",flags=flags)
    runbypattern(pattern, "a",flags=flags)
    runbypattern(pattern, "aa",flags=flags)
    runbypattern(pattern, "  ",flags=flags)


def test_slow(flags=Flags()):
    bignumber = 1*10**4
    longstring = "c"*bignumber+"ab"
    pattern = 'lpeg.P{ lpeg.P"ab" + 1 * lpeg.V(1) }'
    #matches any string that ends with "ab"
    runbypattern(pattern,longstring,flags=flags)
    runbypattern(pattern,longstring[0:1000],flags=flags) 


def test_grammar_call_jmp_ret(flags=Flags()):
    grammar = """lpeg.P{
    "a";
    a =     lpeg.V("b") * lpeg.V("c"),
    b = lpeg.P("b"),
    c = lpeg.P("c")}"""
    #matches exactly the string "bc"
    runbypattern(grammar, "bc",flags=flags)
    runbypattern(grammar, "",flags=flags)
    runbypattern(grammar, "b",flags=flags)


def test_fullcapture_simple(flags=Flags()):
    #fullcapture tests for captures of fixed length
    pattern = 'lpeg.C(lpeg.P("a"))'
    #captures exactly the string "a"
    res = processcaptures(runbypattern(pattern, "a").captures,"a",flags=flags).split()
    assert res == ["a"]
    res = processcaptures(runbypattern(pattern, "").captures,"",flags=flags).split()
    assert res == []


def test_fullcapture_simple_2(flags=Flags()):
    pattern = 'lpeg.C(lpeg.P("ab"))'
    #captures exactly the string "ab"
    runbypattern(pattern, "",flags=flags)
    runbypattern(pattern, "a",flags=flags)
    vmout = runbypattern(pattern, "ab",flags=flags)
    assert processcaptures(vmout.captures,"ab").split() == ["ab"]
    runbypattern(pattern, "banana") 


def test_fullcapture_position(flags=Flags()):
    pattern = 'lpeg.P"a"^0*lpeg.Cp()'
    #captures the position of the end of a string of "a"s
    vmout = runbypattern(pattern, "a",flags=flags)
    assert processcaptures(vmout.captures, "a").split() == ["POSITION:1"]
    runbypattern(pattern, "b",flags=flags)
    runbypattern(pattern, "",flags=flags)


def test_opencapture_simple_closecapture(flags=Flags()):
    pattern = 'lpeg.C(lpeg.R("09")^0)'
    #captures a number
    captures = runbypattern(pattern, "123").captures
    assert captures is not None
    assert processcaptures(captures, "123").split() == ["123"]
    #TODO: more tests, figure out how to write this elegantly


def test_opencapture_simple_closecapture_search(flags=Flags()):  # needs more debugging.
    #current hypothesis is that the bytecode generated for this pattern is bugged
    pattern = 'lpeg.P{ lpeg.C(lpeg.R("09")^1) + 1 * lpeg.V(1)}^0'
    #searches text for numbers
    input = "1h12h999x"
    captures = runbypattern(pattern, input).captures
    #print captures
    assert captures is not None
    assert processcaptures(captures, input).split() == ["999","12","1"]

def test_processcapture_open_simple(flags=Flags()):
    pattern = 'lpeg.R("09")^0 *  lpeg.C( lpeg.R("az")) * lpeg.R("09")^0'
    #captures a number
    #followed by a letter
    #followed by a number
    inputstring = "123a567"
    captures = runbypattern(pattern, inputstring).captures
    assert processcaptures(captures, inputstring).split() == ["a"]
    #TODO: more tests, figure out how to write this elegantly


def test_processcapture_full_position(flags=Flags()):
    pattern = 'lpeg.P"a"^0*lpeg.Cp()'
    #captures the position of the end of a string of "a"s
    inputstring = "aaaa"
    captures = runbypattern(pattern, inputstring).captures
    assert processcaptures(captures, inputstring).split() == ["POSITION:4"]


def test_orderedchoice(flags=Flags(debug=True, optimize_char=False)):
    pattern="lpeg.P{lpeg.P'x'*lpeg.V(1)*lpeg.P'x' + lpeg.P'x'}"
    input = ""
    runbypattern(pattern, input, flags=flags)
    input = "x"
    runbypattern(pattern, input, flags=flags)
    input = "xx"
    runbypattern(pattern, input, flags=flags)
    input = "xxx"
    runbypattern(pattern, input, flags=flags)


def test_optimize_char_2(flags=Flags(optimize_char=True)):
    pattern = 'lpeg.P"h"'
    input = "x"
    runbypattern(pattern, input, flags=flags)
    input = "h"
    runbypattern(pattern, input, flags=flags)


def test_optimize_char_1(flags=Flags(debug=False, optimize_char=True)):
    #tests if the code runs in principle
    from pypeg.vm import look_for_chars, match_many_chars
    pattern = 'lpeg.P"Hallo"'
    bytecode = relabel(parse(runpattern(pattern)))
    assert look_for_chars(bytecode, 0,) == 5
    assert match_many_chars(bytecode, 0, 5, "Hallo",0)


def test_optimize_char(flags=Flags(debug=False,optimize_char=True)):
    #return  # currently this test doesnt work, still needs debugging
    pattern = 'lpeg.P"Hallo"'
    input = "Hallo"
    runbypattern(pattern,input,flags=flags)
    input = "Hallx"
    runbypattern(pattern,input,flags=flags)
    input = "Hal"
    runbypattern(pattern,input,flags=flags)
    input = "Hall"
    runbypattern(pattern,input,flags=flags)
    input = "Halloo"
    runbypattern(pattern,input,flags=flags)
    input = ""
    runbypattern(pattern, input, flags=flags)


def test_optimize_testchar(flags=Flags(optimize_testchar=True)):
    pattern = 'lpeg.P{lpeg.P"Hallo" + 1 * lpeg.V(1)}^0'
    input="z"*20 + "Hallo"
    runbypattern(pattern, input, flags=flags)
    input="unrelated input"
    runbypattern(pattern, input, flags=flags)
    input=""
    runbypattern(pattern, input, flags=flags)


def test_optimize_testset(flags=Flags(optimize_testchar=True)):
    pattern = "lpeg.P{lpeg.S'hH'*lpeg.P'allo' + 1 * lpeg.V(1)}"
    input = "z"*20 + "Hallo"
    runbypattern(pattern, input, flags=flags)
    input="unrelated input"
    runbypattern(pattern, input, flags=flags)
    input=""
    runbypattern(pattern, input, flags=flags)
