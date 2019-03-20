class Flags(object):
    _immutable_fields_ = ["debug", "optimize_char", "optimize_testchar","jumptargets","optimize_choicepoints"]

    def __init__(self, debug=False, optimize_char=True,
                 optimize_testchar=True, jumptargets=True,
	             optimize_choicepoints=True):
        self.debug = debug
        self.optimize_char = optimize_char
        self.optimize_testchar = optimize_testchar
        self.jumptargets = jumptargets
        self.optimize_choicepoints = optimize_choicepoints

    def __str__(self):
        return ("Flags(Debug: " + str(self.debug)
                + ", optimize_chars: " + str(self.optimize_char)
                + ", optimize_testchar: "+str(self.optimize_testchar)
                + ")")

    def __repr__(self):
        return str(self)
