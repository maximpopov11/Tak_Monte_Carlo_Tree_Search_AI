import sys
from Tak import *
from collections import deque
import math as m
from MCTS import *
import logging
logger = logging.getLogger(__name__)  

file_handler = logging.FileHandler('sample.log')
logger.addHandler(file_handler)




# #Tests Stack movement
# board[4][4].append(Piece(PieceColor.WHITE, PieceType.CAPSTONE,(4,4,0)))
# board[3][4].append(Piece(PieceColor.BLACK, PieceType.TILE, (3,4,0)))
# board[2][4].append(Piece(PieceColor.BLACK, PieceType.TILE, (2,4,0)))
# move1 = StackMove(board[4][4][-1],Direction.UP,[1])
# print(top_board_string(board))
# board = result(board, move1)
# print(top_board_string(board))
# print(move1)
# print(stacks_string(board))
# move2 = StackMove(board[3][4][-1],Direction.UP,[1,1])
# board = result(board,move2)
# print(top_board_string(board))
# print(move2)
# print(stacks_string(board))
# print(board[2][4])
# print(board[1][4][-1].position)


#Tests results of getting placement move in clear scenario.
# board = blank_board()
# for i in range(len(board)):
#     for j in range(len(board)):
#         board[i][j].append(Piece(PieceColor.WHITE, PieceType.TILE, (i,j,0)))
# board[1][2].clear()
# print(top_board_string(board))
# print(get_moves(board, PieceColor.BLACK))


#Tests getting stack moves in clear scenario
# board = blank_board()
# for i in range(len(board)):
#     for j in range(len(board)):
#         board[i][j].append(Piece(PieceColor.WHITE, PieceType.WALL, (i,j,0)))

# board[2][1].append(Piece(PieceColor.WHITE, PieceType.TILE, (2,1,0)))
# board[2][3].append(Piece(PieceColor.WHITE, PieceType.WALL, (2,3,0)))
# board[3][2].append(Piece(PieceColor.WHITE, PieceType.WALL, (3,2,0)))
# board[1][2].append(Piece(PieceColor.WHITE, PieceType.CAPSTONE, (1,2,0)))
# board[2][2].append(Piece(PieceColor.BLACK, PieceType.WALL, (2,2,0)))
# print(top_board_string(board))
# print(get_moves(board,PieceColor.BLACK))


#Tests get_moves() for finding squashing opportunities
# board = blank_board()

# board[2][1].append(Piece(PieceColor.WHITE, PieceType.WALL, (2,1,0)))
# board[2][3].append(Piece(PieceColor.WHITE, PieceType.WALL, (2,3,0)))
# board[3][2].append(Piece(PieceColor.WHITE, PieceType.TILE, (3,2,0)))
# board[1][2].append(Piece(PieceColor.WHITE, PieceType.CAPSTONE, (1,2,0)))
# board[2][2].append(Piece(PieceColor.BLACK, PieceType.TILE, (2,2,0)))
# board[2][2].append(Piece(PieceColor.BLACK, PieceType.CAPSTONE, (2,2,1)))
# for i in range(len(board)):
#     for j in range(len(board)):
#         if not len(board[i][j]):
#             board[i][j].append(Piece(PieceColor.WHITE, PieceType.WALL, (i,j,0)))


# print(top_board_string(board))
# print(get_moves(board,PieceColor.BLACK))


