#usage: call from commandline python lua_to_instr.py myluafile.lua. only works with lua files that only output bytecode (no other printlines allowed)
import subprocess, sys, copy
class Instruction(object):
    def __init__(self,name,label,goto=None,charlist=None, idx=None, size=None):
        self.name=name
        self.label=label
        self.goto=goto
        self.charlist=charlist
        self.idx=idx
        self.size=size
    def __str__(self):
        ret="Instruction (Name:"+self.name+", Label:"+str(self.label)
        if self.charlist is not None:
            templist=[]#code to make the list look more pretty. instead of outputting [a,b,c,...,z] it should output [a-z]
            for sublist in self.charlist:
                if sublist == charrange("a","z"):
                    templist.append(["a-z"])
                elif sublist == charrange("A","Z"):
                    templist.append(["A-Z"])
                elif sublist == charrange("0","9"):
                    templist.append(["0-9"])
                else:
                    templist.append(sublist)
            ret+=", Charlist:"+str(templist)
        if self.goto is not None:
            ret+=", Goto:"+str(self.goto)
        if self.idx is not None:
            ret+=", idx:"+str(self.idx)
        if self.size is not None:
            ret+=", size:"+str(self.size)
        return ret+")"
    def __repr__(self):
        return __str__(self)
def charrange(a,b):
    ret=[]
    for i in range(ord(a),ord(b)+1):
        ret.append(chr(i))
    return ret
def line_to_instruction(line):
    labelsplit=line.split(":")
    label=int(labelsplit[0])
    line=labelsplit[1]
    goto=charlist=idx=size=None
    if "->" in line:#assuming format of "stuff -> int"
        gotosplit=line.split("->")
        goto=int(gotosplit[1])
        line = gotosplit[0]
    if "[" in line and "]" in line:#assuming format similar to "labelname [stuff]"
        cut1=line.find("[")
        cut2=line.find("]")+1
        bracketline=line[cut1:cut2]
        line=line[:cut1]+line[cut2:]
        bracketsplit=bracketline.split(")(")
        charlist=[]
        for element in bracketsplit:
            element=element.replace("(","").replace(")","").replace("[","").replace("]","")
            if "-" in element:#describes a range of values
                sublist=[]
                rangevalues=element.split("-")
                range1=int("0x"+rangevalues[0],16)
                range2=int("0x"+rangevalues[1],16)
                for i in range(range1,range2+1):
                    sublist.append(chr(i))
                charlist.append(sublist)
            else:
                charlist.append(chr(int("0x"+element,16)))
    if "(" in line:#assuming format simillar to "labelname (something = int) (somethingelse = int)"
        parensplit=line.split("(")
        line=parensplit[0]
        for element in parensplit:
            number=""
            for character in element:
                if character.isdigit():
                    number+=character
            if "idx" in element:
                idx=int(number)
            elif "size" in element:
                size=int(number)
            elif ")" in element:
                raise Exception("Unexpected bytecode parameter: "+element)
    name=line
    while name[-1]==" ":
        name=name[:-1]
    while name[0]==" ":
        name=name[1:]#didnt use strip() method because some bytecode have spaces in the middle of them
    return Instruction(name,label,goto,charlist,idx,size)
if __name__=="__main__":
    bytecode=subprocess.check_output(["lua",sys.argv[1]])
    bytecode=bytecode.split("\n")
    instructionlist=[]
    for line in bytecode:
        if line.strip():#if line is not empty
            instruction=line_to_instruction(line)
            instructionlist.append(instruction)
    for instruction in instructionlist:
        print(instruction)
