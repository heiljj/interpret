from enum import Enum
import string

class TokenType(Enum):
    PAR_LEFT = 1
    PAR_RIGHT = 2
    BRAC_LEFT = 3
    BRAC_RIGHT = 4

    QUOTE = 5
    SEMI = 6
    COMMA = 7

    NUM = 8
    STR = 9
    BOOL = 10
    IDENTIFIER = 11

    FUNC = 12
    DECL_EQ = 13
    DECL = 14

    OP_PLUS = 15
    OP_MINUS = 16
    OP_MUL = 17
    OP_DIV = 18

    OR = 19
    AND = 20

    COMP_EQ = 21
    COMP_NEQ = 22
    COMP_LT_EQ = 23
    COMP_GT_EQ = 24
    COMP_LT = 25
    COMP_GT = 26

    DEBUG = 27

    IF = 28
    ELSE = 29
    WHILE = 30
    FOR = 31
    CONTINUE = 32
    BREAK = 33
    RETURN = 34

    CLASS = 35
    DOT = 36
    ERR = 37

class Token:
    def __init__(self, kind: TokenType, value=None):
        self.value = value
        self.kind = kind

token_map = {
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
    "ERR" : TokenType.ERR,
    "," : TokenType.COMMA,
    "return" : TokenType.RETURN,

    "if" : TokenType.IF,
    "else" : TokenType.ELSE,
    "while" : TokenType.WHILE,
    "for" : TokenType.FOR,
    "break" : TokenType.BREAK,
    "continue" : TokenType.CONTINUE,

    "class" : TokenType.CLASS,
    "." : TokenType.DOT
}

reverse_token_map = dict(zip(token_map.values(), token_map.keys()))
class Tokenizer:
    def __init__(self, text: str, token_map=token_map):
        self.text = "".join(text.splitlines())
        self.length = len(self.text)
        self.index = 0
        self.tokens = []
        self.token_map = token_map

        self.token_tree = {}
        for token in token_map:
            current = self.token_tree

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

            if c == " ":
                self.next()
                continue

            if c in map(float.__str__, range(10)):
                self.parseNumber()
                continue

            if c == '"':
                self.parseString()
            
            current_branch = self.token_tree
            chars = ""

            while self.isNext():
                c = self.peek()

                if c in current_branch:
                    self.next()
                    chars += c
                    current_branch = current_branch[c]
                else:
                    break

            if chars in self.token_map:
                tokentype = self.token_map[chars]
                self.tokens.append(Token(tokentype))
                continue

            else:
                while self.isNext():
                    c = self.peek()

                    if c == " " or c in "({!=;})+-/*,.":
                        break

                    chars += self.next()

                if chars == "true":
                    self.tokens.append(Token(TokenType.BOOL, True))
                    continue 

                if chars == "false":
                    self.tokens.append(Token(TokenType.BOOL, False))
                    continue

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
            s += f"{reverse_token_map[t.kind]} "
    
    print(s)
