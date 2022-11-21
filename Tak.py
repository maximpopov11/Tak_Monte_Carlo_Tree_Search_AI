from collections import deque, namedtuple
from copy import deepcopy
from enum import Enum

GameState = namedtuple('GameState', 'to_move, board, moves')


class PieceColor(Enum):
    BLACK, WHITE = range(2)


class PieceType(Enum):
    """Enum enables easy access to standardized piece characteristics."""
    WALL, TILE, CAPSTONE = range(3)


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


class Direction(Enum):
    """Direction for stack movement."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class StackMove:
    """Tak stack movement move."""

    def __init__(self, position, direction, stack_remainders):
        self.position = position
        self.direction = direction
        self.stack_remainders = stack_remainders


class Tak:
    """Tak game object which controls all game aspects."""

    def __init__(self, board_length, num_stones, num_capstones, board=[]):
        """Set the initial game state."""
        self.board = board
        if len(self.board) == 0:
            for i in range(board_length):
                self.board.append([])
                for j in range(board_length):
                    self.board[i].append(deque())
        self.white_pieces = [num_stones, num_capstones]
        self.black_pieces = [num_stones, num_capstones]
        board = self.board
        to_move = PieceColor.WHITE
        self.moves = self.__get_moves(board, to_move)
        self.board_length = board_length
        self.initial = GameState(to_move=to_move, board=board, moves=self.moves)

    def play_game(self, white_agent, black_agent):
        state = self.initial
        agent = white_agent
        while True:
            move = agent.query(state)
            state = self.result(state, move)
            agent = white_agent if agent == black_agent else black_agent
            if self.terminal_test():
                break

    def result(self, state, move):
        """Adjudicates the result of the game after the move being made."""
        if move not in state.moves:
            raise ValueError('Given move is not in state.moves.')
        board = deepcopy(state.board)
        if isinstance(move, PlacementMove):
            board[move.position[0]][move.position[1]].append(move.piece)
        elif isinstance(move, StackMove):
            initial_y = move.position[0]
            initial_x = move.position[1]
            initial_space = GameState.board[initial_y, initial_x]
            target_y = initial_y + (len(move.stack_remainders) - 1) * move.direction[0]
            target_x = initial_x + (len(move.stack_remainders) - 1) * move.direction[1]
            target_space = GameState.board[target_y, target_x]
            for i in range(len(move.stack_remainders) - 1, 0):
                for j in range(move.stack_remainders[i]):
                    target_space.appendleft(initial_space.pop())
                target_y -= move.direction[0]
                target_x -= move.direction[1]
                target_space = GameState.board[target_y, target_x]
        else:
            raise ValueError('Given move has a nonexistent type.')
        to_move = PieceColor.WHITE if GameState.to_move == PieceColor.BLACK else PieceColor.BLACK
        moves = self.__get_moves(state, to_move)
        return GameState(to_move=to_move, board=board, moves=moves)

    def __get_moves(self, board, color):
        """Returns legal moves."""
        moves = []
        pieces = self.white_pieces if color == PieceColor.WHITE else self.black_pieces
        for y in range(0, self.board_length):
            for x in range(0, self.board_length):
                stack = board[y][x]
                # placement moves
                if len(stack) == 0:
                    if pieces[0] > 0:
                        moves.append(PlacementMove((x, y), Piece(color, PieceType.TILE, (x, y))))
                        moves.append(PlacementMove((x, y), Piece(color, PieceType.WALL, (x, y))))
                    if pieces[1] > 0:
                        moves.append(PlacementMove((x, y), Piece(color, PieceType.CAPSTONE, (x, y))))
                # stack moves
                elif stack[-1].color == color:
                    self.__get_stack_moves_in_direction(moves, (x, y), Direction.UP)
                    self.__get_stack_moves_in_direction(moves, (x, y), Direction.DOWN)
                    self.__get_stack_moves_in_direction(moves, (x, y), Direction.LEFT)
                    self.__get_stack_moves_in_direction(moves, (x, y), Direction.RIGHT)
        return moves

    STACK_REMAINDERS = [
        [1],
        [2],
        [3],
        [4],
        [5],
        [1, 1],
        [2, 1],
        [1, 2],
        [3, 1],
        [2, 2],
        [1, 3],
        [4, 1],
        [3, 2],
        [2, 3],
        [1, 4],
        [1, 1, 1],
        [2, 1, 1],
        [1, 2, 1],
        [1, 1, 2],
        [3, 1, 1],
        [1, 3, 1],
        [1, 1, 3],
        [2, 2, 1],
        [2, 1, 2],
        [1, 2, 2],
        [1, 1, 1, 1],
        [2, 1, 1, 1],
        [1, 2, 1, 1],
        [1, 1, 2, 1],
        [1, 1, 1, 2],
    ]

    def __get_stack_moves_in_direction(self, moves, position, direction):
        max_distance = 0
        while True:
            end_x = position[0] + direction[0]
            end_y = position[1] + direction[1]
            if end_x < 0 or end_x >= self.board_length or end_y < 0 or end_y >= self.board_length:
                break
            else:
                max_distance += 1
        for stack_remainders in self.STACK_REMAINDERS:
            if len(stack_remainders) > max_distance:
                break
            else:
                moves.append(StackMove(position, direction, stack_remainders))

    def terminal_test(self):
        """Terminal States:\n\t
        Board Win: all pieces of a player are used or board is covered\n\t
        Road Win (Dragon): a move results in an orthogonally connected path 
        of player tiles/capstone pieces belonging to a single player. If a move 
        causes both players to have roads, the moving player wins."""
        all_pieces_placed = self.white_pieces == [0, 0] or self.black_pieces == [0, 0]
        player_roads = set()
        fewest_pieces = 1
        # Checks for roads and board coverage
        for j, row in enumerate(self.board):
            for i, space in enumerate(row):
                fewest_pieces = min(len(space), fewest_pieces)  # Tracks board coverage for flat win condition
                # Road checking begins below
                if i == 0 or j == 0:  # We are on the top or left edges of the board
                    if len(space) > 0:  # There's at least 1 piece in the current location
                        if space[len(space) - 1].type != PieceType.WALL:  # Piece can be part of road
                            if self.__find_roads(space[len(space) - 1]):
                                player_roads.add(space[len(space) - 1].color)
        if len(player_roads):
            # player who made the winning move gets the win, regardless of whether not enemy also had a road
            if player_roads.intersection({GameState.to_move}):
                if len(player_roads) == 2:
                    print(f"Winner: {player_roads.difference({GameState.to_move}).pop()}")
                else:
                    print(f"Winner: {GameState.to_move}")
            else:
                print(f"Winner: {player_roads.pop()}")
            return True

        # Score tallies after flat win condition detected
        if fewest_pieces == 1 or all_pieces_placed:
            print("Either the board is covered or a player is out of stones! Tallying scores...")
            white = 0
            black = 0
            for row in self.board:
                for space in row:
                    if space[len(space) - 1].type == PieceType.TILE:
                        if space[len(space) - 1].color == PieceColor.WHITE:
                            white += 1
                        else:
                            black += 1
            print(f"White: {white} | Black: {black}")
            return True

        return False

    def __find_roads(self, piece):
        """Starting point of a recursive DFS looking for roads across the 2D board array.
        Returns true if a road is found originating from the given piece."""
        row = piece.position[0]
        col = piece.position[1]
        left = col - 1
        right = left + 2
        up = row - 1
        down = up + 2
        if row == 0 and col == 0:  # Top left corner, D & R
            return self.__find_roads_rec(down, col, piece.color, True, True, {(row, col)}) or \
                   self.__find_roads_rec(row, right, piece.color, True, True, {(row, col)})
        elif row == 0 and col == self.board_length - 1:  # Top right corner, D & L
            return self.__find_roads_rec(down, col, piece.color, True, False, {(row, col)}) or \
                   self.__find_roads_rec(row, left, piece.color, True, False, {(row, col)})
        elif row == self.board_length - 1 and col == 0:  # Bottom left corner, U & R
            return self.__find_roads_rec(up, col, piece.color, False, True, {(row, col)}) or \
                   self.__find_roads_rec(row, right, piece.color, False, True, {(row, col)})
        elif row == 0:  # Top row, LRD
            return self.__find_roads_rec(down, col, piece.color, True, False, {(row, col)}) or \
                   self.__find_roads_rec(row, left, piece.color, True, False, {(row, col)}) or \
                   self.__find_roads_rec(row, right, piece.color, True, False, {(row, col)})
        elif col == 0:  # Left col, UDR
            return self.__find_roads_rec(row, right, piece.color, False, True, {(row, col)}) or \
                   self.__find_roads_rec(down, col, piece.color, False, True, {(row, col)}) or \
                   self.__find_roads_rec(up, col, piece.color, False, True, {(row, col)})

    def __find_roads_rec(self, i, j, color, row_start, col_start, seen):
        """Recursive DFS across the 2D board array along orthogonal paths, 
        returns true if current node is at opposite end from starting node."""
        top_stack = len(self.board[i][j]) - 1  # If there's a piece at the passed coords
        if top_stack >= 0:
            piece = self.board[i][j][top_stack]  # Top piece of stack at passed coords
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

        if row == self.board_length - 1 and row_start:  # Piece, belongs to same player, and on opposite edge of start
            return True
        elif col == self.board_length - 1 and col_start:  # same as above
            return True

        seen.add((piece.position[0], piece.position[1]))  # Seen set passed down to avoid visiting ancestors

        for rowDir in row_dirs:
            if rowDir in range(self.board_length) and (rowDir, col) not in seen:
                return self.__find_roads_rec(rowDir, col, piece.color, row_start, col_start, seen)
        for colDir in col_dirs:
            if colDir in range(self.board_length) and (row, colDir) not in seen:
                return self.__find_roads_rec(row, colDir, piece.color, row_start, col_start, seen)
