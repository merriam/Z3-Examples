# from blog at https://davidsherenowitsa.party/2018/09/19/solving-logic-puzzles-with-z3.html
# and source at https://gist.github.com/divergentdave/13a2a557c26146fc3e3b15a398f8428b

from z3 import (
    Solver,
    Function,
    EnumSort,
    IntSort,
    Const,
    Distinct,
    And,
    Or,
    sat,
    unsat,
)

ORDINALS = {
    1: "1st",
    2: "2nd",
    3: "3rd",
    4: "4th",
    5: "5th",
}


def poker_puzzle():
    solver = Solver()

    Player, player_consts = EnumSort("Player",
                                 ["Usain", "Terry", "Oliver", "Neil", "Ian"])
    usain, terry, oliver, neil, ian = player_consts

    # ??? Source had an error here, reusing "Player"
    Card, card_consts = EnumSort("Card",
                                 ["2", "5", "6", "7", "J", "Q", "K"])
    card_2, card_5, card_6, card_7, card_J, card_Q, card_K = card_consts

    left = Function("left", Player, Card)
    solver.add(Distinct([left(name) for name in player_consts]))
    for name in player_consts:
        solver.add(Or(left(name) == card_6,
                      left(name) == card_7,
                      left(name) == card_J,
                      left(name) == card_Q,
                      left(name) == card_K))

    right = Function("right", Player, Card)
    solver.add(Distinct([right(name) for name in player_consts]))
    for name in player_consts:
        solver.add(Or(right(name) == card_2,
                      right(name) == card_5,
                      right(name) == card_J,
                      right(name) == card_Q,
                      right(name) == card_K))

    fold = Function("fold", Player, IntSort())
    solver.add(Distinct([fold(name) for name in player_consts]))
    for name in player_consts:
        solver.add(fold(name) >= 1, fold(name) <= 5)

    # ... nobody was dealt a pair in hand.
    for name in player_consts:
        solver.add(left(name) != right(name))

    # One player, first to fold, ... "That's the worst possible hand..."
    name_clue2 = Const("name_clue2", Player)
    solver.add(fold(name_clue2) == 1)
    solver.add(Or(And(left(name_clue2) == card_2,
                      right(name_clue2) == card_7),
                  And(left(name_clue2) == card_7,
                      right(name_clue2) == card_2)))

    # The card in Oliver's right hand had given him a pair on the flop
    solver.add(right(oliver) == card_Q)

    # Ian folded 4th, having chased an inside straight that he'd seen on the
    # flop, though he didn't get so much as a pair
    solver.add(fold(ian) == 4)
    solver.add(left(ian) != card_J, right(ian) != card_J)
    solver.add(left(ian) != card_Q, right(ian) != card_Q)
    solver.add(left(ian) != card_K, right(ian) != card_K)

    # Terry had two pair with the turn card
    solver.add(Or(left(terry) == card_Q, right(terry) == card_Q))
    solver.add(Or(left(terry) == card_J, right(terry) == card_J))

    # The third player to fold, ... had a queen in his left hand
    name_clue6 = Const("name_clue6", Player)
    solver.add(fold(name_clue6) == 3)
    solver.add(left(name_clue6) == card_Q)

    # Neil folded next after Usain, refusing to chase an inside straight...
    solver.add(fold(neil) == fold(usain) + 1)

    if solver.check() == sat:
        m = solver.model()
        for name in player_consts:
            print("{} had {}{} and folded {}"
                  .format(name,
                          m.eval(left(name)),
                          m.eval(right(name)),
                          ORDINALS[m.eval(fold(name)).as_long()]))

        expressions = []
        for name in player_consts:
            expressions.append(left(name) != m.eval(left(name)))
            expressions.append(right(name) != m.eval(right(name)))
            expressions.append(fold(name) != m.eval(fold(name)))
        solver.add(Or(expressions))
        if solver.check() == unsat:
            print("Solution is unique")
        else:
            print("Solution is not unique")


if __name__ == "__main__":
    poker_puzzle()