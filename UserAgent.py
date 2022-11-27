from Tak import *


def print_state(board):
    print(top_board_string(board))
    print(stacks_string(board))


class User:

    def __init__(self, color):
        self.color = color

    def query(self, board):
        print_state(board)
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
                move = self.__get_placement_move(position, piece_type, moves)
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

    def __get_placement_move(self, position, piece_type, moves):
        for move in moves:
            if type(move) == PlacementMove and move.position[0] == position[0] and move.position[1] == position[1] and \
                    move.piece.type == piece_type and move.player == self.color:
                return move
        return None

    def __get_stack_move(self, position, direction, stack_remainders, moves):
        for move in moves:
            if type(move) == StackMove and move.position[0] == position[0] and move.position[1] == position[1] and \
                    move.direction == direction and move.stack_remainders == stack_remainders and \
                    move.player == self.color:
                return move
        return None


def main():
    board = blank_board()
    play_game(board, User(PieceColor.WHITE), User(PieceColor.BLACK))


if __name__ == "__main__":
    main()
