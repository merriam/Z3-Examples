#!/usr/bin/env python3
from z3 import (
    Solver,
    Function,
    EnumSort,
    IntSort,
    RealSort,
    Const,
    Consts,
    Distinct,
    Or,
    Xor,
    sat,
    unsat,
)

"""
points: 82, 89, 96, 103
jumpers: Denise, Madeline, Patti, Shawna
distances: 90.1 meters, 95.0 meters, 96.3 meters, 102.9 meters

1. The skier who jumped 90.1 meters scored more points than Denise.
2. Patti scored 7 fewer points than the contestant who jumped 102.9 meters.
3. The jumper who scored 103 points was either Patti or the contestant who
jumped 102.9 meters.
4. Shawna jumped 96.3 meters.
5. Denise scored 89 points.
"""


def skiing_puzzle():
    # create an EnumSort for names
    # store points/distances as ints/floats (so we can do relations later)
    # make functions from name to points and name to distance
    # handle clues that don't use names by making up a constant for it
    solver = Solver()

    Skier, skier_consts = EnumSort("Skier",
                                 ["Denise", "Madeline", "Patti", "Shawna"])
    denise, madeline, patti, shawna = skier_consts

    points = Function("points", Skier, IntSort())
    solver.add(Distinct([points(name) for name in skier_consts]))
    for name in skier_consts:
        solver.add(Or(points(name) == 82,
                      points(name) == 89,
                      points(name) == 96,
                      points(name) == 103))

    distance = Function("distance", Skier, RealSort())
    solver.add(Distinct([distance(name) for name in skier_consts]))
    for name in skier_consts:
        solver.add(Or(distance(name) == 90.1,
                      distance(name) == 95.0,
                      distance(name) == 96.3,
                      distance(name) == 102.9))

    # 1. The skier who jumped 90.1 meters scored more points than Denise.
    name_clue1 = Const("name_clue1", Skier)
    solver.add(distance(name_clue1) == 90.1)
    solver.add(points(name_clue1) > points(denise))

    # 2. Patti scored 7 fewer points than the contestant who jumped 102.9
    # meters.
    name_clue2 = Const("name_clue2", Skier)
    solver.add(points(patti) == points(name_clue2) - 7)
    solver.add(distance(name_clue2) == 102.9)

    # 3. The jumper who scored 103 points was either Patti or the contestant
    # who jumped 102.9 meters.
    name1_clue3, name2_clue3 = Consts("name1_clue3 name2_clue3", Skier)
    solver.add(points(name1_clue3) == 103)
    solver.add(distance(name2_clue3) == 102.9)
    solver.add(Xor(name1_clue3 == patti, name1_clue3 == name2_clue3))

    # 4. Shawna jumped 96.3 meters.
    solver.add(distance(shawna) == 96.3)

    # 5. Denise scored 89 points.
    solver.add(points(denise) == 89)

    if solver.check() == sat:
        m = solver.model()
        for name in skier_consts:
            print("{}: {} points, {}m"
                  .format(name,
                          m.eval(points(name)),
                          m.eval(distance(name)).as_decimal(1)))
        # eliminate this solution and check if it is unique
        expressions = []
        for name in skier_consts:
            expressions.append(points(name) != m.eval(points(name)))
            expressions.append(distance(name) != m.eval(distance(name)))
        solver.add(Or(expressions))
        if solver.check() == unsat:
            print("Solution is unique")
        else:
            print("Solution is not unique")
    else:
        print("Contradiction!")


if __name__ == "__main__":
    skiing_puzzle()