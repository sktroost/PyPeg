class Capture():
#possible refactor: inherit by kind, may or may not be useful

    def __init__(self, status="\0", kind="\n", size=-1, index=-1):
        self.status = status  # "open" or "full"
        self.kind = kind  # "simple" or "position" (more in the future)
        self.size = size
        self.index = index

    def __repr__(self):
        return str(self)

    def __str__(self):
        return(self.status + "capture " + self.kind
               + " size:"+str(self.size) + "index: " + str(self.index))
