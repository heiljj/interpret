from Tokenizer import Token, TokenType, reverse_token_map

class Debug:
    def __init__(self, expr):
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveDebug(self)
    
    def __str__(self):
        return f"DEBUG {self.expr}"


class Statements:
    def __init__(self, statements):
        self.statements = statements
    
    def resolve(self, interpret):
        return interpret.resolveStatements(self)
    
    def __str__(self):
        return "".join(map(lambda x: str(x) + "\n", self.statements))


class Block:
    def __init__(self, statements: Statements):
        self.statements = statements
    
    def resolve(self, interpret):
        return interpret.resolveBlock(self)
    
    def __str__(self):
        return f"{{{self.statements}}}"


class Class:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods
    
    def resolve(self, interpret):
        return interpret.resolveClass(self)
    
    def __str__(self):
        method_str = "".join(map(lambda x : str(x) + "\n", self.methods))
        return f"class {self.name} {{{method_str}}}"

class ObjectGetter:
    def __init__(self, identifier, property_list):
        self.identifier = identifier
        self.property_list = property_list
    
    def resolve(self, interpret):
        return interpret.resolveObjectGetter(self)

class ObjectSetter:
    def __init__(self, identifier, properties, expression):
        self.identifier = identifier
        self.properties = properties 
        self.expression = expression
    
    def resolve(self, interpret):
        return interpret.resolveObjectSetter(self)

class ObjectMethodCall:
    def __init__(self, identifier, properties, args):
        self.identifier = identifier
        self.properties = properties
        self.args = args
    
    def resolve(self, interpret):
        return interpret.resolve(self)

class If:
    def __init__(self, cond, if_expr, else_expr):
        self.cond = cond
        self.if_expr = if_expr
        self.else_expr = else_expr
    
    def resolve(self, interpret):
        interpret.resolveIf(self)

    def __str__(self):
        if self.else_expr:
            return f"if ({self.cond}) {self.if_expr} else {self.else_expr}"


class While:
    def __init__(self, cond, expr):
        self.cond = cond
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveWhile(self)
    
    def __str__(self):
        return f"while ({self.cond}) {self.expr}"

class For:
    def __init__(self, decl, cond, assign, block):
        self.decl = decl
        self.cond = cond
        self.assign = assign
        self.block = block
    
    def resolve(self, interpret):
        return interpret.resolveFor(self)
    
    def __str__(self):
        return f"for ({self.decl}; {self.cond}; {self.assign}) {self.block}"

class Continue:
    def resolve(self, interpret):
        interpret.resolveContinue(self)
    
    def __str__(self):
        return "continue;"
    

class Break:
    def resolve(self, interpret):
        interpret.resolveBreak(self)
    
    def __str__(self):
        return "break;"


class FunctionDecl:
    def __init__(self, name, args, block):
        self.name = name
        self.args = args
        self.block = block
    
    def resolve(self, interpret):
        return interpret.resolveFunctionDecl(self)

    def __str__(self):
        arg_str = "".join(map(lambda x : x + ", ", self.args))
        if arg_str:
            arg_str = arg_str[:-2]

        return f"def {self.name}({arg_str}) {self.block}"


class Return:
    def __init__(self, expr):
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveReturn(self)
    
    def __str__(self):
        return f"return {self.expr};"


class FunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args
    
    def resolve(self, interpret):
        return interpret.resolveFunctionCall(self)
    
    def __str__(self):
        arg_str = "".join(map(lambda x : str(x) + ", ", self.args))
        if arg_str:
            arg_str = arg_str[:-2]
        
        return f"{self.name}({arg_str})"
    


class VariableDeclAndSet:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveVariableDeclAndSet(self)
    
    def __str__(self):
        return f"var {self.name} = {self.expr};"


class VariableDecl:
    def __init__(self, name):
        self.name = name
    
    def resolve(self, interpret):
        return interpret.resolveVariableDecl(self)
    
    def __str__(self):
        return f"var {self.name};"


class VariableSet:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def resolve(self, interpret):
        return interpret.resolveVariableSet(self)
    
    def __str__(self):
        return f"{self.name} = {self.expr};"


class VariableGet:
    def __init__(self, name):
        self.name = name
    
    def resolve(self, interpret):
        return interpret.resolveVariableGet(self)
    
    def __str__(self):
        return self.name 
    

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    
    def resolve(self, interpret):
        return interpret.resolveBinaryOp(self)
    
    def __str__(self):
        return f"{self.left} {reverse_token_map[self.op]} {self.right}"


class Value:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def resolve(self, interpret):
        return interpret.resolveValue(self)
    
    def __str__(self):
        return str(self.value)


# outside of parser class so it can follow the same format as generated functions 
def generateParseValue(prec, expression_prec):
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
                self.previous()
                return self.parsePrec(expression_prec)
    return parseValue
    

