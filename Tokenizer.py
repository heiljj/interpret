from enum import Enum

class TokenType(Enum):
    PAR_LEFT = 1
    PAR_RIGHT = 2
    BRAC_LEFT = 3
    BRAC_RIGHT = 4

    OP_PLUS = 5
    OP_MINUS = 6
    OP_MUL = 7
    OP_DIV = 8

    FUNC = 9
    DECL_EQ = 10
    DECL = 11
    QUOTE = 12
    SEMI = 13

    COMP_EQ = 14
    COMP_LT_EQ = 15
    COMP_GT_EQ = 16
    COMP_LT = 17
    COMP_GT = 18

    NUM = 19

class Token:
    def __init__(self, kind: TokenType, value=None):
        self.value = value
        self.kind = kind

tokenmap = {
    "(" : TokenType.PAR_LEFT,
    ")" : TokenType.PAR_RIGHT,
    "{" : TokenType.BRAC_LEFT,
    "}" : TokenType.BRAC_RIGHT,

    "+" : TokenType.OP_PLUS,
    "-" : TokenType.OP_MINUS,
    "*" : TokenType.OP_MUL,
    "/" : TokenType.OP_DIV,

    "fun" : TokenType.FUNC,
    "=" : TokenType.DECL_EQ,
    "var" : TokenType.DECL,
    '"' : TokenType.QUOTE,
    ";" : TokenType.SEMI,

    "==" : TokenType.COMP_EQ,
    "<=" : TokenType.COMP_LT_EQ,
    ">=" : TokenType.COMP_GT_EQ,
    "<" : TokenType.COMP_LT,
    ">" : TokenType.COMP_GT
}
class Tokenizer:
    def __init__(self, text: str, tokenmap=tokenmap):
        self.text = "".join(text.split())
        self.length = len(self.text)
        self.index = 0
        self.tokens = []
        self.tokenmap = tokenmap

        self.charmap = {}
        for token in tokenmap:
            current = self.charmap

            for letter in token:
                if letter in current:
                    current = current[letter]
                else:
                    current[letter] = {}
                    current = current[letter]
    
        self.parse()
    
    def next(self):
        char = self.text[self.index]
        self.index += 1
        return char

    def previous(self) -> str:
        self.index -= 1
        return self.text[self.index]
    
    def isNext(self):
        return self.index < self.length
    
    def peek(self):
        return self.text[self.index]

    def parseNumber(self):
        value = ""
        nums = list(map(float.__str__, range(10)))
        nums += "."

        while (n := self.next()) in nums:
            value += n
        
        if n != "":
            self.previous()
        return value
    
    def parse(self):
        while self.isNext():

            c = self.peek()

            if c in map(float.__str__, range(10)):
                self.tokens.append(Token(TokenType.NUM, self.parseNumber()))
                continue


            current = self.charmap
            chars = ""

            while self.isNext():
                c = self.next()

                if c in current:
                    chars += c
                    current = current[c]
                else:
                    self.previous()
                    break

            if chars in self.tokenmap:
                self.tokens.append(Token(self.tokenmap[chars]))
            else:
                if chars == "":
                    break

                raise Exception("Token not in map")

def tokenize(text: str) -> list[Token]:
    tokenizer = Tokenizer(text)
    return tokenizer.tokens
