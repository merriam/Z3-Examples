""" create puzzle from long description string """
from z3 import *


def rip(string, ripped):
    # rip('2,343', ',') -> '2343'
    return ''.join(string.split(ripped))


class Struct:    # an empty class, basically handy a dict that uses dot notation.
    pass


"""
This is the first logic puzzle I coded.  You will see functions made without helpers.   It takes me writing some
code about three times before I can generalize it.  I'm following Dave Cook's logic for now.
---
Tiffany is looking for a new podcast to listen to on her commute to and from work each day. Help her narrow down 
her choices by matching each podcast host to his or her topic, and determine how many total downloads each podcast 
currently has and what year it began.

1. Eva Estrada's podcast has 1 million fewer downloads than Dixie Dean's podcast.
2. Of the show that began in 2012 and the show that began in 2014, one has 2 million downloads and the other is Dixie Dean's.
3. Faye Fender's podcast is either the show that began in 2012 or the show that began in 2011.
4. Bobby Bora's show is either the podcast with 3 million downloads or the show with 1 million downloads.
5. The show that began in 2010 has more downloads than the show that began in 2011.

"""
def podcast_puzzle():
    print("\n====\nPodcast Puzzle\n\n====")
    p = Struct()

    s = Solver()

    # enum Hosts, with local labels in p struct
    host_names = "BobbyBora,DixieDean,EvaEstrada,FayeFender".split(",")
    Host, host_consts = EnumSort("Host", host_names)
    p.Bobby, p.Dixie, p.Eva, p.Faye = host_consts
    # The problem with allowing both 'Host' and 'host' is trying to read code aloud.
    # Also, EnumSort names are global across solvers and there appears no way to delete or reuse a name.

    # Years
    year = Function("year", Host, IntSort())  # year_to_host()
    # While it is not documented:  It's Function(name, input_type, return_type)
    # So, this could be called host_to_year().
    s.add(Distinct([year(host) for host in host_consts]))
    for host in host_consts:
        s.add(Or(year(host) == 2010,
                 year(host) == 2011,
                 year(host) == 2012,
                 year(host) == 2014))

    # Downloads, in millions
    download = Function("download", Host, IntSort())  # host_to_download()
    s.add(Distinct([download(host) for host in host_consts]))
    for host in host_consts:
        s.add(Or(download(host) == 1,
                 download(host)==2,
                 download(host)==3,
                 download(host)==4))

    # Clues...
    # 1. Eva Estrada's podcast has 1 million fewer downloads than Dixie Dean's podcast.
    s.add(download(p.Eva) - 1 == download(p.Dixie))

    # 2. Of the show that began in 2012 and the show that began in 2014, one has 2 million downloads and the other is Dixie Dean's.
    host2012, host2014 = Consts("host2012 host2014", Host)
    s.add(year(host2012) == 2012, year(host2014) == 2014)
    s.add(Xor(And(download(host2012) == 2, host2014 == p.Dixie),
              And(download(host2014) == 2, host2012 == p.Dixie)))

    # 3. Faye Fender's podcast is either the show that began in 2012 or the show that began in 2011.
    host2011 = Const("host2011", Host)
    s.add(year(host2011) == 2011)
    # note that host2012 is the same as clue 2.  We could make another variable and make the solver
    # figure out they are the same.  You decide which is clearer to write.
    s.add(Xor(p.Faye == host2012, p.Faye == host2011))

    # 4. Bobby Bora's show is either the podcast with 3 million downloads or the show with 1 million downloads.
    host1million, host3million = Consts("host1million host3million", Host)
    s.add(download(host1million)==1, download(host3million) == 3)
    s.add(Xor(p.Bobby == host1million, p.Bobby == host3million))

    # 5. The show that began in 2010 has more downloads than the show that began in 2011.
    host2010 = Const("host2010", Host)
    s.add(download(host2010) > download(host2011))

    solver=s   # because I cut and paste and did not want to rename :)
    # solver.check() means the engine should do its thing
    if solver.check() == sat:
        # If we find a solution, we can use the model to get the full grid
        m = solver.model()
        for host in host_consts:
            print("{}: {} million downloads, started in {}"
                  .format(host,
                          m.eval(download(host)),
                          m.eval(year(host))))
        # eliminate this solution and check if it is unique
        expressions = []
        for name in host_consts:
            expressions.append(download(name) != m.eval(download(name)))
            expressions.append(year(name) != m.eval(year(name)))
        solver.add(Or(expressions))
        if solver.check() == unsat:
            print("Solution is unique")
        else:
            print("Solution is not unique")
    else:
        print("Contradiction!  No solution possible.")