def defineBinaryOpFunction(prec, op):
    def parseBinaryOp(self):
        left = self.parsePrec(prec + 1)

        while self.tryMatch(op):
            right = self.parsePrec(prec + 1)
            left = BinaryOp(left, op, right)

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
        if self.tryMatch(TokenType.DEBUG):
            inner = self.parsePrec(prec+1)
            return Debug(inner)
        
        return self.parsePrec(prec + 1)
    
    return parseDebug

def generateParseVarDecl(prec):
    def parseVarDecl(self):
        if self.tryMatch(TokenType.DECL):
            identifier = self.match(TokenType.IDENTIFIER)

            if self.tryMatch(TokenType.DECL_EQ):
                right = self.parsePrec(prec + 1)
                self.match(TokenType.SEMI)
                return VariableDeclAndSet(identifier.value, right)

            self.match(TokenType.SEMI)
            return VariableDecl(identifier.value)

        return self.parsePrec(prec + 1)
    
    return parseVarDecl

def generateParseVarSet(prec):
    def parseVarSet(self):
        if (token := self.tryMatch(TokenType.IDENTIFIER)):

            if not self.tryMatch(TokenType.DECL_EQ):
                self.previous()
                return self.parsePrec(prec + 1)
            
            expr = self.parsePrec(prec + 1)
            self.match(TokenType.SEMI)
            return VariableSet(token.value, expr)
        
        return self.parsePrec(prec + 1)
    
    return parseVarSet

def generateParseBlock(prec):
    def parseBlock(self):
        if not self.tryMatch(TokenType.BRAC_LEFT):
            return self.parsePrec(prec + 1)
        
        if self.tryMatch(TokenType.BRAC_RIGHT):
            return Block(Value(TokenType.NUM), 0)
        
        middle = self.parsePrec(0)
        self.match(TokenType.BRAC_RIGHT)

        return Block(middle)
    
    return parseBlock

def generateParseFunctionDefinition(prec, block_prec):
    def parseFunctionDefinition(self):
            if not self.tryMatch(TokenType.FUNC):
                return self.parsePrec(prec + 1)

            identifier = self.match(TokenType.IDENTIFIER).value
            self.match(TokenType.PAR_LEFT)

            args = []

            while (token := self.tryMatch(TokenType.IDENTIFIER)):
                args.append(token.value)

                if not self.tryMatch(TokenType.COMMA):
                    break
            
            self.match(TokenType.PAR_RIGHT)
            block = self.parsePrec(block_prec)
            return FunctionDecl(identifier, args, block)
    
    return parseFunctionDefinition


def generateParseFunctionCall(prec, expression_prec):
    def parseFunctionCall(self):
        if not (identifier := self.tryMatch(TokenType.IDENTIFIER)):
            return self.parsePrec(prec + 1)
        
        if not self.tryMatch(TokenType.PAR_LEFT):
            self.previous()
            return self.parsePrec(prec + 1)

        args = []

        while self.peek().kind != TokenType.PAR_RIGHT:
            args.append(self.parsePrec(expression_prec))

            if not self.tryMatch(TokenType.COMMA):
                break
        
        self.match(TokenType.PAR_RIGHT)
        return FunctionCall(identifier.value, args)
    
    return parseFunctionCall

def generateParseReturn(prec, expression_prec):
    def parseReturn(self):
        if not self.tryMatch(TokenType.RETURN):
            return self.parsePrec(prec + 1)
        
        expr = self.parsePrec(expression_prec)
        self.match(TokenType.SEMI)

        return Return(expr)
    
    return parseReturn

def generateParseIf(prec, block_prec, expr_prec):
    def parseIf(self):
        if self.tryMatch(TokenType.IF):
            self.match(TokenType.PAR_LEFT)
            cond = self.parsePrec(expr_prec)
            self.match(TokenType.PAR_RIGHT)

            if_expr = self.parsePrec(block_prec)

            if not self.tryMatch(TokenType.ELSE):
                return If(cond, if_expr, None)
            
            else_expr = self.parsePrec(block_prec)
            return If(cond, if_expr, else_expr)
        
        return self.parsePrec(prec + 1)
    
    return parseIf 


def generateParseWhile(prec, block_prec, expr_prec):
    def parseWhile(self):
        if not self.tryMatch(TokenType.WHILE):
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.PAR_LEFT)
        cond = self.parsePrec(expr_prec)
        self.match(TokenType.PAR_RIGHT)

        block = self.parsePrec(block_prec)
        return While(cond, block)
        
    return parseWhile

def generateParseFor(prec, block_prec, var_decl_prec):
    def parseFor(self):
        if not self.tryMatch(TokenType.FOR):
            return self.parsePrec(prec + 1)

        self.match(TokenType.PAR_LEFT)

        decl = self.parsePrec(var_decl_prec)
        cond = self.parsePrec(var_decl_prec)
        self.match(TokenType.SEMI)
        incr = self.parsePrec(var_decl_prec)

        self.match(TokenType.PAR_RIGHT)

        block = self.parsePrec(block_prec)

        return For(decl, cond, incr, block)

    return parseFor


