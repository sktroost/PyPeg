class ReturnAddress(object):
    _attrs_ = ["pc", "prev"]

    def __init__(self, pc, prev=None):
        self.pc = pc
        self.prev = prev

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("ReturnAddress: "+str(self.pc))


class ChoicePoint(ReturnAddress):
    def __init__(self, pc, index, capturelength, prev=None):
        ReturnAddress.__init__(self, pc, prev)
        self.index = index
        self.capturelength = capturelength

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("Choicepoint(pc:" + str(self.pc)
               + ", index:" + str(self.index)
               + "capturelength:" + str(self.capturelength)+")")
