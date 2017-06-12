from token import *
from lexical_analyser import *
from symbols import *
from type_analyser import *
import copy




class IterToken(object):

    def __init__(self, idx, tok):
        self.idx = idx
        self.token = tok

    def __str__(self):
        return "%s " % self.token

token = tg.tokens()
crtToken = IterToken(0, all_tokens[0])
consumedTk = 0

symbols = []
crtDepth = 0
crtFunc = []
crtStruct = []


def next_(crtToken):
    next_idx = crtToken.idx + 1
    return IterToken(next_idx, all_tokens[next_idx])


def consume(code):
    global crtToken
    if crtToken.token.code == code:
        try:
            crtToken = next_(crtToken)
        except IndexError:
            return True
        return True
    return False



def ruleWhile():
    if not consume(TOKENS["WHILE"]):
        return False
    if not consume(TOKENS["LPAR"]):
        raise TokenError(crtToken, "missing ( after while")
    if not expression():
        raise TokenError(crtToken, "invalid expression after (")
    if not consume(TOKENS["RPAR"]):
        raise TokenError(crtToken, "missing ) after while")
    if not stm():
        raise TokenError(crtToken, "missing while statement")
    return True

def expr():
    return exprAssign()

def exprAssign():
    global crtToken
    startToken = copy.copy(crtToken)
    br = True
    rv = exprUnary()
    if rv:
        if not consume(TOKENS["ASSIGN"]):
            crtToken = copy.copy(startToken)
            br = False
        if br:
            rve = exprAssign()
            if not rve:
                raise TokenError(crtToken, "missing exprAssign after assign token")
            if not rv.isLVal:
                raise TokenError(crtToken, "cannot assign to a non lval")
            if rv.tpe.n_elems > -1 or rve.tpe.n_elems > -1:
                raise TokenError(crtToken, "the arrays cannot be assigned")
            cast(rve.tpe, rv.tpe)
            return rv
    rv = exprOr()
    if rv:
        return rv
    return False


def exprUnary():
    tkOp = consume(TOKENS["SUB"])
    if tkOp:
        rv = exprUnary()
        if not rv:
            raise TokenError(crtToken, "missing exprUnary after SUB token")
        if rv.tpe.n_elems >= 0:
            raise TokenError(crtToken, "unary MINUS cannot be applied to array")
        if rv.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "unary MINUS cannot be applied to struct")
        return rv

    tkOp = consume(TOKENS["NOT"])
    if tkOp:
        rv = exprUnary()
        if not rv:
            raise TokenError(crtToken, "missing exprUnary after NOT token")
        if rv.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "NOT cannot be applied to struct")
        rv.tpe = create_type(TypeBase['INT'], -1)
        return rv

    rv = exprPostfix()
    return rv


def exprPrimary():
    tk = copy.copy(crtToken.token)
    if consume(TOKENS["INT_VAL"]):
        rv = RetVal(tpe=create_type(TypeBase['INT'], -1),ctVal=tk.value)
        rv.isCtVal = True
        return rv
    if consume(TOKENS["DOUBLE_VAL"]):
        rv = RetVal(tpe=create_type(TypeBase['DOUBLE'], -1),ctVal=tk.value)
        rv.isCtVal = True
        return rv
    if consume(TOKENS["CHAR"]):
        rv = RetVal(tpe=create_type(TypeBase['CHAR'], -1),ctVal=tk.value)
        rv.isCtVal = True
        return rv
    if consume(TOKENS["STRING"]):
        rv = RetVal(tpe=create_type(TypeBase['CHAR'], 0),ctVal=tk.value)
        rv.isCtVal = True
        return rv
    if consume(TOKENS["LPAR"]):
        rv = expr()
        if not rv:
            raise TokenError(crtToken, "missing expr after LPAR token")
        if not consume(TOKENS["RPAR"]):
            raise TokenError(crtToken, "missing RPAR after expr")
        return rv

    tk = copy.copy(crtToken.token)
    if consume(TOKENS["ID"]):
        sym = findSymbol(symbols, tk.value)
        if sym is None: 
            raise TokenError(crtToken, "Symbol is undefined {}".format(tk.value))
        rv = RetVal(tpe=copy.copy(sym.tpe))
        rv.isLVal = True
        exprPrOp1(rv, sym, tk)
        return rv
    return False


