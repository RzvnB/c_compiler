from symbols import Tpe


def create_type(type_base, n_elems):
    t = Tpe(type_base)
    t.n_elems = n_elems
    return t

class RetVal(object):

    def __init__(self, tpe=None, ctVal=None):
        self.tpe = tpe
        self.ctVal = ctVal
        self.isCtVal = None
        self.isLVal = None
        if self.ctVal is not None:
            self.isCtVal = True

    def __str__(self):
        return "{} {} {} {}".format(self.tpe, self.ctVal, self.isLVal, self.isCtVal)
    