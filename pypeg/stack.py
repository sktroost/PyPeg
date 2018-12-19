class Stack():
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
