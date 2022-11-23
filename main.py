import sys
from Tak import *
from collections import deque
import math as m

<<<<<<< HEAD

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
print(board)	

# NUM_CAPSTONES = 1   #per player	
# NUM_PIECES = 21     #per player	
# BOARD_SIZE = 5      	

# # Encoding info: format whitepieces,whitecapstone,blackpieces,blackcapstone	

# xbits =  m.ceil(m.log(BOARD_SIZE,2))	
# ybits = xbits	
# zbits = m.ceil(m.log(2*(NUM_CAPSTONES+NUM_PIECES),2))	
# PIECE_SIZE = xbits+ybits+zbits + 1  #No. of bits used in binary encoding of a piece	
# CAPSTONE_SIZE = PIECE_SIZE - 1      #No. of bits used in binary encoding of a capstone	
# GAMESIZE = 2 * (PIECE_SIZE*NUM_PIECES + CAPSTONE_SIZE*NUM_CAPSTONES)      #No. of bits used in binary encoding of game board	

# j = 0b101	
# print(f"{sys.getsizeof(j)}")	

# test = deque()	
# test.append(1)	
# test.append(2)	
# test.append(3)	
# print(test.pop())	

# from enum import Enum	

# class Test(Enum):	
#     T1,T2 = range(2)	

#     def __str__(self):	
#         if self == Test.T1:	
#             return "T1"	
#         else:	
#             return "T2"	

# t = Test.T1	
# print(t)	
# 0 commen
=======
>>>>>>> 0e991f27068a48cd6b673851072db07989d2a749
