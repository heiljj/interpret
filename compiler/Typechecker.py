from Parser import INT, CHAR, VOID, BaseType, StructType, PointerType, UnknownStructType, StructLookUp, ListIndex

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

            if expected_type != actual_type:
                raise TypeError(f"List init type mismatch expected {expected_type} was {actual_type}")
        
        return PointerType(actual_type, len(l.exprs))


    def resolveErr(self, err):
        pass
            
    def resolveBinaryOp(self, op):
        left = op.left.resolve(self)
        right = op.right.resolve(self)

        if left != right:
            raise TypeError(f"{left} != {right} on {op}")
        
        op.type = left
        return left
            
    def resolveVariableDecl(self, vardecl):
        self.decl(vardecl.name)
        self.set(vardecl.name, vardecl.type)

        if not vardecl.expr:
            return
        
        actual = vardecl.expr.resolve(self)
        if not vardecl.type.equiv(actual):
            raise TypeError(f"variable {vardecl.name} of type {vardecl.type} assigned {vardecl.expr}")
            

    def resolveVariableSet(self, varset):
        expected_type = self.get(varset.name)
        actual = varset.expr.resolve(self)

        if not expected_type.equiv(actual):
            raise TypeError(f"variable {varset.name} of type {varset.type} assigned {varset.expr}")
    
    def resolveVariableGet(self, varget):
        var_type = self.get(varget.name)

        if not varget.lookup:
            return var_type
        
        last_type = var_type
        next_ = varget.lookup

        while next_:
            if type(next_) == StructLookUp:
                if next_.identifier not in last_type.properties:
                    raise Exception(f"Property {next_.identifier} not a member of struct {last_type}")
                
                last_type = last_type.getPropertyType(next_.identifier)
            
            elif type(next_) == ListIndex:
                if type(last_type) != PointerType:
                    raise Exception("Index on non pointer")
                
                if next_.expr.resolve(self) != INT:
                    raise Exception("Non int index")
                
                last_type = last_type.type

            else:
                raise Exception()
            
            next_.type = last_type
            next_ = next_.next
        
        varget.type = last_type
        return last_type

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
            raise TypeError(f"Wrong number of args : {call}")
        
        for i in range(len(decl.args)):
            t = call.args[i].resolve(self)
            if t != decl.argtypes[i]:
                raise TypeError(f"arg of wrong type, call: {call} arg: {call.args[i]}")
        
        return decl.type
    
    def resolveReturn(self, ret):
        t = ret.expr.resolve(self)
        if self.getExpectedReturnType() != t:
            raise TypeError("wrong return type")

        
def typecheck(ast):
    checker = Typechecker(ast)
    checker.run()
    