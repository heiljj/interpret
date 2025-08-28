from Binary import Binary

ZERO = "00000000000000000000000000000000"
register_name_to_num = {"x0":0, "zero":0, "x1":1, "ra":1,
                        "x2":2, "sp":2, "x3":3, "gp":3, 
                        "x4":4, "tp":4, "x5":5, "t0":5,
                        "x6":6, "t1":6, "x7":7, "t2":7,
                        "x8":8, "s0":8, "fp":8, 
                        "x9":9, "s1":9, "x10":10, "a0":10, 
                        "x11":11, "a1":11, "x12":12, "a2":12,
                        "x13":13, "a3":13, "x14":14, "a4":14,
                        "x15":15, "a5":15, "x16":16, "a6":16,
                        "x17":17, "a7":17, "x18":18, "s2":18,
                        "x19":19, "s3":19, "x20":20, "s4":20,
                        "x21":21, "s5":21, "x22":22, "s6":22,
                        "x23":23, "s7":23, "x24":24, "s8":24,
                        "x25":25, "s9":25, "x26":26, "s10":26,
                        "x27":27, "s11":27, "x28":28, "t3":28,
                        "x29":29, "t4":29, "x30":30, "t5":30,
                        "x31":31, "at":31, "PC": 32
                        }

class Emu:
    def __init__(self, instrs, debug=False):
        self.debug = debug
        self.instrs = instrs
        self.index = 0
        self.regs = [Binary(ZERO) for _ in range(33)]
        self.mem = [Binary(ZERO) for _ in range(1000)]
        self.stop = False

    def getReg(self, reg_name):
        index = register_name_to_num[reg_name]
        return self.regs[index]
    
    def setReg(self, reg_name, value):
        index = register_name_to_num[reg_name]
        self.regs[index] = value

    def addPC(self, value):
        self.setReg("PC", self.getReg("PC") + value)
    
    def next(self):
        pc = int(self.getReg("PC")) 

        if pc % 4 != 0:
            raise Exception("Bad pc")

        instr = self.instrs[pc // 4]
        if self.debug:
            print(instr)

        instr.resolve(self)
        self.addPC(4)
    
    def run(self):
        i = 0
        while not self.stop:
            self.next()

            i += 1
            if i > 1000:
                raise Exception("Loop")
    
    def resolveComment(self, instr):
        pass
    
    def resolveStop(self, instr):
        self.stop = True
    
    def resolveRType(self, instr, op):
        r1_value = self.getReg(instr.r1)
        r2_value = self.getReg(instr.r2)
        result = op(r1_value, r2_value)
        self.setReg(instr.rd, result)
    
    def resolveAdd(self, add):
        self.resolveRType(add, lambda x, y : x + y)
        
    def resolveSub(self, sub):
        self.resolveRType(sub, lambda x, y : x - y)
    
    def resolveXor(self, xor):
        self.resolveRType(xor, lambda x, y : x.bitwiseXor(y))

    def resolveOr(self, or_):
        self.resolveRType(or_, lambda x, y : x.bitwiseOr(y))

    def resolveAnd(self, and_):
        self.resolveRType(and_, lambda x, y : x.bitwiseAnd(y))
    

    def resolveAddi(self, addi):
        r1_value = self.getReg(addi.r1)
        self.setReg(addi.rd, r1_value + addi.imm)
    
    def resolveLw(self, lw):
        addr = int(self.getReg(lw.r1) + lw.imm)

        if addr % 4 != 0:
            raise Exception("Bad address")
        
        index = addr // 4
        self.setReg(lw.rd, self.mem[index])
    
    def resolveJalr(self, jalr):
        self.setReg("rd", self.getReg("PC") + 4)
        self.setReg("pc", self.getReg(jalr.r1) + self.getReg(jalr.imm))

    def resolveBType(self, instr, cmp):
        r1_value = self.getReg(instr.r1)
        r2_value = self.getReg(instr.r2)
        if cmp(r1_value, r2_value):
            self.addPC(int(instr.imm) - 4)
    
    def resolveBeq(self, beq):
        self.resolveBType(beq, lambda x, y : x == y)
    
    def resolveBne(self, bne):
        self.resolveBType(bne, lambda x, y : x != y)
    
    def resolveBlt(self, blt):
        self.resolveBType(blt, lambda x, y : x < y)
    
    def resolveBge(self, bge):
        self.resolveBType(bge, lambda x, y : x >= y)


    def resolveSw(self, sw):
        addr = int(self.getReg(sw.r1) + sw.imm)

        if addr % 4 != 0:
            raise Exception("Bad address")
        
        index = addr // 4
        self.mem[index] = self.getReg(sw.r2)
    

    def resolveJal(self, jal):
        self.setReg(jal.rd, self.getReg("PC") + 4)
        self.setReg("PC", jal.imm + 4)

    