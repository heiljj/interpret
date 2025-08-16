from Tokenizer import TokenType

class ReturnValue(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value
    

binops = {
    TokenType.OP_PLUS : lambda x, y : x + y,
    TokenType.OP_MINUS : lambda x, y : x - y,
    TokenType.OP_MUL : lambda x, y : x * y,
    TokenType.OP_DIV : lambda x, y : x / y,

    TokenType.COMP_EQ : lambda x, y : x == y,
    TokenType.COMP_NEQ : lambda x, y : x != y,
    TokenType.COMP_LT_EQ : lambda x, y : x <= y,
    TokenType.COMP_GT_EQ : lambda x, y : x >= y,
    TokenType.COMP_LT : lambda x, y : x < y,
    TokenType.COMP_GT : lambda x, y : x > y,

    TokenType.OR : lambda x, y : x or y,
    TokenType.AND : lambda x, y : x and y
}

class Interpreter:
    def __init__(self):
        self.globals = {}
        self.locals = []
        self.scope = 0
        self.debug_info = None

    def interpret(self, ast):
        return ast.resolve(self)
    
    def beginScope(self):
        self.scope += 1
        self.locals.append({})
    
    def endScope(self):
        self.scope -= 1
        self.locals.pop()
    
    def decl(self, var):
        if self.scope == 0:
            self.declGlobal(var)
        else:
            self.declLocal(var)
    
    def declGlobal(self, var):
        if var in self.globals:
            raise Exception("Global already declared")

        self.globals[var] = None
    
    def declLocal(self, var):
        locals = self.locals[-1]

        if var in locals:
            raise Exception("Local already declared")
        
        locals[var] = None
    
    def set(self, var, value):
        for locals in reversed(self.locals):
            if var not in locals:
                continue

            locals[var] = value
            return
        
        if var not in self.globals:
            raise Exception("Variable not declared")
        
        self.globals[var] = value
    
    def get(self, var):
        for locals in reversed(self.locals):
            if var not in locals:
                continue

            return locals[var]

        
        if var not in self.globals:
            raise Exception("Variable does not exist")
        
        return self.globals[var]

    def resolveValue(self, value):
        return value.value
    
    def resolveBinaryOp(self, binop):
        left = binop.left.resolve(self)
        right = binop.right.resolve(self)

        return binops[binop.op](left, right)
    
    def resolveVariableDecl(self, vardecl):
        self.decl(vardecl.name)

        if vardecl.value != None:
            value = vardecl.value.resolve(self)
            self.set(vardecl.name, value)
        
        return value
    
    def resolveVariableSet(self, varset):
        value = varset.expr.resolve(self)
        self.set(varset.name, value)

        return value
    
    def resolveVariableDeclAndSet(self, vardeclset):
        self.decl(vardeclset.name)
        value = vardeclset.expr.resolve(self)
        self.set(vardeclset.name, value)

        return value
    
    def resolveVariableGet(self, varget):
        return self.get(varget.name)
    
    def resolveStatements(self, statements):
        value = None
        for s in statements.statements:
            value = s.resolve(self)
        
        return value

    
    def resolveDebug(self, debug):
        value = debug.expr.resolve(self)
        self.debug_info = value
        return value
    
    def resolveBlock(self, block):
        self.beginScope()
        value = block.statements.resolve(self)
        self.endScope()
        return value
    
    def resolveBlocks(self, blocks):
        for block in blocks.blocks:
            block.resolve(self)
    
    def resolveFunctionDecl(self, func):
        self.decl(func.name)
        self.set(func.name, func)
    
    def resolveFunctionCall(self, call):
        func = self.get(call.name)

        self.beginScope()

        for param, arg in zip(func.args, call.args):
            value = arg.resolve(self)

            if value == 1 or value == 0:
                t=1
            self.decl(param)
            self.set(param, value)

        scope = self.scope

        try:
            value = func.block.resolve(self)
        except ReturnValue as v:

            while scope != self.scope:
                self.endScope()
            
            self.endScope()
            return v.value

        self.endScope()
    
    def resolveReturn(self, r):
        raise ReturnValue(r.expr.resolve(self))
    
    def resolveIf(self, ifblock):
        cond = ifblock.cond.resolve(self)

        if cond:
            return ifblock.if_expr.resolve(self)
        else:
            if ifblock.else_expr != None:
                return ifblock.else_expr.resolve(self)

    def resolveWhile(self, wh):
        while (wh.cond.resolve(self)):
            wh.expr.resolve(self)




    