def generateParseParns(prec, expr_prec):
    def parseParns(self):
        if not self.tryMatch(TokenType.PAR_LEFT):
            return self.parsePrec(prec + 1)
        
        expr = self.parsePrec(expr_prec)
        self.match(TokenType.PAR_RIGHT)
        return expr
    
    return parseParns

def generateParseBreak(prec):
    def parseBreak(self):
        if not self.tryMatch(TokenType.BREAK):
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.SEMI)

        return Break()
    
    return parseBreak

def generateParseContinue(prec):
    def parseContinue(self):
        if not self.tryMatch(TokenType.CONTINUE):
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.SEMI)

        return Continue()
    
    return parseContinue


def generateParseClass(prec, function_prec):
    def parseClass(self):
        if not self.tryMatch(TokenType.CLASS):
            return self.parsePrec(prec + 1)
        
        name = self.match(TokenType.IDENTIFIER).value

        self.match(TokenType.BRAC_LEFT)
        methods = []


        while self.peek().kind == TokenType.FUNC:
            methods.append(self.parsePrec(function_prec))
        
        self.match(TokenType.BRAC_RIGHT)
        return Class(name, methods)
    
    return parseClass

def generateParseClassGetter(prec):
    def parseClassGetter(self):
        ret = self.parseProperties()

        if not ret:
            return self.parsePrec(prec + 1)
        
        identifier, properties = ret
        
        return ObjectGetter(identifier.value, properties)
    
    return parseClassGetter

def generateParseClassSetter(prec, expr_prec):
    def parseClassSetter(self):
        saved_index = self.index

        ret = self.parseProperties()
        if not ret:
            return self.parsePrec(prec + 1)
        
        identifier, properties = ret

        if not self.tryMatch(TokenType.DECL_EQ):
            self.index = saved_index
            return self.parsePrec(prec + 1)
        
        expr = self.parsePrec(expr_prec)
        self.match(TokenType.SEMI)
        
        return ObjectSetter(identifier.value, properties, expr)
    
    return parseClassSetter

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
        self.saved_index = 0
        self.end = len(self.tokens)

        self.parsers = [
            generateParseStatements(0),
            generateParseClass(1, 2),
            generateParseFunctionDefinition(2, 6),
            generateParseWhile(3, 6, 14),
            generateParseFor(4, 6, 8),
            generateParseIf(5, 6, 14),
            generateParseBlock(6),
            generateParseDebug(7),
            generateParseVarDecl(8),
            generateParseClassSetter(9, 14),
            generateParseVarSet(10),
            generateParseReturn(11, 10),
            generateParseContinue(12),
            generateParseBreak(13),
            defineBinaryOpFunction(14, TokenType.OR),
            defineBinaryOpFunction(15, TokenType.AND),
            defineBinaryOpFunction(16, TokenType.COMP_EQ),
            defineBinaryOpFunction(17, TokenType.COMP_NEQ),
            defineBinaryOpFunction(18, TokenType.COMP_GT),
            defineBinaryOpFunction(19, TokenType.COMP_LT),
            defineBinaryOpFunction(20, TokenType.COMP_GT_EQ),
            defineBinaryOpFunction(21, TokenType.COMP_LT_EQ),
            defineBinaryOpFunction(22, TokenType.OP_PLUS),
            defineBinaryOpFunction(23, TokenType.OP_MINUS),
            defineBinaryOpFunction(24, TokenType.OP_MUL),
            defineBinaryOpFunction(25, TokenType.OP_DIV),
            generateParseFunctionCall(26, 14),
            generateParseClassGetter(27),
            generateParseParns(28, 14),
            generateParseValue(29, 14)
        ]

        self.ast = self.parsePrec(0)
    
    def match(self, t):
        token = self.tokens[self.index]
        self.index += 1

        if (t != token.kind):
            raise Exception(f"Expected token of type {t} but was {token.kind}")
        
        return token
    
    def tryMatch(self, t):
        if not self.isNext():
            return False

        token = self.peek()

        if token.kind == t:
            return self.match(t)
        
        return False
        
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
    
    def parseProperties(self):
        if not (identifier := self.tryMatch(TokenType.IDENTIFIER)):
            return None
        
        if not self.tryMatch(TokenType.DOT):
            self.previous()
            return None
        
        property_list = []

        while (prop_token := self.tryMatch(TokenType.IDENTIFIER)):
            property_list.append(prop_token.value)

            if not self.tryMatch(TokenType.DOT):
                break
        
        return identifier, property_list
        


def parse(tokens: list[Token]):
    parser = Parser(tokens)
    return parser.ast



