from Types import *
from Parser import INT, VOID

from Instruction import *

class TypeError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class Typechecker:
    def __init__(self, ast):
        self.globals = {}
        self.locals = []
        self.ast = ast

        self.expected_return_type = None
        self.found_return = True
    
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

    def resolveErr(self, err):
        pass
    
    def resolveValue(self, value):
        return value.type
    
    def resolveDereference(self, ref):
        t = ref.expr.resolve(self)

        if type(t) != PointerType:
            raise TypeError("Deref on non pointer")
        
        ref.type = t.type
        return t.type

    def resolveStruct(self, struct):
        types = []
        for expr in struct.exprs:
            types.append(expr.resolve(self))
        
        t = UnknownStructType(types)
        struct.type = t
        return t

    def resolveList(self, l):
        if not l.exprs:
            return PointerType(VOID, 0)
        
        expected_type = l.exprs[0].resolve(self)
        for i in range(1, len(l.exprs)):
            actual_type = l.exprs[i].resolve(self)

            if not expected_type == actual_type:
                raise TypeError(f"List init type mismatch expected {expected_type} was {actual_type}")
        
        return PointerType(actual_type, len(l.exprs))

    def resolveBinaryOp(self, op):
        left = op.left.resolve(self)
        right = op.right.resolve(self)

        if left != right and not (type(left) == PointerType and right == INT):
            raise TypeError(f"{left} != {right} on {op}")
        
        op.type = left
        return left
    
    def resolveStructLookUp(self, slu):
        expr = slu.expr.resolve(self)
        slu.type = expr

        if type(expr) != PointerType:
            raise TypeError("expected incoming type of struct look up to be a pointer")
        
        if type(expr.type) != StructType:
            raise TypeError("expected struct but found pointer")

        return PointerType(expr.type.getPropertyType(slu.identifier))

    def resolveVariableDecl(self, vardecl):
        self.decl(vardecl.name)
        self.set(vardecl.name, vardecl.type)

        if vardecl.expr:
            t = vardecl.expr.resolve(self)
            if vardecl.type != t:
                raise TypeError(f"variable {vardecl.name} assigned {vardecl.expr}")

    def resolveVariableSet(self, varset):
        addr_expr = varset.addr_expr.resolve(self)
        value_expr = varset.value_expr.resolve(self)

        if addr_expr != PointerType(value_expr):
            raise TypeError(f"address {varset.addr_expr} of type {addr_expr} assigned {varset.value_expr} of type {value_expr}")

    def resolveVariableGet(self, varget):
        var_type = self.get(varget.name)
        var_type = PointerType(var_type)
        varget.type = var_type
        return var_type
    
    def resolveDebug(self, debug):
        debug.expr.resolve(self)

    def resolveExprStatement(self, exprs):
        exprs.s.resolve(self)

    def resolveBlock(self, block):
        self.beginScope()
        block.statements.resolve(self)
        self.endScope()

    def resolveIf(self, if_):
        cond = if_.cond.resolve(self)

        if cond != INT:
            raise TypeError(f"if cond was type {cond}")
        
        if_.if_expr.resolve(self)

        if if_.else_expr:
            if_.else_expr.resolve(self)

    def resolveWhile(self, wh):
        cond = wh.cond.resolve(self)

        if cond != INT:
            raise Exception(f"Typecheck error: while cond was type {cond}")
        
        wh.expr.resolve(self)
    
    def resolveFunctionDecl(self, fn):
        self.decl(fn.name)
        self.set(fn.name, fn)
        # works as long as there are not nested functions, which are not supported anyways
        self.setExpectedReturnType(fn.type)
        self.found_return = False
        self.beginScope()

        if len(fn.args) != len(fn.argtypes):
            raise Exception("Mismatched args and argtypes")
        
        for i in range(len(fn.args)):
            self.decl(fn.args[i])
            self.set(fn.args[i], fn.argtypes[i])

        fn.block.resolve(self)

        if not self.found_return:
            raise TypeError("Function with no return")

        self.endScope()
        self.set(fn.name, fn)
    
    def resolveFunctionCall(self, call):
        decl = self.get(call.name)

        if len(decl.args) != len(call.args):
            raise TypeError(f"Wrong number of args : {call}")
        
        for i in range(len(decl.args)):
            t = call.args[i].resolve(self)
            if t != decl.argtypes[i]:
                raise TypeError(f"arg of wrong type, call: {call} arg: {call.args[i]}")
        
        call.type = decl.type
        return decl.type
    
    def resolveReturn(self, ret):
        self.found_return = True
        t = ret.expr.resolve(self)
        if self.getExpectedReturnType() != t:
            raise TypeError("wrong return type")

    def resolveStatements(self, stmts):
        for s in stmts.statements:
            s.resolve(self)

        
def typecheck(ast):
    checker = Typechecker(ast)
    checker.run()
    