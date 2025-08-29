from Tokenizer import TokenType
from Instruction import *

class Compiler:
    def __init__(self, ast):
        self.ast = ast
        self.stream = ""

        self.current_stack = 0

        self.globals = {}
        self.locals = []
    
    def run(self):
        #TODO
        return self.ast.resolve(self) + [Stop()]
    
    def beginScope(self):
        self.locals.append({})
    
    def endScope(self):
        return self.locals.pop()
    
    def decl(self, var):
        if self.locals:
            self.declLocal(var)
        else:
            self.declGlobal(var)
    
    def declGlobal(self, var):
        if var in self.globals:
            raise Exception("Global already declared")

        self.globals[var] = self.current_stack
        self.current_stack += 1
    
    def declLocal(self, var):
        locals = self.locals[-1]

        if var in locals:
            raise Exception("Local already declared")
        
        locals[var] = self.current_stack
        self.current_stack += 1

    def get(self, var):
        for locals in reversed(self.locals):
            if var not in locals:
                continue

            return locals[var]

        
        if var not in self.globals:
            raise Exception("Variable does not exist")
        
        return self.globals[var]
    


    def resolveStatements(self, stmts):
        instr = []
        for stmt in stmts.statements:
            instr += stmt.resolve(self)
        
        return instr
    
    def pushValue(self, binary):
        self.current_stack += 1

        return [
            Addi("t0", "x0", binary),
            Sw("sp", "t0", 0),
            Addi("sp", "sp", 4)
        ]

    def pushReg(self, reg):
        self.current_stack += 1

        return [
            Sw("sp", reg, 0),
            Addi("sp", "sp", 4)
        ]
    
    def pop(self, reg):
        self.current_stack -= 1

        return [
                Addi("sp", "sp", -4),
                Lw(reg, "sp", 0)
        ]
    
    def resolveValue(self, value):
        if value.type == TokenType.NUM:
            return self.pushValue(Binary(value.value))
        
        if value.type == TokenType.BOOL:
            return self.pushValue(Binary(int(value.value)))

        raise NotImplementedError
            
    
    def resolveBinaryOp(self, op):
        c1 = [Comment(f"#binaryop {op.left} {op.op.name} {op.right}")]
        left = op.left.resolve(self)
        right = op.right.resolve(self)
        right_value = self.pop("t1")
        left_value = self.pop("t0")
        
        op_instr = None

        match op.op:
            case TokenType.OP_PLUS:
                op_instr = [Add("t0", "t0", "t1")]
            case TokenType.OP_MINUS:
                op_instr = [Sub("t0", "t0", "t1")]
            case TokenType.OP_MUL:
                op_instr = [Mul("t0", "t0", "t1")]
            case TokenType.OP_DIV:
                op_instr = [Div("t0", "t0", "t1")]
            case TokenType.COMP_EQ:
                op_instr = [Xor("t0", "t0", "t1"),
                            SltiU("t0", "t0", 1)]

            case TokenType.COMP_NEQ:
                op_instr = [Xor("t0", "t0", "t1"),
                            SltU("t0", "x0", "t0")]

            case TokenType.COMP_GT:
                op_instr = [Sub("t0", "t0", "t1"),
                            Slt("t0", "x0", "t0")]

            case TokenType.COMP_LT:
                op_instr = [Sub("t0", "t1", "t0"),
                            Slt("t0", "x0", "t0")]

            case TokenType.COMP_GT_EQ:
                op_instr = [Sub("t0", "t1", "t0"),
                            Addi("t1", "x0", 1),
                            Slt("t0", "t0", "t1")]

            case TokenType.COMP_LT_EQ:
                op_instr = [Sub("t0", "t0", "t1"),
                            Addi("t1", "x0", 1),
                            Slt("t0", "t0", "t1")]
            
            case TokenType.OR:
                op_instr = [Or("t0", "t0", "t1"),
                            SltU("t0", "x0", "t0")]
            
            case TokenType.AND:
                op_instr = [And("t0", "t0", "t1"),
                            SltU("t0", "x0", "t0")]

            case _:
                raise NotImplementedError
        
        push = self.pushReg("t0")
        c2 = [Comment(f"#END binaryop {op.left} {op.op.name} {op.right}")]
        return c1 + left + right + right_value + left_value + op_instr + push + c2
    
    def resolveVariableDeclAndSet(self, vardeclandset):
        instr = [Comment(f"#var {vardeclandset.name} = {vardeclandset.expr}")]
        instr += vardeclandset.expr.resolve(self)
        instr += self.pop("t0")
        self.decl(vardeclandset.name)
        instr.append(Sw("sp", "t0", 0))
        instr.append(Addi("sp", "sp", 4))
        instr.append(Comment("#END varsetanddecl"))
        return instr
    
    def resolveVariableDecl(self, vardecl):
        self.decl(vardecl.name)

    def resolveVariableSet(self, varset):
        instr = [Comment(f"#{varset.name} = {varset.expr}")]
        instr += varset.expr.resolve(self)
        instr += self.pop("t0")

        stack_diff = 4 * (self.get(varset.name) - self.current_stack)
        instr.append(Sw("sp", "t0", stack_diff))
        instr.append(Comment(f"END varset"))
        return instr
    
    def resolveVariableGet(self, varget):
        stack_target = self.get(varget.name)
        stack_difference = 4 * (stack_target - self.current_stack)

        instr = [Comment(f"varget {varget.name}")]
        instr.append(Lw("t0", "sp", stack_difference))
        instr += self.pushReg("t0")
        instr.append(Comment(f"END varget"))

        return instr
    
    def resolveExprStatement(self, exprs):
        instr = exprs.s.resolve(self)
        instr.append(Addi("sp", "sp", -4))
        return instr
    
    def resolveDebug(self, debug):
        instr = debug.expr.resolve(self)
        instr.append(Debug())
        return instr
    
    def resolveBlock(self, block):
        self.beginScope()

        stack_start = self.current_stack

        instr = [Comment("#block start")]
        for s in block.statements.statements:
            instr += s.resolve(self)
        
        stack_diff = 4 * (stack_start - self.current_stack)
        instr.append(Addi("sp", "sp", stack_diff))
        instr.append(Comment("#END block"))
        self.current_stack = stack_start

        self.endScope()
        return instr


def comp(ast):
    c = Compiler(ast)
    instr = c.run()
    return instr
            
        

        
        

    
    
    
    