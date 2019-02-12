class AbstractCapture(object):
    #openstatus = 0
    #fullstatus = 1
    name = "AbstractCapture"

    def __init__(self, index, prev=None):

        self.index = index
        self.prev = prev

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Abstract Capture(index="+str(self.index)+")"


class SimpleCapture(AbstractCapture):
    _immutable_fields_ = ["OPENSTATUS", "FULLSTATUS", "statusdict",
                          "max_size", "name"]
    OPENSTATUS = 0
    FULLSTATUS = 1
    statusdict = {1: "Full", 0: "Open", -1: "Error"}
    max_size = 0xfffffffffffffff  # 2^60-1
    name = "SimpleCapture"

    def __init__(self, status, size, index, prev=None):
        assert size <= self.max_size  # max size value
        AbstractCapture.__init__(self, index, prev)
        self.status_size = status << 62
        self.status_size += size

    def get_status(self):
        return self.status_size >> 62

    def get_size(self):
        return self.status_size & self.max_size

    def set_status_full(self):
        assert self.get_status() == self.OPENSTATUS
        self.status_size += 1 << 62

    def set_size(self, size):
        assert self.status_size == 0
        self.status_size += size

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ("Simple Capture(status=" +
                self.statusdict[self.get_status()] +
                "size: " + str(self.get_size()) +
                "index="+str(self.index)+")")


class PositionCapture(AbstractCapture):
    _immutable_fields_ = ["name"]
    name = "PositionCapture"

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Position Capture(index="+str(self.index)+")"
    pass


class Capture(object):  # OUTDATED! TODO: REFACTOR OUT
#possible refactor: inherit by kind, may or may not be useful

    SIMPLEKIND = 0
    POSITIONKIND = 1
    OPENSTATUS = 0
    FULLSTATUS = 1

    statusdict = {1: "Full", 0: "Open", -1: "Error"}
    kinddict = {0: "Simple", 1: "Position", -1: "Error"}

    def __init__(self, status=-1, kind=-1, size=-1, index=-1):
        self.status = status  # "open" or "full"
        self.kind = kind  # "simple" or "position" (more in the future)
        self.size = size
        self.index = index

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.status == self.kind == self.size == self.index == -1:
            return("(empty capture)")
        return(self.statusdict[self.status]
               + "capture " + self.kinddict[self.kind]
               + " size:"+str(self.size) + "index: " + str(self.index))
