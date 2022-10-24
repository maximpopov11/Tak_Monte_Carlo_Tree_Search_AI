from collections import deque, namedtuple

GameState = namedtuple('GameState', 'to_move, board, pieces, moves')


class Tak:
    """Tak game object which controls all game aspects."""

    def __init__(self, board_length, num_stones, num_capstones):
        """Set the initial game state."""
        board = [board_length][board_length]
        for i in range(0, board_length):
            for j in range(0, board_length):
                board[i][j] = deque()
        self.white_pieces = [num_stones, num_capstones]
        self.black_pieces = [num_stones, num_capstones]
        self.placements = [(x, y) for x in range(0, board_length) for y in range(0, board_length)]
        self.white_moves = []
        self.black_moves = []
        moves = self.placements + self.white_moves
        self.initial = GameState(to_move='W', board=board, pieces=self.white_pieces, moves=moves)
