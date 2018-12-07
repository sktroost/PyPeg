class ReturnAddress():

    def __init__(self, pc):
        self.pc = pc

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("ReturnAddress: "+str(self.pc))

class ChoicePoint(ReturnAddress):
    def __init__(self, pc, index, capturelength):
        ReturnAddress.__init__(self,pc)
        self.index = index
        self.capturelength = capturelength

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("Choicepoint(pc:" + str(self.pc)
               + ", index:" + str(self.index)
               + "capturelength:" + str(self.capturelength)+")")
