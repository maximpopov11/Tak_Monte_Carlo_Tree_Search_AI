from collections import deque, namedtuple
from copy import deepcopy
from enum import Enum
import math as m
from typing import Union

"""
Collection of functions to perform various tasks reflective of the game Tak
Game board represented in 2 formats:

    Binary encoding:    whitepieces,whitecap,blackpieces,blackcap
                        See more about the encoding scheme further below.

    Game Board:         [[deque(BottomPiece,...,TopPiece)*BOARD_SIZE]*BOARD_SIZE]

 Most functions operate on the game board format, and take a parameter `board`, expecting
 the above list->lists->deques formatting.

 Functions which expect the encoded format will take a parameter `state_int`
 of type int().
 """

# Game parameters. Use these to change the size of the game.
# Note: values which are powers of 2 may cause unexpected behavior with encoding

NUM_CAPSTONES = 1  # per player
NUM_PIECES = 21  # per player
BOARD_SIZE = 5

# Encoding info: format whitepieces,whitecapstone,blackpieces,blackcapstone
# Unplaced pieces or capstones encoded as [1]*PIECE_SIZE or [1]*CAPSTONE_SIZE

ROWBITS = m.ceil(m.log(BOARD_SIZE, 2))
COLBITS = ROWBITS
ZBITS = m.ceil(m.log(2 * (NUM_CAPSTONES + NUM_PIECES), 2))
PIECE_SIZE = ROWBITS + COLBITS + ZBITS + 1  # No. of bits used in binary encoding of a piece
CAPSTONE_SIZE = PIECE_SIZE - 1  # No. of bits used in binary encoding of a capstone
GAMESIZE = 2 * (
        PIECE_SIZE * NUM_PIECES + CAPSTONE_SIZE * NUM_CAPSTONES)  # No. of bits used in binary encoding of game board

GameState = namedtuple('GameState', 'to_move, moves, board')


class PieceColor(Enum):
    """Enum enables easy access to standardized piece colors."""
    BLACK, WHITE = range(2)

    def __str__(self):
        return "White" if self == PieceColor.WHITE else "Black"


class PieceType(Enum):
    """Enum enables easy access to standardized piece types."""
    WALL, TILE, CAPSTONE = range(3)

    def __str__(self):
        if self == PieceType.WALL:
            return "Wall"
        elif self == PieceType.CAPSTONE:
            return "Capstone"
        else:
            return "Tile"


class Piece:
    """Tak game piece represents color, type, and XYZ position of piece."""

    def __init__(self, color, type, position):
        self.color = color
        self.type = type
        self.position = [position[0], position[1], position[2]]  # row, col, dequeIndex

    def __repr__(self):
        rep = "B" if self.color == PieceColor.BLACK else "W"
        if self.type == PieceType.WALL:
            rep += "W"
        elif self.type == PieceType.TILE:
            rep += "T"
        else:
            rep += "C"
        return rep


class PlacementMove:
    """Tak piece placement move."""

    def __init__(self, position, piece):
        self.position = position
        self.piece = piece
        self.player = piece.color

    def __repr__(self):
        return f"{self.piece} {self.position}"


class Direction(Enum):
    """Direction for stack movement."""
    # value: tuple[int,int]
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class StackMove:
    """Tak stack movement move."""

    def __init__(self, piece, direction, stack_remainders):
        self.piece = piece
        self.position = piece.position
        self.player = piece.color
        self.direction = direction
        self.stack_remainders = stack_remainders

    def __repr__(self):
        return f"Stack at {self.position}, {self.direction}, Order: {self.stack_remainders}"


class TakGame:
    """The actual instance of the game that is played/matters"""

    def __init__(self, board):
        self.board = board


# -----------------------------Utility functions-------------------------------#

