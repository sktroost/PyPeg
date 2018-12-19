import sys
from rpython import conftest


class o:
    view = False
    viewloops = True
conftest.option = o

from rpython.rlib.nonconst import NonConstant
from rpython.jit.metainterp.test.test_ajit import LLJitMixin

from pypeg.vm import run, runbypattern, processcaptures
from pypeg.instruction import Instruction
from pypeg.parser import parse, relabel
from pypeg.utils import runpattern
from pypeg.charlistelement import SingleChar, CharRange


class TestLLtype(LLJitMixin):
    def run_string(self, instructionlist, input):

        def interp_w(switch):
            if switch: # hack to make arguments nicht constant
                x = instructionlist
                y = input
            else:
                x = []
                y = ""
            run(x, y)

        interp_w(1)  # check that it runs

        # ast = parse_module(expand_string(str))
        self.meta_interp(interp_w, [1], listcomp=True, listops=True, backendopt=True)

    def test_complex(self):
        pattern = '(lpeg.P"aa"+lpeg.P"zz")^0'
        instructionlist=relabel(parse(runpattern(pattern)))
        input = "aa"*100 + "zz" * 50 + "aaaa"
        self.run_string(instructionlist, input)

    def test_email(self):
        pattern = '(lpeg.P{ lpeg.C(lpeg.R("az","AZ","09")^1*lpeg.P("@")*lpeg.R("az","AZ","09")^1*lpeg.P(".de")) + 1 * lpeg.V(1)})^0'
        instructionlist=relabel(parse(runpattern(pattern)))
        input = " und es endet mit noch ner mail: fds99877jnffhjkllLLa@test.dehier kommt was:, asdfasdf asdf@web.de" * 100
        self.run_string(instructionlist, input)

    def test_set(self):
        pattern = 'lpeg.P{lpeg.P"c" + (lpeg.P"a"+lpeg.P"z") * lpeg.V(1)}'
        instructionlist=relabel(parse(runpattern(pattern)))
        input = "azaaazaz" * 100 + "c"
        self.run_string(instructionlist, input)

    def test_testset(self):
        #this instructionset should match an arbitrarily long string of
        #'a's and 'b's, terminating with another character
        instructionlist =(
        [Instruction(name="testset", label=0, goto=3, charlist=[CharRange("a","b")]),
         Instruction(name="any", label=1),
         Instruction(name="jmp", label=2, goto=0),
         Instruction(name="any", label=3),
         Instruction(name="end", label=4)])
        input = "abba"*100+"c"
        self.run_string(instructionlist,input)
        # await approval from cfbolz. requires vm to run by instructionlist,
        # which requires run_string to change (as far as i understand pypy)

    def test_callret(self):
        instructionlist = [
         Instruction(name="jmp", label=0, goto=3),
         Instruction(name="ret", label=1),
         Instruction(name="any", label=2),
         Instruction(name="call", label=3, goto=1),
         Instruction(name="testchar", character="a", label=4, goto=2),
         Instruction(name="any", label=5),
         Instruction(name="end", label=6)]
        input="b"*100+"a"
        self.run_string(instructionlist,input)
        #await approval from cfbolz. see test_testset
