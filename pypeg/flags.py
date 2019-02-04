class Flags(object):
    _immutable_fields_ = ["debug", "optimize_chars", "optimize_testchar"]

    def __init__(self, debug=False, optimize_chars=False,
                 optimize_testchar=False):
        self.debug = debug
        self.optimize_chars = optimize_chars
        self.optimize_testchar = optimize_testchar

    def __str__(self):
        return ("Flags(Debug: " + str(self.debug)
                + ", optimize_chars: " + str(self.optimize_chars)
                + ", optimize_testchar: "+str(self.optimize_testchar)
                + ")")

    def __repr__(self):
        return str(self)
