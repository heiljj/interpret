from Tokenizer import TokenType
from Instruction import *
from Parser import INT, CHAR, VOID, PointerType, StructType, StructLookUp, ListIndex
from StackManager import StackManager

class Compiler:
    def __init__(self, ast, types):
        self.ast = ast
        self.types = types

        self.stack = StackManager()

        self.globals = {}
        self.locals = []

        self.function_instr = Instructions()
        self.function_addrs = {}
        self.function_returns = {}
    
    def run(self):
        instr = self.ast.resolve(self) + Stop()

        start = Instructions(Jal("x0", len(self.function_instr) * 4 + 4))
        return start + self.function_instr + instr
    
    def beginScope(self):
        self.locals.append({})
    
    def endScope(self):
        return self.locals.pop()
    
    def bindPosition(self, varname, type_, rel_stack_pos):
        if self.locals:
            locals = self.locals[-1]

            if varname in locals:
                raise Exception("Variable already bound")

            locals[varname] = (type_, self.stack.getCurrent() + rel_stack_pos)
        else:
            if varname in self.globals:
                raise Exception("Variable already bound")

            self.globals[varname] = (type_, self.stack.getCurrent() + rel_stack_pos)

    def get(self, var):
        for locals in reversed(self.locals):
            if var not in locals:
                continue

            return locals[var]

        if var not in self.globals:
            raise Exception("Variable does not exist")
        
        return self.globals[var]
    
    def push(self, value):
        self.stack.push(VOID)

        return Instructions(
            Addi("t0", "x0", value),
            Sw("sp", "t0", 0),
            Addi("sp", "sp", 4)
        )

    def pushReg(self, reg):
        self.stack.push(VOID)

        return Instructions(
            Sw("sp", reg, 0),
            Addi("sp", "sp", 4)
        )
    
    def pop(self, reg):
        self.stack.pop()

        return Instructions(
                Addi("sp", "sp", -4),
                Lw(reg, "sp", 0)
        )

    def linkFutureBeq(self, instructions, addr_rel_start):
        for i, instr in enumerate(instructions):
            if type(instr) == FutureBeq:
                instructions[i] = Beq("x0", "x0", addr_rel_start - i * 4)
                instructions[i].comment = instr.comment

    def walkIndexes(self, type_, tree):
        instr = Instructions()

        while tree:
            if type(tree) == StructLookUp:
                offset = 4 * type_.getPropertyOffset(tree.identifier)
                instr += self.pop("t0")
                instr += Addi("t0", "t0", offset)
                instr += self.pushReg("t0")

                type_ = tree.type
                tree = tree.next

            elif type(tree) == ListIndex:
                instr += tree.expr.resolve(self)
                instr += self.pop("t0")

                instr += Addi("t1", "x0", type_.type.getWords() * 4)
                instr += Mul("t0", "t1", "t0")

                instr += self.pop("t1")

                instr += Add("t0", "t0", "t1")
                instr += self.pushReg("t0")

                type_ = tree.type
                tree = tree.next

            else:
                raise Exception()
        
        return instr, type_

    def resolveErr(self, err):
        return Instructions(RaiseError())

    def resolveValue(self, value):
        if value.type == INT or type(value) == PointerType:
            return self.push(Binary(value.value))
        
        if value.type == CHAR:
            return self.push(ord(value.value))

        raise NotImplementedError
    
    def resolveStruct(self, struct):
        instr = Instructions()
        for expr in struct.exprs:
            instr += expr.resolve(self)
        
        self.stack.popItems(len(struct.exprs))
        self.stack.push(struct.type)
        
        return instr
    
    def resolveList(self, l):
        instr = Instructions()
        for expr in l.exprs:
            instr += expr.resolve(self)
        
        return instr
            
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
        
    def resolveVariableDecl(self, vardecl):
        self.bindPosition(vardecl.name, vardecl.type, 0)

        if vardecl.expr:
            instr = vardecl.expr.resolve(self)
            instr.commentLast("END varsetanddecl")
            return instr

        instr = Instructions()
        for _ in range(vardecl.type.getWords()):
            instr += self.push(0)

        return instr
    
    def resolveVariableSet(self, varset):
        instr = varset.expr.resolve(self)
        instr.commentFirst(f"#{varset.name} = {varset.expr}")

        type_, pos = self.get(varset.name)
        stack_diff = self.stack.getCurrent() - pos

        byte_amount = self.stack.pop()

        instr += self.push(byte_amount - stack_diff)
        if varset.lookup:
            index_instr, _ = self.walkIndexes(type_, varset.lookup)
            instr += index_instr

        instr += self.pop("t1")

        for _ in range(byte_amount // 4):
            instr += Addi("sp", "sp", -4)
            instr += Lw("t0", "sp", 0)
            instr += Add("t2", "t1", "sp")
            instr += Sw("t2", "t0", 0)
        
        return instr

    def resolveVariableGet(self, varget):
        type_, pos = self.get(varget.name)
        instr = Instructions()

        instr += self.push(pos - self.stack.getCurrent())

        if varget.lookup:
            index_instr, type_ = self.walkIndexes(type_, varget.lookup)
            instr += index_instr

        byte_amount = type_.getWords() * 4
        instr += self.pop("t1")

        for _ in range(byte_amount // 4):
            instr += Add("t0", "sp", "t1")
            instr += Lw("t0", "t0", 0)
            instr += Sw("sp", "t0", 0)
            instr += Addi("sp", "sp", 4)
        
        self.stack.push(type_)
        instr.commentFirst(f"varget {varget.name}")
        instr.commentLast(f"END varget")
        return instr

    def resolveDebug(self, debug):
        instr = debug.expr.resolve(self)
        instr += Debug()
        return instr
    
    def resolveExprStatement(self, exprs):
        instr = exprs.s.resolve(self)
        amount = self.stack.pop()
        instr += Addi("sp", "sp", -amount)
        return instr
    
    def resolveBlock(self, block):
        if not block.statements:
            return Instructions()

        self.beginScope()

        stack_start = self.stack.getCurrent()

        instr = block.statements.resolve(self)
        instr.commentFirst("#block start")
        
        stack_diff = stack_start - self.stack.getCurrent()
        instr += Addi("sp", "sp", stack_diff)
        instr.commentLast("#END block")
        self.stack.popUntil(stack_start)

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
    
    def resolveContinue(self, cont):
        raise NotImplementedError()
    
    def resolveBreak(self, cont):
        raise NotImplementedError()
    
    def resolveFunctionDecl(self, fn):
        self.function_addrs[fn.name] = len(self.function_instr) * 4 + 4
        self.function_returns[fn.name] = fn.type

        self.beginScope()

        for i, arg in enumerate(fn.args):
            self.bindPosition(arg, fn.argtypes[i], -4 * fn.argtypes[i].getWords() * (len(fn.args) - i))
        
        instr = self.pushReg("ra")
        instr.commentFirst(f"# function {fn.name}")
        instr.commentLast("# ra pushed to stack")

        # adds return value to stack
        self.function_stack = self.stack.getCurrent()
        instr += fn.block.resolve(self).commentFirst("# resolve function block")

        self.linkFutureBeq(instr, 4 * len(instr))

        instr.commentLast("# end function block")
        instr += self.pop("ra").commentFirst("# start of function exit prec")
        instr += Addi("sp", "sp", -4 * len(fn.args))
        instr.commentLast("# restore stack")

        # copy old stack
        b = fn.type.getWords()

        for i in range(b):
            instr += Lw("t0", "a0", -4 * b + i * 4)

            instr += Sw("sp", "t0", 0)
            instr += Addi("sp", "sp", 4)
        
        self.stack.push(fn.type)

        instr += Jalr("x0", "ra", 0)
        self.endScope()

        self.function_instr += instr

        return Instructions()
    
    def resolveFunctionCall(self, call):
        instr = Instructions()
        for arg in call.args:
            instr += arg.resolve(self)

        instr += Jalr("ra", "x0", self.function_addrs[call.name])
        self.stack.popItems(len(call.args))
        self.stack.push(self.function_returns[call.name])
        instr.commentFirst(f"#CALL {call.name}")
        instr.commentLast("#END call")
        return instr
    
    def resolveReturn(self, ret):
        instr = ret.expr.resolve(self)
        instr += Addi("a0", "sp", 0)
        instr += Addi("sp", "sp", self.function_stack - self.stack.getCurrent())
        instr += FutureBeq("x0", "x0")
        instr.commentFirst("# return start")
        instr.commentLast("# return jump")
        return instr
    
    def resolveStatements(self, stmts):
        instr = Instructions()
        for stmt in stmts.statements:
            instr += stmt.resolve(self)
        
        return instr

def comp(ast, types):
    c = Compiler(ast, types)
    instr = c.run().instr
    return instr
            
        

        
        

    
    
    
    