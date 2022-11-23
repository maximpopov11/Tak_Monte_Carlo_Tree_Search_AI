from collections import deque, namedtuple
from copy import deepcopy
from enum import Enum
import math as m

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


#Game parameters. Use these to change the size of the game.
#Note: values which are powers of 2 may cause unexpected behavior with encoding

NUM_CAPSTONES = 1   #per player
NUM_PIECES = 21     #per player
BOARD_SIZE = 5      

# Encoding info: format whitepieces,whitecapstone,blackpieces,blackcapstone
# Unplaced pieces or capstones encoded as [1]*PIECE_SIZE or [1]*CAPSTONE_SIZE

ROWBITS =  m.ceil(m.log(BOARD_SIZE,2))
COLBITS = ROWBITS
ZBITS = m.ceil(m.log(2*(NUM_CAPSTONES+NUM_PIECES),2))
PIECE_SIZE = ROWBITS+COLBITS+ZBITS + 1  #No. of bits used in binary encoding of a piece
CAPSTONE_SIZE = PIECE_SIZE - 1      #No. of bits used in binary encoding of a capstone
GAMESIZE = 2 * (PIECE_SIZE*NUM_PIECES + CAPSTONE_SIZE*NUM_CAPSTONES)      #No. of bits used in binary encoding of game board


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


