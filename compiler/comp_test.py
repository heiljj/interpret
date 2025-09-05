from Tokenizer import tokenize
from Parser import parse
from Typechecker import typecheck, TypeError
from Compiler import comp
from Emu import Emu

def test_expr1():
    buildtest("DEBUG true;", True)

def test_expr2():
    buildtest("DEBUG false;", False)

def test_expr3():
    buildtest("DEBUG false and true;", False)

def test_expr4():
    buildtest("DEBUG true and false;", False)

def test_expr5():
    buildtest("DEBUG false and false;", False)

def test_expr6():
    buildtest("DEBUG true and true;", True)

def test_expr7():
    buildtest("DEBUG false or true;", True)

def test_expr8():
    buildtest("DEBUG true or false;", True)

def test_expr9():
    buildtest("DEBUG false or false;", False)

def test_expr10():
    buildtest("DEBUG true or true;", True)

def test_expr11():
    buildtest("DEBUG false and false or true and true;", True)
    buildtest("DEBUG false and true or false and false;", False)
    buildtest("DEBUG false or true or false;", True)
    buildtest("DEBUG true and true and true and true;", True)
    buildtest("DEBUG true and true and false and true;", False)

def test_expr11():
    buildtest("DEBUG 1 == 1;", True)
    buildtest("DEBUG 1 == 2;", False)

    buildtest("DEBUG 1 != 1;", False)
    buildtest("DEBUG 1 != 2;", True)

    buildtest("DEBUG 1 < 2;", True)
    buildtest("DEBUG 2 < 1;", False)

    buildtest("DEBUG 1 > 2;", False)
    buildtest("DEBUG 2 > 1;", True)

    buildtest("DEBUG 1 <= 2;", True)
    buildtest("DEBUG 2 <= 1;", False)
    buildtest("DEBUG 1 <= 1;", True)

    buildtest("DEBUG 1 >= 2;", False)
    buildtest("DEBUG 2 >= 1;", True)
    buildtest("DEBUG 1 >= 1;", True)

def test_expr12():
    buildtest("DEBUG 1 == 1 and 2 == 2;", True)
    buildtest("DEBUG 1 >= 1 or 2 != 2;", True)
    buildtest("DEBUG 1 != 1 or true and true;", True)

def test_expr13():
    buildtest("DEBUG false and (false or false) and true;", False)
    buildtest("DEBUG true and (true or false) and true;", True)

    buildtest("DEBUG true and (true or false);", True)
    buildtest("DEBUG true and (false or false);", False)

    buildtest("DEBUG (true or false) and true;", True)
    buildtest("DEBUG (false or false) and true;", False)

def test_var1():
    buildtest("int a = 10; int b = 5; DEBUG a;", 10)
    buildtest("int a = 10; int b = 5; DEBUG b;", 5)
    buildtest("int a = 10; int b = 5; a = b; DEBUG b;", 5)
    buildtest("int a = 10; int b = 5; b = a; DEBUG b;", 10)
    buildtest("int a; a = 10; DEBUG a;", 10)

def test_var2():
    buildtest("int a = 10; int b = 5; a = 6 + 2; DEBUG a;", 8)
    buildtest("int a = 10; int b = 5; b = 6 + 2; DEBUG b;", 8)
    buildtest("int a = 10; int b = 5; b = 6 + 2; DEBUG a;", 10)
    buildtest("int a = 10; int b = 5; a = 6 + 2; DEBUG b;", 5)

def test_if1():
    buildtest("if (1) {DEBUG 1;}", 1)
    buildtest("if (0) {ERR;}", None)

    buildtest("if (1) {DEBUG 1;} else {ERR;}", 1)
    buildtest("if (0) {ERR;} else {DEBUG 0;}", 0)

    buildtest("if (1 == 1) {DEBUG 1;}", 1)
    buildtest("if (0 == 1) {ERR;}", None)

def test_if2():
    buildtest("int a = 1; if (1) {a = 2;} else {ERR;} DEBUG a;", 2)
    buildtest("int a = 1; if (0) {ERR;} else {a = 3;} DEBUG a;", 3)
    buildtest("int a = 1; if (1) {int a = 2;} DEBUG a;", 1)

def test_while1():
    buildtest("int a = 0; while (0) {ERR;} a = 1; DEBUG a;", 1)
    buildtest("int a = 0; while (0) {a = a + 1;} DEBUG a;", 0)
    buildtest("int a = 0; while (a < 10) {a = a + 1;} DEBUG a;", 10)
    buildtest("int a = 10; while (a != 0) {a = a - 1;} DEBUG a;", 0)

