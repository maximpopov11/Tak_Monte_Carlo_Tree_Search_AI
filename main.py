import sys
from TakGame import *
from collections import deque

BOARD_LENGTH = 5
NUM_STONES = 21
NUM_CAPSTONES = 1

def bits_to_int(bits):
    res = 0
    for b in bits:
        res *= 2
        res += b
    return res

def make_board():
    board = []
    for i in range(5):
        board.append([])
        for j in range(5):
            board[i].append(deque())
            if i != 3:
                board[i][j].append(Piece(PieceColor.WHITE,PieceType.TILE,(i,j,0)))
                board[i][j].append(Piece(PieceColor.BLACK,PieceType.TILE,(i,j,1)))
    return board

    
    
board = make_board()
game = Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES,board)

print(decode_state(game.encode_state()))#100 100 000000 1

