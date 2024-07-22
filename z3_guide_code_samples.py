from z3 import *


def section(name):
    print(f"\n#\n# {name}\n#")


def sample():
    print("\n----")


def z3_guide_samples():
    # samples from https://microsoft.github.io/z3guide/programming/Z3%20Python%20-%20Readonly/Introduction
    section_getting_started()

    section_boolean_logic()

    section_solvers()

    section_arithmetic()

    section_machine_arithmetic()

    section_functions()

    section_satisfiability_and_validity()

    section_list_comprehensions()

    section_kinematic_equations()

    section_bit_tricks()

    section_puzzles()

    section_install_puzzle()


def section_install_puzzle():
    section("Application:  Install Problem")
    sample()
    print("Code is first presented as fragments; only finished section shown")

    def DependsOn(pack, deps):
        if is_expr(deps):
            return Implies(pack, deps)
        else:
            return And([Implies(pack, dep) for dep in deps])

    def Conflict(*packs):
        return Or([Not(pack) for pack in packs])

    a, b, c, d, e, f, g, z = Bools('a b c d e f g z')

    def install_check(*problem):
        s = Solver()
        s.add(*problem)
        if s.check() == sat:
            m = s.model()
            r = []
            for x in m:
                if is_true(m[x]):
                    # x is a Z3 declaration
                    # x() returns the Z3 expression
                    # x.name() returns a string
                    r.append(x())
            print(r)
        else:
            print("invalid installation profile")

    print("Check 1")
    install_check(DependsOn(a, [b, c, z]),
                  DependsOn(b, d),
                  DependsOn(c, [Or(d, e), Or(f, g)]),
                  Conflict(d, e),
                  Conflict(d, g),
                  a, z)
    print("Check 2")
    install_check(DependsOn(a, [b, c, z]),
                  DependsOn(b, d),
                  DependsOn(c, [Or(d, e), Or(f, g)]),
                  Conflict(d, e),
                  Conflict(d, g),
                  a, z, g)


def section_puzzles():
    section("Puzzles")
    sample()
    # Create 3 integer variables
    dog, cat, mouse = Ints('dog cat mouse')
    solve(dog >= 1,  # at least one dog
          cat >= 1,  # at least one cat
          mouse >= 1,  # at least one mouse
          # we want to buy 100 animals
          dog + cat + mouse == 100,
          # We have 100 dollars (10000 cents):
          #   dogs cost 15 dollars (1500 cents),
          #   cats cost 1 dollar (100 cents), and
          #   mice cost 25 cents
          1500 * dog + 100 * cat + 25 * mouse == 10000)
    sample()
    # 9x9 matrix of integer variables
    X = [[Int("x_%s_%s" % (i + 1, j + 1)) for j in range(9)]
         for i in range(9)]
    # each cell contains a value in {1, ..., 9}
    cells_c = [And(1 <= X[i][j], X[i][j] <= 9)
               for i in range(9) for j in range(9)]
    # each row contains a digit at most once
    rows_c = [Distinct(X[i]) for i in range(9)]
    # each column contains a digit at most once
    cols_c = [Distinct([X[i][j] for i in range(9)])
              for j in range(9)]
    # each 3x3 square contains a digit at most once
    sq_c = [Distinct([X[3 * i0 + i][3 * j0 + j]
                      for i in range(3) for j in range(3)])
            for i0 in range(3) for j0 in range(3)]
    sudoku_c = cells_c + rows_c + cols_c + sq_c
    # sudoku instance, we use '0' for empty cells
    instance = ((0, 0, 0, 0, 9, 4, 0, 3, 0),
                (0, 0, 0, 5, 1, 0, 0, 0, 7),
                (0, 8, 9, 0, 0, 0, 0, 4, 0),
                (0, 0, 0, 0, 0, 0, 2, 0, 8),
                (0, 6, 0, 2, 0, 1, 0, 5, 0),
                (1, 0, 2, 0, 0, 0, 0, 0, 0),
                (0, 7, 0, 0, 0, 0, 5, 2, 0),
                (9, 0, 0, 0, 6, 5, 0, 0, 0),
                (0, 4, 0, 9, 7, 0, 0, 0, 0))
    instance_c = [If(instance[i][j] == 0,
                     True,
                     X[i][j] == instance[i][j])
                  for i in range(9) for j in range(9)]
    s = Solver()
    s.add(sudoku_c + instance_c)
    if s.check() == sat:
        m = s.model()
        r = [[m.evaluate(X[i][j]) for j in range(9)]
             for i in range(9)]
        print_matrix(r)
    else:
        print("failed to solve")
    sample()
    # We know each queen must be in a different row.
    # So, we represent each queen by a single integer: the column position
    Q = [Int('Q_%i' % (i + 1)) for i in range(8)]
    # Each queen is in a column {1, ... 8 }
    val_c = [And(1 <= Q[i], Q[i] <= 8) for i in range(8)]
    # At most one queen per column
    col_c = [Distinct(Q)]
    # Diagonal constraint
    diag_c = [If(i == j,
                 True,
                 And(Q[i] - Q[j] != i - j, Q[i] - Q[j] != j - i))
              for i in range(8) for j in range(i)]
    solve(val_c + col_c + diag_c)


