from Tokenizer import TokenType
from Parser import Type, INT
from Instruction import *

class Typechecker:
    def __init__(self, ast):
        self.globals = {}
        self.locals = []
        self.ast = ast

        self.expected_return_type = None
    
    def run(self):
        self.ast.resolve(self)
    
    def setExpectedReturnType(self, t):
        self.return_expected_type = t

    def getExpectedReturnType(self):
        return self.return_expected_type
    
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
    

    def resolveStatements(self, stmts):
        for s in stmts.statements:
            s.resolve(self)
    
    def resolveValue(self, value):
        return value.type
    
    def resolveErr(self, err):
        pass
            
    def resolveBinaryOp(self, op):
        left = op.left.resolve(self)
        right = op.right.resolve(self)

        if left != right:
            raise Exception(f"Typecheck error: {left} != {right} on {op}")
        
        op.type = left
        return left

        
    def resolveVariableDeclAndSet(self, vardeclandset):
        t = vardeclandset.expr.resolve(self)

        if t != vardeclandset.type:
            raise Exception(f"Typecheck error: {t} != {vardeclandset.type} on {vardeclandset}")
        
        self.decl(vardeclandset.name)
        self.set(vardeclandset.name, vardeclandset.type)
            
    def resolveVariableDecl(self, vardecl):
        self.decl(vardecl.name)
        self.set(vardecl.name, vardecl.type)

    def resolveVariableSet(self, varset):
        expected_type = self.get(varset.name)
        actual = varset.expr.resolve(self)

        if expected_type != actual:
            raise Exception(f"Typecheck error: variable {varset.name} of type {varset.type} assigned {varset.expr}")
    
    def resolveVariableGet(self, varget):
        return self.get(varget.name)

    def resolveExprStatement(self, exprs):
        exprs.s.resolve(self)
    
    def resolveDebug(self, debug):
        debug.expr.resolve(self)
    
    def resolveBlock(self, block):
        self.beginScope()
        block.statements.resolve(self)
        self.endScope()

    
    def resolveIf(self, if_):
        cond = if_.cond.resolve(self)

        if cond != INT:
            raise Exception(f"Typecheck error: if cond was type {cond}")
        
        if_.if_expr.resolve(self)

        if if_.else_expr:
            if_.else_expr.resolve(self)

    def resolveWhile(self, wh):
        cond = wh.cond.resolve(self)

        if cond != INT:
            raise Exception(f"Typecheck error: while cond was type {cond}")
        
        wh.expr.resolve(self)
    
    def resolveFor(self, for_):
        self.beginScope()
        for_.decl.resolve(self)
        cond = for_.cond.resolve(self)

        if cond != INT:
            raise Exception(f"Typecheck error: for cond was type {cond}")
        
        for_.assign.resolve(self)
        for_.block.resolve(self)
        self.endScope()
    
    def resolveFunctionDecl(self, fn):
        self.decl(fn.name)
        self.set(fn.name, fn)
        # works as long as there are not nested functions, which are not supported anyways
        self.setExpectedReturnType(fn.type)
        self.beginScope()

        if len(fn.args) != len(fn.argtypes):
            raise Exception("Mismatched args and argtypes")
        
        for i in range(len(fn.args)):
            self.decl(fn.args[i])
            self.set(fn.args[i], fn.argtypes[i])

        fn.block.resolve(self)

        self.endScope()
        self.set(fn.name, fn)
    
    def resolveFunctionCall(self, call):
        decl = self.get(call.name)

        if len(decl.args) != len(call.args):
            raise Exception(f"Typecheck error: Wrong number of args : {call}")
        
        for i in range(len(decl.args)):
            t = call.args[i].resolve(self)
            if t != decl.argtypes[i]:
                raise Exception(f"Typecheck error: arg of wrong type, call: {call} arg: {call.args[i]}")
        
        return decl.type
    
    def resolveReturn(self, ret):
        t = ret.expr.resolve(self)
        if t != self.getExpectedReturnType():
            raise Exception("Typecheck error: wrong return type")

        
def typecheck(ast):
    checker = Typechecker(ast)
    checker.run()
    