""""
This is the beginnings of a generic class for handling Logic puzzles with less coding for 
specific puzzles.  There is actually little variation in the puzzles themselves, and the code
is usually translating back and forth from a primary type.  So a minilanguage is possible.
 
 For example, the coral_city puzzle would look like this:
 
 p = Puzzle.from_text('''
          Month: January, February, March, April, May, June, July;
          Visitor:  6425, 6910, 7525, 8060, 8880, 9500, 10425;
          Country:  Chile, Eritrea,  Honduras, Iraq, Jamaica, Kyrgzstan, Norway;
          Exhibit:  armor, basketry, ceramics, firearms, glassware, lacquerware, sculpture''')
          
# 1. The presentation from Kyrgyzstan was held 3 months after the exhibit from Jamaica.
p.clue("Kyrgyzstan.num == Jamica.num + 3")
# 2. February's exhibit is either the presentation that pulled in 6,910 visitors or the firearms presentation.
p.clue("February == (6910 or Firearms)")   # alternate reverse polic like "February 6910 Firearms or =="

This work would some more coding, may need an eval() to run correctly, and would not add to my z3 understanding.
"""
class Puzzle:
    def __init__(self, group_dict):
        self.labels = dict()

        # dictionary with keys being the labels for used in the puzzle, with a leading underscore.
        # The values are the z3 data reference types
        # This means `add(p._Mark == p._Baseball)` is something you might write.

        self.solver = Solver()

    """ Create from a block of text, where the text block is just a dictionary, e.g., 'key1: value1, value2, value3 ; key2:....'"""
    @classmethod
    def from_text(cls, text_block):
        d = dict()
        groups = text_block.split(';')
        for key, value_block in [g.split(':') for g in groups]:
            raw_values = [value.strip() for value in value_block.split(',')]
            try:
                values = [int(rip(v, ',')) for v in raw_values]
            except ValueError:
                try:
                    values = [float(rip(v, ',')) for v in raw_values]
                except ValueError:
                    values = raw_values
            d[key.strip()] = values
        return cls(d)




# p = Puzzle.from_text("""
#          Month: January, February, March, April, May, June, July;
#          Visitor:  6425, 6910, 7525, 8060, 8880, 9500, 10425;
#          Country:  Chile, Eritrea,  Honduras, Iraq, Jamaica, Kyrgzstan, Norway;
#          Exhibit:  armor, basketry, ceramics, firearms, glassware, lacquerware, sculpture""")

"""
Create a Z3 EnumSort, and add the constants to struct"""
def make_enum(p, kind_name, kind_values):
    kind, kind_consts = EnumSort(kind_name, kind_values)
    for i in range(len(kind_values)):
        setattr(p, "_"+str(kind_values[i]), kind_consts[i])
    return kind, kind_consts

# create functions to and from the primary puzzle enum.
def make_func(solver, name, back_name, from_kind, from_consts, to_kind, to_values):
    fn = Function(name, from_kind, to_kind)
    solver.add(Distinct([fn(con) for con in from_consts]))
    for con in from_consts:
        solver.add(Or([(fn(con) == val) for val in to_values]))
    back_fn = Function(back_name, to_kind, from_kind)
    solver.add(*[back_fn(fn(con)) == con for con in from_consts])
    solver.add(*[fn(back_fn(val)) == val for val in to_values])  # added during debugging, may be superfluous
    return fn, back_fn


