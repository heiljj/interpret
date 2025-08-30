from Tokenizer import tokenize
from Parser import parse
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

def test_if1():
    buildtest("if (1) {DEBUG 1;}", 1)
    buildtest("if (0) {ERR;}", None)

    buildtest("if (1) {DEBUG 1;} else {ERR;}", 1)
    buildtest("if (0) {ERR;} else {DEBUG 0;}", 0)

    buildtest("if (1 == 1) {DEBUG 1;}", 1)
    buildtest("if (0 == 1) {ERR;}", None)

    buildtest("var a = 1; if (1) {a = 2;} else {ERR;} DEBUG a;", 2)



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
    buildtest("var i = 1; DEBUG i == 1 or i == 0;", True)


def test_shadow1():
    buildtest("var a = 1; {a = 2;} DEBUG a;", 2)

def test_shadow2():
    buildtest("var a = 1; {var a = 2;} DEBUG a;", 1)


def buildtest(code , value):
    tokens = tokenize(code)
    ast = parse(tokens)
    instr = comp(ast)

    emu = Emu(instr)
    emu.run()

    if type(value) == bool:
        value = int(value)

    assert value == emu.debug_info
