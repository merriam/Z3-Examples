from z3 import *
from z3_guide_code_samples import z3_guide_samples
from dave_cook_poker_sample import poker_puzzle
from dave_cook_skiing_puzzle import skiing_puzzle
from dave_cook_tv_puzzle import television_puzzle


def z3_hello():
    print("Attempting z3 hello")
    x = Int('x')
    y = Int('y')
    solve(x > 2, y < 10, x + 2 * y == 7)
    print("z3 hello passed")

if __name__ == '__main__':
    z3_hello()
    z3_guide_samples()
    poker_puzzle()
    skiing_puzzle()
    television_puzzle()

