from Emu import Binary

class Instruction:
    def __init__(self):
        self.comment = ""

    def resolve(self, emu):
        attr = emu.__getattribute__(f"resolve{type(self).__name__}")
        attr(self)
    
    def padComment(self, str):
        str += "".join([" " for _ in range(20 - len(str))])
        return str + f"{self.comment}"


class Instructions:
    def __init__(self, *args):
        self.instr = list(iter(args))
    
    def __add__(self, o):
        if type(o) == Instructions:
            self.instr += o.instr
        elif isinstance(o, Instruction):
            self.instr.append(o)
        else:
            raise Exception(f"Unexpected type {type(o)}")

        return self
    
    def __iadd__(self, o):
        return self + o
    
    def commentFirst(self, text):
        self.instr[0].comment = text
        return self
    
    def commentLast(self, text):
        self.instr[-1].comment = text
        return self
    
    def __getitem__(self, idx):
        return self.instr[idx]
    
    def __iter__(self):
        return iter(self.instr)
    
    def __str__(self):
        return "".join(str(i) + "\n" for i in self)
    
    def __len__(self):
        return len(self.instr)

class RType(Instruction):
    def __init__(self, rd, r1, r2):
        super().__init__()
        self.rd = rd
        self.r1 = r1
        self.r2 = r2
    
    def __str__(self):
        op = type(self).__name__.lower()
        return self.padComment(f"{op} {self.rd} {self.r1} {self.r2}")

class Add(RType):
    def __init__(self, rd, r1, r2):
        super().__init__(rd, r1, r2)
    
class Sub(RType):
    def __init__(self, rd, r1, r2):
        super().__init__(rd, r1, r2)
    
class Xor(RType):
    def __init__(self, rd, r1, r2):
        super().__init__(rd, r1, r2)
    
class Or(RType):
    def __init__(self, rd, r1, r2):
        super().__init__(rd, r1, r2)
    
class And(RType):
    def __init__(self, rd, r1, r2):
        super().__init__(rd, r1, r2)

class Mul(RType):
    def __init__(self, rd, r1, r2):
        super().__init__(rd, r1, r2)

class Div(RType):
    def __init__(self, rd, r1, r2):
        super().__init__(rd, r1, r2)

class Slt(RType):
    def __init__(self, rd, r1, r2):
        super().__init__(rd, r1, r2)

class SltU(RType):
    def __init__(self, rd, r1, r2):
        super().__init__(rd, r1, r2)


class IType(Instruction):
    def __init__(self, rd, r1, imm):
        super().__init__()
        self.rd = rd
        self.r1 = r1

        if type(imm) != Binary:
            imm = Binary(imm)
            
        self.imm = imm
    
    def __str__(self):
        op = type(self).__name__.lower()
        return self.padComment(f"{op} {self.rd} {self.r1} {int(self.imm)}")

class Addi(IType):
    def __init__(self, rd, r1, imm):
        super().__init__(rd, r1, imm)

class Jalr(IType):
    def __init__(self, rd, r1, imm):
        super().__init__(rd, r1, imm)

class Lw(IType):
    def __init__(self, rd, r1, imm):
        super().__init__(rd, r1, imm)

class Slti(IType):
    def __init__(self, rd, r1, imm):
        super().__init__(rd, r1, imm)

class SltiU(IType):
    def __init__(self, rd, r1, imm):
        super().__init__(rd, r1, imm)

class BType(Instruction):
    def __init__(self, r1, r2, imm):
        super().__init__()
        self.r1 = r1
        self.r2 = r2
        
        if type(imm) != Binary:
            imm = Binary(imm)

        self.imm = imm
    
    def __str__(self):
        op = type(self).__name__.lower()
        return self.padComment(f"{op} {self.r1} {self.r2} {int(self.imm)}")

class Beq(BType):
    def __init__(self, r1, r2, imm):
        super().__init__(r1, r2, imm)

    def __str__(self):
        op = type(self).__name__.lower()
        return self.padComment(f"{op} {self.r1} {self.r2} {int(self.imm)}")

class Bne(BType):
    def __init__(self, r1, r2, imm):
        super().__init__(r1, r2, imm)

class Blt(BType):
    def __init__(self, r1, r2, imm):
        super().__init__(r1, r2, imm)

class Bge(BType):
    def __init__(self, r1, r2, imm):
        super().__init__(r1, r2, imm)


class JType(Instruction):
    def __init__(self, rd, imm):
        super().__init__()
        self.rd = rd

        if type(imm) != Binary:
            imm = Binary(imm)

        self.imm = imm

    def __str__(self):
        op = type(self).__name__.lower()
        return self.padComment(f"{op} {self.rd} {int(self.imm)}")

class Jal(JType):
    def __init__(self, rd, imm):
        super().__init__(rd, imm)


class SType(Instruction):
    def __init__(self, r1, r2, imm):
        super().__init__()
        self.r1 = r1
        self.r2 = r2
        self.imm = imm

    def __str__(self):
        op = type(self).__name__.lower()
        return self.padComment(f"{op} {self.r1} {self.r2} {self.imm}")

class Sw(SType):
    def __init__(self, r1, r2, imm):
        super().__init__(r1, r2, imm)

class Stop(Instruction):
    def __init__(self):
        super().__init__()

class Debug(Instruction):
    def __init__(self):
        super().__init__()

class RaiseError(Instruction):
    def __init__(self):
        super().__init__()