def exprPrOp1(rv, sym, tk):
    if consume(TOKENS["LPAR"]):
        crt_def_args = sym.args
        if sym.clss != Clss['FUNC'] and sym.clss != Clss['EXTFUNC']:
            raise TokenError(crtToken, "Can't call non-function")
        parsed_args = exprPrOp2(rv, sym)
        if not consume(TOKENS["RPAR"]):
            raise TokenError(crtToken, "missing RPAR after exprPrOp2")
        if len(crt_def_args) > parsed_args:
            raise TokenError(crtToken, "Not enough arguments in function call")
        rv.tpe = sym.tpe
        return rv
    if sym.clss == Clss['FUNC'] or sym.clss == Clss['EXTFUNC']:
        raise TokenError(crtToken, "Missing call for function {}".format(tk.value))
    return False


def exprPrOp2(rv, sym):
    crt_def_args = sym.args
    arg_idx = 0
    arg = expr()
    if arg:
        if len(crt_def_args) <= arg_idx:
            raise TokenError(crtToken, "too many arguments in function call")
        cast(arg.tpe, crt_def_args[arg_idx].tpe)
        arg_idx += 1
        while True:
            if consume(TOKENS["COMMA"]):
                arg = expr()
                if not arg:
                    raise TokenError(crtToken, "missing expr after comma")
                if len(crt_def_args) <= arg_idx:
                    raise TokenError(crtToken, "too many arguments in function call")
                cast(arg.tpe, crt_def_args[arg_idx].tpe)
                arg_idx += 1
            else:
                break
        return arg_idx
    return False


def exprPostfix():
    rv = exprPrimary()
    if rv:
        exprPostfix_(rv)
        return rv
    return False


def exprPostfix_(rv):
    tk = copy.copy(crtToken)
    if consume(TOKENS["LBRACKET"]):
        rve = expr()
        if not rve:
            raise TokenError(crtToken, "Missing expr after LBRACKET")
        if rv.tpe.n_elems < 0:
            raise TokenError(crtToken, "only arrays can be indexed")
        tpe = create_type(TypeBase['INT'], -1)
        cast(rve.tpe, tpe)
        
        rv.tpe = rv.tpe
        rv.tpe.n_elems = -1
        rv.isLVal = True
        if not consume(TOKENS["RBRACKET"]):
            raise TokenError(crtToken, "Missing RBACKET after expr")
        exprPostfix_(rv)
        return rv
    if consume(TOKENS["DOT"]):
        if rv.tpe.n_elems != -1:
            raise TokenError(crtToken, "dot cannot be applied to an array")
            
        tk = copy.copy(crtToken.token)
        if not consume(TOKENS["ID"]):
            raise TokenError(crtToken, "Missing ID after DOT in exprPostfix")
        struct_symbol = rv.tpe.symbol

        struct_member = findSymbol(struct_symbol.members, tk.value)

        if struct_member is None:
            raise TokenError(crtToken, "struct {} does not have a member {}".format(struct_symbol.name, tk.value))
        rv.tpe = struct_member.tpe
        rv.isLVal = True
        exprPostfix_(rv)
        return rv
    return False
 

def exprOr():
    rv = exprAnd()
    if rv:
        exprOr_(rv)
        return rv
    return False
    

def exprOr_(rv):
    if consume(TOKENS["OR"]):
        rve = exprAnd()
        if not rve:
            raise TokenError(crtToken, "Missing andExpr after OR token")
        if rv.tpe.type_base == TypeBase['STRUCT'] or rve.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "a structure cannot be logically tested")
        rv.tpe = create_type(TypeBase['INT'], -1)
        exprOr_(rv)
        return rv
    return False


def exprAnd():
    rv = exprEq()
    if rv:
        exprAnd_(rv)
        return rv
    return False
    

def exprAnd_(rv):
    if consume(TOKENS["AND"]):
        rve = exprEq()
        if not rve:
            raise TokenError(crtToken, "Missing exprEq after AND token")
        if rv.tpe.type_base == TypeBase['STRUCT'] or rve.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "a structure cannot be logically tested")
        rv.tpe = create_type(TypeBase['INT'], -1)
        exprAnd_(rv)
        return rv
    return False

def exprEq():
    rv = exprRel()
    if rv:
        exprEq_(rv)
        return rv
    return False
        