def section_bit_tricks():
    section("Bit Tricks")
    sample()
    x = BitVec('x', 32)
    powers = [2 ** i for i in range(32)]
    fast = And(x != 0, x & (x - 1) == 0)
    slow = Or([x == p for p in powers])
    print(fast)
    prove(fast == slow)
    print("trying to prove buggy version...")
    fast = x & (x - 1) == 0
    prove(fast == slow)
    sample()
    x = BitVec('x', 32)
    y = BitVec('y', 32)
    # Claim: (x ^ y) < 0 iff x and y have opposite signs
    trick = (x ^ y) < 0
    # Naive way to check if x and y have opposite signs
    opposite = Or(And(x < 0, y >= 0),
                  And(x >= 0, y < 0))
    prove(trick == opposite)


def section_kinematic_equations():
    section("Kinematic Equations")
    sample()
    print("Sample did not include declarations")
    print("Sample had extra comma.  Sample used double equals not single")
    v_i, t, a = Reals("v_i t a")
    d = v_i * t + (a * t ** 2) / 2
    v_f = v_i + a * t
    sample()
    d, a, t, v_i, v_f = Reals('d a t v__i v__f')
    equations = [
        d == v_i * t + (a * t ** 2) / 2,
        v_f == v_i + a * t,
    ]
    print("Kinematic equations:")
    print(equations)
    # Given v_i, v_f and a, find d
    problem = [
        v_i == 30,
        v_f == 0,
        a == -8
    ]
    print("Problem:")
    print(problem)
    print("Solution:")
    solve(equations + problem)
    sample()
    d, a, t, v_i, v_f = Reals('d a t v__i v__f')
    equations = [
        d == v_i * t + (a * t ** 2) / 2,
        v_f == v_i + a * t,
    ]
    # Given v_i, t and a, find d
    problem = [
        v_i == 0,
        t == 4.10,
        a == 6
    ]
    solve(equations + problem)
    # Display rationals in decimal notation
    set_option(rational_to_decimal=True)
    solve(equations + problem)


def section_list_comprehensions():
    section("List Comprehensions")
    sample()
    # Create list [1, ..., 5]
    print([x + 1 for x in range(5)])
    # Create two lists containing 5 integer variables
    X = [Int('x%s' % i) for i in range(5)]
    Y = [Int('y%s' % i) for i in range(5)]
    print(X)
    # Create a list containing X[i]+Y[i]
    X_plus_Y = [X[i] + Y[i] for i in range(5)]
    print(X_plus_Y)
    # Create a list containing X[i] > Y[i]
    X_gt_Y = [X[i] > Y[i] for i in range(5)]
    print(X_gt_Y)
    print(And(X_gt_Y))
    # Create a 3x3 "matrix" (list of lists) of integer variables
    X = [[Int("x_%s_%s" % (i + 1, j + 1)) for j in range(3)]
         for i in range(3)]
    pp(X)
    sample()
    X = IntVector('x', 5)
    Y = RealVector('y', 5)
    P = BoolVector('p', 5)
    print(X)
    print(Y)
    print(P)
    print([y ** 2 for y in Y])
    print(Sum([y ** 2 for y in Y]))


