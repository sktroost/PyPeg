class StackEntry:

    def __init__(self, pc):
        self.pc = pc


class ChoicePoint(StackEntry):

    def __init__(self, pc, index, captures):
        StackEntry.__init__(self, pc)
        self.index = index
        self.captures = captures

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("Choicepoint(pc:" + str(self.pc)
               + ", index:" + str(self.index)
               + "captures:" + str(self.captures))


class ReturnAddress(StackEntry):

    def __init__(self, pc):
        StackEntry.__init__(self, pc)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("ReturnAddress: "+str(self.pc))
