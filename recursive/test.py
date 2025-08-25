from Tokenizer import tokenize
from Parser import parse
from Interpreter import Interpreter

tokens = tokenize("""
        class C {
            fun init(value, value2) {
                self.wrapper = value + value2;
            }
        }

        var c = C(10, 5);
        DEBUG c.wrapper
        """)
ast = parse(tokens)
inter = Interpreter()
inter.interpret(ast)
print(inter.debug_info)
t=1