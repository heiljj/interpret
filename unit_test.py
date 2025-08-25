from Tokenizer import tokenize
from Parser import parse
from Interpreter import Interpreter

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

def test_expr8():
    buildtest("DEBUG (1 + 2) * (1 + 2)", 9)

def test_expr9():
    buildtest("fun add(a, b) {return a + b;} DEBUG (add(1, 2) + 1) * 4", 16)

def test_expr10():
    buildtest("DEBUG 1+(2*(1+(2)))", 7)

def test_expr11():
    buildtest("DEBUG (((2)+1)*2)+1", 7)

def test_expr12():
    buildtest("DEBUG 1 == 2 or 2 == 2", True)

def test_expr13():
    buildtest("var i = 1; DEBUG i == 1 or i == 0", True)


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

def test_fn5():
    buildtest("fun add(a, b) {return a + b;} DEBUG add(add(1, 2), add(3, 4))", 10)


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


def test_loop1():
    buildtest("var i = 0; while(i < 5) {i = i + 1;} DEBUG i", 5)

def test_loop2():
    buildtest("var i = 0; for (var j = 0; j < 5; j = j + 1;) {i = i + 1;} DEBUG i", 5)

def test_loop3():
    buildtest("var i = 0; for (var j = 0; j < 3; j = j + 1;) {for (var k = 0; k < 3; k = k + 1;) {i = j + k + i;}} DEBUG i", 18)

def test_loop4():
    buildtest("var i = 0; while(i < 5) {i = i + 1;if (i == 3) {break;}} DEBUG i", 3)

def test_loop5():
    buildtest("var i = 0; for (var j = 0; j < 5; j = j + 1;) {if (j == 3) {continue;} i = i + 1;} DEBUG i", 4)


def test_class1():
    buildtest("class c {} var i = c(); i.id = 1; DEBUG i.id", 1)

def test_class2():
    buildtest("class a {fun init() {self.value = 1;}} var c = a(); DEBUG c.value", 1)

def test_class3():
    buildtest("class a {fun init() {self.value = 0;} fun inc() {self.value = self.value + 10;}} var c = a(); c.inc() DEBUG c.value", 10)

def test_class4():
    buildtest("class a {fun init() {self.value = 0;} fun inc() {self.value = self.value + 10;}} var c = a(); c.inc() c.inc() DEBUG c.value", 20)

def test_class5():
    buildtest("""
        class C {
            fun init() {
                self.value = 1;
            }

            fun incr(amount) {
                self.value = self.value + amount;
            }

            fun add(b) {
                self.value = self.value + b.value;
            }
        }

        var a = C();
        a.incr(9)
        var b = C();
        a.add(b)
        DEBUG a.value""", 11)

def test_class6():
    buildtest("""
        class C {
            fun init() {
                self.value = 0;
            }
        }

        fun incr() {
            self.value = self.value + 1;
        }

        var c = C();
        c.add = incr;
        c.incr()
        DEBUG c.value
              """, 1)

def test_class7():
    buildtest("""
        class C {
            fun init() {
                self.wrapper = 1;
            }
        }

        var c = C();
        c.wrapper = C();
        c.wrapper.wrapper = c.wrapper.wrapper + 1;
        DEBUG c.wrapper.wrapper""", 2)

def test_class8():
    buildtest("""
        class C {
            fun init() {
                self.wrapper = 1;
            }

            fun get() {
                return self.wrapper;
            }
        }

        var c = C();
        DEBUG c.get()
        """, 1)

def test_class9():
    buildtest("""
        class C {
            fun init() {
                self.wrapper = 1;
            }

            fun get() {
                return self.wrapper;
            }
        }

        var c = C();
        c.wrapper = C();
        c.wrapper.wrapper = c.wrapper.wrapper + 1;
        DEBUG c.wrapper.get()""", 2)

def test_repl():
    l1 = "var i = 1;"
    l2 = "DEBUG i"

    tokens1 = tokenize(l1)
    tokens2 = tokenize(l2)

    ast1 = parse(tokens1)
    ast2 = parse(tokens2)

    inter = Interpreter()
    inter.interpret(ast1)
    inter.interpret(ast2)
    assert inter.debug_info == 1


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
    inter = Interpreter()
    inter.interpret(ast)
    assert inter.debug_info == res