def exprEq_(rv):
    if consume(TOKENS["EQUAL"]) or consume(TOKENS["NOTEQ"]):
        rve = exprRel()
        if not rve:
            raise TokenError(crtToken, "Missing exprRel in exprEq after token")
        if rv.tpe.type_base == TypeBase['STRUCT'] or rve.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "a structure cannot be compared")
        rv.tpe = create_type(TypeBase['INT'], -1)
        exprEq_(rv)
        return rv
    return False


def exprRel():
    rv = exprAdd()
    if rv:
        exprRel_(rv)
        return rv
    return False


def exprRel_(rv):
    if consume(TOKENS["LESS"]) or consume(TOKENS["LESSEQ"]) or consume(TOKENS["GREATER"]) or consume(TOKENS["GREATEREQ"]):
        rve = exprAdd()
        if not rve:
            raise TokenError(crtToken, "Missing exprAdd in exprRel after rel token")
        if rv.tpe.n_elems > -1 or rve.tpe.n_elems > -1:
            raise TokenError(crtToken, "An array cannot be compared")
        if rv.tpe.type_base == TypeBase['STRUCT'] or rve.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "A struct cannot be compared")
        rv.tpe = create_type(TypeBase['INT'], -1)
        exprRel_(rv)
        return rv
    return False

def exprAdd():
    rv = exprMul()
    if rv:
        exprAdd_(rv)
        return rv
    return False
    

def exprAdd_(rv):
    if consume(TOKENS["ADD"]) or consume(TOKENS["SUB"]):
        rve = exprMul()
        if not rve:
            raise TokenError(crtToken, "Missing exprMul in exprAdd after add token")
        if rv.tpe.n_elems > -1 or rve.tpe.n_elems > -1:
            raise TokenError(crtToken, "An array cannot be added/subtracted")
        if rv.tpe.type_base == TypeBase['STRUCT'] or rve.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "A struct cannot be added/subtracted")
        rv.tpe = getArithType(rv.tpe, rve.tpe)
        exprAdd_(rv)
        return rv
    return False

def exprMul():
    rv = exprCast()
    if rv:
        exprMul_(rv)
        return rv
    return False


def exprMul_(rv):
    if consume(TOKENS["MUL"]) or consume(TOKENS["DIV"]):
        rve = exprCast()
        if not rve:
            raise TokenError(crtToken, "Missing exprCast in exprMul after mul token")
        if rv.tpe.n_elems > -1 or rve.tpe.n_elems > -1:
            raise TokenError(crtToken, "An array cannot be multiplied/divided")
        if rv.tpe.type_base == TypeBase['STRUCT'] or rve.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "A struct cannot be multiplied/divided")
        rv.tpe = getArithType(rv.tpe, rve.tpe)
        exprMul_(rv)
        return rv
    return False


def exprCast():
    rv = exprUnary()
    if rv:
        exprCast_(rv)
        return rv
    return False


def exprCast_(rv):
    if consume(TOKENS["LPAR"]):
        tp = typeName()
        if not tp:
            raise TokenError(crtToken, "Missing typeName after LPAR in exprCast")
        if not consume(TOKENS["RPAR"]):
            raise TokenError(crtToken, "Missing RPAR after typeName")
        cast(rv.tpe, tp)
        exprCast_(rv)
        return rv
    return False


def stmCompound():
    global crtDepth
    startSymbol = symbols[-1]
    if consume(TOKENS["LACC"]):
        crtDepth += 1
        while True:
            if declVar() or stm():
                pass
            else:
                break
        if not consume(TOKENS["RACC"]):
            raise TokenError(crtToken, "missing RACC after stm")
        crtDepth -= 1
        print_symbols()
        deleteSymbolsAfter(symbols, startSymbol)
        return True
    return False

