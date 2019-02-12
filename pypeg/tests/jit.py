import sys
from rpython import conftest


class o:
    view = False
    viewloops = True
conftest.option = o

from rpython.rlib.nonconst import NonConstant
from rpython.rlib import jit
from rpython.jit.metainterp.test.test_ajit import LLJitMixin

from pypeg.vm import run, runbypattern, processcaptures
from pypeg.instruction import Instruction
from pypeg.flags import Flags
from pypeg.parser import parse, relabel
from pypeg.utils import runpattern
from pypeg.charlistelement import SingleChar, CharRange


class TestLLtype(LLJitMixin):
    def run_string(self, instructionlist, input, **flags):
        flagsobj = Flags(**flags)

        def interp_w(switch):
            jit.set_param(None, "disable_unrolling", 5000)
            if switch: # hack to make arguments nicht constant
                x = instructionlist
                y = input
                fl = flagsobj
            else:
                x = []
                y = ""
                fl = Flags()

            run(x, y, flags=fl)

        #interp_w(1)  # check that it runs

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

    def test_url(self):
        pattern = """lpeg.P{
"S";
S = lpeg.V("URL") + lpeg.P(1) * lpeg.V("S"),

URL = lpeg.Cp()*lpeg.C(lpeg.P"http" * lpeg.V("urlchar")^3),

urlchar = lpeg.R("az","AZ","09") + lpeg.S("-._~:/?#@!$&*+,;=")}^0"""
        instructionlist = relabel(parse(runpattern(pattern)))
        input = "das hier ist eine url:https://www3.hhu.de/stups/downloads/pdf/BoCuFiRi09_246.pdf und das hier nicht 192.168.13.37"*100
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

    def test_falseloop(self):
        instructionlist = [
        Instruction(name="call", label=0, goto=5),
        Instruction(name="call", label=1, goto=5),
        Instruction(name="testchar", character="1", label=2, goto=4),
        Instruction(name="jmp",label=3,goto=0),
        Instruction(name="end",label=4),
        Instruction(name="char",character="1",label=5),
        Instruction(name="ret",label=6)]
        input = "1"*100
        self.run_string(instructionlist,input)
        #parsed sowas wie MEMBER = VALUE *  VALUE
        # VALUE = '1'
        #S = MEMBER^0

    def test_optimize_char(self):
        pattern = 'lpeg.P{lpeg.P"Hallo" + 1 * lpeg.V(1)}^0'
        instrs = relabel(parse(runpattern(pattern)))
        input = "z"*100 + "Hallo"*50
        self.run_string(instrs, input, optimize_char=True, optimize_testchar=True)


    def test_optimize_testset(self):
        pattern = 'lpeg.P{lpeg.S"hH" * lpeg.P"allo" + 1 * lpeg.V(1)}^0'
        instrs = relabel(parse(runpattern(pattern)))
        input = "z"*100 + "Halloyxxddcccxxddffhallojjjjjjgfffdssadgh"*50
        self.run_string(instrs, input, optimize_char=True, optimize_testchar=True)


    def test_bug(self):
        with open("examples/jsonpattern") as f:
            p = f.read()
        with open("examples/jsoninput") as f:
            i = f.read()
        instructionlist=relabel(parse(runpattern(p)))
        self.run_string(instructionlist, i)