def section_satisfiability_and_validity():
    section("Satisfiability and Validity")
    sample()
    p, q = Bools('p q')
    demorgan = And(p, q) == Not(Or(Not(p), Not(q)))
    print(demorgan)

    def prove(f):
        s = Solver()
        s.add(Not(f))
        if s.check() == unsat:
            print("proved")
        else:
            print("failed to prove")

    print("Proving demorgan...")
    prove(demorgan)


def section_functions():
    section("Functions")
    sample()
    x = Int('x')
    y = Int('y')
    f = Function('f', IntSort(), IntSort())
    solve(f(f(x)) == x, f(x) == y, x != y)
    sample()
    x = Int('x')
    y = Int('y')
    f = Function('f', IntSort(), IntSort())
    s = Solver()
    s.add(f(f(x)) == x, f(x) == y, x != y)
    print(s.check())
    m = s.model()
    print("f(f(x)) =", m.evaluate(f(f(x))))
    print("f(x)    =", m.evaluate(f(x)))


def section_machine_arithmetic():
    section("Machine Arithmetic")
    sample()
    x = BitVec('x', 16)
    y = BitVec('y', 16)
    print(x + 2)
    # Internal representation
    print((x + 2).sexpr())
    # -1 is equal to 65535 for 16-bit integers
    print(simplify(x + y - 1))
    # Creating bit-vector constants
    a = BitVecVal(-1, 16)
    b = BitVecVal(65535, 16)
    print(simplify(a == b))
    a = BitVecVal(-1, 32)
    b = BitVecVal(65535, 32)
    # -1 is not equal to 65535 for 32-bit integers
    print(simplify(a == b))
    sample()
    # Create to bit-vectors of size 32
    x, y = BitVecs('x y', 32)
    solve(x + y == 2, x > 0, y > 0)
    # Bit-wise operators
    # & bit-wise and
    # | bit-wise or
    # ~ bit-wise not
    solve(x & y == ~y)
    solve(x < 0)
    # using unsigned version of <
    solve(ULT(x, 0))
    sample()
    # Create to bit-vectors of size 32
    x, y = BitVecs('x y', 32)
    solve(x >> 2 == 3)
    solve(x << 2 == 3)
    solve(x << 2 == 24)


def section_arithmetic():
    section("Arithmetic")
    sample()
    x = Real('x')
    y = Int('y')
    a, b, c = Reals('a b c')
    s, r = Ints('s r')
    print(x + y + 1 + (a + s))
    print(ToReal(y) + c)
    sample()
    a, b, c = Ints('a b c')
    d, e = Reals('d e')
    solve(a > b + 2,
          a == 2 * c + 10,
          c + b <= 1000,
          d >= e)
    sample()
    x, y = Reals('x y')
    # Put expression in sum-of-monomials form
    t = simplify((x + y) ** 3, som=True)
    print(t)
    # Use power operator
    t = simplify(t, mul_to_power=True)
    print(t)
    sample()
    x, y = Reals('x y')
    # Using Z3 native option names
    print(simplify(x == y + 2, ':arith-lhs', True))
    # Using Z3Py option names
    print(simplify(x == y + 2, arith_lhs=True))
    print("\nAll available options:")
    help_simplify()
    sample()
    x, y = Reals('x y')
    solve(x + 10000000000000000000000 == y, y > 20000000000000000)
    print(Sqrt(2) + Sqrt(3))
    print(simplify(Sqrt(2) + Sqrt(3)))
    print(simplify(Sqrt(2) + Sqrt(3)).sexpr())
    # The sexpr() method is available for any Z3 expression
    print((x + Sqrt(y) * 2).sexpr())


