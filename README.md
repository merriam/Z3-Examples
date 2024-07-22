# Z3-Examples
**Z3 (Z3Py) Constraint Solver, Well Documented Source Examples**

## What you will find

This repository contains a few samples using the open source Z3 Theorem Provder (constraint solver).

In this repository, you will find:

- Source code from the  [Z3 Python Introduction](https://microsoft.github.io/z3guide/programming/Z3%20Python%20-%20Readonly/Introduction) updated to Python 3.x.   The code shows syntax snippets for Z3, culminating in solving some simple puzzles and a trivial package dependency solver.  The code in one file `z3_guide_code_samples.py`, which is in turn divided into a function for each section of the guide.
- Source code from Dave Cook’s [blog entry on solving logic puzzles in Z3](https://davidsherenowitsa.party/2018/09/19/solving-logic-puzzles-with-z3.htm).   These three examples solve similar logic puzzles of the “The skier with 96 points jumped farther than Denise” variety.   There is also the file `dave_cook_skiiing_comments.py` in which I added lots and lots comments as I gained understanding.  This is a style of coding practical only for exploring code.
- Source code for my own logic puzzle solver, `logic_puzzles.py`.   This is a journey of writing progressively more specific code for logic puzzles in order to make writing any particular puzzle less repetitive.  It is heavily patterned from Dave Cook’s code, and starts using helper functions to add to z3 solutions.

Not in this repository, but worth reading:

- The large example, [Zistack's Satisfactory Optimizer repo](https://github.com/Zistack/Satisfactory-Optimizer), which uses Z3 to model an entire factory and handle production over time.   The code is written in the ‘documentation is bad’ style, though does try to solve a non-toy problem with z3.
- The ["Eric Pony" z3py pages](https://ericpony.github.io/z3py-tutorial/advanced-examples.htm) pages include some advanced topics, detailed information on strategies and fixpoints, and a links to [the z3Py API reference](https://z3prover.github.io/api/html/namespacez3py.html).  The pages are written by  [Leonardo de Moura](http://leodemoura.github.io/) and other z3 authors.

## What is Z3?  What are the parts?

Z3, or “The z3 Theorem Prover”, is a software placed into the public domain and basically abandoned by MicroSoft back in 2017ish.  It is free and is good enough to learn about constraint programming and SMT specifically.   The key pitfalls I would mention:

- Install `z3` before installing the Python bindings for it.  On MacOS, use `brew install z3` and then `pip install z3-solver` for the bindings.  Do not use `pip install z3` which is an obsolete cloud-storage package.
- The introduction will throw a ton of vocabulary at you, mostly academic.  Z3 does take some naming from its underlying mathematics literatures.
    - “Sort” means “z3 Type”.  So you will see an IntSort, EnumSort, etc.
    - “Function” means a z3 Function object for an unspecified function that gets constraints.  That is, a z3 Function created by `x = Function(”x”, IntType(), FloatType())` is a function like `x(int)->float` that could return any float for any int.  If I constrain it in my solver using `solver.add(x(3) == 4.0)` then I know what it will do with the input 3, but not any other input.   These are called “First Order Functions”.
    - “Const” means a z3 variable.  That is, a variable which will end with a value that satisfies constraints if a solution is found.
- The general flow is like a lot of early AI attempts which emphasized some incredibly opaque solver engine and lots of persnickety domain information:
    - Set up a lot of problem specific information, called constraints.  A constraint is a Python statement such as `solver.add(x + y == 3)` where overridden `+` and `==` operators create a structure describing the constraint that is accumulated in the solver.  What looks like an expression is actually deferred until the solver turns its magic crank.
    - Turn the magic crank.   `solver.solve()` takes all constraints given so far and tries to make some concrete values and Function implementations that satisfy the constraints given.  How it does this is complicated, like all turn-the-crank AI.
    - Read the outputs of the solver, usually printing the Const values and evaluating the functions for some inputs.
    
    This means debugging z3 requires a separate skill set than conventional programming.
    
- The Theorem Prover path of AI is mostly dead because it fundamentally deals with deterministic and boolean models.   It can work with “the machine makes a part in six minutes” and cannot work with “the machine makes the part in an average of six minutes, with a bell curve distribution standard deviation of 2 minutes” or “here is data on how long the machine has taken to date”.
- There are many alternates to z3 for those using constraint solving for real work: check the term “operations research” for alternate offerings from Google, Microsoft, and others.  z3 can teach you enough to encode toy problems like Soduku, Pix-a-pix, logic puzzles, and otherwise be dangerous.  There are bindings for various languages, though z3’s “native” language is lisp-like expression chains.

## License

This work incorporates work from different authors.  You distribute my work under the permissive BSD license, and will need to contact other authors for licenses to their work.

## History and Updates

Feel free to contact me by email, using ‘z3’ in the title, at charles.merriam@gmail.com. 

First release of this repository in September, 2023.