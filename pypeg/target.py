from __future__ import print_function
import sys
import time
from rpython.rlib import jit, rgc
from rpython.rlib.objectmodel import we_are_translated
from vm import runbypattern, processcaptures
from flags import Flags


def main(argv):
    printtime = False
    i = 0
    while i < len(argv):
        if argv[i] == "--jit":
            jitarg = argv[i + 1]
            del argv[i: i+2]
            print(jitarg, argv)
            jit.set_user_param(None, jitarg)
        if argv[i] == "--time":
            printtime = True
        i += 1
    patternfilename = argv[1]
    inputfilename = argv[2]
    patternfile = open(patternfilename, "r")
    inputfile = open(inputfilename, "r")
    pattern = patternfile.read()
    patternfile.close()
    inputstring = inputfile.read()
    inputfile.close()
    inputstring = inputstring.strip()
    flags = Flags(optimize_char=True, optimize_testchar=True)
    if not flags.optimize_choicepoints:
        jit.set_param(None, "enable_opts", "intbounds:rewrite:virtualize:string:pure:earlyforce:heap")

    
    if we_are_translated():
        gct1 = rgc.get_stats(rgc.TOTAL_GC_TIME)
    else:
        gct1 = 0
    t1 = time.time()
    captures = runbypattern(pattern, inputstring, flags=flags).captures
    output = processcaptures(captures, inputstring)
    t2 = time.time()
    if we_are_translated():
        gct2 = rgc.get_stats(rgc.TOTAL_GC_TIME)
    else:
        gct2 = 0

    print(output)
    if printtime:
        print("time:", t2 - t1)
        print("gc time:", (gct2 - gct1) / 1000.)    
    return 0


def target(*args):
    return main
if __name__ == "__main__":
    main(sys.argv)
