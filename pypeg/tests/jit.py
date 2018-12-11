import sys
from rpython import conftest


class o:
    view = False
    viewloops = True
conftest.option = o

from rpython.rlib.nonconst import NonConstant
from rpython.jit.metainterp.test.test_ajit import LLJitMixin

from pypeg.vm import run, runbypattern, processcaptures


class TestLLtype(LLJitMixin):
    def run_string(self, pattern, input):

        def interp_w(switch):
            if switch:
                x = input
            else:
                x = ""
            runbypattern(pattern, x)

        interp_w(1) # check that it runs

        # ast = parse_module(expand_string(str))
        self.meta_interp(interp_w, [1], listcomp=True, listops=True, backendopt=True)

    def test_complex(self):
        pattern = '(lpeg.P"aa"+lpeg.P"zz")^0'
        input = "aa"*100 + "zz" * 50 + "aaaa"
        self.run_string(pattern, input)

    def test_email(self):
        pattern = '(lpeg.P{ lpeg.C(lpeg.R("az","AZ","09")^1*lpeg.P("@")*lpeg.R("az","AZ","09")^1*lpeg.P(".de")) + 1 * lpeg.V(1)})^0'
        input = " und es endet mit noch ner mail: fdsa@test.dehier kommt was:, asdfasdf asdf@web.de" * 100
        self.run_string(pattern, input)

    def test_set(self):
        pattern = 'lpeg.P{lpeg.P"c" + (lpeg.P"a"+lpeg.P"z") * lpeg.V(1)}'
        input = "a" * 100 + "c"
        self.run_string(pattern, input)
