from Tokenizer import Token, TokenType, reverse_token_map

class Type:
    def __init__(self, name, pointer=False, size=1, properties={}):
        self.name = name
        self.pointer = pointer
        self.size = size
        self.properties = properties # name -> type
    
    def __eq__(self, o):
        return self.name == o.name and self.pointer == o.pointer
    
    def __str__(self):
        return str(self.name)

INT = Type("int")
CHAR = Type("char")

class Err:
    def __init__(self):
        pass

    def resolve(self, interpret):
        return interpret.resolveErr(self)

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


class If:
    def __init__(self, cond, if_expr, else_expr):
        self.cond = cond
        self.if_expr = if_expr
        self.else_expr = else_expr
    
    def resolve(self, interpret):
        return interpret.resolveIf(self)

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

class ExprStatement:
    def __init__(self, s):
        self.s = s
    
    def resolve(self, interpret):
        return interpret.resolveExprStatement(self)

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
    def __init__(self, name, args, block, type_, argtypes):
        self.name = name
        self.args = args
        self.block = block
        self.type = type_
        self.argtypes = argtypes
    
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
    def __init__(self, name, expr, type_):
        self.name = name
        self.expr = expr
        self.type = type_
    
    def resolve(self, interpret):
        return interpret.resolveVariableDeclAndSet(self)
    
    def __str__(self):
        return f"var {self.name} = {self.expr};"


