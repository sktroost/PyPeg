class SingleChar(object):
    _immutable_fields_ = ["value"]
    def __init__(self,value):
        self.value = value

    def __repr__(self):
        return "'"+str(self)+"'"

    def __str__(self):
        return self.value

    def __eq__(self,other):
        return self.value == other.value

    def is_match(self, char):
        return self.value == char

class CharRange(SingleChar):
    _immutable_fields_ = ["maxval"]
    def __init__(self,minval,maxval):
        SingleChar.__init__(self,minval)
        self.maxval = maxval

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "RANGE("+self.value+"-"+self.maxval+")"

    def __eq__(self,other):
        return self.value == other.value and self.maxval == other.maxval

    def is_match(self, char):
        
        return (self.value <= char) & (char <= self.maxval)
