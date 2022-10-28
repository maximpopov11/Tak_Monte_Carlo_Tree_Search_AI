from collections import deque, namedtuple
from enum import Enum
from logging import raiseExceptions

GameState = namedtuple('GameState', 'to_move, board, pieces, moves')

class pieceType(Enum):
        """"Enum enables easy access to standardized piece characteristics"""
        BLACK, WHITE, WALL,TILE,CAPSTONE = range(5)

class Piece:
    """Tak game piece represents color, type, and XYZ position of piece"""
    def __init__(self, color, type, position):
        self.color = color
        self.type = type
        self.position = [position[0],position[1],position[2]] #row, col, dequeIndex
    
    def __repr__(self):
        rep = "B" if self.color == pieceType.BLACK else "W"
        if self.type == pieceType.WALL:
            rep += "W"
        elif self.type == pieceType.TILE:
            rep += "T"
        else:
            rep += "C"
        return rep

class Tak:
    """Tak game object which controls all game aspects."""
    def __init__(self, board_length, num_stones, num_capstones, board = []):
        """Set the initial game state."""
        self.board = board
        if len(self.board) == 0:
            for i in range(board_length):
                self.board.append([])
                for j in range(board_length):
                    self.board[i].append(deque())
        self.white_pieces = [num_stones, num_capstones]
        self.black_pieces = [num_stones, num_capstones]
        self.placements = [(x, y) for x in range(0, board_length) for y in range(0, board_length)]
        self.white_moves = []
        self.black_moves = []
        self.board_length = board_length
        moves = self.placements + self.white_moves
        self.initial = GameState(to_move='W', board=self.board, pieces=self.white_pieces, moves=moves)

    def terminal_test(self):
        """Terminal States:\n\t
        Board Win: all pieces of a player are used or board is covered\n\t
        Road Win (Dragon): a move results in an orthogonally connected path 
        of player tiles/capstone pieces belonging to a single player. If a move 
        causes both players to have roads, the moving player wins."""
        allPiecesPlaced = self.white_pieces == [0,0] or self.black_pieces == [0,0]
        
        fewestPieces = 1
        #Checks for roads and board coverage
        for j,row in enumerate(self.board):
            for i,space in enumerate(row):
                fewestPieces = min(len(space),fewestPieces) #Tracks board coverage for flat win condition
                #Road checking begins below
                if (i == 0 or j == 0):      #We are on the top or left edges of the board
                    if len(space) > 0:      #There's at least 1 piece in the current location
                        if space[len(space)-1].type != pieceType.WALL: #Piece can be part of road
                            if self.findRoads(space[len(space)-1]):
                                print(f"Road Found! Player: {space[len(space)-1].color}")
                                return True

        #Score tallies after flat win condition detected
        if fewestPieces == 1 or allPiecesPlaced:
            print("Either the board is covered or a player is out of stones! Tallying scores...")
            white = 0
            black = 0
            for row in self.board:
                for space in row:
                    if space[len(space)-1].type == pieceType.TILE:
                        if space[len(space)-1].color == pieceType.WHITE:
                            white += 1
                        else:
                            black += 1
            print(f"Black: {black} | White: {white}")
            return True
        
        return False


    def findRoads(self,piece):
        """Starting point of a recursive DFS looking for roads across the 2D board array.
        Returns true if a road is found originating from the given piece"""
        row = piece.position[0]
        col = piece.position[1]
        left = col - 1
        right = left + 2
        up = row - 1
        down = up + 2
        if row == 0 and col == 0: #Top left corner, D & R
            return self.findRoadsRec(down,col, piece.color, True, True, {(row,col)}) or self.findRoadsRec(row,right, piece.color, True, True, {(row,col)})
        elif row == 0 and col == self.board_length - 1: #Top right corner, D & L
            return self.findRoadsRec(down,col, piece.color,True,False, {(row,col)}) or self.findRoadsRec(row,left, piece.color,True,False, {(row,col)}) 
        elif row == self.board_length-1 and col == 0: #Bottom left corner, U & R
            return self.findRoadsRec(up,col, piece.color,False,True, {(row,col)}) or self.findRoadsRec(row,right, piece.color,False,True, {(row,col)})
        elif row == 0:    #Top row, LRD
            return self.findRoadsRec(down,col, piece.color,True,False, {(row,col)}) or self.findRoadsRec(row,left, piece.color,True,False, {(row,col)})  or self.findRoadsRec(row,right, piece.color,True,False, {(row,col)})
        elif col == 0:    #Left col, UDR
            return self.findRoadsRec(row, right, piece.color,False,True, {(row,col)}) or self.findRoadsRec(down,col, piece.color,False,True, {(row,col)})  or self.findRoadsRec(up,col, piece.color,False,True, {(row,col)})

    def findRoadsRec(self,i,j, color, rowStart, colStart, seen):
        """Recursive DFS across the 2D board array along orthogonal paths, 
        returns true if current node is at opposite end from starting node"""
        topStack = len(self.board[i][j]) - 1 #If there's a piece at the passed coords
        if  topStack >= 0:
            piece = self.board[i][j][topStack] #Top piece of stack at passed coords
        else:
            return False    #No piece at this location
        if piece.color != color or piece.type == pieceType.WALL:
            return False    #piece at this location belongs to opponent or is a non-road
        
        row = piece.position[0]
        col = piece.position[1]
        left = col - 1
        right = left + 2
        up = row - 1
        down = up + 2
        rowDirs = [up,down]
        colDirs = [left, right]

        if row == self.board_length - 1 and rowStart: #Piece, belongs to same player, and on opposite edge of start
            return True
        elif col == self.board_length - 1 and colStart: # same as above
            return True

        seen.add((piece.position[0],piece.position[1])) #Seen set passed down to avoid visiting ancestors

        for rowDir in rowDirs:
            if rowDir in range(self.board_length) and (rowDir,col) not in seen:
                return self.findRoadsRec(rowDir,col, piece.color, rowStart, colStart, seen)
        for colDir in colDirs:
            if colDir in range(self.board_length) and (row, colDir) not in seen:
                return self.findRoadsRec(row, colDir, piece.color, rowStart, colStart, seen)
                            
        
            


        
                            

                                    

                                    

    
    