def top_board_string(board):
    res = '   0    1    2    3    4\n0|'
    for i in range(len(board)):
        for j in range(len(board)):
            if len(board[i][j]):
                res += f" {board[i][j][-1]} |"
            else:
                res += "    |"
        res += f"\n{i + 1}|"
    return res[:-2]


def stacks_string(board):
    res = ''
    for i in range(len(board)):
        for j in range(len(board)):
            if len(board[i][j]):
                res += (f"[{i},{j}]: {board[i][j]}\n")
    return res


def blank_board():
    board = []
    for i in range(BOARD_SIZE):
        board.append([])
        for j in range(BOARD_SIZE):
            board[i].append(deque())
    return board


def player_still_has_pieces(board, player):
    """Returns a list of bools of length 2, first
    index corresponds to whether or not a player still has
    wall/tile pieces left to place, second index to whether they
    still have capstones for the given state_int"""
    capstones = NUM_CAPSTONES
    pieces = NUM_PIECES
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if len(board[i][j]):
                for piece in board[i][j]:
                    if piece.color == player:
                        if piece.type == PieceType.CAPSTONE:
                            capstones -= 1
                        else:
                            pieces -= 1
    return [pieces > 0, capstones > 0]


# ------------------------------------Moves------------------------------------#
def play_game(board, white_agent, black_agent, testing=False):
    """Plays the game by querying the given agents for moves and updating the board respectively"""
    # first move works differently
    if not testing:
        move = white_agent.query(board, True)
        board = result(board, move)
        move = black_agent.query(board, True)
        board = result(board, move)
    agent = white_agent
    while True:
        move = agent.query(board)
        board = result(board, move)
        terminal = terminal_test(board, agent.color)
        if terminal[0]:
            print('The winner is', terminal[1], '!!!')
            break
        agent = white_agent if agent == black_agent else black_agent


def make_move(game, move):
    """Updates a game instance to reflect a real change in game,
    i.e. a non-simulation move."""
    game.board = result(game.board, move)


def result(board, move):
    """Adjudicates the result of the game after the move being made."""
    # moves = get_moves(board, move.player)
    # # TODO: Issue with below conditional, not recognizing move in moves (1st move, wc (4,4,0) in moves[74], conditional returns false)
    # # if move not in moves:
    # #     raise ValueError('Given move is not in state.moves.')
    board_c = deepcopy(board)
    if isinstance(move, PlacementMove):
        board_c[move.position[0]][move.position[1]].append(move.piece)
    elif isinstance(move, StackMove):
        initial_x = move.position[1]
        initial_y = move.position[0]
        initial_space = board_c[initial_y][initial_x]
        target_y = initial_y + (len(move.stack_remainders)) * move.direction.value[0]
        target_x = initial_x + (len(move.stack_remainders)) * move.direction.value[1]
        target_space = board_c[target_y][target_x]
        for i in range(len(move.stack_remainders) - 1, -1, -1):
            l = deque()
            for j in range(move.stack_remainders[i]):
                piece = initial_space.pop()
                piece.position[0] = target_y
                piece.position[1] = target_x
                piece.position[2] = len(target_space)
                piece.position[2] += move.stack_remainders[i] - j - 1
                l.appendleft(piece)
            if len(l) == 1 and l[0].type == PieceType.CAPSTONE:
                if len(target_space):
                    if target_space[-1].type == PieceType.WALL:
                        target_space[-1].type = PieceType.TILE
            target_space.extend(l)
            target_y -= move.direction.value[0]
            target_x -= move.direction.value[1]
            target_space = board_c[target_y][target_x]
    else:
        raise ValueError('Given move has a nonexistent type.')
    return board_c


def get_moves_first_turn(board, color):
    """Returns legal first turn moves."""
    opposite_color = PieceColor.WHITE if color == PieceColor.BLACK else PieceColor.BLACK
    moves = []
    for row in range(0, BOARD_SIZE):
        for col in range(0, BOARD_SIZE):
            stack = board[row][col]
            if len(stack) == 0:
                moves.append(PlacementMove((row, col, 0), Piece(opposite_color, PieceType.TILE, (row, col, 0))))
    return moves


