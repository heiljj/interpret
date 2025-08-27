from Emu import Binary

class Instruction:
    def resolve(self, emu):
        attr = emu.__getattribute__(f"resolve{type(self).__name__}")
        attr(self)


class RType(Instruction):
    def __init__(self, rd, r1, r2):
        self.rd = rd
        self.r1 = r1
        self.r2 = r2
    
    def __str__(self):
        op = type(self).__name__.lower()
        return f"{op} {self.rd} {self.r1} {self.r2}"

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


class IType(Instruction):
    def __init__(self, rd, r1, imm):
        super().__init__()
        self.rd = rd
        self.r1 = r1
        self.imm = Binary(imm)
    
    def __str__(self):
        op = type(self).__name__.lower()
        return f"{op} {self.rd} {self.r1} {int(self.imm)}"

class Addi(IType):
    def __init__(self, rd, r1, imm):
        super().__init__(rd, r1, imm)

class Jalr(IType):
    def __init__(self, rd, r1, imm):
        super().__init__(rd, r1, imm)


class BType(Instruction):
    def __init__(self, r1, r2, imm):
        self.r1 = r1
        self.r2 = r2
        self.imm = Binary(imm)
    
    def __str__(self):
        op = type(self).__name__.lower()
        return f"{op} {self.r1} {self.r2} {int(self.imm)}"

class Beq(BType):
    def __init__(self, r1, r2, imm):
        super().__init__(r1, r2, imm)

    def __str__(self):
        op = type(self).__name__.lower()
        return f"{op} {self.r1} {self.r2} {int(self.imm)}"

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
        self.imm = Binary(imm)

    def __str__(self):
        op = type(self).__name__.lower()
        return f"{op} {self.rd} {int(self.imm)}"

class Jal(JType):
    def __init__(self, rd, imm):
        super().__init__(rd, imm)


class Stop(Instruction):
    def __init__(self):
        super().__init__()
    


