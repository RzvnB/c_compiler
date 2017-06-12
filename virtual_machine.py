import struct

from functools import partial


OpCode = Enum('OpCode', 'ADD_C ADD_D ADD_I AND_A AND_C AND_D AND_I CALL CALLEXT CAST_C_D CAST_C_I CAST_D_C CAST_D_I CAST_I_C CAST_I_D DIV_C DIV_D DIV_I DROP ENTER EQ_A EQ_C EQ_D EQ_I GREATER_C GREATER_D GREATER_I GREATEREQ_C GREATEREQ_D GREATEREQ_I HALT INSERT JF_A JF_C JF_D JF_I JMP JT_A JT_C JT_D JT_I LESS_C LESS_D LESS_I LESSEQ_C LESSEQ_D LESSEQ_I LOAD MUL_C MUL_D MUL_I NEG_C NEG_D NEG_I NOP NOT_A NOT_C NOT_D NOT_I NOTEQ_A NOTEQ_C NOTEQ_D NOTEQ_I OFFSET OR_A OR_C OR_D OR_I PUSHFPADDR PUSHCT_A PUSHCT_C PUSHCT_D PUSHCT_I RET STORE SUB_C, SUB_D, SUB_I')

instructions = None
lastInstruction = None

class Arg(object):

    def __init__(self):
        self.i = None
        self.d = None
        self.addr = None


class Instr(object):

    def __init__(self, opcode):
        self.opcode = opcode
        self.arg0 = Arg()
        self.arg1 = Arg()
        self.next = None
        self.before = None


def insert_instr_after(after, instr):
    instr.next = after.next
    instr.before = after
    after.next = instr
    if instr.next is None:
        lastInstruction = instr

def add_instr(opcode):
    instr = Instr(opcode)
    instr.before = lastInstruction
    if lastInstruction is not None:
        lastInstruction.next = instr
    else:
        instructions = instr
    lastInstruction = instr
    return instr

def add_instr_after(after, opcode):
    instr = Instr(opcode)
    insert_instr_after(after, instr)
    return instr

def add_instr_addr(opcode, addr):
    instr = add_instr(opcode)
    instr.arg0.addr = addr
    return instr

def add_instr_int(opcode, i):
    instr = add_instr(opcode)
    instr.arg0.i = i
    return instr

def add_instr_int_int(opcode, i1, i2):
    instr = add_instr(opcode)
    instr.arg0.i = i
    instr.arg1.i = i

def delete_instr_after(start):
    start.next = None
    


class StackError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Stack(bytearray):

    def __init__(self, stack_size, stack_pointer):
        self.STACK_SIZE = stack_size
        self.STACK_POINTER = stack_pointer

    def push(self, val, fmt=None):
        size = struct.calcsize(fmt)
        if self.STACK_POINTER + size > self.STACK_SIZE:
            raise StackError('out of stack')
        self.extend(struct.pack(fmt, val))
        self.STACK_POINTER += size

    def pop(self, fmt=None):
        neg_size = struct.calcsize(fmt) * (-1)
        self.STACK_POINTER += neg_size
        if self.STACK_POINTER < 0:
            raise StackError('not enough stack to pop')
        val = struct.unpack(fmt, self[neg_size:])[0]
        del self[neg_size:]
        return val

    def __getattr__(self, name):
        accepted = ['a', 'd', 'i', 'c']
        tpe = name[-1]
        if tpe not in accepted:
            raise StackError("unsupported stack operation")
        if tpe.startswith('a'):
            tpe = 'P'
        tpe = '>' + tpe
        if name.startswith('pop'):
            return partial(self.pop, fmt=tpe)
        elif name.startswith('push'):
            return partial(self.push, fmt=tpe)
        else:
            raise StackError("unsupported stack operation")


