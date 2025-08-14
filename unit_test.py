from Tokenizer import tokenize
from Parser import parse
from Interpreter import Interpreter

#TODO remove semis

def test_expr1():
    buildtest("DEBUG true", True)

def test_expr2():
    buildtest("DEBUG false", False)

def test_expr3():
    buildtest("DEBUG false and true", False)

def test_expr4():
    buildtest("DEBUG false or true", True)

def test_expr5():
    buildtest("DEBUG 1 + 2", 3)

def test_expr6():
    buildtest("DEBUG 1 + 2 * 3", 7)

def test_expr7():
    buildtest("DEBUG 1 * 2 + 3", 5)


def test_shadow1():
    buildtest("var a = 1; {a = 2;} DEBUG a", 2)

def test_shadow2():
    buildtest("var a = 1; {var a = 2;} DEBUG a", 1)

def test_shadow3():
    buildtest("fun test() {var a = 2;} var a = 1; test() DEBUG a", 1)

def test_fn1():
    buildtest("fun test(a) {return a;} DEBUG test(1)", 1)

def test_fn2():
    buildtest("fun test(a, b) {return a + b;} DEBUG test(1, 2)", 3)

def test_fn3():
    buildtest("fun test(a) {return a;} DEBUG test(1) + test(2)", 3)

def test_fn4():
    def fib(i):
        return 1 if i == 0 or i == 1 else fib(i-1) + fib(i-2)

    for i in range(10):
        buildtest("fun fib(i) {             \
            if (i == 0 or i == 1) {         \
                return 1;                   \
            } else {                        \
                return fib(i-1) + fib(i-2); \
            }} DEBUG fib(" + str(i) + ")    \
        ", fib(i))


def test_if1():
    buildtest("if (true) {DEBUG 1}", 1)

def test_if2():
    buildtest("if (false) {DEBUG 1}", None)

def test_if3():
    buildtest("if (true) {DEBUG 1} else {DEBUG 2}", 1)

def test_if4():
    buildtest("if (false) {DEBUG 1} else {DEBUG 2}", 2)

def test_if5():
    buildtest("if (1 > 0) {DEBUG 1} else {DEBUG 2}", 1)

def test_if6():
    buildtest("fun test() {return true;} if (test()) {DEBUG 1} else {DEBUG 2}", 1)



def test1():
    buildtest("DEBUG 1 + 2 + 3", 6)

def test2():
    buildtest("DEBUG 1 + 2 * 3", 7)

def test3():
    buildtest("DEBUG 3 < 6 and 4 > 2", True)

def test4():
    buildtest("DEBUG 1 == 1 and 1 == 1 or 1 != 2", True)

def test5():
    buildtest("var abc = 1;{abc = 2 + 3;}DEBUG abc", 5)

def test6():
    buildtest("var abc = 1;{var abc = 2 + 3;}DEBUG abc", 1)

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