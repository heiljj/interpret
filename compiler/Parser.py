from Tokenizer import Token, TokenType, reverse_token_map
from AST import *

class BaseType:
    def __init__(self, name, words):
        self.name = name
        self.words = words
    
    def __eq__(self, o):
        return self.name == o.name 
    
    def __str__(self):
        return str(self.name)
    
    def getWords(self):
        return self.words
    
    def equiv(self, o):
        return self == o

# NOTE this might be better to be apart of the basetype instead 
class StructType:
    def __init__(self, name, properties, property_types):
        if len(properties) != len(property_types):
            raise Exception

        self.name = name
        self.properties = properties
        self.property_types = property_types

        self.property_word_offsets = {}

        s = 0
        for i in range(len(self.properties)):
            self.property_word_offsets[self.properties[i]] = s
            s += self.property_types[i].getWords()
        
        self.words = s
    
    def getWords(self):
        return self.words
    
    def getPropertyType(self, name):
        return self.property_types[self.properties.index(name)]
    
    def getPropertyOffset(self, name):
        return self.property_word_offsets[name]
    
    def getPropertySize(self, name):
        return self.property_types[self.properties.index(name)].getWords()
    
    def equiv(self, o):
        if type(o) != UnknownStructType:
            return self == o
        
        if len(o.property_types) != len(self.property_types):
            return False
        
        for i in range(len(o.property_types)):
            if not o.property_types[i].equiv(self.property_types[i]):
                return False
        
        return True
    
    def __eq__(self, o):
        if type(o) == BaseType:
            return False
        # structs with the same stuff are considered equiv - this is probably fine?
        return self.property_types == o.property_types
    
    def __ne__(self, o):
        return not self == o
        
        
class UnknownStructType:
    def __init__(self, property_types):
        self.property_types = property_types
        self.words = 0

        for t in self.property_types:
            self.words += t.getWords() 
        
    def getWords(self):
        return self.words
    
    def equiv(self, o):
        if len(o.property_types) != len(self.property_types):
            return False

        for i in range(len(o.property_types)):
            if not o.property_types[i].equiv(self.property_types[i]):
                return False
        
        return True



class PointerType:
    def __init__(self, type_, amount=0):
        self.type = type_
        self.amount = amount
    
    def getWords(self):
        if self.amount:
            return self.type.getWords() * self.amount
        return 1
    
    def getPointedWords(self):
        return self.type.getWords()
    
    def __eq__(self, o):
        return self.type == o.type and self.amount == o.amount
    
    def equiv(self, o):
        return self.type == o.type