def stm():
    if consume(TOKENS["IF"]):
        if not consume(TOKENS["LPAR"]):
            raise TokenError(crtToken, "missing lpar after if")
        rv = expr()
        if not rv:
            raise TokenError(crtToken, "missing expr after lpar")
        if rv.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "a structure cannot be logically tested")
        if not consume(TOKENS["RPAR"]):
            raise TokenError(crtToken, "missing rpar after expr")
        if not stm():
            raise TokenError(crtToken, "missing stm after if")
        ifOp()
        return True

    if consume(TOKENS["WHILE"]):
        if not consume(TOKENS["LPAR"]):
            raise TokenError(crtToken, "missing lpar after while")
        rv = expr()
        if not rv:
            raise TokenError(crtToken, "missing expr after lpar")
        if rv.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "a structure cannot be logically tested")
        if not consume(TOKENS["RPAR"]):
            raise TokenError(crtToken, "missing rpar after expr in while")
        if not stm():
            raise TokenError(crtToken, "missing stm in while block")
        return True

    if consume(TOKENS["FOR"]):
        if not consume(TOKENS["LPAR"]):
            raise TokenError(crtToken, "missing lpar after for")
        rv1 = expr()
        if not consume(TOKENS["SEMICOLON"]):
            raise TokenError(crtToken, "missing semicolon in for")
        rv2 = expr()
        if rv2.tpe.type_base == TypeBase['STRUCT']:
            raise TokenError(crtToken, "a structure cannot be logically tested")
        if not consume(TOKENS["SEMICOLON"]):
            raise TokenError(crtToken, "missing semicolon in for")
        rv3 = expr()
        if not consume(TOKENS["RPAR"]):
            raise TokenError(crtToken, "missing rpar after expr in for")
        if not stm():
            raise TokenError(crtToken, "missing stm in for block")
        return True

    if consume(TOKENS["BREAK"]):
        if not consume(TOKENS["SEMICOLON"]):
            raise TokenError(crtToken, "missing semicolon after break")
        return True

    if consume(TOKENS["RETURN"]):
        rv = expr()
        if rv:
            if crtFunc.tpe.type_base == TypeBase['VOID']:
                raise TokenError(crtToken, "a void function cannot return a value")
            cast(rv.tpe, crtFunc.tpe)
        if not consume(TOKENS["SEMICOLON"]):
            raise TokenError(crtToken, "missing semicolon after return")
        return True
    if stmCompound():
        return True
    rv = expr()
    if rv:
        if not consume(TOKENS["SEMICOLON"]):
            raise TokenError(crtToken, "missing semicolong after expression")
        return True
    if consume(TOKENS["SEMICOLON"]):
        return True
    return False


def ifOp():
    if consume(TOKENS["ELSE"]):
        if not stm():
            raise TokenError(crtToken, "missing stm after else")
        return True
    return False


def declStruct():
    global crtToken
    global crtStruct
    startToken = copy.copy(crtToken)

    if consume(TOKENS["STRUCT"]):
        tk = copy.copy(crtToken.token)
        if not consume(TOKENS["ID"]):
            raise TokenError(crtToken, "missing id after struct")
        if not consume(TOKENS["LACC"]):
            crtToken = copy.copy(startToken)
            return False
        struct_annot(tk)        

        while True:
            if declVar():
                pass
            else:
                break
        if not consume(TOKENS["RACC"]):
            raise TokenError(crtToken, "missing RACC after struct")
        if not consume(TOKENS["SEMICOLON"]):
            raise TokenError(crtToken, "missing SEMICOLON after struct decl")
        crtStruct = []

        return True
    crtToken = copy.copy(startToken)
    return False

def struct_annot(tk):
    global crtStruct
    if findSymbol(symbols, tk.value) is not None:
        raise TokenError(crtToken, "symbol redefinition: {}".format(tk.value))
    crtStruct = addSymbol(symbols, tk.value, Clss['STRUCT'], crtDepth)     


def declVar():
    global crtToken
    global symbols
    startToken = copy.copy(crtToken)
    tpe = typeBase()
    if tpe:
        tk = copy.copy(crtToken.token)
        if not consume(TOKENS["ID"]):
            raise TokenError(crtToken, "missing id after typeBase")

        n_elems = arrayDecl()
        if type(n_elems) is int:
            tpe.n_elems = n_elems
        else:
            tpe.n_elems = -1
        addVar(tk, tpe)

        declVarOp(tpe)
        if not consume(TOKENS["SEMICOLON"]):
            symbols.pop()
            crtToken = copy.copy(startToken)
            return False
        return True
    return False


def declVarOp(tpe):
    while True:
        if consume(TOKENS["COMMA"]):
            tk = copy.copy(crtToken.token)
            if not consume(TOKENS["ID"]):
                raise TokenError(crtToken, "missing id after comma in declvar")
            tpe_ = copy.copy(tpe)
            n_elems = arrayDecl()
            if type(n_elems) is int:
                tpe_.n_elems = n_elems
            else:
                tpe_.n_elems = -1
            addVar(tk, tpe_)
        else:
            break


