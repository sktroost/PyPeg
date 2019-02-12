class AbstractReturnAddress(object):
    _attrs_ = ["pc", "prev"]
    _immutable_fields_ = ["pc", "prev"]

    def __init__(self, pc, prev=None):
        self.pc = pc
        self.prev = prev

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("ReturnAddress: "+str(self.pc)+",\n"+str(self.prev))


class ReturnAddress(AbstractReturnAddress):
    pass


class ReturnAddressPair(AbstractReturnAddress):
    _immutable_fields_ = ["pclast"]

    def __init__(self, pc0, pc1, prev=None):
        self.pclast = pc0
        AbstractReturnAddress.__init__(self, pc1, prev)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("ReturnAddressPair: " + str(self.pclast) + ", " +
               str(self.pc) + ",\n" + str(self.prev))


class ChoicePoint(AbstractReturnAddress):
    def __init__(self, pc, index, capturelength, prev=None):
        AbstractReturnAddress.__init__(self, pc, prev)
        self.index = index
        self.capturelength = capturelength

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("Choicepoint(pc:" + str(self.pc)
               + ", index:" + str(self.index)
               + "capturelength:" + str(self.capturelength)+"),\n"
               + str(self.prev))