"""
I wrote this example second.  I finalized use the make_func() and make_enum() 
helper functions making the code felt less repetitive.   I found it necessary, for
sanity's sake, to use abbreviations for the long labels used in the puzzle.  For 
example, "Deep Shadow" is "Deep" and "Mission Vale" is "Mission".   I also used
two way functions to encode the clues more clearly.  

It became clear breaking out the solution printing into `solver_check()` was useful.  
I ended up coding the puzzle, then immediately printing a solution.  I could verify by eye that the solution,
while ignoring any clues, did have a uniques exhibits in unique months.   After adding each clue, I could see
the solution it came up with satisfied the clues given.   If it did not, I had localized the problem.

Unfortunately, I found that the puzzle site generated this puzzle with multiple solutions by not having 
quite enough clues.

--
A number of "real life superheroes" have set up shop in Paradise City, hoping to clean up the streets. Match each 
person to his superhero identity, and determine the year he started and the neighborhood he patrols.

1. Red Reilly began 1 year before "Deep Shadow".
2. The hero who patrols Idyllwild isn't Ned Nielsen.
3. Arnold Ashley is either "Deep Shadow" or "Green Avenger".
4. The superhero who started in 2010, "Deep Shadow", the superhero who patrols Libertyville, the hero who patrols Summerland and the person who patrols Tenth Avenue are all different people.
5. "Wonderman" began sometime before Hal Houston.
6. Of the superhero who patrols Frazier Park and the hero who started in 2007, one is Lyle Lucas and the other is "Wonderman".
7. Red Reilly began sometime after the hero who patrols Mission Vale.
8. The hero who started in 2009 is either Cal Copeland or Arnold Ashley.
9. The person who patrols Mission Vale began 1 year before Lyle Lucas.
10. Neither the superhero who started in 2012 nor "Deep Shadow" is the hero who patrols Libertyville.
11. "Ultra Hex" is either the person who patrols Frazier Park or Ned Nielsen.
12. "Prism Shield" doesn't patrol Idyllwild.
13. The person who patrols Mission Vale isn't Ned Nielsen.
14. Cal Copeland began sometime before "Max Fusion".
15. The superhero who patrols Frazier Park began 3 years before "Criminal Bane".
16. Of "Green Avenger" and "Prism Shield", one patrols Tenth Avenue and the other is Peter Powers.
"""
def hero_puzzle():
    print("\n====\nHero Puzzle\n\n====")

    s = Solver()
    p = Struct()

    # The setup
    hero_values = "Criminal, Deep, Green, Max, Prism, Ultra, Wonderman".split(", ")
    name_values = "Arnold, Cal, Hal, Lyle, Ned, Peter, Red".split(", ")
    hood_values = "Apple, Frazier, Idyllwild, Libertyville, Mission, Summerland, Tenth".split(", ")
    year_values = 2007, 2008, 2009, 2010, 2011, 2012, 2013
    Hero, hero_consts = make_enum(p, "hero", hero_values)
    Name, name_consts = make_enum(p, "Name", name_values)
    Hood, hood_consts = make_enum(p, "Hood", hood_values)
    hero_to_name, name_to_hero = make_func(s, "hero_to_name", "name_to_hero", Hero, hero_consts, Name, name_consts)
    hero_to_hood, hood_to_hero = make_func(s, "hero_to_hood", "hood_to_hero", Hero, hero_consts, Hood, hood_consts)
    hero_to_year, year_to_hero = make_func(s, "hero_to_year", "year_to_hero", Hero, hero_consts, IntSort(), year_values)

    # solver_check args
    primary_consts = hero_consts
    helper_fn = [hero_to_name, hero_to_hood, hero_to_year]
    line = "The hero {:13} (aka {:7}) has patrolled {:>13} since {}"

    # Clues.  Notice how reverse functions cut out temporary variables
    # 1. Red Reilly began 1 year before "Deep Shadow".
    s.add(hero_to_year(name_to_hero(p._Red)) + 1 == hero_to_year(p._Deep))

    # 2. The hero who patrols Idyllwild isn't Ned Nielsen.
    s.add(hood_to_hero(p._Idyllwild) != name_to_hero(p._Ned))

    # 3. Arnold Ashley is either "Deep Shadow" or "Green Avenger".
    s.add(Or(name_to_hero(p._Arnold) == p._Deep, name_to_hero(p._Arnold) == p._Green))
    # In a future program, this could encode as `Or(Arnold == Deep, Arnold == Green)`
    # or even `Arnold == (Deep, Green)`

    # 4. The superhero who started in 2010, "Deep Shadow", the superhero who patrols Libertyville, the hero who
    # patrols Summerland and the person who patrols Tenth Avenue are all different people.
    s.add(Distinct(year_to_hero(2010), p._Deep, hood_to_hero(p._Libertyville), hood_to_hero(p._Summerland), hood_to_hero(p._Tenth)))

    # 5. "Wonderman" began sometime before Hal Houston.
    s.add(hero_to_year(p._Wonderman) < hero_to_year(name_to_hero(p._Hal)))

    # 6. Of the superhero who patrols Frazier Park and the hero who started in 2007, one is Lyle Lucas and the other is "Wonderman".
    s.add(Xor(And(hood_to_hero(p._Frazier) == name_to_hero(p._Lyle), year_to_hero(2007) == p._Wonderman),
              And(hood_to_hero(p._Frazier) == p._Wonderman, year_to_hero(2007) == name_to_hero(p._Lyle))))

    # 7. Red Reilly began sometime after the hero who patrols Mission Vale.
    s.add(hero_to_year(name_to_hero(p._Red)) > hero_to_year(hood_to_hero(p._Mission)))

    # 8. The hero who started in 2009 is either Cal Copeland or Arnold Ashley.
    s.add(Xor(year_to_hero(2009) == name_to_hero(p._Cal), year_to_hero(2009) == name_to_hero(p._Arnold)))

    # 9. The person who patrols Mission Vale began 1 year before Lyle Lucas.
    s.add(hero_to_year(hood_to_hero(p._Mission)) + 1 == hero_to_year(name_to_hero(p._Lyle)))
    # Mission.year + 1 == Lyle.year

    # 10. Neither the superhero who started in 2012 nor "Deep Shadow" is the hero who patrols Libertyville.
    s.add(And(hood_to_hero(p._Libertyville) != year_to_hero(2012),
              hood_to_hero(p._Libertyville) != p._Deep))

    # 11. "Ultra Hex" is either the person who patrols Frazier Park or Ned Nielsen.
    s.add(Xor(p._Ultra == hood_to_hero(p._Frazier), p._Ultra == name_to_hero(p._Ned)))


    # 12. "Prism Shield" doesn't patrol Idyllwild.
    s.add(p._Prism != hood_to_hero(p._Idyllwild))

    # 13. The person who patrols Mission Vale isn't Ned Nielsen.
    s.add(hood_to_hero(p._Mission) != name_to_hero(p._Ned))

    # 14. Cal Copeland began sometime before "Max Fusion".
    s.add(hero_to_year(name_to_hero(p._Cal)) < hero_to_year(p._Max))

    # 15. The superhero who patrols Frazier Park began 3 years before "Criminal Bane".
    s.add(hero_to_year(hood_to_hero(p._Frazier)) + 3 == hero_to_year(p._Criminal))

    # 16. Of "Green Avenger" and "Prism Shield", one patrols Tenth Avenue and the other is Peter Powers.
    s.add(Xor(And(p._Green == hood_to_hero(p._Tenth),
                  p._Prism == name_to_hero(p._Peter)),
              And(p._Green == name_to_hero(p._Peter),
                  p._Prism == hood_to_hero(p._Tenth))))

    solver_check(s, line, primary_consts, helper_fn)


