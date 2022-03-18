"""
COMP30024 Artificial Intelligence, Semester 1, 2022
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json

from sympy import true

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from util import *
def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)
    
    print(apply_ansi("Hi Selena in RED", True, "r"))
    print(apply_ansi("Hi Selena in BLUE", True, "b"))
    
    board_n, start_board, start_cell, goal_cell = process_input(data)
    print_board(n=board_n,board_dict=start_board,message= apply_ansi(str(start_board), True, "b"),ansi=True)
    
    # TODO:
    # Find and print a solution to the board configuration described
    # by `data`.
    # Why not start by trying to print this configuration out using the
    # `print_board` helper function? (See the `util.py` source code for
    # usage information).
