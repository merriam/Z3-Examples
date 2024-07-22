#!/usr/bin/env python3
from z3 import (
    Solver,
    Function,
    EnumSort,
    IntSort,
    Const,
    Distinct,
    And,
    Or,
    Xor,
    sat,
    unsat,
)


def television_puzzle():
    solver = Solver()

    Station, station_consts = EnumSort("Station",
                                 ["BNRG", "CVT", "KWTM", "PCR", "TWL"])
    bnrg, cvt, kwtm, pcr, twl = station_consts

    Show, show_consts = EnumSort("Show",
                                 ["Moneygab", "Ponyville", "Powertrips",
                                  "Soap_Suds", "Top_Chow"])
    moneygab, ponyville, powertrips, soapsuds, topchow = show_consts

    show = Function("show", Station, Show)
    solver.add(Distinct([show(name) for name in station_consts]))
    for name in station_consts:
        solver.add(Or(show(name) == moneygab,
                      show(name) == ponyville,
                      show(name) == powertrips,
                      show(name) == soapsuds,
                      show(name) == topchow))

    viewers = Function("viewers", Station, IntSort())
    solver.add(Distinct([viewers(name) for name in station_consts]))
    for name in station_consts:
        solver.add(viewers(name) >= 1, viewers(name) <= 5)

    channel = Function("channel", Station, IntSort())
    solver.add(Distinct([channel(name) for name in station_consts]))
    for name in station_consts:
        solver.add(Or(channel(name) == 15,
                      channel(name) == 22,
                      channel(name) == 43,
                      channel(name) == 56,
                      channel(name) == 62))

    # 1. Soap Suds (which doesn't have the most viewers) doesn't air on BNRG,
    # which has one million fewer viewers than the channel that airs
    # Powertrips.
    name1_clue1 = Const("name1_clue1", Station)
    name2_clue1 = Const("name2_clue1", Station)
    solver.add(show(name1_clue1) == soapsuds)
    solver.add(viewers(name1_clue1) != 5)
    solver.add(name1_clue1 != bnrg)
    solver.add(show(name2_clue1) == powertrips)
    solver.add(viewers(bnrg) == viewers(name2_clue1) - 1)

    # 2. Channel 22 has fewer viewers than the channel that airs Top Chow,
    # which has fewer viewers than TWL.
    name1_clue2 = Const("name1_clue2", Station)
    solver.add(channel(name1_clue2) == 22)
    name2_clue2 = Const("name2_clue2", Station)
    solver.add(show(name2_clue2) == topchow)
    solver.add(viewers(name1_clue2) < viewers(name2_clue2))
    solver.add(viewers(name2_clue2) < viewers(twl))

    # 3. TWL, which isn't carried on channel 56, boasts the most viewers of
    # all five channels.
    solver.add(channel(twl) != 56)
    solver.add(viewers(twl) == 5)

    # 4. Between PCR and the channel that airs Moneygab, one has three million
    # viewers and the other is on channel 22.
    name1_clue4 = Const("name1_clue4", Station)
    solver.add(show(name1_clue4) == moneygab)
    solver.add(Xor(And(viewers(pcr) == 3, channel(name1_clue4) == 22),
                   And(channel(pcr) == 22, viewers(name1_clue4) == 3)))

    # 5. Of channel 15 and the station that airs Ponyville, one is KWTM and
    # the other has the smallest viewership of all five channels.
    name1_clue5 = Const("name1_clue5", Station)
    solver.add(channel(name1_clue5) == 15)
    name2_clue5 = Const("name2_clue5", Station)
    solver.add(show(name2_clue5) == ponyville)
    solver.add(Xor(And(name1_clue5 == kwtm, viewers(name2_clue5) == 1),
                   And(name2_clue5 == kwtm, viewers(name1_clue5) == 1)))

    # 6. Moneygab doesn't air on either channel 15 or 56.
    name_clue6 = Const("name_clue6", Station)
    solver.add(show(name_clue6) == moneygab)
    solver.add(channel(name_clue6) != 15)
    solver.add(channel(name_clue6) != 56)

    # 7. CVT isn't carried on channel 62.
    solver.add(channel(cvt) != 62)

    if solver.check() == sat:
        m = solver.model()
        for name in station_consts:
            print("{}: {} million, {}, #{}"
                  .format(name,
                          m.eval(viewers(name)),
                          m.eval(show(name)),
                          m.eval(channel(name))))
        # eliminate this solution and check if it is unique
        expressions = []
        for name in station_consts:
            expressions.append(viewers(name) != m.eval(viewers(name)))
            expressions.append(channel(name) != m.eval(channel(name)))
            expressions.append(show(name) != m.eval(show(name)))
        solver.add(Or(expressions))
        if solver.check() == unsat:
            print("Solution is unique")
        else:
            print("Solution is not unique")
    else:
        print("Contradiction!")


if __name__ == "__main__":
    television_puzzle()