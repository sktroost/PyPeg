from utils import runpattern
from parser import parse, relabel
def run(pattern, inputstring):
    bytecodestring = runpattern(pattern, inputstring)
    bytecodelist = parse(bytecodestring)
    bytecodelist = relabel(bytecodelist)

    #The state of the VM is realized by 4 values p, i, e and c.
    #Their definitions are found in the paper.
    p = 0  # probably the index of the instructionlist
    i = 0  # probably the index of the inputstring
    e = "something"  # TODO: find out what that is
    c = "something"  # TODO: find out what that is
    while True:  # Iterating over every Bytecode once is impractical
        if p == "FAIL":
            return None  # TODO: backtracking instead of returning false
        bytecode = bytecodelist[p]
        if bytecode.name == "char":
            char = bytecode.character
            if char == inputstring[i]:
                p += 1
                i += 1
            else:
                p = "FAIL"
        elif bytecode.name == "end":
            if p != "FAIL":
                return True  # currently only outputs that we matched, not where
            else:
                return None
        else:
            raise Exception("Unknown Bytecode! "+bytecode.name)
