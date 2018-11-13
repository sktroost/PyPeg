from utils import charrange


class Instruction(object):
    def __init__(self, name, label,
                 goto=None, charlist=None, idx=None,
                 size=None, character=None):
        self.name = name
        self.label = label
        self.goto = goto
        self.charlist = charlist
        self.idx = idx
        self.size = size
        self.character = character

    def __str__(self):
        ret = "Instruction (Name:"+self.name+", Label:"+str(self.label)
        if self.charlist is not None:
            templist = []  # code to make the list look more pretty.
            #instead of outputting [a,b,c,...,z] it should output [a-z]
            for sublist in self.charlist:
                if sublist == charrange("a", "z"):
                    templist.append(["a-z"])
                elif sublist == charrange("A", "Z"):
                    templist.append(["A-Z"])
                elif sublist == charrange("0", "9"):
                    templist.append(["0-9"])
                else:
                    templist.append(sublist)
            ret += ", Charlist:"+str(templist)
        if self.goto is not None:
            ret += ", Goto:"+str(self.goto)
        if self.idx is not None:
            ret += ", idx:"+str(self.idx)
        if self.size is not None:
            ret += ", size:"+str(self.size)
        if self.character is not None:
            ret += ", character:"+str(self.character)
        return ret+")"

    def __repr__(self):
        return str(self)
