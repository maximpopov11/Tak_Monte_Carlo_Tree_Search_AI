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

gameBinary = game.encode_state()
print("Game State as Binary")
print(gameBinary)
print(f"Length of game binary: {len(gameBinary)}")
num = bits_to_int(gameBinary)
print(f"Game State Int: {num}")
print(f"Size of game state int: {sys.getsizeof(num)} bytes") #100 bytes. 10 game states per kilobyte, 100 per meg, 1000 per gig... plus all the other overhead... oh boy

test = [1] * 285
testNum = bits_to_int(test)
print(f"Size of avg. case var len encoding board: {sys.getsizeof(testNum)} bytes") #64 bytes, worthwhile savings?