def get_moves(board, color):
    """Returns legal moves."""
    moves = []
    pieces_left = player_still_has_pieces(board, color)
    for row in range(0, BOARD_SIZE):
        for col in range(0, BOARD_SIZE):
            stack = board[row][col]
            # placement moves
            if len(stack) == 0:
                if pieces_left[0]:
                    moves.append(PlacementMove((row, col, 0), Piece(color, PieceType.TILE, (row, col, 0))))
                    moves.append(PlacementMove((row, col, 0), Piece(color, PieceType.WALL, (row, col, 0))))
                if pieces_left[1]:
                    moves.append(PlacementMove((row, col, 0), Piece(color, PieceType.CAPSTONE, (row, col, 0))))
            # stack moves
            elif stack[-1].color == color:
                get_stack_moves_in_direction(moves, board, (row, col), Direction.UP)
                get_stack_moves_in_direction(moves, board, (row, col), Direction.DOWN)
                get_stack_moves_in_direction(moves, board, (row, col), Direction.LEFT)
                get_stack_moves_in_direction(moves, board, (row, col), Direction.RIGHT)
    return moves


# MAINTAIN SUM - LEN ORDERING
STACK_REMAINDERS = [
    [1],
    [2],
    [1, 1],
    [3],
    [2, 1],
    [1, 2],
    [1, 1, 1],
    [4],
    [3, 1],
    [2, 2],
    [1, 3],
    [2, 1, 1],
    [1, 2, 1],
    [1, 1, 2],
    [1, 1, 1, 1],
    [5],
    [4, 1],
    [3, 2],
    [2, 3],
    [1, 4],
    [3, 1, 1],
    [1, 3, 1],
    [1, 1, 3],
    [2, 2, 1],
    [2, 1, 2],
    [1, 2, 2],
    [2, 1, 1, 1],
    [1, 2, 1, 1],
    [1, 1, 2, 1],
    [1, 1, 1, 2],
]


def get_stack_moves_in_direction(moves, board, position, direction):
    """Adds all possible stack moves in the given direction to moves"""
    max_distance = 0
    end_row = position[0]
    end_col = position[1]

    # Set ex and ey to last valid spot in that direction (edge of board, or as far as the stack can possibly go)
    while True:
        end_col += direction.value[1]
        end_row += direction.value[0]
        if end_row < 0 or end_row >= BOARD_SIZE or end_col < 0 or end_col >= BOARD_SIZE or max_distance >= len(
                board[position[0]][position[1]]):
            break
        else:
            max_distance += 1

    if max_distance == 0:
        return
    # If you can move that far (moving 4 away is 1,1,1,1, and perms(1,1,1,2) e.g. sum(stack_remainders) = 5 or (1,1,1,1) = 4)
    for stack_remainders in STACK_REMAINDERS:
        if len(stack_remainders) > max_distance:  # Trying to move further than possible
            continue
        if sum(stack_remainders) > len(board[position[0]][position[1]]):  # Trying to move more pieces than possible
            break  # sum-asc Order of STACK_REMAINDERS means we can break not continue here
        cFlag = 0
        # Trying to cover a wall or capstone?
        num_pieces_already_placed = 0
        size_of_stack = sum(stack_remainders)
        for i in range(len(stack_remainders)):  # Length of stack placement path is == len(stack_remainders)
            target_space = board[position[0] + (i + 1) * direction.value[0]][position[1] + (i + 1) * direction.value[1]]
            covering_piece = board[position[0]][position[1]][-1 * size_of_stack + num_pieces_already_placed]
            if len(target_space):
                if target_space[-1].type != PieceType.TILE:
                    if covering_piece.type != PieceType.CAPSTONE:
                        cFlag = 1
                        break
                    if target_space[-1].type == PieceType.CAPSTONE:
                        cFlag = 1
                        break
            num_pieces_already_placed += stack_remainders[i]
        if cFlag:
            continue
        moves.append(StackMove(board[position[0]][position[1]][-1], direction, stack_remainders))


