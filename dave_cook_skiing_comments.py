#!/usr/bin/env python3

# The "shebang" or ("she" for the '#' shell, 'bang' for the "!") line means that that making this line
# a Unix executable (`chmod +x`)  will run using the currently set python3 executable.
# python3 is just the name of python, while python2 is the old version of python.  'python' might be eithe.

# from blog at https://davidsherenowitsa.party/2018/09/19/solving-logic-puzzles-with-z3.html
# and source at https://gist.github.com/divergentdave/13a2a557c26146fc3e3b15a398f8428b
# and comments added by Charles Merriam in 2023.

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
# An alternate approach is to `import * from z3`.
# Personally, I love how Python allows easy transition from writing exploratory code that can be thrown away to a
# somewhat higher quality control.  Exploratory, or throw away code, might use `import * from z3` to just get on with
# exploration.

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
"""
First, note that a lot rules are common to all of these logic puzzles.  For example,
each point value is scored by exactly one skier.  The set up of the puzzle consists
of the groups, available values, and stripping the units off.  One could imagine calling
a function to describe the entire puzzle setup:


   Puzzle('''Jumpers:  Denise, Madeline, Patti, Shawna
             Points:  82, 89, 96, 103
             Distances: 90.1, 95.0, 96.3, 102.9```)
             
             
Also, you might notice for this puzzle that we could encode a bit more compactly.  The points are exactly 7 apart; 
the names have a unique first letter. Encoding the clues in the most readable manner is more important than saving
a few keystrokes.

This one long function, because its basically exploratory code.
"""

def skiing_puzzle():
    solver = Solver()    # create the solver to which we will add constraints

    # Set up the puzzle.  This section encodes our groups and values.  We pick Skier as the primary
    # group from which we use functions to get the Point and Distance values.  Points will be integers
    # and distances will be floating point.  Integers and floating point values allow comparison operators like
    # greater-than will be needed when encoding the clues.

    # store points/distances as ints/floats (so we can do relations later)
    # make functions from name to points and name to distance
    # handle clues that don't use names by making up a constant for it

    # Create the Skier EnumSort, an array of all skiers in `skier_consts`, and individual
    # variables for each Skier const.  Remember Z3 vocabulary:  "Sort" means "Z3 type" and "Const"
    # means "Z3 variable".

    Skier, skier_consts = EnumSort("Skier",
                                 ["Denise", "Madeline", "Patti", "Shawna"])
    denise, madeline, patti, shawna = skier_consts

    # Create a Z3 function `points`, which is a short name for `skier_to_points(skier)->points`.
    # Z3 functions have no bodies, just a set of constraints they must meet.
    points = Function("points", Skier, IntSort())
    # `points(skier)` must return a different number of points for the different skiers
    solver.add(Distinct([points(name) for name in skier_consts]))
    # `points(skier)` must return one of the point values used in the puzzle
    for name in skier_consts:
        solver.add(Or(points(name) == 82,
                      points(name) == 89,
                      points(name) == 96,
                      points(name) == 103))

    # Create a Z3 function `distance`, which is a short name for `skier_to_distance(skier)->distance`.
    distance = Function("distance", Skier, RealSort())
    # distance(skier) must return different distances for each of the the different skiers
    solver.add(Distinct([distance(name) for name in skier_consts]))
    # distance(skier) must return one of the distances used in the puzzle
    for name in skier_consts:
        solver.add(Or(distance(name) == 90.1,
                      distance(name) == 95.0,
                      distance(name) == 96.3,
                      distance(name) == 102.9))

    # Encode the clues.
    # Each clue will add contraints to the solution, hopefully ending in a unique solution.  One common
    # debugging technique is to add only one clue, run the solver, and hand verify that the (non-unique) solution
    # found satisfies the clue.  Adding each clue and running again eventually gets the unique solution.

    # 1. The skier who jumped 90.1 meters scored more points than Denise.
    # Or, "An unknown skier, skier_clue1, satisfies the constraint distance(skier_clue1) == 90.1
    # and also satisfies points(skier_clue1) > points(Denise)".  Z3 will solve the question of which
    # skier is skier_clue1, but we don't print it out.
    skier_clue1 = Const("skier_clue1", Skier)
    solver.add(distance(skier_clue1) == 90.1)
    solver.add(points(skier_clue1) > points(denise))

    # There is a totally different way of writing these clues.  If we write the reverse function,
    # `distance_to_skier(distance) -> Skier` than we could encode the clue as
    # `solver.add(distance_to_skier(90.1) > points(denise))`
    #
    # That is, we could add this to the problem set up:
    #     distance_to_skier = Function("distance_to_skier", RealSort(), Skier)
    #     solver.add(Distinct([distance_to_skier(dist) for dist in [90.1, 95.0, 96.3, 102.9]]))
    #     for name in skier_consts:
    #         solver.add(Or(distance_to_skier(90.1) == name,
    #                       distance_to_skier(95.0) == name,
    #                       distance_to_skier(96.3) == name,
    #                       distance_to_skier(102.9) == name))
    # solver.add(points(distance_to_skier(90.1)) > points(denise))

    # 2. Patti scored 7 fewer points than the contestant who jumped 102.9
    # meters.
    skier_clue2 = Const("skier_clue2", Skier)
    solver.add(points(patti) == points(skier_clue2) - 7)
    solver.add(distance(skier_clue2) == 102.9)

    # 3. The jumper who scored 103 points was either Patti or the contestant
    # who jumped 102.9 meters.

    # For this clue, we will need multiple unknown skiers to 'run the points function backward'.
    # An alternate naming convention might be "skier_103_points" or "skier_1029_meters"
    skier1_clue3, skier2_clue3 = Consts("skier1_clue3 skier2_clue3", Skier)
    solver.add(points(skier1_clue3) == 103)
    solver.add(distance(skier2_clue3) == 102.9)
    solver.add(Xor(skier1_clue3 == patti, skier1_clue3 == skier2_clue3))
    # Notice this rule of logic puzzles are constructed:  the clue language states Patti did not jump 102.9 meters.
    # It is XOR, not an OR.

    # 4. Shawna jumped 96.3 meters.
    solver.add(distance(shawna) == 96.3)

    # 5. Denise scored 89 points.
    solver.add(points(denise) == 89)

    # Now, all the constraints are added.  The solver will do its thing (`solver.check()`) and try to find a
    # solution that we can print.  "sat" or "satisfied" is Z3 vocabulary for "solution was found"
    if solver.check() == sat:
        # If we find a solution, we can use the model to print the solution values by evaluating the solution's
        # functions.
        m = solver.model()
        for name in skier_consts:
            print("{}: {} points, {}m"
                  .format(name,
                          m.eval(points(name)),
                          m.eval(distance(name)).as_decimal(1)))

        # See if the solution is unique.
        # We do this by adding the constraint "And this exact solution is not it", meaning one of
        # the functions in the above grid returned a different value.
        # If we can still solve with this new constraint, then the solution was not unique.
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
        print("Contradiction!  No solution possible.")  # solver.check() returned unsat


if __name__ == "__main__":
    skiing_puzzle()