class Direction(Enum):
    """Direction for stack movement."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class StackMove:
    """Tak stack movement move."""

    def __init__(self, piece, direction, stack_remainders):
        self.position = piece.position
        self.player = piece.color
        self.direction = direction
        self.stack_remainders = stack_remainders

#-----------------------------Utility functions-------------------------------#

def blank_board():
    board = []
    for i in range(5):
        board.append([])
        for j in range(5):
            board[i].append(deque())
    return board

def player_still_has_pieces(board, player):
    """Returns a list of bools of length 2, first
    index corresponds to whether or not a player still has
    wall/tile pieces left to place, second index to whether they
    still have capstones for the given state_int"""
    
    state_int = encode_state(board)
    binary = int_to_bits(state_int, GAMESIZE)
    
    if player == PieceColor.WHITE:
        last_piece = binary[len(binary)/2 - NUM_CAPSTONES * CAPSTONE_SIZE - PIECE_SIZE: len(binary)/2 - NUM_CAPSTONES * CAPSTONE_SIZE]
        last_cap = binary[len(binary)/2 - CAPSTONE_SIZE: len(binary)/2]
        return [last_piece == [1] * PIECE_SIZE, last_cap == [1] * CAPSTONE_SIZE]
    else:
        last_piece = binary[len(binary) - NUM_CAPSTONES * CAPSTONE_SIZE - PIECE_SIZE: len(binary) - NUM_CAPSTONES * CAPSTONE_SIZE]    
        last_cap = binary[len(binary) - CAPSTONE_SIZE: len(binary)]
        return [last_piece == [1] * PIECE_SIZE, last_cap == [1] * CAPSTONE_SIZE]


#------------------------------------Moves------------------------------------#

def result(board, move):
    """Adjudicates the result of the game after the move being made."""
    moves = get_moves(board, move.player)
    if move not in moves:
        raise ValueError('Given move is not in state.moves.')
    board_c = deepcopy(board)
    if isinstance(move, PlacementMove):
        board_c[move.position[0]][move.position[1]].append(move.piece)
    elif isinstance(move, StackMove):
        initial_x = move.position[0]
        initial_y = move.position[1]
        initial_space = board_c[initial_y][initial_x]
        target_y = initial_y + (len(move.stack_remainders) - 1) * move.direction[0]
        target_x = initial_x + (len(move.stack_remainders) - 1) * move.direction[1]
        target_space = board_c[target_y][target_x]
        for i in range(len(move.stack_remainders) - 1, 0):
            l = deque()
            for j in range(move.stack_remainders[i]):
                l.appendleft(initial_space.pop())
            target_space.extend(l)
            target_y -= move.direction[0]
            target_x -= move.direction[1]
            target_space = board_c[target_y][target_x]
    else:
        raise ValueError('Given move has a nonexistent type.')
    return board_c
    

def get_moves(board, color):
    """Returns legal moves."""
    moves = []
    pieces_left = player_still_has_pieces(board, color)
    for y in range(0, BOARD_SIZE):
        for x in range(0, BOARD_SIZE):
            stack = board[y][x]
            # placement moves
            if len(stack) == 0:
                if pieces_left[0]:
                    moves.append(PlacementMove((x, y, 0), Piece(color, PieceType.TILE, (x, y, 0))))
                    moves.append(PlacementMove((x, y, 0), Piece(color, PieceType.WALL, (x, y, 0))))
                if pieces_left[1]:
                    moves.append(PlacementMove((x, y, 0), Piece(color, PieceType.CAPSTONE, (x, y, 0))))
            # stack moves
            elif stack[-1].color == color:
                get_stack_moves_in_direction(moves, board, (x, y), Direction.UP)
                get_stack_moves_in_direction(moves, board, (x, y), Direction.DOWN)
                get_stack_moves_in_direction(moves, board, (x, y), Direction.LEFT)
                get_stack_moves_in_direction(moves, board, (x, y), Direction.RIGHT)
    return moves


def get_stack_moves_in_direction(moves, board, position, direction):
    stack = board[position[1]][position[0]]
    max_moving = min(len(stack), BOARD_SIZE)
    for num_moving in range(1, max_moving):
        end_x = position[0] + direction[0]
        end_y = position[1] + direction[1]
        if end_x < 0 or end_x >= BOARD_SIZE or end_y < 0 or end_y >= BOARD_SIZE:
            break
        for space_range in range(1, num_moving):
            # for each combination of extra piece allocations create a new move
            stack_remainders = []
            unassigned = num_moving
            for i in range(space_range):
                stack_remainders.append(1)
                unassigned -= 1
            # TODO: iterate through all combinations of extra piece allocations into array and add a move for each
            moves.append(StackMove(stack[0], direction, stack_remainders))


#-----------------------------Terminal Test Code------------------------------#
def terminal_test(board,last_to_move):
    """Given a board and the last player to move, returns
    a tuple (terminal, winner), with terminal = True or False
    depending on if the board represents a terminal state, and
    winner = PieceColor of last_to_move (default) or the winning player."""
    all_pieces_placed = not(sum(player_still_has_pieces(board, PieceColor.BLACK))) or not(sum(player_still_has_pieces(board,PieceColor.BLACK)))
    players_with_roads = set()
    fewest_pieces = 1
    # Checks for roads and board coverage
    for j, row in enumerate(board):
        for i, space in enumerate(row):
            fewest_pieces = min(len(space), fewest_pieces)  # Tracks board coverage for flat win condition
            # Road checking begins below
            if i == 0 or j == 0:  # We are on the top or left edges of the board
                if len(space) > 0:  # There's at least 1 piece in the current location
                    if space[-1].type != PieceType.WALL:  # Piece at top of stack can be part of road
                        if find_roads(board,space[-1]):
                            players_with_roads.add(space[-1].color)
    if len(players_with_roads):
        # player who made the winning move gets the win, regardless of whether not enemy also had a road
        if players_with_roads.intersection(last_to_move):
            print(f"Winner: {last_to_move}")
            return(True, last_to_move)
        else:
            winner = players_with_roads.pop()
            print(f"Winner: {winner}")
            return(True, winner)

    # Score tallies after flat win condition detected
    if fewest_pieces == 1 or all_pieces_placed:
        print("Either the board is covered or a player is out of pieces! Tallying scores...")
        white = 0
        black = 0
        for row in board:
            for space in row:
                if space[-1].type == PieceType.TILE:
                    if space[-1].color == PieceColor.WHITE:
                        white += 1
                    else:
                        black += 1
        print(f"White: {white} | Black: {black}")
        winner = PieceColor.WHITE if white > black else PieceColor.BLACK
        print(f"Winner: {winner}")
        return (True, winner)
    return False

def find_roads(board,piece):
    """Starting point of a recursive DFS looking for roads across the 2D board array.
    Returns true if a road is found originating from the given piece."""
    row = piece.position[0]
    col = piece.position[1]
    left = col - 1
    right = left + 2
    up = row - 1
    down = up + 2
    if row == 0 and col == 0:  # Top left corner, D & R
        return find_roads_rec(board,down, col, piece.color, True, True, {(row, col)}) or \
               find_roads_rec(board,row, right, piece.color, True, True, {(row, col)})
    elif row == 0 and col == BOARD_SIZE - 1:  # Top right corner, D & L
        return find_roads_rec(board,down, col, piece.color, True, False, {(row, col)}) or \
               find_roads_rec(board,row, left, piece.color, True, False, {(row, col)})
    elif row == BOARD_SIZE - 1 and col == 0:  # Bottom left corner, U & R
        return find_roads_rec(board,up, col, piece.color, False, True, {(row, col)}) or \
               find_roads_rec(board,row, right, piece.color, False, True, {(row, col)})
    elif row == 0:  # Top row, LRD
        return find_roads_rec(board,down, col, piece.color, True, False, {(row, col)}) or \
               find_roads_rec(board,row, left, piece.color, True, False, {(row, col)}) or \
               find_roads_rec(board,row, right, piece.color, True, False, {(row, col)})
    elif col == 0:  # Left col, UDR
        return find_roads_rec(board,row, right, piece.color, False, True, {(row, col)}) or \
               find_roads_rec(board,down, col, piece.color, False, True, {(row, col)}) or \
               find_roads_rec(board,up, col, piece.color, False, True, {(row, col)})


def find_roads_rec(board,i, j, color, row_start, col_start, seen):
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
    if row == BOARD_SIZE - 1 and row_start:  # Piece, belongs to same player, and on opposite edge of start
        return True
    elif col == BOARD_SIZE - 1 and col_start:  # same as above
        return True
    seen.add((piece.position[0], piece.position[1]))  # Seen set passed down to avoid visiting ancestors
    for rowDir in row_dirs:
        if rowDir in range(BOARD_SIZE) and (rowDir, col) not in seen:
            return find_roads_rec(rowDir, col, piece.color, row_start, col_start, seen)
    for colDir in col_dirs:
        if colDir in range(BOARD_SIZE) and (row, colDir) not in seen:
            return find_roads_rec(row, colDir, piece.color, row_start, col_start, seen)

#----------------------State Encoding/Decoding Functions----------------------#
def encode_state(board):
    """Given board of format: [[deque(bottom_piece,...,top_piece)*BOARD_LENGTH]*BOARD_LENGTH]
    returns a large distinct integer derived from binary encoding of distinct board state"""
    white = []
    black = []
    white_end = None
    black_end = None
    #iterate through pieces on board
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
    while len(white) + len(black) < GAMESIZE-2*CAPSTONE_SIZE*NUM_CAPSTONES:
        if len(white) < GAMESIZE/2 - CAPSTONE_SIZE*NUM_CAPSTONES:
            white.append(1)
        if len(black) < GAMESIZE/2 - CAPSTONE_SIZE*NUM_CAPSTONES:
            black.append(1)
    if not white_end:
        white_end = [1]*CAPSTONE_SIZE
    if not black_end:
        black_end = [1]*CAPSTONE_SIZE
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
    res.extend(int_to_bits(piece.position[1],3))
    res.extend(int_to_bits(piece.position[2],6))
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
        if i in range(GAMESIZE / 2 - NUM_CAPSTONES * CAPSTONE_SIZE,GAMESIZE/2) or i in range(GAMESIZE - NUM_CAPSTONES*CAPSTONE_SIZE,GAMESIZE):
            piece = game_binary[i:i+CAPSTONE_SIZE]
            capstone = True
            i -= 1
        else:
            piece = game_binary[i:i+PIECE_SIZE]
            capstone = False
        i+=PIECE_SIZE
        if piece == [1] * PIECE_SIZE or piece == [1] * CAPSTONE_SIZE:
            continue
        row = bits_to_int(piece[0:ROWBITS])
        col = bits_to_int(piece[ROWBITS:ROWBITS+COLBITS])
        dqidx = bits_to_int(piece[ROWBITS+COLBITS:ROWBITS+COLBITS+ZBITS])
        if capstone:
            type = PieceType.CAPSTONE
        elif piece[-1]:
            type = PieceType.TILE
        else:
            type = PieceType.WALL
        piece = Piece(PieceColor.WHITE if i < GAMESIZE/2  else PieceColor.BLACK,type, (row,col,dqidx))
        while len(board[row][col]) < dqidx+1:
            board[row][col].append(None)
        board[row][col][dqidx] = piece

    return board