# Temp:
# board = blank_board()
# board[0][0].append(Piece(PieceColor.BLACK, PieceType.WALL, (0,0,0)))
# board[0][1].append(Piece(PieceColor.WHITE, PieceType.WALL, (0,1,0)))
# board[0][4].append(Piece(PieceColor.WHITE, PieceType.WALL, (0,4,0)))
# board[1][0].append(Piece(PieceColor.WHITE, PieceType.TILE, (1,0,0)))
# board[1][2].append(Piece(PieceColor.BLACK, PieceType.WALL, (1,2,0)))
# board[1][3].append(Piece(PieceColor.WHITE, PieceType.WALL, (1,3,0)))
# board[1][4].append(Piece(PieceColor.WHITE, PieceType.TILE, (1,4,0)))
# board[2][1].append(Piece(PieceColor.BLACK, PieceType.WALL, (2,1,0)))
# board[2][3].append(Piece(PieceColor.WHITE, PieceType.TILE, (2,3,0)))
# board[2][3].append(Piece(PieceColor.BLACK, PieceType.WALL, (2,3,1)))
# board[3][0].append(Piece(PieceColor.WHITE, PieceType.TILE, (3,0,0)))
# board[3][2].append(Piece(PieceColor.WHITE, PieceType.TILE, (3,2,0)))
# board[3][3].append(Piece(PieceColor.BLACK, PieceType.CAPSTONE, (3,3,0)))
# board[4][0].append(Piece(PieceColor.BLACK, PieceType.WALL, (4,0,0)))
# board[4][1].append(Piece(PieceColor.BLACK, PieceType.TILE, (4,1,0)))
# board[4][2].append(Piece(PieceColor.BLACK, PieceType.TILE, (4,2,0)))
# board[4][4].append(Piece(PieceColor.WHITE, PieceType.CAPSTONE, (4,4,0)))
# print(top_board_string(board))
# print(stacks_string(board))
# print(get_moves(board,PieceColor.BLACK))
# print(get_moves(board, PieceColor.WHITE))

# BW = 'BW'
# BT = 'BT'
# BC = 'BC'
# WT = 'WT'
# WC = 'WC'
# WW = 'WW'
# # Temp:
# board = blank_board()
# test = {[0,0]: deque([WT]),
# [0,1]: deque([WT]),
# [0,2]: deque([BW]),
# [0,3]: deque([BW]),
# [1,1]: deque([WT]),
# [1,2]: deque([BC]),
# [1,3]: deque([BW]),
# [1,4]: deque([WW]),
# [2,0]: deque([BT]),
# [2,4]: deque([WT]),
# [3,0]: deque([BT]),
# [3,2]: deque([WW]),
# [3,3]: deque([BW]),
# [3,4]: deque([BW, WC]),
# [4,1]: deque([WW]),
# [4,3]: deque([BT])}
# for key in test.keys():
    
#     board[key[0]][key[1]].append()
# print(stacks_string(board))
# print(get_moves(board,PieceColor.BLACK))

# board = blank_board()
# board[0][1].append(Piece(PieceColor.BLACK, PieceType.TILE, (0,1,0)))
# board[0][4].append(Piece(PieceColor.WHITE, PieceType.WALL, (0,4,0)))
# board[1][0].append(Piece(PieceColor.BLACK, PieceType.WALL, (1,0,0)))
# board[1][1].append(Piece(PieceColor.WHITE, PieceType.WALL, (1,1,0)))
# board[1][2].append(Piece(PieceColor.WHITE, PieceType.WALL, (1,2,0)))
# board[2][3].append(Piece(PieceColor.BLACK, PieceType.TILE, (2,3,0)))
# board[2][4].append(Piece(PieceColor.WHITE, PieceType.WALL, (2,4,0)))
# board[3][0].append(Piece(PieceColor.BLACK, PieceType.TILE, (3,0,0)))
# board[4][0].append(Piece(PieceColor.BLACK, PieceType.CAPSTONE, (4,0,0)))
# board[4][2].append(Piece(PieceColor.WHITE, PieceType.TILE, (4,2,0)))
# board[4][3].append(Piece(PieceColor.BLACK, PieceType.TILE, (4,3,0)))
# print(top_board_string(board))
# print(stacks_string(board))
# n = MCTSNode(encode_state(board), agent= PieceColor.WHITE, turn = PieceColor.WHITE)
# n.best_action()
# moves = get_moves(board, PieceColor.WHITE)
# for move in moves:
#     print(move)

def test(t):
    t.pop()

t = deque()
try:
    test(t)
except IndexError:
    f = open('test.txt',"w")
    f.write(f"""Error found! {t}""")
    f.close()