from Tokenizer import tokenize
from Parser import parse
from Interpreter import Interpreter

import sys

if __name__ == "__main__":
    if len(sys.argv) == 2:
        fpath = sys.argv[1]

        with open(fpath) as f:
            contents = f.read()

            tokens = tokenize(contents)
            ast = parse(tokens)

            inter = Interpreter()
            print(inter.interpret(ast))

    else:
        inter = Interpreter()
        while True:

            text = input("> ")
            try:
                tokens = tokenize(text)
                ast = parse(tokens)

                print(inter.interpret(ast))
            except Exception as e:
                print(e)

