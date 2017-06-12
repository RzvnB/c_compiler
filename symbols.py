from enum import Enum


TypeBase = Enum('TypeBase', 'INT DOUBLE CHAR STRUCT VOID')
Clss = Enum('Clss', 'VAR FUNC EXTFUNC STRUCT')
Mem = Enum('Mem', 'GLOBAL ARG LOCAL DEFAULT')


class Tpe(object):

    def __init__(self, type_base):
        self.type_base = type_base
        self.n_elems = -1
        self.symbol = []   

    def __key(self):
        return (self.type_base, self.n_elems, self.symbol)

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __str__(self):
        return "{} {} {}".format(self.type_base, self.n_elems, self.symbol)

class Symbol(object):

    def __init__(self, name, clss, depth):
        self.name = name
        self.clss = clss
        self.depth = depth
        self.members = []
        self.mem = Mem['DEFAULT']
        self.args = []

    def set_args(self, args):
        self.args = args

    def set_members(self, members):
        self.members = members

    def set_mem(self, mem):
        self.mem = mem

    def set_tpe(self, tpe):
        self.tpe = tpe

    def get_members(self):
        return self.members

    def get_args(self):
        return self.args

    def get_mem(self):
        return self.mem

    def get_tpe(self):
        return self.tpe

    def __key(self):
        return (self.name, self.clss, self.depth)

    def __hash__(self):
        return hash(self.__key)

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __str__(self):
        return "{} {} {}".format(self.name, self.clss, self.mem)

def addSymbol(symbols, name, clss, depth):
    s = Symbol(name, clss, depth)
    symbols.append(s)
    return s


def findSymbol(symbols, name):
    reversed_symbols = reversed(symbols)
    filtered_list = list(filter(lambda x: x.name == name, reversed_symbols))
    if len(filtered_list) == 0:
        return None
    else:
        return filtered_list[0]

def deleteSymbolsAfter(symbols, symbol):
    idx = -1
    try:
        idx = symbols.index(symbol)
    except:
        print("@deleteSymbolsAfter, symbol not in symbols")
    return symbols[0:idx+1]


def addExtFunc(symbols, name, tpe, depth):
    s = addSymbol(symbols, name, Clss['EXTFUNC'], depth)
    s.tpe = tpe
    return s

def addFuncArg(func, name, tpe, depth):
    a = addSymbol(func.args, name, Clss['VAR'], depth)
    a.tpe = tpe
    return a