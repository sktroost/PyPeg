from pypeg.vm import run, processcaptures
from pypeg.vm import runbypattern as pypeg_runbypattern
from pypeg.parser import parse, relabel
from pypeg.utils import checklpegoutput

def runbypattern(pattern, input, debug=False):
    #from pypeg.vm import runbypattern
    result1 = pypeg_runbypattern(pattern, input, debug=debug)
    result2 = checklpegoutput(pattern, input)
    if result2 == "nil":
        assert result1.fail
    elif "lpeg.C" not in pattern:  # output is different in capture case
        assert result1.index +1  == int(result2)
    return result1

def test_any():
    pattern = 'lpeg.P(1)'
    #matches any string of length 1
    runbypattern(pattern, "K")
    runbypattern(pattern, "") 
    runbypattern(pattern, "AA") 


def test_char_end():
    pattern = 'lpeg.P"a"'
    #matches exactly the string "a"
    runbypattern(pattern, "a")
    runbypattern(pattern, "b") 
    runbypattern(pattern, "") 


def test_char_end_2():
    pattern = 'lpeg.P"ab"'
    #matches exactly the string "ab"
    runbypattern(pattern, "ab")
    runbypattern(pattern, "ac") 
    runbypattern(pattern, "b") 
    runbypattern(pattern, "") 


def test_set():
    pattern = 'lpeg.P"a"+lpeg.P"c"+lpeg.P"z"'
    #matches either of these 3 strings: "a","c","z"
    runbypattern(pattern, "a")
    runbypattern(pattern, "c")
    runbypattern(pattern, "z")
    runbypattern(pattern, "b") 
    runbypattern(pattern, "") 


def test_testchar():
    pattern = 'lpeg.P"aa"+lpeg.P"bb"'
    #matches either of these 2 strings: "aa", "bb"
    runbypattern(pattern, "aa")
    runbypattern(pattern, "bb")
    runbypattern(pattern, "ab") 
    runbypattern(pattern, "ba") 
    runbypattern(pattern, "banana") 
    runbypattern(pattern, "") 


def test_choice_commit():
    pattern = 'lpeg.P"aa"+lpeg.P"ab"'
    #matches either of these 2 strings: "aa", "ab"
    runbypattern(pattern, 'aa')
    runbypattern(pattern, 'ab')
    runbypattern(pattern, 'aaa') 
    runbypattern(pattern, '') 


def test_testset_partial_commit():  # possible todo: find shorter example
    pattern = '(lpeg.P"aa"+lpeg.P"zz")^0'
    #matches arbitrarily many repetitions
    #of either of these 2 strings: "aa","zz"
    runbypattern(pattern, "")
    runbypattern(pattern, "aazzaa")
    runbypattern(pattern, "zzaazz")
    runbypattern(pattern, "azazaz") 
    runbypattern(pattern, "aaaaaz") 
    runbypattern(pattern, "banana") 


def test_span():
    pattern = '(lpeg.P"a"+lpeg.P"b")^0'
    #matches arbitrarily many repetitions
    #of either of these 2 strings: "a", "b"
    runbypattern(pattern, "")
    runbypattern(pattern, "aaaaa")
    runbypattern(pattern, "b")
    runbypattern(pattern, "aaac") 
    runbypattern(pattern, "abca") 


#def test_behind():
 #   pattern = 'lpeg.B(lpeg.P"a")'
  #  #matches exactly the string "a" without consuming input
   # runbypattern(pattern, "") 
    #runbypattern(pattern, "a")


#def test_behind_2():
 #   pattern = '#lpeg.P(2)'
  #  #matches any 2 characters without consuming them
   # runbypattern(pattern, "") 
    #runbypattern(pattern, "z") 
    #runbypattern(pattern, "ak")
    #runbypattern(pattern, "lol") 


def test_testany_fail():
    pattern = 'lpeg.P(-1)'
    # matches only on empty string
    runbypattern(pattern, "")
    runbypattern(pattern, "a") 
    runbypattern(pattern, " ") 


def test_failtwice():
    pattern = 'lpeg.P(-2)'
    #Matches any String of length 1 or less
    runbypattern(pattern, "")
    runbypattern(pattern, "a", debug=True)
    runbypattern(pattern, "aa") 
    runbypattern(pattern, "  ") 


def test_slow():
    bignumber = 1*10**4
    longstring = "c"*bignumber+"ab"
    pattern = 'lpeg.P{ lpeg.P"ab" + 1 * lpeg.V(1) }'
    #matches any string that ends with "ab"
    runbypattern(pattern,
                            longstring)
    runbypattern(pattern,
                        longstring[0:1000]) 


def test_grammar_call_jmp_ret():
    grammar = """lpeg.P{
    "a";
    a =     lpeg.V("b") * lpeg.V("c"),
    b = lpeg.P("b"),
    c = lpeg.P("c")}"""
    #matches exactly the string "bc"
    runbypattern(grammar, "bc")
    runbypattern(grammar, "") 
    runbypattern(grammar, "b") 


def test_fullcapture_simple():
    #fullcapture tests for captures of fixed length
    pattern = 'lpeg.C(lpeg.P("a"))'
    #captures exactly the string "a"
    res = processcaptures(runbypattern(pattern, "a").captures,"a")
    assert res == ["a"]
    res = processcaptures(runbypattern(pattern, "").captures,"")
    assert res == []


def test_fullcapture_simple_2():
    pattern = 'lpeg.C(lpeg.P("ab"))'
    #captures exactly the string "ab"
    runbypattern(pattern, "") 
    runbypattern(pattern, "a") 
    vmout = runbypattern(pattern, "ab")
    assert processcaptures(vmout.captures,"ab") == ["ab"]
    runbypattern(pattern, "banana") 


def test_fullcapture_position():
    pattern = 'lpeg.P"a"^0*lpeg.Cp()'
    #captures the position of the end of a string of "a"s
    vmout = runbypattern(pattern, "a")
    assert processcaptures(vmout.captures, "a") == ["POSITION: 1"]
    runbypattern(pattern, "b") 
    runbypattern(pattern, "")


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
