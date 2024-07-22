from z3 import *

"""
This was an attempt at the pix-a-pix colored puzzles.  I finally gave up from too
many instabilities in z3.  Lots of "sometimes eval returns a string of the variable name
but sometimes it returns a value" or "I think a segfault seems good right now".   
"""
"""
First puzzle:
   5 by 5, (blank), Red, Green, Brown
   Rows are  3R;5R;5R;1B;5G
   Cols are 2R,1G;3R,1G;3R,1B,1G;3R,1G;2R,1G
"""


def mushroom_puzzle():
    def show(title):
        if solver.check() == unsat:
            print(f"{title}:  No solution found, contradiction.")
        else:
            print(f"{title}:  Solution found.")
            m = solver.model()
            print("Current starts:")
            for s in starts:
                print(f"   {s}: {m.eval(s)}")
            for row in range(num_rows):
                for col in range(num_cols):
                    g = grid[row][col]
                    print(f" Grid {row}, {col}, variable {g}, value {m.eval(g)}")
                    g.sort()
                    print(f" {grid[row][col]}={m.eval(grid[row][col])}={m.eval(g)}")
                    pass
            print("\n\n\n\n")
            # print board
            max_clues = 8
            clue_width = 3
            indent = max_clues * clue_width + 2

    # Puzzle definition; what makes the mushroom puzzle is its codes and colors
    raw_row_clues = "3R;5R;5R;1B;5G"
    raw_col_clues = "2R,1G;3R,1G;3R,1B,1G;3R,1G;2R,1G"
    color_codes = ".RGB"


    row_clues = [[(int(code[:-1]), color_codes.find(code[-1]))
                   for code in block.split(',')]
                  for block in raw_row_clues.split(';')]
    col_clues = [[(int(code[:-1]), color_codes.find(code[-1]))
                   for code in block.split(',')]
                  for block in raw_col_clues.split(';')]
    num_rows, num_cols, num_colors = len(row_clues), len(col_clues), len(color_codes)

    solver = Solver()

    # z3 has some interesting theories about arrays, which is not useful for this
    # project.  At least, I could not get useful information from the documentation.
    #
    # I happened across the IntVector sort, which turns out to be a simple Python routine
    # for naming independent Const variables.  It does not allow me to use a list subscript
    # that is an expression, e.g., "my_list[my_z3_const_intSort]".  So that didn't work.
    #
    # If I invert the puzzle a bit, each non-blank cell is both in a horizontal block of cells
    # defined by a row clue's position and a vertical block defined by a row clue's position.
    # The only set of starting indexes of these blocks that work is the final solution.
    #
    # Fun fact, every z3 Const must have a unique name and type combination.  Reusing the same name returns
    # the previous Const.   That is, two calls to "Const('a_const', IntSort())" return the same reference.
    #
    # Current Data Structures
    # * row_clues and col_clues are tuples of the number of blocks followed by the color index for each clue.
    #   clues are stored as an list of lists.  For example, if raw_col_clues starts with "2R,1G;" then col_clues[0]
    #   (clues for the first column) will be [(2 {blocks}, 1 {color index of R}, (1,2)].  These are not z3 consts.
    #
    # * starts is a list of the starting indexes (IntSort) of each clue's block of colored cells,
    #   for one   They are named "clue_{row|col}_{#}_clue_{#}", e.g., "clue_col_0_clue_0" or
    #   "clue_col_1_clue_1".  The Python variable starts is a list reused for each line.
    #
    # * grid[rows][cols] is a matrix of squares, each an IntSort() resolving having the color code of the square.
    #   The color code 0 means blank, and the codes are the index into color_codes.
    #   Each square is named as "grid_row_{#}_col_{#}".
    #


    grid = [ [ Const(f"grid_row_{row}_col_{col}", IntSort())
               for col in range(num_cols)]
             for row in range(num_rows)]

    print("1", solver.check())

    # Now add constraints for the row and column clues.
    # This is annoyingly, almost, but not quite parameterized between rows and columns
    # row_params = ("line", num_lines, line_clues)
    # col_params= ("col", num_cols, col_clues)
    # for params in (row_params, col_params):
    #     line_row, range_var, clues = params

    # Row clues.
    for row in range(num_rows):
        prefix = "row"
        clues = row_clues[row]

        # for each line of clues (each row), get starts, the starting index Consts.
        starts = [Const(f"{prefix}_{row}_code_{code_num}", IntSort())
                  for code_num in range(len(clues))]
        print(f"2 {row=}", solver.check())

        last_start, last_end, last_color = None, 0, 0
        for code_num, (length, color) in enumerate(clues):
            start = starts[code_num]
            end = start + length - 1
            # block must fit within grid
            solver.add(start >= 0, end  < num_cols)
            print(f"3 {row=} {code_num=}", solver.check())

            # block must start after last block, or with one spacer if same color
            if last_start is not None:
                if color != last_color:
                    solver.add(start > last_end)
                else:
                    solver.add(start > last_end + 1)  # add at least one blank square between
            last_start, last_end, last_color = start, end, color
        print(f"4 {row=}", solver.check())

        # Now add color requirement to each grid cell
        # which is "blank if in no block, or the color of the block the cell is in"
        for col in range(num_cols):
            g = grid[row][col]
            in_block = []
            in_block_with_color = []
            for code_num, (length, color) in enumerate(clues):
                start = starts[code_num]  # start is a IntSort
                end = start + length - 1  # end is an ArithRef
                in_block.append(And([start >= col, col <= end]))
                in_block_with_color.append(And([g == color, start >= col, end <= col]))
            in_any_block = Or(in_block)
            is_blank = g == 0  # square is color 0, meaning blank or '.'
            solver.add(Xor(is_blank, in_any_block))  # g is blank iff it is not in a block
            print(show(f"5 {row=} {col=}"))

            # solver.add(Or(is_blank, Or(in_block_with_color)))  # if not blank, be color of block
            print(f"6 {row=} {col=}", solver.check())




if __name__ == "__main__":
    mushroom_puzzle()
    print("This program is gratified to be of use.")
