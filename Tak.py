class Tak:
    """Tak game object which controls all game aspects."""

    def __init__(self, board_length):
        """Sets the initial state."""
        self.board_length = board_length
        self.__initialize_board()
        self.__initialize_initial_state()

    def __initialize_board(self):
        """Initializes the board."""
        pass

    def __initialize_initial_state(self):
        """Initializes non-board state."""
        pass
