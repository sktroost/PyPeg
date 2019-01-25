class Flags:

    def __init__(self, debug=False, optimize_chars=False):
        self.debug = debug
        self.optimize_chars = optimize_chars

    def __str__(self):
        return ("Flags(Debug: "+str(self.debug)
               +", optimize_chars: "+str(optimize_chars))

    def __repr__(self):
        return str(self)