class VariableDecl:
    def __init__(self, name, type_):
        self.name = name
        self.type = type_
    
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

        self.registered_types = {
            "int" : INT,
            "char" : CHAR
        }

        self.parsers = [
            self.parseStatements,                               #0
            self.parseFunctionDefinition,                       #1
            self.parseWhile,                                    #2
            self.parseFor,                                      #3
            self.parseIf,                                       #4
            self.parseBlock,                                    #5
            self.parseStatement,                                #6
            self.parseVarDecl,                                  #7
            self.parseVarSet,                                   #8
            self.parseReturn,                                   #9
            self.parseContinue,                                 #10
            self.parseBreak,                                    #11
            self.parseExprStatement,                            #12
            self.parseDebug,                                    #13
            self.defineBinaryOpFunction(TokenType.OR),          #14
            self.defineBinaryOpFunction(TokenType.AND),         #15
            self.defineBinaryOpFunction(TokenType.COMP_EQ),     #16
            self.defineBinaryOpFunction(TokenType.COMP_NEQ),    #17
            self.defineBinaryOpFunction(TokenType.COMP_GT),     #18
            self.defineBinaryOpFunction(TokenType.COMP_LT),     #19
            self.defineBinaryOpFunction(TokenType.COMP_GT_EQ),  #20
            self.defineBinaryOpFunction(TokenType.COMP_LT_EQ),  #21
            self.defineBinaryOpFunction(TokenType.OP_PLUS),     #22
            self.defineBinaryOpFunction(TokenType.OP_MINUS),    #23
            self.defineBinaryOpFunction(TokenType.OP_MUL),      #24
            self.defineBinaryOpFunction(TokenType.OP_DIV),      #25
            self.parseFunctionCall,                             #26
            self.parseParns,                                    #27
            self.parseValue                                     #28
        ]

        self.expression_prec = 14
        self.block_prec = 5
        self.function_prec = 1
        self.var_decl_prec = 7

        self.ast = self.parsePrec(0)
    
    def getType(self, name):
        return self.registered_types[name]
    
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
        return self.parsers[prec](prec)
    
    def parseExprStatement(self, prec):
        value = ExprStatement(self.parsePrec(prec + 1))
        return value
    
    def parseStatement(self, prec):
        v = self.parsePrec(prec + 1)
        self.match(TokenType.SEMI)
        return v
    
    def parseValue(self, prec):
        token = self.next()

        match token.kind:
            case TokenType.NUM:
                return Value(INT, token.value)
            case TokenType.STR:
                if len(token.value) != 1:
                    raise NotImplementedError("string")
                return Value(CHAR, token.value)
            case TokenType.IDENTIFIER:
                return VariableGet(token.value)
            case TokenType.BOOL:
                return Value(INT, int(token.value))
            case TokenType.ERR:
                return Err()
            case _:
                # self.previous()
                # return self.parsePrec(self.expression_prec)
                raise Exception("Unknown value token")

    def defineBinaryOpFunction(self, op) :
        def parseBinaryOp(prec):
            left = self.parsePrec(prec + 1)

            while self.tryMatch(op):
                right = self.parsePrec(prec + 1)
                left = BinaryOp(left, op, right)
            
            return left

        return parseBinaryOp

    def parseStatements(self, prec):
        statements = []
        while self.isNext():
            statements.append(self.parsePrec(prec + 1))

            if not self.isNext() or self.peek().kind == TokenType.BRAC_RIGHT:
                break
        
        return Statements(statements)

    def parseDebug(self, prec):
        if self.tryMatch(TokenType.DEBUG):
            inner = self.parsePrec(prec+1)
            return Debug(inner)
        
        return self.parsePrec(prec + 1)
    
    
    def parseVarDecl(self, prec):
        # if not self.tryMatch(TokenType.DECL):
        #     return self.parsePrec(prec + 1)
        
        if not (type_ := self.tryMatch(TokenType.IDENTIFIER)):
            return self.parsePrec(prec + 1)

        if not (identifier := self.tryMatch(TokenType.IDENTIFIER)):
            self.previous()
            return self.parsePrec(prec + 1)
        
        #NOTE this will break if something with greater prec has two IDs in a row
        if not self.tryMatch(TokenType.DECL_EQ):
            return VariableDecl(identifier.value, self.getType(type_.value))

        right = self.parsePrec(self.expression_prec)
        return VariableDeclAndSet(identifier.value, right, self.getType(type_.value))


    def parseVarSet(self, prec):
        if not (token := self.tryMatch(TokenType.IDENTIFIER)):
            return self.parsePrec(prec + 1)

        if not self.tryMatch(TokenType.DECL_EQ):
            self.previous()
            return self.parsePrec(prec + 1)
        
        expr = self.parsePrec(self.expression_prec)
        return VariableSet(token.value, expr)
        

    def parseBlock(self, prec):
        if not self.tryMatch(TokenType.BRAC_LEFT):
            return self.parsePrec(prec + 1)
        
        if self.tryMatch(TokenType.BRAC_RIGHT):
            return Block(Statements([]))
        
        middle = self.parsePrec(0)
        self.match(TokenType.BRAC_RIGHT)

        return Block(middle)


    def parseFunctionDefinition(self, prec):
            if not (type_ := self.tryMatch(TokenType.IDENTIFIER)):
                return self.parsePrec(prec + 1)
            
            if not (identifier := self.tryMatch(TokenType.IDENTIFIER)):
                self.previous()
                return self.parsePrec(prec + 1)

            identifier = identifier.value

            if not self.tryMatch(TokenType.PAR_LEFT):
                self.previous()
                self.previous()
                return self.parsePrec(prec + 1)

            args = []
            arg_types = []

            while (arg_type := self.tryMatch(TokenType.IDENTIFIER)):
                arg = self.match(TokenType.IDENTIFIER)
                args.append(arg.value)
                arg_types.append(self.getType(arg_type.value))

                if not self.tryMatch(TokenType.COMMA):
                    break
            
            self.match(TokenType.PAR_RIGHT)
            block = self.parsePrec(self.block_prec)
            return FunctionDecl(identifier, args, block, self.getType(type_.value), arg_types)
    

    def parseFunctionCall(self, prec):
        if not (identifier := self.tryMatch(TokenType.IDENTIFIER)):
            return self.parsePrec(prec + 1)
        
        if not self.tryMatch(TokenType.PAR_LEFT):
            self.previous()
            return self.parsePrec(prec + 1)

        args = []

        while self.peek().kind != TokenType.PAR_RIGHT:
            args.append(self.parsePrec(self.expression_prec))

            if not self.tryMatch(TokenType.COMMA):
                break
        
        self.match(TokenType.PAR_RIGHT)
        return FunctionCall(identifier.value, args)
    

    def parseReturn(self, prec):
        if not self.tryMatch(TokenType.RETURN):
            return self.parsePrec(prec + 1)
        
        expr = self.parsePrec(self.expression_prec)

        return Return(expr)
    

    def parseIf(self, prec):
        if not self.tryMatch(TokenType.IF):
            return self.parsePrec(prec + 1)

        self.match(TokenType.PAR_LEFT)
        cond = self.parsePrec(self.expression_prec)
        self.match(TokenType.PAR_RIGHT)

        if_expr = self.parsePrec(self.block_prec)

        if not self.tryMatch(TokenType.ELSE):
            return If(cond, if_expr, None)
        
        else_expr = self.parsePrec(self.block_prec)
        return If(cond, if_expr, else_expr)
        


    def parseWhile(self, prec):
        if not self.tryMatch(TokenType.WHILE):
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.PAR_LEFT)
        cond = self.parsePrec(self.expression_prec)
        self.match(TokenType.PAR_RIGHT)

        block = self.parsePrec(self.block_prec)
        return While(cond, block)

    def parseFor(self, prec):
        if not self.tryMatch(TokenType.FOR):
            return self.parsePrec(prec + 1)

        self.match(TokenType.PAR_LEFT)

        decl = self.parsePrec(self.var_decl_prec)
        self.match(TokenType.SEMI)
        cond = self.parsePrec(self.expression_prec)
        self.match(TokenType.SEMI)
        incr = self.parsePrec(self.var_decl_prec)

        self.match(TokenType.PAR_RIGHT)

        block = self.parsePrec(self.block_prec)

        return For(decl, cond, incr, block)

    def parseParns(self, prec):
        if not self.tryMatch(TokenType.PAR_LEFT):
            return self.parsePrec(prec + 1)
        
        expr = self.parsePrec(self.expression_prec)
        self.match(TokenType.PAR_RIGHT)
        return expr

    def parseBreak(self, prec):
        if not self.tryMatch(TokenType.BREAK):
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.SEMI)

        return Break()

    def parseContinue(self, prec):
        if not self.tryMatch(TokenType.CONTINUE):
            return self.parsePrec(prec + 1)
        
        self.match(TokenType.SEMI)

        return Continue()


def parse(tokens: list[Token]):
    parser = Parser(tokens)
    return parser.ast



