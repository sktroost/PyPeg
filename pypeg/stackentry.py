class ReturnAddress():

    def __init__(self, pc):
        self.pc = pc

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("ReturnAddress: "+str(self.pc))

class ChoicePoint():#inheritance messes with isinstance

    def __init__(self, pc, index, capturelength):
        self.pc = pc
        self.index = index
        self.capturelength = capturelength

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("Choicepoint(pc:" + str(self.pc)
               + ", index:" + str(self.index)
               + "capturelength:" + str(self.capturelength)+")")
