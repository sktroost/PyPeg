from subprocess import check_output
from os import chdir


def charrange(a, b):
    ret = []
    for i in range(ord(a), ord(b) + 1):
        ret.append(chr(i))
    return ret


def runlpeg(filename):
    chdir("./lpeg")  # extremly unsafe.
    # i do this because the lpeg import by lua fails if i don't. no clue why.
    bytecodestring = check_output(["lua", filename])
    chdir("..")
    return bytecodestring


def runpattern(pattern,inputstring):
    chdir("./lpeg")
    f = open("temp.lua","w")
    code = (
        "local lpeg = require(\"lpeg\"); lpeg.match("
        + pattern
        + ", \"" 
        + inputstring 
        + "\")"
    )
    f.write(code)
    f.close()
    chdir("..")
    ret = runlpeg("temp.lua")
    return ret