def typeBase():
    if consume(TOKENS["STRUCT"]):
        tk = copy.copy(crtToken.token)
        if not consume(TOKENS["ID"]):
            raise TokenError(crtToken, "missing id after struct typeBase")
        s = findSymbol(symbols, tk.value)
        if s is None:
            raise TokenError(crtToken, "undefined symbol: {}".format(tk.value))
        if s.clss != Clss['STRUCT']:
            raise TokenError(crtToken, "{} is not a struct".format(tk.value))
        tpe = Tpe(TypeBase['STRUCT'])
        tpe.symbol = s
        return tpe
    if consume(TOKENS["INT"]):
        return Tpe(TypeBase['INT'])
    if consume(TOKENS["DOUBLE"]):
        return Tpe(TypeBase['DOUBLE'])
    if consume(TOKENS["CHAR"]):
        return Tpe(TypeBase['CHAR'])
    return False

def arrayDecl():
    n_elems = -1
    if consume(TOKENS["LBRACKET"]):
        rv = expr()
        if rv:
            if not rv.isCtVal:
                raise TokenError(crtToken, "the array size is not a constant")
            if rv.tpe.type_base != TypeBase['INT']:
                raise TokenError(crtToken, "the array size is not an integer")
            n_elems = int(rv.ctVal)
        else:
            n_elems = 0
        if not consume(TOKENS["RBRACKET"]):
            raise TokenError(crtToken, "missing RBRACKET in arrayDecl")
        return n_elems
    return False


def typeName():
    tpe = typeBase()
    if tpe:
        n_elems = arrayDecl()
        if type(n_elems) is int:
            tpe_.n_elems = n_elems
        return tpe
    return False

def funcArg():
    tpe = typeBase()
    if tpe:
        tk = copy.copy(crtToken.token)
        if not consume(TOKENS["ID"]):
            raise TokenError(crtToken,"missing id in funcArg")
        n_elems = arrayDecl()
        if type(n_elems) is int:
            tpe.n_elems = n_elems
        arg_annot(tk, tpe)
        return True
    return False

def arg_annot(tk, tpe):
    s = addSymbol(symbols, tk.value, Clss['VAR'], crtDepth)
    s.set_mem(Mem['ARG'])
    s.set_tpe(tpe)
    s = addSymbol(crtFunc.get_args(), tk.value, Clss['VAR'], crtDepth)
    s.set_mem(Mem['ARG'])
    s.set_tpe(tpe)

def declFunc():
    global crtToken
    startToken = copy.copy(crtToken)
    tpe = typeBase()
    if tpe:
        if consume(TOKENS["MUL"]):
            tpe.n_elems = 0
        if not declFunc_(tpe):
            raise TokenError(crtToken, "missing id after declFunc")
        return True
    if consume(TOKENS["VOID"]):
        tpe = Tpe(TypeBase['VOID'])
        if not declFunc_(tpe):
            raise TokenError(crtToken, "missing id after declFunc")
        return True
    crtToken = copy.copy(startToken)
    return False


def declFunc_(tpe):
    global crtDepth
    global symbols
    global crtFunc
    tk = copy.copy(crtToken.token)
    if consume(TOKENS["ID"]):
        if not consume(TOKENS["LPAR"]):
            raise TokenError(crtToken, "missing lpar in declFunc")
        func_annot(tk, tpe)
        declFuncOp()
        if not consume(TOKENS["RPAR"]):
            raise TokenError(crtToken, "missing rpar in declFunc")
        crtDepth -= 1
        if not stmCompound():
            raise TokenError(crtToken, "missing stmComp in declFunc")
        symbols = deleteSymbolsAfter(symbols, crtFunc)
        crtFunc = []
        return True
    return False

def declFuncOp():
    if funcArg():
        while True:
            if consume(TOKENS["COMMA"]):
                if not funcArg():
                    raise TokenError(crtToken, "missing funcarg after comma")
            else:
                break
        return True
    return False

def func_annot(tk, tpe):
    global crtDepth
    global crtFunc
    if findSymbol(symbols, tk.value) is not None:
        raise TokenError(crtToken, "symbol redefinition in func_annot: {}".format(tk.value))
    crtFunc = addSymbol(symbols, tk.value, Clss['FUNC'], crtDepth)
    crtFunc.set_args([])
    crtFunc.set_tpe(tpe)
    crtDepth += 1

def unit():
    while True:
        if declStruct():
            pass
        elif declVar():
            pass
        elif declFunc():
            pass
        else:
            break
    if consume(TOKENS["END"]):
        pass
    else:
        raise TokenError(crtToken, "bad syntax!")