INT = BaseType("int", 1)
CHAR = BaseType("char", 1)
VOID = BaseType("void", 1)

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0
        self.saved_index = 0
        self.end = len(self.tokens)

        self.registered_types = {
            "int" : INT,
            "char" : CHAR,
        }

        self.parsers = [
            self.parseStatements,                               #0
            self.parseDefStruct,                                #1
            self.parseFunctionDefinition,                       #2
            self.parseWhile,                                    #3
            self.parseFor,                                      #4
            self.parseIf,                                       #5
            self.parseBlock,                                    #6
            self.parseStatement,                                #7
            self.parseErr,                                      #8
            self.parseVarDecl,                                  #9
            self.parseVarSet,                                   #10
            self.parseReturn,                                   #11
            self.parseContinue,                                 #12
            self.parseBreak,                                    #13
            self.parseExprStatement,                            #14
            self.parseDebug,                                    #15
            self.defineBinaryOpFunction(TokenType.OR),          #16
            self.defineBinaryOpFunction(TokenType.AND),         #17
            self.defineBinaryOpFunction(TokenType.COMP_EQ),     #18
            self.defineBinaryOpFunction(TokenType.COMP_NEQ),    #19
            self.defineBinaryOpFunction(TokenType.COMP_GT),     #20
            self.defineBinaryOpFunction(TokenType.COMP_LT),     #21
            self.defineBinaryOpFunction(TokenType.COMP_GT_EQ),  #22
            self.defineBinaryOpFunction(TokenType.COMP_LT_EQ),  #23
            self.defineBinaryOpFunction(TokenType.OP_PLUS),     #24
            self.defineBinaryOpFunction(TokenType.OP_MINUS),    #25
            self.defineBinaryOpFunction(TokenType.OP_MUL),      #26
            self.defineBinaryOpFunction(TokenType.OP_DIV),      #27
            self.parseFunctionCall,                             #28
            self.parseParns,                                    #29
            self.parseVariableGet,                              #30
            self.parseValue                                     #31
        ]

        self.expression_prec = 16
        self.block_prec = 6
        self.function_prec = 2
        self.var_decl_prec = 9
        self.const_prec = 31

        self.ast = self.parsePrec(0)
    
    def getType(self, name):
        return self.registered_types[name]
    
    def getTypes(self):
        return self.registered_types
    
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
    
    def parseErr(self, prec):
        if self.tryMatch(TokenType.ERR):
            return Err()
        
        return self.parsePrec(prec + 1)
    
    def parseStatement(self, prec):
        v = self.parsePrec(prec + 1)
        self.match(TokenType.SEMI)
        return v
    
    def parseDefStruct(self, prec):
        if not self.tryMatch(TokenType.STRUCT):
            return self.parsePrec(prec + 1)
        
        name = self.match(TokenType.IDENTIFIER).value
        self.match(TokenType.BRAC_LEFT)

        properties = []
        property_types = []

        while (type_ := self.tryParseType()):
            property_types.append(type_)
            properties.append(self.match(TokenType.IDENTIFIER).value)
            self.match(TokenType.SEMI)
        
        type_ = StructType(name, properties, property_types)
        self.registered_types[name] = type_

        self.match(TokenType.BRAC_RIGHT)
        self.match(TokenType.SEMI)

        return None
    
    def parseVariableGet(self, prec):
        if not (identifier := self.tryMatch(TokenType.IDENTIFIER)):
            return self.parsePrec(prec + 1)
        
        varget = VariableGet(identifier.value)
        prev = None

        while True:
            if self.tryMatch(TokenType.DOT):
                next_ = StructLookUp(self.match(TokenType.IDENTIFIER).value)
            elif self.tryMatch(TokenType.SQUARE_BRAC_LEFT):
                expr = self.parsePrec(self.expression_prec)
                self.match(TokenType.SQUARE_BRAC_RIGHT)
                next_ = ListIndex(expr)
            else:
                break
            
            if prev:
                prev.next = next_
                prev = next_
            else:
                varget.lookup = next_
                prev = next_
        
        return varget


    def parseValue(self, prec):
        token = self.next()

        match token.kind:
            case TokenType.NUM:
                return Value(INT, token.value)
            case TokenType.STR:
                if len(token.value) != 1:
                    raise NotImplementedError("string")
                return Value(CHAR, token.value)
            case TokenType.BOOL:
                return Value(INT, int(token.value))
            case TokenType.SQUARE_BRAC_LEFT:
                exprs = []

                while True:
                    exprs.append(self.parsePrec(self.expression_prec))
                    if not self.tryMatch(TokenType.COMMA):
                        break
                
                self.match(TokenType.SQUARE_BRAC_RIGHT)

                return List(exprs)
            case TokenType.BRAC_LEFT:
                parms = []
                while not self.tryMatch(TokenType.BRAC_RIGHT):
                    parms.append(self.parsePrec(self.expression_prec))

                    if not self.tryMatch(TokenType.COMMA):
                        break
                
                self.match(TokenType.BRAC_RIGHT)
                return Struct(parms)

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
            n = self.parsePrec(prec + 1)
            if n:
                statements.append(n)

            if not self.isNext() or self.peek().kind == TokenType.BRAC_RIGHT:
                break
        
        return Statements(statements)

    def parseDebug(self, prec):
        if self.tryMatch(TokenType.DEBUG):
            inner = self.parsePrec(prec+1)
            return Debug(inner)
        
        return self.parsePrec(prec + 1)
    
    
    def parseVarDecl(self, prec):
        saved_index = self.index

        if not (type_ := self.tryParseType()):
            return self.parsePrec(prec + 1)
        
        if not (identifier := self.tryMatch(TokenType.IDENTIFIER)):
            self.index = saved_index
            return self.parsePrec(prec + 1)
        
        #NOTE this will break if something with greater prec has two IDs in a row
        if not self.tryMatch(TokenType.DECL_EQ):
            return VariableDecl(identifier.value, None, type_)

        right = self.parsePrec(self.expression_prec)
        return VariableDecl(identifier.value, right, type_)


    def parseVarSet(self, prec):
        saved_index = self.index
        if not (token := self.tryMatch(TokenType.IDENTIFIER)):
            return self.parsePrec(prec + 1)

        first = None
        prev = None

        while True:
            if self.tryMatch(TokenType.DOT):
                next_ = StructLookUp(self.match(TokenType.IDENTIFIER).value)
            elif self.tryMatch(TokenType.SQUARE_BRAC_LEFT):
                expr = self.parsePrec(self.expression_prec)
                self.match(TokenType.SQUARE_BRAC_RIGHT)
                next_ = ListIndex(expr)
            else:
                break
            
            if prev:
                prev.next = next_
                prev = next_
            else:
                prev = next_
                first = prev

        if not self.tryMatch(TokenType.DECL_EQ):
            self.index = saved_index
            return self.parsePrec(prec + 1)
        
        expr = self.parsePrec(self.expression_prec)
        return VariableSet(token.value, expr, first)
        

    def parseBlock(self, prec):
        if not self.tryMatch(TokenType.BRAC_LEFT):
            return self.parsePrec(prec + 1)
        
        if self.tryMatch(TokenType.BRAC_RIGHT):
            return Block(Statements([]))
        
        middle = self.parsePrec(0)
        self.match(TokenType.BRAC_RIGHT)

        return Block(middle)


    def parseFunctionDefinition(self, prec):
            save_index = self.index
            if not (type_ := self.tryParseType()):
                return self.parsePrec(prec + 1)
            
            if not (identifier := self.tryMatch(TokenType.IDENTIFIER)):
                self.index = save_index
                return self.parsePrec(prec + 1)

            identifier = identifier.value

            if not self.tryMatch(TokenType.PAR_LEFT):
                self.index = save_index
                return self.parsePrec(prec + 1)

            args = []
            arg_types = []

            while (arg_type := self.tryParseType()):
                arg_types.append(arg_type)

                args.append(self.match(TokenType.IDENTIFIER).value)

                if not self.tryMatch(TokenType.COMMA):
                    break
            
            self.match(TokenType.PAR_RIGHT)
            block = self.parsePrec(self.block_prec)
            return FunctionDecl(identifier, args, block, type_, arg_types)
    

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

        while_block = While(cond, Block(Statements([block, incr])))
        return Block(Statements([decl, while_block]))

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
    
    def tryParseType(self):
        if not (identifier := self.tryMatch(TokenType.IDENTIFIER)):
            return False
        
        if identifier.value not in self.registered_types:
            self.previous()
            return False

        type_ = self.getType(identifier.value)

        while self.tryMatch(TokenType.OP_MUL):
            type_ = PointerType(type_)
        
        if self.tryMatch(TokenType.SQUARE_BRAC_LEFT):
            amount = self.match(TokenType.NUM).value
            type_ = PointerType(type_, amount)
            self.match(TokenType.SQUARE_BRAC_RIGHT)
        
        return type_


def parse(tokens: list[Token]):
    parser = Parser(tokens)
    return (parser.ast, parser.getTypes())