def test_for1():
    buildtest("for(int j = 0; j != 0; j = j + 1) {ERR;}", None)
    buildtest("for (int i = 0; i < 1; i = i + 1) {}", None)
    buildtest("int i = 0; for (int j = 0; j <= 10; j = j + 1) {i = j;} DEBUG i;", 10)
    buildtest("int i = 2; for (int j = 0; j < 4; j = j + 1) {i = i * 2;} DEBUG i;", 32)
    buildtest("for (int i = 0; i < 5; i = i + 1) {DEBUG i;}", [0, 1, 2, 3, 4])

def test_fn1():
    buildtest("int f() {DEBUG 1;} f();", 1)
    buildtest("int f() {DEBUG 1;}", None)
    buildtest("int f() {return 1;} DEBUG f();", 1)
    buildtest("int f() {return 1;} f(); f(); f(); DEBUG f();", 1)
    buildtest("int add(int a, int b) {return a + b;} DEBUG add(1, 5);", 6)
    buildtest("int add(int a, int b) {return a + b;} DEBUG add(add(1, 2), add(3, 4));", 10)
    buildtest("int add(int a, int b) {return a + b;} DEBUG add(add(add(add(1, 0), 2), 3), 4);", 10)

def test_fn2():
    buildtest("int f() {int a = 1; return 2;} DEBUG f();", 2)
    buildtest("int f() {return 1; DEBUG 10;} f();", None)
    buildtest("""
        int f() {
            int a = 6;
            if (true) {
                return a;
            } else {
                ERR;
            }
        }
        DEBUG f();
    """, 6)
    buildtest("""
        int f() {
            int a = 6;
            if (false) {
                ERR;
            } else {
                return a;
            }
        }
        DEBUG f();
    """, 6)

def test_fn3():
    buildtest("""
        int f(int x) {
            if (x == 0) {
                return 0;
            } else {
                return x + f(x-1);
            }
        }
        DEBUG f(4);
    """, 10)

def test_fn4():
    def fib(i):
        return 1 if i == 0 or i == 1 else fib(i-1) + fib(i-2)

    for i in range(10):
        buildtest("int fib(int i) {             \
            if (i == 0 or i == 1) {         \
                return 1;                   \
            } else {                        \
                return fib(i-1) + fib(i-2); \
            }} DEBUG fib(" + str(i) + ");   \
        ", fib(i))

def test_fn5():
    buildtest("""
        int add(int a, int b) {
            return a + b;
        }

        int mul(int a, int b) {
            return a * b;
        }
        DEBUG mul(add(1, 2), add(5, 5));
    """, 30)

def test_typecheck1():
    buildtest_expect('DEBUG 1 + "1";', TypeError)
    buildtest_expect('char f() {return 1;}', TypeError)
    buildtest_expect('int f(char a) {return 1;} f(1);', TypeError)
    buildtest_expect('char f() {if (1) {return "a";} else {return 1;}}', TypeError)


def test_expr_old5():
    buildtest("DEBUG 1 + 2;", 3)

def test_expr_old6():
    buildtest("DEBUG 1 + 2 * 3;", 7)

def test_expr_old7():
    buildtest("DEBUG 1 * 2 + 3;", 5)

def test_expr_old8():
    buildtest("DEBUG (1 + 2) * (1 + 2);", 9)

def test_expr_old10():
    buildtest("DEBUG 1+(2*(1+(2)));", 7)

def test_expr_old11():
    buildtest("DEBUG (((2)+1)*2)+1;", 7)

def test_expr_old12():
    buildtest("DEBUG 1 == 2 or 2 == 2;", True)

def test_expr_old13():
    buildtest("int i = 1; DEBUG i == 1 or i == 0;", True)


def test_shadow1():
    buildtest("int a = 1; {a = 2;} DEBUG a;", 2)

def test_shadow2():
    buildtest("int a = 1; {int a = 2;} DEBUG a;", 1)


def buildtest(code , value):
    if value is None:
        value = []

    if type(value) != list:
        value = [value]

    tokens = tokenize(code)
    ast, types = parse(tokens)
    typecheck(ast)

    instr = comp(ast, types)

    emu = Emu(instr)
    emu.run()

    if type(value) == bool:
        value = int(value)

    assert value == emu.debug_info

def buildtest_expect(code, er):
    try:
        buildtest(code, None)
    except er as e:
        return
    except AssertionError:
        raise Exception()
    else:
        raise Exception()
