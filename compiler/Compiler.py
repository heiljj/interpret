from Tokenizer import TokenType
from Instruction import *
from Parser import INT, CHAR

class Compiler:
    def __init__(self, ast):
        self.ast = ast
        self.stream = ""

        self.current_stack = 0

        self.globals = {}
        self.locals = []

        self.function_instr = Instructions()
        self.functions = {}
    
    def run(self):
        instr = self.ast.resolve(self) + Stop()

        start = Instructions(Jal("x0", len(self.function_instr) * 4 + 4))
        return start + self.function_instr + instr
    
    def beginScope(self):
        self.locals.append({})
    
    def endScope(self):
        return self.locals.pop()
    
    def decl(self, var):
        self.bindPosition(var, 0)
        self.current_stack += 1
    
    def bindPosition(self, varname, rel_stack_pos):
        if self.locals:
            locals = self.locals[-1]

            if varname in locals:
                raise Exception("Variable already bound")

            locals[varname] = self.current_stack + rel_stack_pos
        else:
            if varname in self.globals:
                raise Exception("Variable already bound")

            self.globals[varname] = self.current_stack + rel_stack_pos

    def get(self, var):
        for locals in reversed(self.locals):
            if var not in locals:
                continue

            return locals[var]

        
        if var not in self.globals:
            raise Exception("Variable does not exist")
        
        return self.globals[var]
    


    def resolveStatements(self, stmts):
        instr = Instructions()
        for stmt in stmts.statements:
            instr += stmt.resolve(self)
        
        return instr
    
    def pushValue(self, binary):
        self.current_stack += 1

        return Instructions(
            Addi("t0", "x0", binary),
            Sw("sp", "t0", 0),
            Addi("sp", "sp", 4)
        )

    def pushReg(self, reg):
        self.current_stack += 1

        return Instructions(
            Sw("sp", reg, 0),
            Addi("sp", "sp", 4)
        )
    
    def pop(self, reg):
        self.current_stack -= 1

        return Instructions(
                Addi("sp", "sp", -4),
                Lw(reg, "sp", 0)
        )
    
    def resolveValue(self, value):
        if value.type == INT:
            return self.pushValue(Binary(value.value))
        
        if value.type == CHAR:
            return self.pushValue(ord(value.value))

        raise NotImplementedError
    
    def resolveErr(self, err):
        return Instructions(RaiseError())
            
    def resolveBinaryOp(self, op):
        instr = op.left.resolve(self)
        instr.commentFirst(f"#binaryop {op.left} {op.op.name} {op.right}")

        instr += op.right.resolve(self)
        instr += self.pop("t1")
        instr += self.pop("t0")
        
        op_instr = None

        match op.op:
            case TokenType.OP_PLUS:
                op_instr = Add("t0", "t0", "t1")
            case TokenType.OP_MINUS:
                op_instr = Sub("t0", "t0", "t1")
            case TokenType.OP_MUL:
                op_instr = Mul("t0", "t0", "t1")
            case TokenType.OP_DIV:
                op_instr = Div("t0", "t0", "t1")
            case TokenType.COMP_EQ:
                op_instr = Instructions(
                            Xor("t0", "t0", "t1"),
                            SltiU("t0", "t0", 1))

            case TokenType.COMP_NEQ:
                op_instr = Instructions(
                            Xor("t0", "t0", "t1"),
                            SltU("t0", "x0", "t0"))

            case TokenType.COMP_GT:
                op_instr = Instructions(
                            Sub("t0", "t0", "t1"),
                            Slt("t0", "x0", "t0"))

            case TokenType.COMP_LT:
                op_instr = Instructions(
                            Sub("t0", "t1", "t0"),
                            Slt("t0", "x0", "t0"))

            case TokenType.COMP_GT_EQ:
                op_instr = Instructions(
                            Sub("t0", "t1", "t0"),
                            Addi("t1", "x0", 1),
                            Slt("t0", "t0", "t1"))

            case TokenType.COMP_LT_EQ:
                op_instr = Instructions(
                            Sub("t0", "t0", "t1"),
                            Addi("t1", "x0", 1),
                            Slt("t0", "t0", "t1"))
            
            case TokenType.OR:
                op_instr = Instructions(
                            Or("t0", "t0", "t1"),
                            SltU("t0", "x0", "t0"))
            
            case TokenType.AND:
                op_instr = Instructions(
                            And("t0", "t0", "t1"),
                            SltU("t0", "x0", "t0"))

            case _:
                raise NotImplementedError
        
        instr += op_instr
        instr += self.pushReg("t0")
        instr.commentLast("#END binaryop")

        return instr
        
    
    def resolveVariableDeclAndSet(self, vardeclandset):

        instr = vardeclandset.expr.resolve(self)
        instr.commentFirst(f"#var {vardeclandset.name} = {vardeclandset.expr}")
        instr += self.pop("t0")
        self.decl(vardeclandset.name)

        instr += Sw("sp", "t0", 0)
        instr += Addi("sp", "sp", 4)
        instr.commentLast("#END varsetanddecl")
        return instr
    
    def resolveVariableDecl(self, vardecl):
        self.decl(vardecl.name)

    def resolveVariableSet(self, varset):
        instr = varset.expr.resolve(self)
        instr.commentFirst(f"#{varset.name} = {varset.expr}")
        instr += self.pop("t0")

        stack_diff = 4 * (self.get(varset.name) - self.current_stack)
        instr += Sw("sp", "t0", stack_diff)
        instr.commentLast(f"END varset")
        return instr
    
    def resolveVariableGet(self, varget):
        stack_target = self.get(varget.name)
        stack_difference = 4 * (stack_target - self.current_stack)

        instr = Instructions(Lw("t0", "sp", stack_difference))
        instr.commentFirst(f"varget {varget.name}")
        instr += self.pushReg("t0")
        instr.commentLast(f"END varget")

        return instr
    
    def resolveExprStatement(self, exprs):
        instr = exprs.s.resolve(self)
        instr += Addi("sp", "sp", -4)
        self.current_stack -= 1
        return instr
    
    def resolveDebug(self, debug):
        instr = debug.expr.resolve(self)
        instr += Debug()
        return instr
    
    def resolveBlock(self, block):
        if not block.statements:
            return Instructions()

        self.beginScope()

        stack_start = self.current_stack

        instr = block.statements.resolve(self)
        instr.commentFirst("#block start")
        
        stack_diff = 4 * (stack_start - self.current_stack)
        instr += Addi("sp", "sp", stack_diff)
        instr.commentLast("#END block")
        self.current_stack = stack_start

        self.endScope()
        return instr
    
    def resolveIf(self, if_):
        cond = if_.cond.resolve(self)
        cond.commentFirst("#IF cond start")
        cond += self.pop("t0")

        if if_.else_expr:

            else_expr = if_.else_expr.resolve(self)
            else_expr.commentFirst("#ELSE expr start")
            else_expr.commentLast("#END else expr")

            if_expr = if_.if_expr.resolve(self)
            if_expr.commentFirst("IF expr start")

            if_expr += Beq("x0", "x0", 4 * len(else_expr) + 4)
            if_expr.commentLast("#IF expr end")

            cond += Beq("t0", "x0", 4 * len(if_expr) + 4)
            cond.commentLast("#IF cond end")
            return cond + if_expr + else_expr

        else:
            if_expr = if_.if_expr.resolve(self)
            if_expr.commentFirst("#IF expr start")
            cond += Beq("t0", "x0", 4 * len(if_expr) + 4)
            cond.commentLast("#IF cond end")
            return cond + if_expr

    def resolveWhile(self, wh):
        cond = wh.cond.resolve(self)
        cond.commentFirst(f"#WHILE {wh.cond}")
        cond += self.pop("t0")

        block = wh.expr.resolve(self)
        block += Beq("x0", "x0", - 4 * len(block) - 4 * len(cond) - 4)
        block.commentLast("#END while")
        cond += (Beq("t0", "x0", 4 * len(block) + 4))
        return cond + block
    
    def resolveFor(self, for_):
        self.beginScope()
        decl = for_.decl.resolve(self)
        decl.commentFirst("#FOR")
        decl.commentLast("#for decl end")

        cond = for_.cond.resolve(self)
        cond.commentFirst("#COND start")
        cond += self.pop("t0")
        cond.commentLast("#COND end")

        block = for_.block.resolve(self)
        block += for_.assign.resolve(self)
        block += Beq("x0", "x0", -4 * len(cond) - 4 * len(block))
        block.commentFirst("body start")

        cond += Beq("t0", "x0", 4 * len(block) + 4)
        
        return decl + cond + block
    
    def resolveFunctionDecl(self, fn):
        self.functions[fn.name] = len(self.function_instr) * 4 + 4

        self.beginScope()

        for i, arg in enumerate(fn.args):
            self.bindPosition(arg, -1 * (len(fn.args) - i))
        
        instr = self.pushReg("ra")
        instr.commentFirst(f"# function {fn.name}")
        instr.commentLast("# ra pushed to stack")

        # adds return value to stack
        self.function_stack = self.current_stack
        instr += fn.block.resolve(self).commentFirst("# resolve function block")

        self.linkFutureBeq(instr, 4 * len(instr))

        # TODO copy return value to the bottom of the stack instead of using a0

        instr.commentLast("# end function block")
        instr += self.pop("ra").commentFirst("# start of function exit prec")
        instr += Addi("sp", "sp", -4 * len(fn.args))
        instr.commentLast("# restore stack")
        instr += Jalr("x0", "ra", 0)
        self.endScope()

        self.function_instr += instr

        return Instructions()
    
    def resolveFunctionCall(self, call):
        instr = Instructions()
        for arg in call.args:
            instr += arg.resolve(self)

        instr += Jalr("ra", "x0", self.functions[call.name])
        self.current_stack -= len(call.args)
        instr.commentFirst(f"#CALL {call.name}")
        instr += self.pushReg("a0")
        instr.commentLast("#END call")
        return instr
    
    def resolveReturn(self, ret):
        instr = ret.expr.resolve(self)
        instr += self.pop("a0")
        instr += Addi("sp", "sp", 4 * self.function_stack - 4 * self.current_stack)
        instr += FutureBeq("x0", "x0")
        instr.commentFirst("# return start")
        instr.commentLast("# return jump")
        return instr
    
    def linkFutureBeq(self, instructions, addr_rel_start):
        for i, instr in enumerate(instructions):
            if type(instr) == FutureBeq:
                instructions[i] = Beq("x0", "x0", addr_rel_start - i * 4)
                instructions[i].comment = instr.comment





        

        


# -pass args through stack, ra 
# -bind stack positions to variables
# -put ra on stack
# execute stuff
# put return in arg
# pop args from stack, return to ra
# add returned value to stack



def comp(ast):
    c = Compiler(ast)
    instr = c.run().instr
    return instr
            
        

        
        

    
    
    
    