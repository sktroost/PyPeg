import sys
from rpython.rlib import jit
from vm import runbypattern, processcaptures
from flags import Flags


def main(argv):
    for i in range(len(argv)):
        if argv[i] == "--jit":
            jitarg = argv[i + 1]
            del argv[i: i+2]
            print jitarg, argv
            jit.set_user_param(None, jitarg)
            break
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
    captures = runbypattern(pattern, inputstring, flags=flags).captures
    output = processcaptures(captures, inputstring)
    print output
    return 0


def target(*args):
    return main
if __name__ == "__main__":
    main(sys.argv)