# -----------------------------Terminal Test Code------------------------------#
def terminal_test(board, last_to_move):
    """Given a board and the last player to move, returns
    a tuple (terminal, winner), with terminal = True or False
    depending on if the board represents a terminal state, and
    winner = PieceColor of last_to_move (default) or the winning player."""
    white_pieces = NUM_PIECES + NUM_CAPSTONES
    black_pieces = NUM_PIECES + NUM_CAPSTONES
    white_flat_win_tally = 0
    black_flat_win_tally = 0
    players_with_roads = set()
    fewest_pieces = 1
    enemy_road_created = False
    # Checks for roads and board coverage
    for j, row in enumerate(board):
        for i, space in enumerate(row):
            fewest_pieces = min(len(space), fewest_pieces)  # Tracks board coverage for flat win condition
            # Road checking begins below
            if len(space) > 0:  # There's at least 1 piece in the current location
                if i == 0 or j == 0:  # We are on the top or left edges of the board
                    # Road Win
                    if space[-1].type != PieceType.WALL:  # Piece at top of stack can be part of road
                        if find_roads(board, space[-1]):
                            if space[-1].color == last_to_move:
                                return (True, last_to_move)  # If road belongs to road-making player
                            enemy_road_created = True  # Flag handles enemy road and no road-maker road.
                # Flat Win Scoring
                if space[-1].type == PieceType.TILE:
                    if space[-1].color == PieceColor.WHITE:
                        white_flat_win_tally += 1
                    else:
                        black_flat_win_tally += 1
                # Flat Win Condition Tracking
                for piece in space:
                    if piece.color == PieceColor.WHITE:
                        white_pieces -= 1
                    else:
                        black_pieces -= 1

    if enemy_road_created:
        winner = PieceColor.BLACK if last_to_move == PieceColor.WHITE else PieceColor.WHITE
        return (True, winner)

    # Score tallies after flat win condition detected
    if fewest_pieces == 1 or black_pieces == 0 or white_pieces == 0:
        winner = PieceColor.WHITE if white_flat_win_tally > black_flat_win_tally else PieceColor.BLACK
        # print("Flat win: ", winner,f"|White: {white_flat_win_tally}   Black: {black_flat_win_tally}")
        return (True, winner)
    return (False, None)


def find_roads(board, piece):
    """Starting point of a recursive DFS looking for roads across the 2D board array.
    Returns true if a road is found originating from the given piece."""
    row = piece.position[0]
    col = piece.position[1]
    left = col - 1
    right = left + 2
    up = row - 1
    down = up + 2
    if row == 0 and col == 0:  # Top left corner, D & R
        return find_roads_rec(board, down, col, piece.color, True, True, {(row, col)}) or \
               find_roads_rec(board, row, right, piece.color, True, True, {(row, col)})
    elif row == 0 and col == BOARD_SIZE - 1:  # Top right corner, D & L
        return find_roads_rec(board, down, col, piece.color, True, False, {(row, col)}) or \
               find_roads_rec(board, row, left, piece.color, True, False, {(row, col)})
    elif row == BOARD_SIZE - 1 and col == 0:  # Bottom left corner, U & R
        return find_roads_rec(board, up, col, piece.color, False, True, {(row, col)}) or \
               find_roads_rec(board, row, right, piece.color, False, True, {(row, col)})
    elif row == 0:  # Top row, LRD
        return find_roads_rec(board, down, col, piece.color, True, False, {(row, col)}) or \
               find_roads_rec(board, row, left, piece.color, True, False, {(row, col)}) or \
               find_roads_rec(board, row, right, piece.color, True, False, {(row, col)})
    elif col == 0:  # Left col, UDR
        return find_roads_rec(board, row, right, piece.color, False, True, {(row, col)}) or \
               find_roads_rec(board, down, col, piece.color, False, True, {(row, col)}) or \
               find_roads_rec(board, up, col, piece.color, False, True, {(row, col)})


