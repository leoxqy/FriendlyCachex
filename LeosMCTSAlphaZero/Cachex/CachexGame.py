from __future__ import print_function
from itertools import islice
import numpy as np
from .CachexLogic import *
from Game import Game

class CachexGame(Game):
    content_lookup = {-1: "B", 0: "-", 1:"R"}
    
    @staticmethod
    def getPieceContent(piece):
        return CachexGame.content_lookup[piece]

    def __init__(self, n):
        self.n = n
        
    def getInitBoard(self):
        # return the board at init
        board = Board(self.n)
        return np.array(board._data)

    def getBoardSize(self):
        # return initial board
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n*self.n + 1

    def getNextState(self, board, player, action):
        # action must be a valid move
        move = (int(action/self.n), action%self.n)
        board.execute_move(move, player)
        # switch player
        return (board._data, -player) 
    
    
    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        b = Board(self.n)
        b._data = np.copy(board)
        legalMoves =  b.get_legal_moves(player)
        for r, q in legalMoves:
            valids[self.n*r+q]=1
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost, small non-zero val for draw
        # player = 1
        return board.check_win_move(player)

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player*board

    def getSymmetries(self, board, pi):
        return [(board,pi)]

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []
        # rot 180 deg and itsef
        for i in [2,4]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)

                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    
    def stringRepresentation(self, board):
        return board.tostring()

    def stringRepresentationReadable(self, board):
        board_s = "".join(self.content_lookup[cell] for r in board for cell in r)
        return board_s

    def getScore(self, board, player):
        # for greedy algorithm, defined the round number of a player win 
        b = Board(self.n)
        b._data = np.copy(board)
        return 

    
    

    # # #
    # Game display
    #
    def apply_ansi(str, bold=True, color=None):
        """
        Wraps a string with ANSI control codes to enable basic terminal-based
        formatting on that string. Note: Not all terminals will be compatible!
        Don't worry if you don't know what this means - this is completely
        optional to use, and not required to complete the project!

        Arguments:

        str -- String to apply ANSI control codes to
        bold -- True if you want the text to be rendered bold
        color -- Colour of the text. Currently only red/"r" and blue/"b" are
            supported, but this can easily be extended if desired...

        """
        bold_code = "\033[1m" if bold else ""
        color_code = ""
        if color == "r":
            color_code = "\033[31m"
        if color == "b":
            color_code = "\033[34m"
        return f"{bold_code}{color_code}{str}\033[0m"




    # Original
    def print_board(n, board_dict, message="", ansi=False, **kwargs):
        """
        For help with visualisation and debugging: output a board diagram with
        any information you like (tokens, heuristic values, distances, etc.).

        Arguments:

        n -- The size of the board
        board_dict -- A dictionary with (r, q) tuples as keys (following axial
            coordinate system from specification) and printable objects (e.g.
            strings, numbers) as values.
            This function will arrange these printable values on a hex grid
            and output the result.
            Note: At most the first 5 characters will be printed from the string
            representation of each value.
        message -- A printable object (e.g. string, number) that will be placed
            above the board in the visualisation. Default is "" (no message).
        ansi -- True if you want to use ANSI control codes to enrich the output.
            Compatible with terminals supporting ANSI control codes. Default
            False.
        
        Any other keyword arguments are passed through to the print function.

        Example:

            >>> board_dict = {
            ...     (0, 4): "hello",
            ...     (1, 1): "r",
            ...     (1, 2): "b",
            ...     (3, 2): "$",
            ...     (2, 3): "***",
            ... }
            >>> print_board(5, board_dict, "message goes here", ansi=False)
            # message goes here
            #              .-'-._.-'-._.-'-._.-'-._.-'-.
            #             |     |     |     |     |     |
            #           .-'-._.-'-._.-'-._.-'-._.-'-._.-'
            #          |     |     |  $  |     |     |
            #        .-'-._.-'-._.-'-._.-'-._.-'-._.-'
            #       |     |     |     | *** |     |
            #     .-'-._.-'-._.-'-._.-'-._.-'-._.-'
            #    |     |  r  |  b  |     |     |
            #  .-'-._.-'-._.-'-._.-'-._.-'-._.-'
            # |     |     |     |     |hello| 
            # '-._.-'-._.-'-._.-'-._.-'-._.-'
            
        """

        stitch_pattern = ".-'-._"
        edge_col_len = 3
        v_divider = "|"
        h_spacing = len(stitch_pattern)
        output = message + "\n"

        # Helper function to only selectively apply ansi formatting if enabled
        apply_ansi_s = apply_ansi if ansi else lambda str, **_: str

        # Generator to repeat pattern string (char by char) infinitely
        def repeat(pattern):
            while True:
                for c in pattern:
                    yield c

        # Generate stitching pattern given some offset and length
        def stitching(offset, length):
            return "".join(islice(repeat(stitch_pattern), offset, length))

        # Loop through each row i from top (print ordering)
        # Note that n - i - 1 is equivalent to r in axial coordinates
        for i in range(n):
            x_padding = (n - i - 1) * int(h_spacing / 2)
            stitch_length = (n * h_spacing) - 1 + \
                (int(h_spacing / 2) + 1 if i > 0 else 0)
            mid_stitching = stitching(0, stitch_length)

            # Handle coloured borders for ansi outputs
            # Fairly ugly code, but there is no "simple" solution
            if i == 0:
                mid_stitching = apply_ansi_s(mid_stitching, color="r")
            else:
                mid_stitching = \
                    apply_ansi_s(mid_stitching[:edge_col_len], color="b") + \
                    mid_stitching[edge_col_len:-edge_col_len] + \
                    apply_ansi_s(mid_stitching[-edge_col_len:], color="b")

            output += " " * (x_padding + 1) + mid_stitching + "\n"
            output += " " * x_padding + apply_ansi_s(v_divider, color="b")

            # Loop through each column j from left to right
            # Note that j is equivalent to q in axial coordinates
            for j in range(n):
                coord = (n - i - 1, j)
                value = str(board_dict.get(coord, ""))
                # Leo added this if on 1st April 2022
                c = None
                if (len(value)> 1):
                    c = value[0]
                    value = value[1:]
                
                contents = value.center(h_spacing - 1)
                if ansi:
                    # Leo modified on 1st April 2022
                    # contents = apply_ansi_s(contents, color=value)
                    contents = apply_ansi_s(contents, color=(c if c else None))
                output += contents + (v_divider if j < n - 1 else "")
            output += apply_ansi_s(v_divider, color="b")
            output += "\n"
        
        # Final/lower stitching (note use of offset here)
        stitch_length = (n * h_spacing) + int(h_spacing / 2)
        lower_stitching = stitching(int(h_spacing / 2) - 1, stitch_length)
        output += apply_ansi_s(lower_stitching, color="r") + "\n"

        # Print to terminal (with optional args forwarded)
        print(output, **kwargs)


    def display(board:Board):
        board_dict = dict()
        for r in range(board.n):
            for q in range(board.n ):
                coord = (r,q)
                if board[coord] == -1:
                    board_dict.update({coord:"bB"})
                elif board[coord] == 1:
                    board_dict.update({coord:"rR"})
        print_board(board.n, board_dict, "", True)