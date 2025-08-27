from Emu import Binary
from random import randint

def test_add():
    for _ in range(5000):
        a = randint(-2 ** 31, 2 ** 31 - 1)
        a //= 2
        b = randint(-2 ** 31, 2 ** 31 - 1)
        b //= 2

        create_binary_test(a, b, lambda x, y : x + y)

def test_sub():
    for _ in range(500):
        a = randint(-2 ** 31, 2 ** 31 - 1)
        a //= 2
        b = randint(-2 ** 31, 2 ** 31 - 1)
        b //= 2
        create_binary_test(a, b, lambda x, y : x - y)


def create_binary_test(a, b, op):
    assert op(a, b) == int(op(Binary(a), Binary(b)))