def find_roads_rec(board, i, j, color, row_start, col_start, seen):
    """Recursive DFS across the 2D board array along orthogonal paths, 
    returns true if current node is at opposite end from starting node."""
    if len(board[i][j]):
        piece = board[i][j][-1]  # Top piece of stack at passed coords
    else:
        return False  # No piece at this location
    if piece.color != color or piece.type == PieceType.WALL:
        return False  # piece at this location belongs to opponent or is a non-road
    row = piece.position[0]
    col = piece.position[1]
    left = col - 1
    right = left + 2
    up = row - 1
    down = up + 2
    row_dirs = [up, down]
    col_dirs = [left, right]
    rowSearch = False
    colSearch = False
    if row == BOARD_SIZE - 1 and row_start:  # Piece, belongs to same player, and on opposite edge of start
        return True
    if col == BOARD_SIZE - 1 and col_start:  # same as above
        return True
    seen.add((piece.position[0], piece.position[1]))  # Seen set passed down to avoid visiting ancestors
    for rowDir in row_dirs:
        if rowDir in range(BOARD_SIZE) and (rowDir, col) not in seen:
            rowSearch = find_roads_rec(board, rowDir, col, piece.color, row_start, col_start, seen)
    for colDir in col_dirs:
        if colDir in range(BOARD_SIZE) and (row, colDir) not in seen:
            colSearch = find_roads_rec(board, row, colDir, piece.color, row_start, col_start, seen)
    return rowSearch or colSearch

#-----------------------------Heuristic Utilities------------------------------#
# h1 only cares about the pieces on the top level of their respective stacks
# this means we should be able to get clear changes in h1's value without
# full or even overly-extensive partial board re-evals between moves.
def h1(board:list[list[deque]])->int:
    score = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if len(board[i][j]):
                top_piece = board[i][j][-1]
                if top_piece.color == PieceColor.WHITE:
                    if top_piece.type == PieceType.WALL:
                        score += 1
                    else:
                        score += 2
                else:
                    if top_piece.type == PieceType.WALL:
                        score -= 1
                    else:
                        score -= 2
                # for k in range(-2,max(-6,-1*len(board[i][j])),-1):
                #     if board[i][j][k].color == color and board[i][j][k].type != PieceType.WALL:
                #         score += 5 / (-1*k)
    return score

def h1_delta(board:list[list[deque]], move: Union[PlacementMove, StackMove], base_score:int)->int:
    delta = 0
    color_factor = 1 if move.piece.color == PieceColor.WHITE else -1
    
    if isinstance(move,PlacementMove):
        delta += 1*color_factor if move.piece.type == PieceType.WALL else 2*color_factor
    else:
        size_of_stack = sum(move.stack_remainders)
        num_pieces_already_placed = 0
        init_space = board[move.position[0]][move.position[1]]
        for i in range(len(move.stack_remainders)):
            covered_space = board[move.position[0] + (i + 1) * move.direction.value[0]][move.position[1] + (i + 1) * move.direction.value[1]]
            new_top= board[move.position[0]][move.position[1]][-1 * size_of_stack + num_pieces_already_placed + move.stack_remainders[i] - 1]
            new_top_color_factor = 1 if new_top.color == PieceColor.WHITE else -1
            if len(covered_space):
                covered_piece = covered_space[-1]
                covered_piece_color_factor = -1 if covered_piece.color == PieceColor.WHITE else 1
                if covered_piece.type == PieceType.WALL:
                    delta += 1*covered_piece_color_factor 
                else:
                    delta += 2*covered_piece_color_factor
            
            if new_top.type == PieceType.WALL:
                delta += 1*new_top_color_factor
            else:
                delta += 2*new_top_color_factor

    return delta+base_score

