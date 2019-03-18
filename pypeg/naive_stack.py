class NaiveReturnAddress(object):
    def __init__(self, pc):
        self.pc = pc


class NaiveChoicePoint(object):
    def __init__(self, pc, index, captures):
        self.pc = pc
        self.index = index
        self.captures = captures
    def get_pc(self):
        return self.pc


class NaiveStack(object):
    def __init__(self):
        self.storage = [None]*128
        self.index = 0

    def push(self, element):
        if self.index + 1 >= len(self.storage):
            self.doublestack()
        self.storage[self.index] = element
        self.index += 1

    def append(self, element):  # to improve list compatibility
        self.push(element)

    def realpop(self):
        self.index -= 1
        ret = self.storage[self.index]
        if self.index < 0:
            self.index = 0
            return None
        return ret

    def pop(self):  # only makes sense in the context of list compatibility
        self.realpop()  # can not be called to recieve the popped value
        return self

    def doublestack(self):
        self.storage.extend([None]*len(self.storage))

    def __repr__(self):
        return str(self)

    def __str__(self):
        ret = "STACK\n"
        for i in range(self.index):
            ret += "<element: "+str(self.storage[i])+">"
        return ret


class NaiveBottom(NaiveStack):
    def push_return_address(self, pc):
        entry = NaiveReturnAddress(pc)
        self.push(entry)
        print self
        return self
    def push_choice_point(self, pc, index, captures):
        entry = NaiveChoicePoint(pc, index, captures)
        self.push(entry)
        print self
        return self
    def pop_return_address(self):
        print self
        return self.realpop().pc, self
    def mod_choice_point(self, index, captures):
        #assert stacktop is instance choicepoint
        mod_cp = self.storage[self.index-1]
        mod_cp.index = index
        mod_cp.captures = captures
    def find_choice_point(self):
        entry = self.realpop()
        while isinstance(entry, NaiveReturnAddress):
            entry = self.realpop()
        print self
        return entry, self