def addVar(tk, tpe):
    s = None
    if crtStruct:
        if findSymbol(crtStruct.get_members(), tk.value) is not None:
            raise TokenError(crtToken, "symbol redefinition: {}".format(tk.value))
        s = addSymbol(crtStruct.get_members(), tk.value, Clss['VAR'], crtDepth)
    elif crtFunc:
        s = findSymbol(symbols, tk.value)
        if s is not None and s.depth == crtDepth:
            raise TokenError(crtToken, "symbol redefinition: {}".format(tk.value))
        s = addSymbol(symbols, tk.value, Clss['VAR'], crtDepth)
        s.set_mem(Mem['LOCAL']) 
    else:
        if findSymbol(symbols, tk.value) is not None:
            raise TokenError(crtToken, "symbol redefinition: {}".format(tk.value))
        s = addSymbol(symbols, tk.value, Clss['VAR'], crtDepth)
        s.set_mem(Mem['GLOBAL'])
    s.set_tpe(tpe)

def print_symbols():
    print("----------")
    print("Printing symbols")
    for symbol in symbols:
        print(symbol)
        if symbol.clss == Clss['STRUCT']:
            for ss in symbol.members:
                print(ss)
    print("----------")


def cast(src, dst):
    if src.n_elems > -1:
        if dst.n_elems > -1:
            if src.type_base != dst.type_base:
                raise TokenError(crtToken, "An array cannot be converted to an array of another type")
        else:
            raise TokenError(crtToken, "An array cannot be converted to a non-array")
    else:
        if dst.n_elems > -1:
            raise TokenError(crtToken, "A non-array cannot be converted to an array")
    if src.type_base == TypeBase['CHAR'] or src.type_base == TypeBase['INT'] or src.type_base == TypeBase['DOUBLE']:
        if dst.type_base == TypeBase['CHAR'] or dst.type_base == TypeBase['INT'] or dst.type_base == TypeBase['DOUBLE']:
            return
    if src.type_base == TypeBase['STRUCT']:
        if dst.type_base == TypeBase['STRUCT']:
            if src.symbol != dst.symbol:
                raise TokenError(crtToken, "A structure cannot be converted to another one")
            return
    raise TokenError(crtToken, "Incompatible Types")


def getArithType(t1, t2):
    if t1.type_base == t2.type_base:
        return Tpe(t1.type_base)
    if t1.type_base == TypeBase['CHAR'] or t2.type_base == TypeBase['CHAR']:
        if t1.type_base == TypeBase['INT'] or t2.type_base == TypeBase['INT']:
            return Tpe(TypeBase['INT'])
    if t1.type_base == TypeBase['DOUBLE'] or t2.type_base == TypeBase['DOUBLE']:
        raise TokenError(crtToken, "Can not convert to/from DOUBLE")


#extfuncs
func = addExtFunc(symbols, "put_s", create_type(TypeBase['VOID'], -1), crtDepth)
addFuncArg(func, "s", create_type(TypeBase['CHAR'], 0), crtDepth)
func = addExtFunc(symbols, "get_s", create_type(TypeBase['VOID'], -1), crtDepth)
addFuncArg(func, "s", create_type(TypeBase['CHAR'], 0), crtDepth)
func = addExtFunc(symbols, "put_i", create_type(TypeBase['VOID'], -1), crtDepth)
addFuncArg(func, "i", create_type(TypeBase['INT'], -1),crtDepth)
func = addExtFunc(symbols, "get_i", create_type(TypeBase['INT'], -1), crtDepth)
func = addExtFunc(symbols, "put_d", create_type(TypeBase['VOID'], -1), crtDepth)
addFuncArg(func, "d", create_type(TypeBase['DOUBLE'], -1),crtDepth)
func = addExtFunc(symbols, "get_d", create_type(TypeBase['DOUBLE'], -1), crtDepth)
func = addExtFunc(symbols, "put_c", create_type(TypeBase['VOID'], -1), crtDepth)
addFuncArg(func, "c", create_type(TypeBase['CHAR'], -1), crtDepth)
func = addExtFunc(symbols, "get_c", create_type(TypeBase['CHAR'], -1), crtDepth)
func = addExtFunc(symbols, "seconds", create_type(TypeBase['DOUBLE'], -1), crtDepth)
#end extfuncs

try:
    unit()
    print_symbols()
except TokenError as te:
    print(te)