# ----------------------State Encoding/Decoding Functions----------------------#
def encode_state(board):
    """Given board of format: [[deque(bottom_piece,...,top_piece)*BOARD_LENGTH]*BOARD_LENGTH]
    returns a large distinct integer derived from binary encoding of distinct board state"""
    white = []
    black = []
    white_end = None
    black_end = None
    # iterate through pieces on board
    for i in range(len(board)):
        for j in range(len(board)):
            for piece in board[i][j]:
                if piece.color == PieceColor.WHITE:
                    if piece.type != PieceType.CAPSTONE:
                        white.extend(piece_to_bits(piece))
                    else:
                        white_end = piece_to_bits(piece)
                else:
                    if piece.type != PieceType.CAPSTONE:
                        black.extend(piece_to_bits(piece))
                    else:
                        black_end = piece_to_bits(piece)
    while len(white) + len(black) < GAMESIZE - 2 * CAPSTONE_SIZE * NUM_CAPSTONES:
        if len(white) < GAMESIZE / 2 - CAPSTONE_SIZE * NUM_CAPSTONES:
            white.append(1)
        if len(black) < GAMESIZE / 2 - CAPSTONE_SIZE * NUM_CAPSTONES:
            black.append(1)
    if not white_end:
        white_end = [1] * CAPSTONE_SIZE
    if not black_end:
        black_end = [1] * CAPSTONE_SIZE
    white.extend(white_end)
    black.extend(black_end)
    white.extend(black)
    return bits_to_int(white)


def bits_to_int(bits):
    res = 0
    for b in bits:
        res *= 2
        res += b
    return res


def piece_to_bits(piece):
    res = []
    res.extend(int_to_bits(piece.position[0], 3))
    res.extend(int_to_bits(piece.position[1], 3))
    res.extend(int_to_bits(piece.position[2], 6))
    if piece.type == PieceType.WALL:
        res.append(0)
    elif piece.type == PieceType.TILE:
        res.append(1)
    return res


def int_to_bits(num, bits):
    res = []
    for _ in range(bits):
        res.append(num % 2)
        num //= 2
    return res[::-1]


def decode_state(num):
    """Given a large integer num, returns a board of format:
    [[deque(bottom_piece,...,top_piece)*BOARD_LENGTH]*BOARD_LENGTH]
    derived from binary encoding of the large integer
    """
    board = blank_board()
    game_binary = int_to_bits(num, GAMESIZE)
    i = 0
    capstone = False
    while i < GAMESIZE:
        if i in range(int(GAMESIZE / 2 - NUM_CAPSTONES * CAPSTONE_SIZE), int(GAMESIZE / 2)) or i in range(
                GAMESIZE - NUM_CAPSTONES * CAPSTONE_SIZE, GAMESIZE):
            piece = game_binary[i:i + CAPSTONE_SIZE]
            capstone = True
            i -= 1
        else:
            piece = game_binary[i:i + PIECE_SIZE]
            capstone = False
        i += PIECE_SIZE
        if piece == [1] * PIECE_SIZE or piece == [1] * CAPSTONE_SIZE:
            continue
        row = bits_to_int(piece[0:ROWBITS])
        col = bits_to_int(piece[ROWBITS:ROWBITS + COLBITS])
        dqidx = bits_to_int(piece[ROWBITS + COLBITS:ROWBITS + COLBITS + ZBITS])
        if capstone:
            p_type = PieceType.CAPSTONE
        elif piece[-1]:
            p_type = PieceType.TILE
        else:
            p_type = PieceType.WALL
        piece = Piece(PieceColor.WHITE if i <= GAMESIZE / 2 else PieceColor.BLACK, p_type, (row, col, dqidx))
        while len(board[row][col]) < dqidx + 1:
            board[row][col].append(None)
        board[row][col][dqidx] = piece

    return board
