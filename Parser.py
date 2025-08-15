from Tokenizer import Token, TokenType, reverse_token_map

class Node:
    def __repr__(self):
        return printAstHelper(self)


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


class Block(Node):
    def __init__(self, statements: Statements):
        self.statements = statements
    
    def resolve(self, interpret):
        return interpret.resolveBlock(self)

class If(Node):
    def __init__(self, cond, if_expr, else_expr):
        self.cond = cond
        self.if_expr = if_expr
        self.else_expr = else_expr
    
    def resolve(self, interpret):
        interpret.resolveIf(self)


class While(Node):
    def __init__(self, cond, expr):
        self.cond = cond
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveWhile(self)


class Continue(Node):
    def __init__(self):
        pass

    def resolve(self, interpret):
        interpret.resolveContinue(self)
    

class Break(Node):
    def __init__(self):
        pass

    def resolve(self, interpret):
        interpret.resolveBreak(self)


class FunctionDecl(Node):
    def __init__(self, name, args, block):
        self.name = name
        self.args = args
        self.block = block
    
    def resolve(self, interpret):
        return interpret.resolveFunctionDecl(self)


class Return(Node):
    def __init__(self, expr):
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveReturn(self)


class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args
    
    def resolve(self, interpret):
        return interpret.resolveFunctionCall(self)


class VariableDeclAndSet(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveVariableDeclAndSet(self)


class VariableDecl(Node):
    def __init__(self, name):
        self.name = name
    
    def resolve(self, interpret):
        return interpret.resolveVariableDecl(self)


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
def generateParseValue(expression_prec):
    def parseValue(self):
        token = self.next()

        match token.kind:
            case TokenType.NUM:
                return Value(TokenType.NUM, token.value)
            case TokenType.STR:
                return Value(TokenType.STR, token.value)
            case TokenType.IDENTIFIER:
                return VariableGet(token.value)
            case TokenType.BOOL:
                return Value(TokenType.BOOL, token.value)
            case _:
                return self.parsePrec(expression_prec)
    
    return parseValue

    
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

            if not self.isNext() or self.peek().kind == TokenType.BRAC_RIGHT:
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
                self.match(TokenType.SEMI)
                return VariableDeclAndSet(identifier.value, right)
                
            self.match(TokenType.SEMI)
            return VariableDecl(identifier.value)
        
        return self.parsePrec(prec + 1)

    return parseVarDecl

def generateParseVarSet(prec):
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
        self.match(TokenType.SEMI)
        return VariableSet(token.value, expr)
            
    return parseVarSet

def generateParseBlock(prec):
    def parseBlock(self):
        if not self.isNext():
            return
        
        token = self.peek()
        if token.kind == TokenType.BRAC_LEFT:
            self.match(TokenType.BRAC_LEFT)
            
            if self.peek().kind == TokenType.BRAC_RIGHT:
                self.match(TokenType.BRAC_RIGHT)
                return Block(Value(TokenType.NUM, 0))

            middle = self.parsePrec(0)

            self.match(TokenType.BRAC_RIGHT)

            return Block(middle)
        
        return self.parsePrec(prec + 1)
    
    return parseBlock

def generateParseBlocks(prec):
    def parseBlocks(self):
        if not self.isNext():
            return
        
        if self.peek().kind != TokenType.BRAC_LEFT:
            return self.parsePrec(prec + 1)

        blocks = []

        while self.isNext():
            blocks.append(self.parsePrec(prec + 1))
        
        return blocks
    
    return parseBlocks

def generateParseFunctionDefinition(prec, block_prec):
    def parseFunctionDefinition(self):
        if not self.isNext():
            return
        
        token = self.peek()

        if token.kind != TokenType.FUNC:
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.FUNC)
        identifier = self.match(TokenType.IDENTIFIER).value
        self.match(TokenType.PAR_LEFT)

        args = []

        while self.peek().kind == TokenType.IDENTIFIER:
            args.append(self.next().value)

            if self.peek().kind == TokenType.COMMA:
                self.match(TokenType.COMMA)
            else:
                break

        self.match(TokenType.PAR_RIGHT)

        # TODO might need to use block prec here?
        block = self.parsePrec(block_prec)

        return FunctionDecl(identifier, args, block)
    return parseFunctionDefinition

def generateParseFunctionCall(prec, expression_prec):
    def parseFunctionCall(self):
        if not self.isNext():
            return
        
        token = self.peek()

        if token.kind != TokenType.IDENTIFIER:
            return self.parsePrec(prec + 1)
        
        identifier = self.next()

        if not self.isNext():
            self.previous()
            return self.parsePrec(prec + 1)

        if self.peek().kind != TokenType.PAR_LEFT:
            self.previous()
            return self.parsePrec(prec + 1)
        
        args = []
        self.match(TokenType.PAR_LEFT)

        while self.peek().kind != TokenType.PAR_RIGHT:
            args.append(self.parsePrec(expression_prec))
        
        self.match(TokenType.PAR_RIGHT)

        return FunctionCall(identifier.value, args)
    
    return parseFunctionCall

def generateParseReturn(prec, expression_prec):
    def parseReturn(self):
        if not self.isNext():
            return
        
        token = self.peek()

        if token.kind != TokenType.RETURN:
            return self.parsePrec(prec + 1)
        
        expr = self.parsePrec(expression_prec)
        self.match(TokenType.SEMI)
        return Return(expr)
    
    return parseReturn

