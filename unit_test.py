from Tokenizer import tokenize
from Parser import parse
from Interpreter import Interpreter

#TODO remove semis
def test1():
    buildtest("DEBUG 1 + 2 + 3;", 6)

def test2():
    buildtest("DEBUG 1 + 2 * 3;", 7)

def test3():
    buildtest("DEBUG 3 < 6 and 4 > 2;", True)

def test4():
    buildtest("DEBUG 1 == 1 and 1 == 1 or 1 != 2;", True)

def test5():
    buildtest("var abc = 1;{abc = 2 + 3;}DEBUG abc;", 5)

def test6():
    buildtest("var abc = 1;{var abc = 2 + 3;}DEBUG abc;", 1)

def test7():
    buildtest("fun name() {var a = 1; {a = 2;} DEBUG a} name()", 2)

def test8():
    buildtest("fun db(a) {DEBUG a} db(1)", 1)

def test9():
    buildtest("fun db(a) {return a;} DEBUG db(1) + db(10)", 11)

def test10():
    buildtest("fun add(a, b) {return a + b;} DEBUG add(1, 2)", 3)

def buildtest(text: str, res):
    tokens = tokenize(text)
    ast = parse(tokens)
    inter = Interpreter(ast)
    assert inter.debuginfo == res