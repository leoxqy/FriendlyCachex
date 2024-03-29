from itertools import islice
import logging
import time
from cachetools import Cache
from Cachex.CachexLogic import Board
from MCTS import MCTS
from Cachex.CachexGame import CachexGame
from Cachex.CachexPlayers import *
from Cachex.pytorch.NNet import NNetWrapper as NNet

from tqdm import tqdm

from utils import dotdict

log = logging.getLogger(__name__)


class ArenavP():
    """
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, game, display=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in cachex/CachexGame). Is necessary for verbose
                     mode.

        see cachex/CachexPlayers.py for an example. See pit.py for pitting
        human players/other baselines with each other.
        """
        self.player1 = player1
        self.game = game
        self.display = display

    def playGame(self, verbose=False):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
        players = ["AI","NONE","HUMAN"]
        aiPlayer = self.player1
        curPlayer = 1
        board = self.game.getInitBoard()
        it = 0
        display(board._data, board.n)
        while self.game.getGameEnded(board, curPlayer) == 0:
            it += 1
            if verbose:
                # assert display(board._data, board.n)
                print("Turn ", str(it), "Player ", str(curPlayer))
                # display(board._data, board.n)
            
            if players[curPlayer+1] == "HUMAN" :
                action = tuple([int(c) for c in input("Please enter your move, format as 'rq'. (e.g., 04 means place a token at pos row = 0, col = 4)  \ncq: ")])
                action = board.n*action[0]+action[1]

            else:
                action = aiPlayer(self.game.getCanonicalForm(board, curPlayer))
                print("The friendly AI's Action: ", (int(action/board.n), action % board.n))
                # display_true(board._data, board.n,False)
            valids = self.game.getValidMoves(self.game.getCanonicalForm(board, curPlayer), 1)
            if valids[action] == 0:
                log.error(f'Action {action} is not valid!')
                log.debug(f'valids = {valids}')
                assert valids[action] > 0
            board, curPlayer = self.game.getNextState(board, curPlayer, action)
            display(board._data, board.n, (it % 2 == 0))
            board.swap_pos()
        if verbose:
            if self.game.getGameEnded(board, curPlayer) == 1:
                print("You win!")
            else:
                print("The Friendly AI winned!")

        return self.game.getGameEnded(board, curPlayer)

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """

        num = int(num / 2)
        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in tqdm(range(num), desc="Arena.playGames (1)"):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == 1:
                oneWon += 1
            elif gameResult == -1:
                twoWon += 1
            else:
                draws += 1

        self.player1, self.player2 = self.player2, self.player1

        for _ in tqdm(range(num), desc="Arena.playGames (2)"):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == -1:
                oneWon += 1
            elif gameResult == 1:
                twoWon += 1
            else:
                draws += 1

        return oneWon, twoWon, draws


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
                apply_ansi_s(
                    mid_stitching[-edge_col_len:], color="b")

        output += " " * (x_padding + 1) + mid_stitching + "\n"
        output += " " * x_padding + \
            apply_ansi_s(v_divider, color="b")

        # Loop through each column j from left to right
        # Note that j is equivalent to q in axial coordinates
        for j in range(n):
            coord = (n - i - 1, j)
            value = str(board_dict.get(coord, ""))
            # Leo added this if on 1st April 2022
            c = None
            if (len(value) > 1):
                c = value[0]
                value = value[1:]

            contents = value.center(h_spacing - 1)
            if ansi:
                # Leo modified on 1st April 2022
                # contents = apply_ansi_s(contents, color=value)
                contents = apply_ansi_s(
                    contents, color=(c if c else None))
            output += contents + (v_divider if j < n - 1 else "")
        output += apply_ansi_s(v_divider, color="b")
        output += "\n"

    # Final/lower stitching (note use of offset here)
    stitch_length = (n * h_spacing) + int(h_spacing / 2)
    lower_stitching = stitching(int(h_spacing / 2) - 1, stitch_length)
    output += apply_ansi_s(lower_stitching, color="r") + "\n"

    # Print to terminal (with optional args forwarded)
    print(output, **kwargs)


def display(canonicalBoard, n, swap = False):
    b = Board(n)
    b._data = np.copy(canonicalBoard)
    if swap:
        b._data = b._data.transpose()
    
    board_dict = dict()
    for r in range(n):
        for q in range(n):
            coord = (r, q)
            if b._data[coord] == -1:
                board_dict.update({coord: "bB"})
            elif b._data[coord] == 1:
                board_dict.update({coord: "rR"})
    print_board(n, board_dict, "", True)

N = 5
g = CachexGame(N)
n1 = NNet(g)
n1.load_checkpoint(folder="H:\COMP30024\\repo\FriendlyCachex\LeosMCTSAlphaZero\\temp5\\", filename='best.pth.tar')
args1 = dotdict({'numMCTSSims': 1000, 'cpuct':1.0})
mcts1 = MCTS(g, n1, args1)
n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

t0 = time.time()
arena = ArenavP(n1p,g,display=CachexGame.display)
duration = time.time()-t0
print("Total time used: ", duration)

print(arena.playGame(True))