def generateParseIf(prec, block_prec, expr_prec):
    def parseIf(self):
        if not self.isNext():
            return
        
        token = self.peek()

        if token.kind != TokenType.IF:
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.IF)
        self.match(TokenType.PAR_LEFT)

        cond = self.parsePrec(expr_prec)

        self.match(TokenType.PAR_RIGHT)

        if_expr = self.parsePrec(block_prec)

        if not self.isNext():
            return If(cond, if_expr, None)
        
        self.match(TokenType.ELSE)
        
        else_expr = self.parsePrec(block_prec)

        return If(cond, if_expr, else_expr)
    
    return parseIf

def generateParseWhile(prec, block_prec, expr_prec):
    def parseWhile(self):
        if not self.isNext():
            return
        
        token = self.peek()

        if token.kind != TokenType.WHILE:
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.WHILE)
        self.match(TokenType.PAR_LEFT)

        cond = self.parsePrec(expr_prec)

        self.match(TokenType.PAR_RIGHT)

        block = self.parsePrec(block_prec)

        return While(cond, block)
    
    return parseWhile

def generateParseFor(prec, block_prec, var_decl_prec):
    def parseFor(self):
        if not self.isNext():
            return
        
        token = self.peek()

        if token.kind != TokenType.FOR:
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.FOR)
        self.match(TokenType.PAR_LEFT)

        assign = self.parsePrec(var_decl_prec)
        cond = self.parsePrec(var_decl_prec)
        self.match(TokenType.SEMI)
        incr = self.parsePrec(var_decl_prec)

        self.match(TokenType.PAR_RIGHT)

        block = self.parsePrec(block_prec)

        while_body = Statements([block, incr])
        while_loop = While(cond, while_body)
        for_loop = Statements([assign, while_loop])

        return Block(for_loop)
    return parseFor

# statements -> (function | assignment | decl | block | statement)*

# function -> identifier(identifier*) block
# delc -> var identifier; | var identifier = expr;
# assignment -> identifier = expr;
# block -> {statements}

# expr -> or_expr (or or_expr)*
# ...
# div_expr -> Value (/ Value*)
# Value -> num | str

# statements -> expression*
# expression -> declaration
# declaration -> var identifier (= )?; | assignment
# assignment -> identifier = or_expr; | or_expr;

        
class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0
        self.end = len(self.tokens)

        self.parsers = [
            generateParseStatements(0),
            generateParseFunctionDefinition(1, 5),
            generateParseWhile(2, 5, 10),
            generateParseFor(3, 5, 7),
            generateParseIf(4, 5, 10),
            generateParseBlock(5),
            generateParseDebug(6),
            generateParseVarDecl(7),
            generateParseVarSet(8),
            generateParseReturn(9, 10),
            defineBinaryOpFunction(10, TokenType.OR),
            defineBinaryOpFunction(11, TokenType.AND),
            defineBinaryOpFunction(12, TokenType.COMP_EQ),
            defineBinaryOpFunction(13, TokenType.COMP_NEQ),
            defineBinaryOpFunction(14, TokenType.COMP_GT),
            defineBinaryOpFunction(15, TokenType.COMP_LT),
            defineBinaryOpFunction(16, TokenType.COMP_GT_EQ),
            defineBinaryOpFunction(17, TokenType.COMP_LT_EQ),
            defineBinaryOpFunction(18, TokenType.OP_PLUS),
            defineBinaryOpFunction(19, TokenType.OP_MINUS),
            defineBinaryOpFunction(20, TokenType.OP_MUL),
            defineBinaryOpFunction(21, TokenType.OP_DIV),
            generateParseFunctionCall(22, 10),
            generateParseValue(10)
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
        return self.index < self.end
    
    def peek(self):
        return self.tokens[self.index]
    
    def parsePrec(self, prec):
        return self.parsers[prec](self)


def printAstHelper(node) -> str:
    if type(node) == Value:
        if node.type == TokenType.STR:
            return f'"{node.value}"'

        return str(node.value)
    elif type(node) == Statements:
        return "".join(map(lambda x : printAstHelper(x) + "", node.statements))
    elif type(node) == Debug:
        return f"DEBUG {printAstHelper(node.expr)}"
    elif type(node) == VariableDeclAndSet:
        return f"var {node.name} = {printAstHelper(node.expr)};\n"
    elif type(node) == VariableDecl:
        return f"var {node.name}"
    elif type(node) == VariableSet:
        return f"{node.name} = {printAstHelper(node.expr)};\n"
    elif type(node) == VariableGet:
        return f"{node.name} "
    elif type(node) == Block:
        return "{" + printAstHelper(node.statements) + "}"
    elif type(node) == FunctionDecl:
        return f"{node.name}({"".join(map(lambda x : printAstHelper(x) + ",", node.args))[0:-1]})" + printAstHelper(node.block)
    elif type(node) == FunctionCall:
        return f"{node.name}({"".join(map(lambda x : printAstHelper(x) + ",", node.args))[0:-1]})"
    elif type(node) == str:
        return node
    elif type(node) == Return:
        return f"return {printAstHelper(node.expr)}"
    elif node == None:
        print("none object in ast")
    elif type(node) == If:
        if node.else_expr == None:
            return f"if ({node.cond})"
        else:
            return f"if ({printAstHelper(node.cond)}) {printAstHelper(node.if_expr)} else {printAstHelper(node.else_expr)}"
    elif type(node) == While:
        return f"while ({printAstHelper(node.cond)}) {node.expr}"
    else:
        op = reverse_token_map[node.op]
        return f"({printAstHelper(node.left)} {op} {printAstHelper(node.right)})" 
def printAst(node):
    print("ast:")
    print(printAstHelper(node))

def parse(tokens: list[Token]):
    parser = Parser(tokens)
    return parser.ast



