from captures import Capture
from captures import AbstractCapture, SimpleCapture, PositionCapture


class NOTIMPLEMENTEDStack(object):
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

    def pop(self):
        self.index -= 1
        ret = self.storage[self.index]
        if self.index < 0:
            self.index = 0
            return None
        return ret

    def doublestack(self):
        self.storage.extend([None]*len(self.storage))

    def __repr__(self):
        return str(self)

    def __str__(self):
        ret = "STACK\n"
        for i in range(self.index):
            ret += "element: "+str(self.storage[i])+"\n"
        return ret


class NOTIMPLEMENTEDCaptureStack(NOTIMPLEMENTEDStack):
    def __init__(self):
        self.storage = [None]*128
        for i in range(len(self.storage)):
            self.storage[i] = Capture()  # fixes call by reference bug
        self.index = 0

    def push(self, status, kind, size, index):
        if self.index + 1 >= len(self.storage):
            self.doublestack()
        self.storage[self.index].status = status
        self.storage[self.index].kind = kind
        self.storage[self.index].size = size
        self.storage[self.index].index = index
        self.index += 1

    def doublestack(self):
        extendee = [None]*len(self.storage)
        for i in range(len(extendee)):
            extendee[i] = Capture()
        self.storage.extend(extendee)
        #self.storage.extend([Capture()]*len(self.storage))

    def append(self, status, kind, size, index):
        #to improve list compatibility
        self.push(status, kind, size, index)


class CaptureList(Capture):
    def __init__(self, status=-1, kind=-1, size=-1, index=-1, prev=None):
        Capture.__init__(self, status, kind, size, index)
        self.prev = prev

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.status == self.kind == self.size == self.index == -1:
            return("(empty capture)")
        return(self.statusdict[self.status]
               + "capture " + self.kinddict[self.kind]
               + " size:"+str(self.size) + "index: " + str(self.index)
               + str(self.prev))


def new_capturelist(is_simple=False, status=0, size=0, index=0, prev=None):
        if is_simple:
            p = SimpleCapture(status, size, index, prev)
        else:
            p = PositionCapture(index, prev)
        #self.capture = capture
        return p
