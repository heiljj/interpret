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
    def __init__(self, tokenmap, text: str):
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
                self.parseNumber()
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
