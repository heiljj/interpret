from Types import *
from AST import StructLookUp, ListIndex
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

    def walkIndexes(self, type_, next_):
        while next_:
            if type(next_) == StructLookUp:
                if next_.identifier not in type_.properties:
                    raise Exception(f"Property {next_.identifier} not a member of struct {type_}")
                
                type_ = type_.getPropertyType(next_.identifier)
            
            elif type(next_) == ListIndex:
                if type(type_) != PointerType:
                    raise Exception("Index on non pointer")
                
                if next_.expr.resolve(self) != INT:
                    raise Exception("Non int index")
                
                type_ = type_.type

            else:
                raise Exception()
            
            next_.type = type_
            next_ = next_.next
        
        return type_

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
    
    def resolveLookUpRoot(self, lur):
        expr = lur.expr.resolve(self)
        lur.next.type = expr
        t = lur.next.resolve(self)
        lur.type = t
        return t
    
    def resolveStructLookUp(self, slu):
        t = slu.type.getPropertyType(slu.identifier)

        if slu.next:
            slu.next.type = t
            return slu.next.resolve(self)
        
        return t
    
    def resolveListIndex(self, li):
        if type(li.type) != PointerType:
            raise TypeError("Non pointer list")

        expr = li.expr.resolve(self)

        if expr != INT:
            raise TypeError("Non int index")
    
        if li.next:
            li.next.type = li.type.type
            return li.next.resolve(self)
        
        return li.type.type

    def resolveVariableDecl(self, vardecl):
        self.decl(vardecl.name)
        self.set(vardecl.name, vardecl.type)

        if not vardecl.expr:
            return
        
        actual = vardecl.expr.resolve(self)
        if not vardecl.type == actual:
            raise TypeError(f"variable {vardecl.name} of type {vardecl.type} assigned {vardecl.expr}")

    def resolveVariableSet(self, varset):
        expected_type = self.get(varset.name)
        actual = varset.expr.resolve(self)

        if not varset.lookup:
            if not expected_type == actual:
                raise TypeError(f"variable {varset.name} of type {expected_type} assigned {varset.expr}")

            return
        
        last_type = self.walkIndexes(expected_type, varset.lookup)
        
        if not last_type == actual:
            raise Exception(f"Property {last_type.identifier} not a member of struct {last_type}")

    def resolveVariableGet(self, varget):
        var_type = self.get(varget.name)
        varget.type = var_type
        return var_type
    
    def resolveVariableGetReference(self, vargetref):
        t = self.resolveVariableGet(vargetref)
        if vargetref.lookup:
            vargetref.lookup.type = t
            t = vargetref.lookup.resolve(self)

        return PointerType(t, 0)
    
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
    