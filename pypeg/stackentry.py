from rpython.rlib import jit


class StackEntry(object):
    _attrs_ = []

    def push_return_address(self, pc):
        raise NotImplementedError("abstract base class")

    def push_choice_point(self, pc, index, captures):
        return ChoicePoint(PcTuple.new(pc), index, captures, self)

    def pop_return_address(self):
        raise NotImplementedError("abstract base class")

    def find_choice_point(self):
        raise NotImplementedError("abstract base class")

    def pop(self):
        raise NotImplementedError("abstract base class")

    def get_pc(self):
        raise NotImplementedError("abstract base class")


class Bottom(StackEntry):
    def __init__(self, pcs=None):
        self.pcs = pcs

    def push_return_address(self, pc):
        if self.pcs is None:
            return Bottom(PcTuple.new(pc))
        return Bottom(jit.promote(self.pcs).push(pc))

    def pop(self):
        raise Exception("pop from emtpy stack")

    def pop_return_address(self):
        pcs = jit.promote(self.pcs)
        if pcs is None:
            raise Exception("pop from emtpy stack")
        return pcs.pc, Bottom(pcs.prev)

    def find_choice_point(self):
        return None, None


class PcTuple(object):
    cache = {}

    _immutable_fields_ = ["pc", "prev"]

    def __init__(self, pc, prev):
        self.pc = pc
        self.prev = prev

    @staticmethod
    def new(pc):
        jit.promote(pc)
        return PcTuple.new_with_cache(pc, None)

    def push(self, pc):
        jit.promote(self)
        jit.promote(pc)
        return PcTuple.new_with_cache(pc, self)

    @staticmethod
    @jit.elidable
    def new_with_cache(pc, prev):
        key = (pc, prev)
        if key in PcTuple.cache:
            return PcTuple.cache[key]
        else:
            res = PcTuple.cache[key] = PcTuple(pc, prev)
            return res

    @jit.elidable
    def discard_all_but_one(self):
        while 1:
            if self.prev is None:
                return self
            self = self.prev

    def __repr__(self):
        l = []
        while self:
            l.append(str(self.pc))
            self = self.prev
        return "<" + ", ".join(l) + ">"


class ChoicePoint(StackEntry):
    def __init__(self, pcs, index, captures, prev=None):
        self.prev = prev
        self.pcs = pcs
        self.index = index
        self.captures = captures

    def __repr__(self):
        return str(self)

    def __str__(self):
        return("Choicepoint(pcs:" + str(self.pcs)
               + ", index:" + str(self.index)
               + "captures:" + str(self.captures)+"),\n"
               + str(self.prev))

    def pop(self):
        assert self.pcs.prev is None
        return self.prev

    def get_pc(self):
        assert self.pcs.prev is None
        return jit.promote(self.pcs).pc

    def push_return_address(self, pc):
        assert self.pcs is not None
        return ChoicePoint(jit.promote(self.pcs).push(pc),
                           self.index, self.captures, self.prev)

    def pop_return_address(self):
        #import pdb;pdb.set_trace()
        pcs = jit.promote(self.pcs)
        return pcs.pc, ChoicePoint(pcs.prev,
                                   self.index, self.captures, self.prev)

    def discard_return_addresses(self):
        pcs = jit.promote(self.pcs)
        if pcs.prev is None:
            return self
        return ChoicePoint(pcs.discard_all_but_one(),
                           self.index, self.captures, self.prev)

    def find_choice_point(self):
        return self.discard_return_addresses(), self.prev
