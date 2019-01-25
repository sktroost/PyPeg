import sys
from rpython.rlib import jit
from vm import runbypattern, processcaptures


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
    captures = runbypattern(pattern, inputstring).captures
    output = processcaptures(captures, inputstring)
    for line in output:
        print line
    return 0


def target(*args):
    return main
if __name__ == "__main__":
    main(sys.argv)