"""
This is the third puzzle solution I wrote.    I did not
push code generalization here, just trying to do a large puzzle with many clues. 

This also had the first bug that took a while to find.  In clue 3, "8880 visitors" are involved.  When I mistyped
to "8800", this meant I was calling a Z3 function `visitors_to_month` ith an unexpected input.   Z3 then sees no
constraints on that, and returns a random month.  It was annoying to track down because reciprocal relationships did
not hold, that is, `month_to_visitors(visitors_to_month(8800)) == 6425`.  I left some of the code I used
in comments at the bottom of this function.  I found that the functions to print the string representations of the
solver's constraints truncate, at least in the Python wrapper.  After the bug, the two ideas I had were to just make
everything an EnumKind, so p._8800 would trigger an identifier error, or to add constraints to the functions that
checked the input was one of the known values.   Or, I could just be careful not to do that again.  Overall, Z3 requires
different debugging skills.
   
---
from https://logic.puzzlebaron.com

The Coral City Museum featured a number of "special exhibits" this year, each on loan from a different country. 
Using only the clues below, match each exhibit to the country that donated it and the month in which it was featured, 
and determine the total number of visitors it saw during its limited engagement.

1. The presentation from Kyrgyzstan was held 3 months after the exhibit from Jamaica.
2. February's exhibit is either the presentation that pulled in 6,910 visitors or the firearms presentation.
3. The presentation that pulled in 8,880 visitors wasn't from Norway.
4. Of the exhibit that pulled in 9,500 visitors and the glassware exhibit, one took place in June and the other was from Kyrgyzstan.
5. The armor exhibit was held 1 month after the presentation from Iraq.
6. The basketry presentation saw 8,880 visitors.
7. The presentation that pulled in 7,525 visitors was held sometime before the exhibit that pulled in 6,425 visitors.
8. The lacquerware presentation is either the exhibit from Jamaica or the presentation from Iraq.
9. The exhibit that pulled in 8,060 visitors was held 1 month before the exhibit from Jamaica.
10. The sculpture exhibit was held 2 months after the presentation that pulled in 8,060 visitors.
11. The firearms exhibit was held 1 month after the presentation that pulled in 8,060 visitors.  
12. The presentation from Honduras was held sometime before the basketry exhibit.
13. The lacquerware exhibit was held sometime after the sculpture presentation.
14. April's exhibit wasn't from Iraq.
15. The presentation that pulled in 7,525 visitors was from Chile.
16. The presentation that pulled in 6,425 visitors wasn't from Kyrgyzstan.
"""

