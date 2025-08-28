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

class ObjectSetter:
    def __init__(self, objectgetterroot, property, expr):
        self.objectgetterroot = objectgetterroot
        self.property = property
        self.expr = expr
    
    def resolve(self, interpret):
        interpret.resolveObjectSetter(self)

class ObjectGetterRoot:
    def __init__(self, identifier, call):
        self.identifier = identifier
        # update scope to that of identifier
        # then resolve call
        # pop scope
        self.call = call
    
    def resolve(self, interpret):
        return interpret.resolveObjectGetter(self)

class ObjectCallMethod:
    def __init__(self, method, args, next_call=None):
        self.method = method
        self.args = args
        self.next_call = next_call
    
    def resolve(self, interpret):
        return interpret.resolveObjectCallMethod(self)

class ObjectGetProperty:
    def __init__(self, property, next_call=None):
        self.property = property
        self.next_call = next_call
    
    def resolve(self, interpret):
        return interpret.resolveObjectGetProperty(self)


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

class ExprStatement:
    def __init__(self, s):
        self.s = s
    
    def resolve(self, interpret):
        return self.s.resolve(interpret)

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
            self.parseStatements,                               #0
            self.parseClass,                                    #1
            self.parseFunctionDefinition,                       #2
            self.parseWhile,                                    #3
            self.parseFor,                                      #4
            self.parseIf,                                       #5
            self.parseBlock,                                    #6
            self.parseVarDecl,                                  #7
            self.parseClassSet,                                 #8
            self.parseVarSet,                                   #9
            self.parseReturn,                                   #10
            self.parseContinue,                                 #11
            self.parseBreak,                                    #12
            self.parseExprStatement,                            #13
            self.parseDebug,                                    #14
            self.defineBinaryOpFunction(TokenType.OR),          #15
            self.defineBinaryOpFunction(TokenType.AND),         #16
            self.defineBinaryOpFunction(TokenType.COMP_EQ),     #17
            self.defineBinaryOpFunction(TokenType.COMP_NEQ),    #18
            self.defineBinaryOpFunction(TokenType.COMP_GT),     #19
            self.defineBinaryOpFunction(TokenType.COMP_LT),     #20
            self.defineBinaryOpFunction(TokenType.COMP_GT_EQ),  #21
            self.defineBinaryOpFunction(TokenType.COMP_LT_EQ),  #22
            self.defineBinaryOpFunction(TokenType.OP_PLUS),     #23
            self.defineBinaryOpFunction(TokenType.OP_MINUS),    #24
            self.defineBinaryOpFunction(TokenType.OP_MUL),      #25
            self.defineBinaryOpFunction(TokenType.OP_DIV),      #26
            self.parseObjectMethodCall,                         #27
            self.parseFunctionCall,                             #28
            self.parseParns,                                    #29
            self.parseValue                                     #30
        ]

        self.expression_prec = 15
        self.block_prec = 6
        self.function_prec = 2
        self.var_decl_prec = 7

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
        return self.parsers[prec](prec)
    
    def parseExprStatement(self, prec):
        value = ExprStatement(self.parsePrec(prec + 1))
        self.match(TokenType.SEMI)
        return value
    
    def parseValue(self, prec):
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
    
    def parseClassSet(self, prec):
        index = self.index

        if not (class_name := self.tryMatch(TokenType.IDENTIFIER)):
            return self.parsePrec(prec + 1)
        
        if not self.tryMatch(TokenType.DOT):
            self.index = index
            return self.parsePrec(prec + 1)
        
        calls = []

        while (identifier := self.tryMatch(TokenType.IDENTIFIER)):
            if not self.tryMatch(TokenType.PAR_LEFT):
                calls.append(ObjectGetProperty(identifier.value))
            else:
                args = []
                while self.peek().kind != TokenType.PAR_RIGHT:
                    args.append(self.parsePrec(self.expression_prec))

                    if not self.tryMatch(TokenType.COMMA):
                        break
                
                self.match(TokenType.PAR_RIGHT)
                calls.append(ObjectCallMethod(identifier.value, args))
            
            if not self.tryMatch(TokenType.DOT):
                break
        
        if not self.tryMatch(TokenType.DECL_EQ):
            self.index = index
            return self.parsePrec(prec + 1)
        
        for i in range(0, len(calls)-2):
            calls[i].next_call = calls[i+1]
        
        objgr = None

        if len(calls) == 1:
            objgr = ObjectGetterRoot(class_name.value, None)
        else:
            objgr = ObjectGetterRoot(class_name.value, calls[0])

        expr = self.parsePrec(self.expression_prec)
        self.match(TokenType.SEMI)

        return ObjectSetter(objgr, calls[-1].property, expr)
    
    def parseVarDecl(self, prec):
        if self.tryMatch(TokenType.DECL):
            identifier = self.match(TokenType.IDENTIFIER)

            if self.tryMatch(TokenType.DECL_EQ):
                right = self.parsePrec(self.expression_prec)
                self.match(TokenType.SEMI)
                return VariableDeclAndSet(identifier.value, right)

            self.match(TokenType.SEMI)
            return VariableDecl(identifier.value)

        return self.parsePrec(prec + 1)

    def parseVarSet(self, prec):
        if (token := self.tryMatch(TokenType.IDENTIFIER)):

            if not self.tryMatch(TokenType.DECL_EQ):
                self.previous()
                return self.parsePrec(prec + 1)
            
            expr = self.parsePrec(self.expression_prec)
            self.match(TokenType.SEMI)
            return VariableSet(token.value, expr)
        
        return self.parsePrec(prec + 1)

    def parseBlock(self, prec):
        if not self.tryMatch(TokenType.BRAC_LEFT):
            return self.parsePrec(prec + 1)
        
        if self.tryMatch(TokenType.BRAC_RIGHT):
            return Block(Value(TokenType.NUM, 0))
        
        middle = self.parsePrec(0)
        self.match(TokenType.BRAC_RIGHT)

        return Block(middle)


    def parseFunctionDefinition(self, prec):
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
            block = self.parsePrec(self.block_prec)
            return FunctionDecl(identifier, args, block)
    

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
        self.match(TokenType.SEMI)

        return Return(expr)
    

    def parseIf(self, prec):
        if self.tryMatch(TokenType.IF):
            self.match(TokenType.PAR_LEFT)
            cond = self.parsePrec(self.expression_prec)
            self.match(TokenType.PAR_RIGHT)

            if_expr = self.parsePrec(self.block_prec)

            if not self.tryMatch(TokenType.ELSE):
                return If(cond, if_expr, None)
            
            else_expr = self.parsePrec(self.block_prec)
            return If(cond, if_expr, else_expr)
        
        return self.parsePrec(prec + 1)


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

    def parseClass(self, prec):
        if not self.tryMatch(TokenType.CLASS):
            return self.parsePrec(prec + 1)
        
        name = self.match(TokenType.IDENTIFIER).value

        self.match(TokenType.BRAC_LEFT)
        methods = []


        while self.peek().kind == TokenType.FUNC:
            methods.append(self.parsePrec(self.function_prec))
        
        self.match(TokenType.BRAC_RIGHT)
        return Class(name, methods)

    def parseObjectMethodCall(self, prec):
        index = self.index

        if not (class_name := self.tryMatch(TokenType.IDENTIFIER)):
            return self.parsePrec(prec + 1)
        
        if not self.tryMatch(TokenType.DOT):
            self.index = index
            return self.parsePrec(prec + 1)
        
        calls = []

        while (identifier := self.tryMatch(TokenType.IDENTIFIER)):
            if not self.tryMatch(TokenType.PAR_LEFT):
                calls.append(ObjectGetProperty(identifier.value))
            else:
                args = []
                while self.peek().kind != TokenType.PAR_RIGHT:
                    args.append(self.parsePrec(self.expression_prec))

                    if not self.tryMatch(TokenType.COMMA):
                        break
                
                self.match(TokenType.PAR_RIGHT)
                calls.append(ObjectCallMethod(identifier.value, args))
            
            if not self.tryMatch(TokenType.DOT):
                break
        

        for i in range(0, len(calls)-1):
            calls[i].next_call = calls[i+1]
        
        return ObjectGetterRoot(class_name.value, calls[0])

def parse(tokens: list[Token]):
    parser = Parser(tokens)
    return parser.ast



