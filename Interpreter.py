from Tokenizer import TokenType
from Parser import BinaryOp, Value


binops = {
    TokenType.OP_PLUS : lambda x, y : x + y,
    TokenType.OP_MINUS : lambda x, y : x - y,
    TokenType.OP_MUL : lambda x, y : x * y,
    TokenType.OP_DIV : lambda x, y : x / y,

    TokenType.COMP_EQ : lambda x, y : x == y,
    TokenType.COMP_LT_EQ : lambda x, y : x <= y,
    TokenType.COMP_GT_EQ : lambda x, y : x >= y,
    TokenType.COMP_LT : lambda x, y : x < y,
    TokenType.COMP_GT : lambda x, y : x > y,

    TokenType.OR : lambda x, y : x or y,
    TokenType.AND : lambda x, y : x and y

}

class Interpreter:
    def __init__(self, ast):
        self.ast = ast

        self.globals = {}
        self.locals = []
        self.scope = 0

        self.res = ast.resolve(self)

    
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
    
    def resolveVariableSet(self, varset):
        value = varset.value.resolve(self)
        self.set(varset.name, value)
    