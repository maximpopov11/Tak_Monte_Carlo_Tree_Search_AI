from Tak import *


def print_state(board):
    print(top_board_string(board))
    print(stacks_string(board))


class User:

    def __init__(self, color):
        self.color = color

    def query(self, board, is_first_turn=False):
        print_state(board)
        if is_first_turn:
            moves = get_moves_first_turn(board, self.color)
        else:
            moves = get_moves(board, self.color)
        print('Follow the prompts to enter a move or restart the process (X).')
        while True:
            move_type = self.__get_move_type()
            if move_type is None:
                continue
            row = self.__get_row()
            if row is None:
                continue
            column = self.__get_column()
            position = (row, column)
            if column is None:
                continue
            if move_type == PlacementMove:
                piece_type = self.__get_piece_type()
                if piece_type is None:
                    continue
                move = self.__get_placement_move(position, piece_type, moves, is_first_turn)
                if move is not None:
                    return move
                else:
                    print('Placement move  of', piece_type.name, 'at', position, 'does not exist.')
                    continue
            elif move_type == StackMove:
                direction = self.__get_direction()
                if direction is None:
                    continue
                stack_remainders = []
                restart = False
                while True:
                    remainder = self.__get_stack_remainder()
                    if remainder is None:
                        restart = True
                        break
                    elif remainder == 0:
                        break
                    else:
                        stack_remainders.append(remainder)
                if restart:
                    continue
                move = self.__get_stack_move(position, direction, stack_remainders, moves)
                if move is not None:
                    return move
                else:
                    print('Stack move at', position, 'in direction', direction, 'at remainders', stack_remainders,
                          'does not exist.')
                pass
            else:
                raise ValueError('__get_move_type() returned an invalid move type.')

    def __get_move_type(self):
        while True:
            command = input('Would you like to make a placement or stack move? (P/S): ')
            if command == 'X':
                return None
            elif command == 'P':
                return PlacementMove
            elif command == 'S':
                return StackMove
            else:
                print('Entered:', command, 'Please enter a valid input.')

    def __get_row(self):
        while True:
            command = input('Enter the number corresponding to the row you would like you make your move in: ')
            if command == 'X':
                return None
            else:
                try:
                    if 0 <= int(command) < BOARD_SIZE:
                        return int(command)
                    else:
                        print('Entered:', command, 'Please enter a valid input.')
                except:
                    print('Entered:', command, 'Please enter a valid input.')

    def __get_column(self):
        while True:
            command = input('Enter the number corresponding to the column you would like you make your move in: ')
            if command == 'X':
                return None
            else:
                try:
                    if 0 <= int(command) < BOARD_SIZE:
                        return int(command)
                    else:
                        print('Entered:', command, 'Please enter a valid input.')
                except:
                    print('Entered:', command, 'Please enter a valid input.')

    def __get_piece_type(self):
        while True:
            command = input('Would you like to place a tile, wall, or capstone? (T/W/C): ')
            if command == 'X':
                return None
            elif command == 'T':
                return PieceType.TILE
            elif command == 'W':
                return PieceType.WALL
            elif command == 'C':
                return PieceType.CAPSTONE
            else:
                print('Entered:', command, 'Please enter a valid input.')

    def __get_direction(self):
        while True:
            command = input('Would you like to move the stack up, down, left, or right? (U, D, L, R): ')
            if command == 'X':
                return None
            elif command == 'U':
                return Direction.UP
            elif command == 'D':
                return Direction.DOWN
            elif command == 'L':
                return Direction.LEFT
            elif command == 'R':
                return Direction.RIGHT
            else:
                print('Entered:', command, 'Please enter a valid input.')

    def __get_stack_remainder(self):
        while True:
            command = input('Enter the number corresponding to the number of pieces you would like to leave in the '
                            'next space or (0) if you do not wish to move the stack further: ')
            if command == 'X':
                return None
            else:
                try:
                    return int(command)
                except:
                    print('Entered:', command, 'Please enter a valid input.')

    def __get_placement_move(self, position, piece_type, moves, first_turn=False):
        color = self.color
        if first_turn:
            color = PieceColor.WHITE if color == PieceColor.BLACK else PieceColor.BLACK
        for move in moves:
            if type(move) == PlacementMove and move.position[0] == position[0] and move.position[1] == position[1] and \
                    move.piece.type == piece_type and move.player == color:
                return move
        return None

    def __get_stack_move(self, position, direction, stack_remainders, moves):
        for move in moves:
            if type(move) == StackMove and move.position[0] == position[0] and move.position[1] == position[1] and \
                    move.direction == direction and move.stack_remainders == stack_remainders and \
                    move.player == self.color:
                return move
        return None


