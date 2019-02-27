class StackEntry(object):
    def push_return_address(self, pc):
        return ReturnAddress(pc, self)

    def push_choice_point(self, pc, index, captures):
        return ChoicePoint(pc, index, captures, self)

    def pop_return_address(self):
        raise NotImplementedError("abstract base class")

    def find_choice_point(self):
        return None, None

    def pop(self):
        raise NotImplementedError("abstract base class")
        



class Bottom(StackEntry):
    def pop(self):
        raise Exception("pop from emtpy stack")

class AbstractReturnAddress(StackEntry):
    _attrs_ = ["pc", "prev"]
    _immutable_fields_ = ["pc", "prev"]

    def __init__(self, pc, prev=None):
        self.pc = pc
        self.prev = prev

    def find_choice_point(self):
        entry = self
        choice_points = self.prev
        while not isinstance(entry, ChoicePoint):
            if type(choice_points) is Bottom:
                return None, None
            entry = choice_points
            choice_points = choice_points.prev
        return entry, choice_points

    def pop(self):
        return self.prev

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("ReturnAddress: "+str(self.pc)+",\n"+str(self.prev))



class ReturnAddress(AbstractReturnAddress):
    def push_return_address(self, pc):
        return ReturnAddressPair(pc, self.pc, self.prev)

    def pop_return_address(self):
        return self.pc, self.prev

   
class ReturnAddressPair(AbstractReturnAddress):
    _immutable_fields_ = ["pclast"]

    def __init__(self, pc0, pc1, prev=None):
        self.pclast = pc0
        AbstractReturnAddress.__init__(self, pc1, prev)

    def pop_return_address(self):
        pc = self.pclast
        return pc, ReturnAddress(self.pc, self.prev)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("ReturnAddressPair: " + str(self.pclast) + ", " +
               str(self.pc) + ",\n" + str(self.prev))


class ChoicePoint(AbstractReturnAddress):
    def __init__(self, pc, index, captures, prev=None):
        AbstractReturnAddress.__init__(self, pc, prev)
        self.index = index
        self.captures = captures

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("Choicepoint(pc:" + str(self.pc)
               + ", index:" + str(self.index)
               + "captures:" + str(self.captures)+"),\n"
               + str(self.prev))