def section_solvers():
    section("Solvers")
    sample()
    x = Int('x')
    y = Int('y')
    s = Solver()
    print(s)
    s.add(x > 10, y == x + 2)
    print(s)
    print("Solving constraints in the solver s ...")
    print(s.check())
    print("Create a new scope...")
    s.push()
    s.add(y < 11)
    print(s)
    print("Solving updated set of constraints...")
    print(s.check())
    print("Restoring state...")
    s.pop()
    print(s)
    print("Solving restored set of constraints...")
    print(s.check())
    sample()
    x = Real('x')
    s = Solver()
    s.add(2 ** x == 3)
    print(s.check())
    sample()
    x = Real('x')
    y = Real('y')
    s = Solver()
    s.add(x > 1, y > 1, Or(x + y > 3, x - y < 2))
    print("asserted constraints...")
    for c in s.assertions():
        print(c)
    print(s.check())
    print("statistics for the last check method...")
    print(s.statistics())
    # Traversing statistics
    for k, v in s.statistics():
        print(k, " : ", v)
    sample()
    x, y, z = Reals('x y z')
    s = Solver()
    s.add(x > 1, y > 1, x + y > 3, z - x < 10)
    print(s.check())
    m = s.model()
    print("x = %s" % m[x])
    print("traversing model...")
    for d in m.decls():
        print("%s = %s" % (d.name(), m[d]))
    sample()
    x = Real('x')
    y = Real('y')
    z = Real('z')


def section_boolean_logic():
    section("Boolean Logic")
    sample()
    p = Bool('p')
    q = Bool('q')
    r = Bool('r')
    solve(Implies(p, q), r == Not(q), Or(Not(p), r))
    sample()
    p = Bool('p')
    q = Bool('q')
    print(And(p, q, True))
    print(simplify(And(p, q, True)))
    print(simplify(And(p, False)))
    sample()
    p = Bool('p')
    x = Real('x')
    solve(Or(x < 5, x > 10), Or(p, x ** 2 == 2), Not(p))


def section_getting_started():
    section("Getting started")
    sample()
    x = Int('x')
    y = Int('y')
    solve(x > 2, y < 10, x + 2 * y == 7)
    sample()
    x = Int('x')
    y = Int('y')
    print(simplify(x + y + 2 * x + 3))
    print(simplify(x < y + x + 2))
    print(simplify(And(x + 1 >= 3, x ** 2 + x ** 2 + y ** 2 + 2 >= 5)))
    sample()
    x = Int('x')
    y = Int('y')
    print(x ** 2 + y ** 2 >= 1)
    set_option(html_mode=False)
    print(x ** 2 + y ** 2 >= 1)
    sample()
    x = Int('x')
    y = Int('y')
    n = x + y >= 3
    print("num args: ", n.num_args())
    print("children: ", n.children())
    print("1st child:", n.arg(0))
    print("2nd child:", n.arg(1))
    print("operator: ", n.decl())
    print("op name:  ", n.decl().name())
    sample()
    x = Real('x')
    y = Real('y')
    solve(x ** 2 + y ** 2 > 3, x ** 3 + y < 5)
    sample()
    x = Real('x')
    y = Real('y')
    solve(x ** 2 + y ** 2 == 3, x ** 3 == 2)
    sample()
    set_option(precision=30)
    print("Solving, and displaying result with 30 decimal places")
    solve(x ** 2 + y ** 2 == 3, x ** 3 == 2)
    sample()
    print(1 / 3)
    print(RealVal(1) / 3)
    print(Q(1, 3))
    x = Real('x')
    print(x + 1 / 3)
    print(x + Q(1, 3))
    print(x + "1/3")
    print(x + 0.25)
    sample()
    x = Real('x')
    solve(3 * x == 1)
    set_option(rational_to_decimal=True)
    solve(3 * x == 1)
    set_option(precision=30)
    solve(3 * x == 1)
    sample()
    x = Real('x')
    solve(x > 4, x < 0)
    sample()
    # This is a comment
    x = Real('x')  # comment: creating x
    print(x ** 2 + 2 * x + 2)  # comment: printing polynomial


if __name__ == '__main__':
    z3_guide_samples()

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
