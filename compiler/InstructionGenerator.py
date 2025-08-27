from Instruction import *
from Emu import register_name_to_num
import Instruction

def verify(reg):
      if reg not in register_name_to_num:
            raise Exception(f"Bad reg: {reg}")

instr_classes = list(filter(lambda x : x[0] != "_", list(Instruction.__dict__.keys())))
instr_classes = list(map(lambda x : Instruction.__dict__[x], instr_classes))

instr_to_class = dict(zip(map(lambda x : x.__name__.lower(), instr_classes), instr_classes))

def parse(asm):

    instr_list = "".join(asm.split(",")).lower()
    instr_list = asm.splitlines()
    instr_list = list(filter(lambda x : x[0] != "#" and x[0] != ";", instr_list))

    output = []

    for line in instr_list:
        args = line.split(" ")
        op = instr_to_class[args[0]]

        instr_type = op.__bases__[0]


        if instr_type == RType:
                verify(args[1])
                verify(args[2])
                verify(args[3])
                output.append(op(args[1], args[2], args[3]))
        elif instr_type == IType or instr_type == BType:
                verify(args[1])
                verify(args[2])
                output.append(op(args[1], args[2], args[3]))
        elif instr_type == JType:
                verify(args[1])
                verify(args[2])
                output.append(op(args[1], args[2]))
        elif op == Stop:
              output.append(Stop())
        else:
            raise Exception("Unknown instruction")
    
    return output

def parseFile(fname):
      with open(fname) as f:
            contents = f.read()
            return parse(contents)
