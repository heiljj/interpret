# block       -> (stmt;);*
# stmt        -> assign_stmt
# assign_stmt -> 'var' [] = expr

# expr       1-> or_expr ('or' or_exp)*
# or_expr    2-> and_expr ('and' and_expr)*
# and_expr   3-> pm_expr ('+' | '-' pm_expr)*
# pm_expr    4-> md_expr ('*' | '/' md_expr)*
# md_expr    5-> String | Num

from Tokenizer import Token, TokenType, reverse_tokenmap

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Value:
    def __init__(self, type, value):
        self.type = type
        self.value = value

# outside of parser class so it can follow the same format as generated functions 
def parseValue(self):
    token = self.next()

    match token.kind:
        case TokenType.NUM:
            return Value(TokenType.NUM, token.value)
        case TokenType.STR:
            return Value(TokenType.STR, token.value)
        case _:
            raise Exception("Token was not of kind value")
class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0
        self.end = len(self.tokens)
    
        self.parsers = {
            2: self.defineBinaryOpFunction(2, TokenType.OR),
            3: self.defineBinaryOpFunction(3, TokenType.AND),
            4: self.defineBinaryOpFunction(4, TokenType.COMP_EQ),
            5: self.defineBinaryOpFunction(5, TokenType.COMP_GT),
            6: self.defineBinaryOpFunction(6, TokenType.COMP_LT),
            7: self.defineBinaryOpFunction(7, TokenType.COMP_GT_EQ),
            8: self.defineBinaryOpFunction(8, TokenType.COMP_LT_EQ),
            9: self.defineBinaryOpFunction(9, TokenType.OP_PLUS),
            10: self.defineBinaryOpFunction(10, TokenType.OP_MINUS),
            11: self.defineBinaryOpFunction(11, TokenType.OP_MUL),
            12: self.defineBinaryOpFunction(12, TokenType.OP_DIV),
            13: parseValue
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


def printAstHelper(node) -> str:
    if type(node) == Value:
        if node.type == TokenType.STR:
            return f'"{node.value}"'

        return node.value
    else:
        op = reverse_tokenmap[node.op]
        return f"({printAstHelper(node.left)} {op} {printAstHelper(node.right)})"

def printAst(node):
    print(printAstHelper(node))

def parse(tokens: list[Token]):
    parser = Parser(tokens)
    return parser.ast



