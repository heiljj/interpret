from functools import total_ordering

def bin2dec(s: str):
    value = -2 ** 31 * int(s[0])
    for i in range(1, 32):
        value += int(s[i]) * 2 ** (31 - i)
    
    return value

def dec2bin(i: int):
    s = bin(i % 2 ** 32)

    if s[0] == "-":
        s = s[3:]
        s = "".join(["1" for i in range(32 - len(s))]) + s
    else:
        s = s[2:]
        s = "".join(["0" for i in range(32 - len(s))]) + s
    
    return s

@total_ordering
class Binary():
    def __init__(self, i):
        if type(i) == float:
            
            if i % 1 != 0:
                raise NotImplementedError

            i = int(i)

        if type(i) == int:
            self.value = dec2bin(i)
            return

        

        if len(i) != 32:
            self.value = dec2bin(int(i))
            return 

        self.value = i
    
    def __iter__(self):
        return iter(self.value)
    
    def __add__(self, op):
        if type(op) == int:
            op = Binary(op)

        carry = 0
        output = ""

        for i in range(31, -1, -1):
            total = carry + int(self.value[i]) + int(op.value[i])

            match total:
                case 0:
                    output = "0" + output
                    carry = 0
                case 1:
                    output = "1" + output
                    carry = 0
                case 2:
                    output = "0" + output
                    carry = 1
                case 3:
                    output = "1" + output
                    carry = 1
                case _:
                    raise Exception
        
        return Binary(output)
    
    def __sub__(self, op):
        if type(op) == int:
            op = Binary(op)

        negation = Binary("".join(["1" if i == "0" else "0" for i in op]))
        negation = negation + Binary(1)
        return self + negation 
    
    def __int__(self):
        return bin2dec(self.value)
    
    def __eq__(self, o):
        return int(self) == int(o)
    
    def __lt__(self, o):
        return int(self) < int(o)

    def bitwise(self, o, op):
        return "".join(map(op), self.value, o.value)
    
    def bitwiseAnd(self, o):
        value = self.bitwise(o, lambda x, y : "1" if x == "1" and y == "1" else "0")
        return Binary(value)
    
    def bitwiseOr(self, o):
        value = self.bitwise(o, lambda x, y : "1" if x == "1" or y == "1" else "0")
        return Binary(value)
    
    def bitwiseXor(self, o):
        value = self.bitwise(o, lambda x, y : 1 if x == "1" or y == "1" and x != y else "0")
        return Binary(value)
    