def test_carry_limit(board):
    """Manual testing for legal carrying limit:
    - legal close [5]
    - legal far [1, 1, 1, 2]
    - illegal carry close [6]
    - illegal carry far [1, 1, 1, 3]
    - illegal space [1, 1, 1, 1, 1]"""
    for i in range(BOARD_SIZE + 1):
        board[0][0].append(Piece(PieceColor.WHITE, PieceType.TILE, (0, 0, i)))


def test_flat_win_piece_type(board):
    """Manual testing for flat win:
    - board fill (place T (4,4)); capstone and wall don't count: black wins"""
    color = PieceColor.WHITE
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            board[row][col].append(Piece(color, PieceType.TILE, (row, col, 0)))
            color = PieceColor.WHITE if color == PieceColor.BLACK else PieceColor.BLACK
    board[0][0].append(Piece(PieceColor.WHITE, PieceType.CAPSTONE, (0, 0, 1)))
    board[0][2].append(Piece(PieceColor.WHITE, PieceType.WALL, (0, 2, 1)))
    board[4][4].pop()


def test_flat_win_tie(board):
    """Manual testing for flat win:
    - pieces used (place C (1, 0)); tie: Black wins"""
    for i in range(NUM_PIECES):
        board[0][0].append(Piece(PieceColor.WHITE, PieceType.TILE, (0, 0, i)))
        board[0][1].append(Piece(PieceColor.BLACK, PieceType.TILE, (0, 0, i)))
    board[1][1].append(Piece(PieceColor.BLACK, PieceType.CAPSTONE, (0, 0, 0)))


def test_road(board):
    """Manual testing for flat win:
    - wall (0,4) = continue -> capstone (4,0) = black win (tests piece types, dragon clause)"""
    for i in range(BOARD_SIZE - 1):
        board[0][i].append(Piece(PieceColor.WHITE, PieceType.TILE, (0, i, 0)))
        board[i][0].append(Piece(PieceColor.WHITE, PieceType.TILE, (i, 0, 0)))
        board[BOARD_SIZE - 1][i + 1].append(Piece(PieceColor.BLACK, PieceType.TILE, (BOARD_SIZE - 1, i + 1, 0)))


def test_stack_moves(board):
    """Manual testing for stack moves:
    - (0, 0) stack right [1] fails (wall blocking)
    - (1, 0) stack right [1] succeeds (wall crushed)
    - (1, 0) stack right [2] fails (wall blocking)
    - (1, 0) stack down [1] succeeds (wall crushed)
    - (0, 0) stack down [1] fails (capstone blocking)"""
    for i in range(BOARD_SIZE + 1):
        board[0][0].append(Piece(PieceColor.WHITE, PieceType.TILE, (0, 0, i)))
        board[1][0].append(Piece(PieceColor.WHITE, PieceType.TILE, (1, 0, i)))
    board[1][0].append(Piece(PieceColor.WHITE, PieceType.CAPSTONE, (1, 0, BOARD_SIZE + 1)))
    board[0][1].append(Piece(PieceColor.BLACK, PieceType.WALL, (0, 1, 0)))
    board[1][1].append(Piece(PieceColor.BLACK, PieceType.WALL, (1, 1, 0)))
    board[2][0].append(Piece(PieceColor.WHITE, PieceType.WALL, (2, 0, 0)))


def main():
    board = blank_board()
    # test_carry_limit(board)
    # test_flat_win_piece_type(board)
    # test_flat_win_tie(board)
    # test_road(board)
    # test_stack_moves(board)
    play_game(board, User(PieceColor.WHITE), User(PieceColor.BLACK))
    # TODO: play out a full game vs self
    # TODO: play out a full game vs AI


if __name__ == "__main__":
    main()
