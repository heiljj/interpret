# expr       1-> or_expr ('or' or_exp)*
# or_expr    2-> and_expr ('and' and_expr)*
# and_expr   3-> pm_expr ('+' | '-' pm_expr)*
# pm_expr    4-> md_expr ('*' | '/' md_expr)*
# md_expr    5-> String | Num

from Tokenizer import Token, TokenType

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Value:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0
        self.end = len(self.tokens)
    
        self.parsers = {
            2: self.defineBinaryOpFunction(2, TokenType.CMP_OR),
            3: self.defineBinaryOpFunction(3, TokenType.CMP_AND),
            4: self.defineBinaryOpFunction(4, TokenType.OP_PLUS),
            5: self.defineBinaryOpFunction(5, TokenType.OP_MINUS),
            6: self.defineBinaryOpFunction(6, TokenType.OP_MUL),
            7: self.defineBinaryOpFunction(7, TokenType.OP_DIV),
        }

        self.ast = self.parsePrec(2)
    
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
    
    def isNext(self):
        return self.index + 1 < self.end
    
    def peek(self):
        return self.tokens[self.index]
    
    def parsePrec(self, prec):
        if prec == len(self.parsers) + 2:
            return self.parseValue()
        else:
            return self.parsers[prec](self)
    
    def defineBinaryOpFunction(self, prec, op):
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

    
    def parseValue(self):
        token = self.next()

        match token.kind:
            case TokenType.NUM:
                return Value(TokenType.NUM, token.value)
            case TokenType.STRING:
                return Value(TokenType.STRING, token.value)
            case _:
                raise Exception("Token was not of kind value")


def printAst(node) -> str:
    if type(node) == Value:
        return node.value
    else:
        op = "+" if node.op == TokenType.OP_PLUS else "*"
        return f"({printAst(node.left)} {op} {printAst(node.right)})"

def parse(tokens: list[Token]):
    parser = Parser(tokens)
    return parser.ast