def coral_city_puzzle():
    print("\n====\nCoral City Puzzle\n\n====")

    s = Solver()
    p = Struct()
    month_values = "January, February, March, April, May, June, July".split(", ")  # primary
    visitor_values = [6425, 6910, 7525, 8060, 8880, 9500, 10425]
    country_values = "Chile, Eritrea, Honduras, Iraq, Jamaica, Kyrgzstan, Norway".split(", ")
    exhibit_values = "Armor, Basketry, Ceramics, Firearms, Glassware, Lacquerware, Sculpture".split(", ")

    Month, month_consts = make_enum(p, "Month", month_values)

    Exhibit, exhibit_consts = make_enum(p, "Exhibit", exhibit_values)
    Country, country_consts = make_enum(p, "Country", country_values)
    month_to_visitors, visitors_to_month = make_func(s, "month_to_visitors", "visitors_to_month", Month, month_consts, IntSort(), visitor_values)
    month_to_country, country_to_month= make_func(s, "month_to_country", "country_to_month", Month, month_consts, Country, country_consts)
    month_to_exhibit, exhibit_to_month = make_func(s, "month_to_exhibit", "exhibit_to_country", Month, month_consts, Exhibit, exhibit_consts)

    # Month enums also need a numeric equivalent to do "before" or "1 month before"
    month_to_number = Function("month_to_number", Month, IntSort())
    for i, month in enumerate(month_consts):
        s.add(month_to_number(month) == i+1)

    # solver_check args
    primary_consts = month_consts
    helper_fn = [month_to_visitors, month_to_country, month_to_exhibit]
    line = "In month {:>9}, there were {:5} visitors to {}'s {} exhibit"

    # Clues.  Coding this got long and repetitive.
    # 1. The presentation from Kyrgyzstan was held 3 months after the exhibit from Jamaica.
    s.add(month_to_number(country_to_month(p._Kyrgzstan)) == month_to_number(country_to_month(p._Jamaica)) + 3)

    # 2. February's exhibit is either the presentation that pulled in 6,910 visitors or the firearms presentation.
    s.add(Xor(p._February == visitors_to_month(6910), p._February == exhibit_to_month(p._Firearms)))

    # 3. The presentation that pulled in 8,880 visitors wasn't from Norway.
    s.add(visitors_to_month(8880) != country_to_month(p._Norway))

    # 4. Of the exhibit that pulled in 9,500 visitors and the glassware exhibit, one took place in June and the other was from Kyrgyzstan.
    s.add(Xor(And(visitors_to_month(9500) == p._June, exhibit_to_month(p._Glassware) == country_to_month(p._Kyrgzstan)),
              And(visitors_to_month(9500) == country_to_month(p._Kyrgzstan), exhibit_to_month(p._Glassware) == p._June)))

    # 5. The armor exhibit was held 1 month after the presentation from Iraq.
    s.add(month_to_number(exhibit_to_month(p._Armor)) == 1 + month_to_number(country_to_month(p._Iraq)))

    # 6. The basketry presentation saw 8,880 visitors.
    s.add(visitors_to_month(8880) == exhibit_to_month(p._Basketry))

    # 7. The presentation that pulled in 7,525 visitors was held sometime before the exhibit that pulled in 6,425 visitors.
    s.add(month_to_number(visitors_to_month(7525)) < month_to_number(visitors_to_month(6425)))

    # 8. The lacquerware presentation is either the exhibit from Jamaica or the presentation from Iraq.
    s.add(Xor(exhibit_to_month(p._Lacquerware) == country_to_month(p._Jamaica),
              exhibit_to_month(p._Lacquerware) == country_to_month(p._Iraq)))

    # 9. The exhibit that pulled in 8,060 visitors was held 1 month before the exhibit from Jamaica.
    s.add(month_to_number(visitors_to_month(8060)) + 1 == month_to_number(country_to_month(p._Jamaica)))

    # 10. The sculpture exhibit was held 2 months after the presentation that pulled in 8,060 visitors.
    s.add(month_to_number(exhibit_to_month(p._Sculpture)) == 2 + month_to_number(visitors_to_month(8060)))

    # 11. The firearms exhibit was held 1 month after the presentation that pulled in 8,060 visitors.
    s.add(month_to_number(exhibit_to_month(p._Firearms)) == 1 + month_to_number(visitors_to_month(8060)))

    # 12. The presentation from Honduras was held sometime before the basketry exhibit.
    s.add(month_to_number(country_to_month(p._Honduras)) < month_to_number(exhibit_to_month(p._Basketry)))

    # 13. The lacquerware exhibit was held sometime after the sculpture presentation.
    s.add(month_to_number(exhibit_to_month(p._Lacquerware)) > month_to_number(exhibit_to_month(p._Sculpture)))

    # 14. April's exhibit wasn't from Iraq.
    s.add(p._April != country_to_month(p._Iraq))

    # 15. The presentation that pulled in 7,525 visitors was from Chile.
    s.add(visitors_to_month(7525) == country_to_month(p._Chile))

    # 16. The presentation that pulled in 6,425 visitors wasn't from Kyrgyzstan.
    s.add(visitors_to_month(6425) != country_to_month(p._Kyrgzstan))

    solver_check(s, line, primary_consts, helper_fn)

    s.check()
    #
    # This is a sample of a bunch of debug I added to track down a problem.
    #
    # I identified where something went wrong, because I was running the program to see output between adding clues.
    # Still, figuring out why I was getting an answer that seemed to contradict the clue took some time.
    #
    # m=s.model()
    # print("So, is the month of basketry same as month of 8880?")
    # print("Basketry month is {} and back {}".format(m.eval(exhibit_to_month(p._Basketry)), m.eval(month_to_exhibit(exhibit_to_month(p._Basketry)))))
    # print("8880 month is {} and back {}".format(m.eval(visitors_to_month(8880)), m.eval(month_to_visitors(visitors_to_month(8880)))))
    #
    # print("\nChecking Exhibits...")
    # for month in month_consts:
    #     print("Month of {} has {} exhibit, which is in month of {}".format(
    #         month, m.eval(month_to_exhibit(month)), m.eval(exhibit_to_month(month_to_exhibit(month)))))
    # for exhibit in exhibit_consts:
    #     print("{} exhibit in month {}, which is {} exhibit".format(
    #         exhibit, m.eval(exhibit_to_month(exhibit)), m.eval(month_to_exhibit(exhibit_to_month(exhibit)))))
    #
    # print("\nChecking Visitors...")
    # for month in month_consts:
    #     print("Month of {} has {} visitors, which are in month of {}".format(
    #         month, m.eval(month_to_visitors(month)), m.eval(visitors_to_month(month_to_visitors(month)))))
    # for visitors in visitor_values:
    #     print("{} visitors in month {}, which had {} visitors".format(
    #         visitors, m.eval(visitors_to_month(visitors)), m.eval(month_to_visitors(visitors_to_month(visitors)))))
    #
    # print("\nChecking clue")
    # print("Clue OK?", m.eval(visitors_to_month(8880) == exhibit_to_month(p._Basketry)))
    # print("Clue OK?", m.eval((visitors_to_month(8880) == exhibit_to_month(p._Basketry))))
    # print("Clue OK? {} == {}".format(m.eval((visitors_to_month(8880))), m.eval(exhibit_to_month(p._Basketry))))
    # print(f"{str(m.eval(visitors_to_month(8880)))=} and {m.eval(exhibit_to_month(p._Basketry))=}")
    # print("so {} == 8880 and {} == Basketry?".format(m.eval(month_to_visitors(p._March)), m.eval(month_to_exhibit(p._March))))
    # print(f"{m.eval(visitors_to_month(8880))=} and {m.eval(visitors_to_month(6910))=}")
    # print(f"{m.eval(month_to_visitors(p._July))=} and {m.eval(visitors_to_month(month_to_visitors(p._July)))=}")
    # print(f"  and {m.eval(visitors_to_month(8880))=}")
    # print("so m->v(March) is wrong, v8880->July, (march) == v")
    # solver.add(*[back_fn(fn(con)) == con for con in from_consts])
    # solver.add(*[fn(back_fn(val)) == val for val in to_values])
    pass


