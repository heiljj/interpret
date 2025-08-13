# block       -> (stmt;);*
# stmt        -> assign_stmt
# assign_stmt -> 'var' [] = expr

# expr       1-> or_expr ('or' or_exp)*
# or_expr    2-> and_expr ('and' and_expr)*
# and_expr   3-> pm_expr ('+' | '-' pm_expr)*
# pm_expr    4-> md_expr ('*' | '/' md_expr)*
# md_expr    5-> String | Num

from Tokenizer import Token, TokenType, reverse_tokenmap

class Node:
    def __init__(self):
        pass
    
    def __repr__(self):
        printAstHelper(self)

class Debug(Node):
    def __init__(self, expr):
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveDebug(self)

class Statements(Node):
    def __init__(self, statements):
        self.statements = statements
    
    def resolve(self, interpret):
        return interpret.resolveStatements(self)

class VariableDecl(Node):
    def __init__(self, name):
        self.name = name
    
    def resolve(self, interpret):
        return interpret.resolveVariableDecl(self)

class VariableDeclAndSet(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveVariableDeclAndSet(self)

class VariableSet(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveVariableSet(self)

class VariableGet(Node):
    def __init__(self, name):
        self.name = name
    
    def resolve(self, interpret):
        return interpret.resolveVariableGet(self)

class BinaryOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    
    def resolve(self, interpret):
        return interpret.resolveBinaryOp(self)

class Value(Node):
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def resolve(self, interpret):
        return interpret.resolveValue(self)


# outside of parser class so it can follow the same format as generated functions 
def parseValue(self):
    token = self.next()

    match token.kind:
        case TokenType.NUM:
            return Value(TokenType.NUM, token.value)
        case TokenType.STR:
            return Value(TokenType.STR, token.value)
        case TokenType.IDENTIFIER:
            return VariableGet(token.value)
        case _:
            raise Exception("Token was not of kind value")

    
def defineBinaryOpFunction(prec, op):
    def parseBinaryOp(self):
        left = self.parsePrec(prec + 1)

        while self.isNext():
            token = self.peek()
            if token.kind == op:
                self.match(op)
                right = self.parsePrec(prec + 1)
                left = BinaryOp(left, op, right)
            else: 
                return left
    
        return left

    return parseBinaryOp

def generateParseStatements(prec):
    def parseStatements(self):
        statements = []
        while self.isNext():
            statements.append(self.parsePrec(prec + 1))
            self.match(TokenType.SEMI)

            if not self.isNext() or self.peek().kind == TokenType.BRAC_LEFT:
                break
        
        return Statements(statements)

    return parseStatements

def generateParseDebug(prec):
    def parseDebug(self):
        if not self.isNext():
            return
        
        token = self.peek()
        if token.kind == TokenType.DEBUG:
            self.match(TokenType.DEBUG)
            inner = self.parsePrec(prec+1)
            return Debug(inner)
        else:
            return self.parsePrec(prec+1)
    
    return parseDebug

def generateParseVarDecl(prec):
    def parseVarDecl(self):
        if not self.isNext():
            return
        
        token = self.peek()
        if token.kind == TokenType.DECL:
            self.match(TokenType.DECL)

            identifier = self.match(TokenType.IDENTIFIER)

            if self.peek().kind == TokenType.DECL_EQ:
                self.match(TokenType.DECL_EQ)
                right = self.parsePrec(prec + 1)
                return VariableDeclAndSet(identifier.value, right)
                
            return VariableDecl(identifier.value)
        
        return self.parsePrec(prec + 1)

    return parseVarDecl

def generateParseVarSet(prec):
    #TODO
    def parseVarSet(self):
        if not self.isNext():
            return
        
        token = self.peek()
        if token.kind != TokenType.IDENTIFIER:
            return self.parsePrec(prec + 1)
        
        token = self.next()

        if not self.isNext() or self.peek().kind != TokenType.DECL_EQ:
            self.previous()
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.DECL_EQ)

        expr = self.parsePrec(prec + 1)
        return VariableSet(token.value, expr)
            
    return parseVarSet

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0
        self.end = len(self.tokens)
    
        self.parsers = [
            generateParseStatements(0),
            generateParseDebug(1),
            generateParseVarDecl(2),
            generateParseVarSet(3),
            defineBinaryOpFunction(4, TokenType.OR),
            defineBinaryOpFunction(5, TokenType.AND),
            defineBinaryOpFunction(6, TokenType.COMP_EQ),
            defineBinaryOpFunction(7, TokenType.COMP_NEQ),
            defineBinaryOpFunction(8, TokenType.COMP_GT),
            defineBinaryOpFunction(9, TokenType.COMP_LT),
            defineBinaryOpFunction(10, TokenType.COMP_GT_EQ),
            defineBinaryOpFunction(11, TokenType.COMP_LT_EQ),
            defineBinaryOpFunction(12, TokenType.OP_PLUS),
            defineBinaryOpFunction(13, TokenType.OP_MINUS),
            defineBinaryOpFunction(14, TokenType.OP_MUL),
            defineBinaryOpFunction(15, TokenType.OP_DIV),
            parseValue
        ]

        self.ast = self.parsePrec(0)
    
    def match(self, t):
        token = self.tokens[self.index]
        self.index += 1

        if (t != token.kind):
            raise Exception(f"Expected token of type {t} but was {token.kind}")
        
        return token
    
    def next(self):
        token = self.tokens[self.index]
        self.index += 1
        return token
    
    def previous(self):
        self.index -= 1
    
    def isNext(self):
        return self.index + 1 < self.end
    
    def peek(self):
        return self.tokens[self.index]
    
    def parsePrec(self, prec):
        return self.parsers[prec](self)


def printAstHelper(node) -> str:
    if type(node) == Value:
        if node.type == TokenType.STR:
            return f'"{node.value}"'

        return node.value
    elif type(node) == Statements:
        return "".join(map(lambda x : printAstHelper(x) + ";\n", node.statements))
    elif type(node) == Debug:
        return f"DEBUG {printAstHelper(node.expr)}"
    elif type(node) == VariableDeclAndSet:
        return f"var {node.name} = {printAstHelper(node.expr)}"
    elif type(node) == VariableDecl:
        return f"var {node.name}"
    elif type(node) == VariableSet:
        return f"{node.name} = {printAstHelper(node.expr)}"
    elif type(node) == VariableGet:
        return f"{node.name} "
    else:
        op = reverse_tokenmap[node.op]
        return f"({printAstHelper(node.left)} {op} {printAstHelper(node.right)})"

def printAst(node):
    print("ast:")
    print(printAstHelper(node))

def parse(tokens: list[Token]):
    parser = Parser(tokens)
    return parser.ast



