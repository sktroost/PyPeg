from captures import Capture
class Stack(object):
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


class CaptureStack(Stack):
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
        self.storage.extend([Capture()]*len(self.storage))

    def append(self, status, kind, size, index):  # to improve list compatibility
        self.push(status, kind, size, index)

class CaptureList(object):
    def __init__(self,capture=Capture(), prev=None):
        self.capture = capture
        self.prev = prev

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.capture)+", "+str(self.prev)

