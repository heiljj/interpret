from enum import Enum

class TokenType(Enum):
    PAR_LEFT = 1
    PAR_RIGHT = 2

    OP_PLUS = 3
    OP_MINUS = 4
    OP_MUL = 5
    OP_DIV = 6

    NUM = 7
    STRING = 8

    CMP_OR = 9
    CMP_AND = 10

class Token:
    def __init__(self, kind: TokenType, value=None):
        self.value = value
        self.kind = kind


class Tokenizer:
    def __init__(self, text: str):
        self.text = "".join(text.split())
        self.index = 0
        self.length = len(self.text)

        self.tokens = []

        self.parse()
    
    def next(self):
        if not self.isNext():
            return ""

        self.index += 1
        return self.text[self.index - 1]
    
    def previous(self) -> str:
        self.index -= 1
        return self.text[self.index]
    
    def match(self, char: str) -> bool:
        return self.next() == char
    
    def isNext(self):
        return self.index < self.length
    
    def parseNumber(self):
        value = ""
        nums = list(map(float.__str__, range(10)))
        nums += "."

        while (n := self.next()) in nums:
            value += n
        
        if n != "":
            self.previous()
        return value
    
    def parseString(self):
        value = ""
        
        while (n := self.next()) != '"' and n != "":
            value += n
        
        self.previous()

    def parse(self):
        while self.isNext():
            match self.next():
                case "(":
                    self.tokens.append(Token(TokenType.PAR_LEFT))
                case ")":
                    self.tokens.append(Token(TokenType.PAR_RIGHT))
                case "+":
                    self.tokens.append(Token(TokenType.OP_PLUS))
                case "-":
                    self.tokens.append(Token(TokenType.OP_MINUS))
                case "*":
                    self.tokens.append(Token(TokenType.OP_MUL))
                case "/":
                    self.tokens.append(Token(TokenType.OP_DIV))
                case '"':
                    self.tokens.append(Token(TokenType.STRING, self.parseString()))
                case i if i in map(float.__str__, range(10)):
                    self.previous()
                    self.tokens.append(Token(TokenType.NUM, self.parseNumber()))
                case _:
                    raise Exception("Unknown char")

def tokenize(chars: str) -> list[Token]:
    tokenizer = Tokenizer(chars)
    return tokenizer.tokens





