from enum import Enum
import string

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
    COMP_NEQ = 15
    COMP_LT_EQ = 16
    COMP_GT_EQ = 17
    COMP_LT = 18
    COMP_GT = 19

    OR = 20
    AND = 21

    NUM = 22
    STR = 23

    IDENTIFIER = 24

    DEBUG = 25
    COMMA = 26
    RETURN = 27

    IF = 28
    ELSE = 29
    WHILE = 30

    BOOL = 31

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
    "!=" : TokenType.COMP_NEQ,
    "<=" : TokenType.COMP_LT_EQ,
    ">=" : TokenType.COMP_GT_EQ,
    "<" : TokenType.COMP_LT,
    ">" : TokenType.COMP_GT,
    "or" : TokenType.OR,
    "and" : TokenType.AND,

    "DEBUG" : TokenType.DEBUG,
    "," : TokenType.COMMA,
    "return" : TokenType.RETURN,

    "if" : TokenType.IF,
    "else" : TokenType.ELSE,
    "while" : TokenType.WHILE,
}

reverse_tokenmap = dict(zip(tokenmap.values(), tokenmap.keys()))
class Tokenizer:
    def __init__(self, text: str, tokenmap=tokenmap):
        self.text = "".join(text.splitlines())
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

        while self.isNext():
            n = self.next()

            if n not in nums:
                self.previous()
                break
            else:
                value += n
        
        self.tokens.append(Token(TokenType.NUM, float(value)))
    
    def parseString(self):
        s = ""
        if self.next() != '"':
            raise Exception("Expected start of string")
        
        while self.isNext():
            c = self.next()

            if c == '"':
                break

            s += c
        
        self.tokens.append(Token(TokenType.STR, s))

    def parseIdentifier(self):
        s = ""
        while self.isNext():
            c = self.next()

            if c not in string.ascii_letters and c not in "123456789_":
                self.previous()
                break

            s += c

        if s[0] in "123456789":
            raise Exception("Identifier cannot begin with a digit")

        self.tokens.append(Token(TokenType.IDENTIFIER, s))
    
    def parse(self):
        while self.isNext():

            c = self.peek()

            if c in map(float.__str__, range(10)):
                self.parseNumber()
                continue

            if c == '"':
                self.parseString()
            
            if c == " ":
                self.next()
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
                tokentype = self.tokenmap[chars]
                self.tokens.append(Token(tokentype))

                if tokentype == TokenType.DECL or tokentype == TokenType.FUNC:
                    if self.next() != " ":
                        raise Exception("delc/func parsed but no space after?")
                    self.parseIdentifier()
            else:

                while self.isNext():
                    c = self.peek()

                    if c == " " or c in "({!=;}),":
                        break

                    chars += self.next()

                if chars == "":
                    break
                
                if chars == "true":
                    self.tokens.append(Token(TokenType.BOOL, True))
                    break

                if chars == "false":
                    self.tokens.append(Token(TokenType.BOOL, False))

                self.tokens.append(Token(TokenType.IDENTIFIER, chars))

def tokenize(text: str) -> list[Token]:
    tokenizer = Tokenizer(text)
    return tokenizer.tokens

def printTokens(tokens: list[Token]):
    print("tokens:")
    s = ""
    for t in tokens:
        if t.kind == TokenType.NUM:
            s += f"{t.value} "
        elif t.kind == TokenType.STR:
            s += f'"{t.value}"'
        elif t.kind == TokenType.IDENTIFIER:
            s += f'{t.value} '
        elif t.kind == TokenType.BOOL:
            s += f'{t.value}'
        else:
            s += f"{reverse_tokenmap[t.kind]} "
    
    print(s)

# add vars to tokenizer
# second passthrough to check for errors
# start scope stuff