def solver_check(solver, line, primary_consts, helper_fn):
    # Run the solver, print the solution, check for uniqueness

    # solver.check() means the engine should do its thing
    if solver.check() == sat:
        # If we find a solution, we can use the model to get the full grid
        m = solver.model()
        for primary in primary_consts:
            print(line.format(str(primary), *[str(m.eval(fn(primary))) for fn in helper_fn]))

        # Eliminate this solution, then solve again to check if it is unique.
        # that is, add the constraint to the solver that least of the functions would return a different
        # value than the current solution.   I did not use the Z3 `push` and `pop` operators
        # to safeguard the solver object from this new constraint.  Therefore, the function is not
        # idempotent:  the new constraint disallows the found solution.
        #
        expressions = []
        for primary in primary_consts:
            for fn in helper_fn:
                expressions.append(fn(primary) != m.eval(fn(primary)))
        solver.add(Or(expressions))
        if solver.check() == unsat:
            print("Solution is unique")
        else:
            print("Solution is not unique")
            print("One alternate solution:")
            m = solver.model()
            for primary in primary_consts:
                print(line.format(str(primary), *[str(m.eval(fn(primary))) for fn in helper_fn]))
    else:
        print("Contradiction!  No solution possible.")


"""
I started designing a fourth puzzle solution, aimed at making the clues easier and less verbose to code.

The goal would be encoding this clue:

    4. Of the exhibit that pulled in 9,500 visitors and the glassware exhibit, one took place in June and the other was from Kyrgyzstan.

as

    clue(s, "(9500, Glass) == (June, Ky)")

Meaning that I would have be able to look up the labels, including just using a prefix "Ky" for the oft misspelled "Kyrgzstan".
I would also use parenthesis for an "Xor" clause.   After a bit of futzing and exploring
about how I would construct the statements given all the operator overloading done to delay processing Z3 variables,
I figured that I would end up doing a bunch of strings and use an evil `eval()`.   Not something I would learn from,
so I didn't do it.
"""

if __name__ == "__main__":
    podcast_puzzle()
    hero_puzzle()
    coral_city_puzzle()
