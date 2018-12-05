from subprocess import check_output, CalledProcessError
from os import chdir, listdir
from rpython.rlib.rfile import create_popen_file



def charrange(a, b):
    ret = []
    for i in range(ord(a), ord(b) + 1):
        ret.append(chr(i))
    return ret


def runlpeg(filename):
    changed = False
    if "lpeg" in listdir("."):
        chdir("./lpeg")  # extremly unsafe.
        changed = True
    # i do this because the lpeg import by lua fails if i don't. no clue why.
    if filename in listdir("."):
        #try:
            #bytecodestring = check_output(["lua", filename])
            c_str = "lua "+filename
            file = create_popen_file(c_str, "r") 
            bytecodestring = file.read()
            file.close()
        #except CalledProcessError:
            #bytecodestring = None
    else:
        bytecodestring = None
    if changed:
        chdir("..")
    return bytecodestring


def runpattern(pattern):
    changed = False
    if "lpeg" in listdir("."):
        chdir("./lpeg")
        changed = True
    f = open("temp.lua", "w")
    code = (
        "local lpeg = require(\"lpeg\"); lpeg.match("
        + pattern
        + ", \""
        + "aaa"  # inputstring is irrelevant for bytecode generation
        + "\")"
    )
    f.write(code)
    f.close()
    if changed:
        chdir("..")
    ret = runlpeg("temp.lua")
    return ret
