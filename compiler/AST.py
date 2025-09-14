from Tokenizer import reverse_token_map

class ASTNode:
    def __init__(self):
        self.type = None

    def resolve(self, visitor):
        attr = visitor.__getattribute__(f"resolve{type(self).__name__}")
        return attr(self)

class Err(ASTNode):
    def __init__(self):
        super().__init__()

class Value(ASTNode):
    def __init__(self, type, value):
        super().__init__()
        self.type = type
        self.value = value
    
    def __str__(self):
        return str(self.value)

class Dereference(ASTNode):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

class Struct(ASTNode):
    def __init__(self, exprs):
        super().__init__()
        self.exprs = exprs

class List(ASTNode):
    def __init__(self, exprs):
        super().__init__()
        self.exprs = exprs
    
    def __str__(self):
        return str(self.exprs)

class StructLookUp(ASTNode):
    def __init__(self, identifier, expr=None):
        super().__init__()
        self.identifier = identifier
        self.expr = expr

class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right
    
    def __str__(self):
        return f"{self.left} {reverse_token_map[self.op]} {self.right}"

class VariableDecl(ASTNode):
    def __init__(self, name, expr, type_):
        super().__init__()
        self.name = name
        self.expr = expr
        self.type = type_
    
    def __str__(self):
        return f"var {self.name} = {self.expr};"

class VariableSet(ASTNode):
    def __init__(self, addr_expr, value_expr):
        super().__init__()
        self.addr_expr = addr_expr
        self.value_expr = value_expr
    
    def __str__(self):
        return f"{self.name} = {self.expr};"

class VariableGet(ASTNode):
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def __str__(self):
        return self.name 

class Debug(ASTNode):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr
    
    def __str__(self):
        return f"DEBUG {self.expr}"

class ExprStatement(ASTNode):
    def __init__(self, s):
        super().__init__()
        self.s = s
    
class Block(ASTNode):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
    
    def __str__(self):
        return f"{{{self.statements}}}"

class If(ASTNode):
    def __init__(self, cond, if_expr, else_expr):
        super().__init__()
        self.cond = cond
        self.if_expr = if_expr
        self.else_expr = else_expr

    def __str__(self):
        if self.else_expr:
            return f"if ({self.cond}) {self.if_expr} else {self.else_expr}"

class While(ASTNode):
    def __init__(self, cond, expr):
        super().__init__()
        self.cond = cond
        self.expr = expr
    
    def __str__(self):
        return f"while ({self.cond}) {self.expr}"

class Continue(ASTNode):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "continue;"
    
class Break(ASTNode):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "break;"

class FunctionDecl(ASTNode):
    def __init__(self, name, args, block, type_, argtypes):
        super().__init__()
        self.name = name
        self.args = args
        self.block = block
        self.type = type_
        self.argtypes = argtypes
    
    def __str__(self):
        arg_str = "".join(map(lambda x : x + ", ", self.args))
        if arg_str:
            arg_str = arg_str[:-2]

        return f"def {self.name}({arg_str}) {self.block}"

class FunctionCall(ASTNode):
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args
    
    def __str__(self):
        arg_str = "".join(map(lambda x : str(x) + ", ", self.args))
        if arg_str:
            arg_str = arg_str[:-2]
        
        return f"{self.name}({arg_str})"

class Return(ASTNode):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr
    
    def __str__(self):
        return f"return {self.expr};"

class Statements(ASTNode):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
    
    def __str__(self):
        return "".join(map(lambda x: str(x) + "\n", self.statements))