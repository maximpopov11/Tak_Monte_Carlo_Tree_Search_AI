from Tak import *


def print_state(board):
    print(top_board_string(board))
    print(stacks_string(board))


class User:

    def __init__(self, color):
        self.color = color

    def query(self, board):
        print_state(board)
        return self.get_move(board)

    def get_move(self, board):
        # TODO: implement a nicer user-friendly move selection
        moves = get_moves(board, self.color)
        index = 0
        for move in moves:
            type = "placement move" if isinstance(move, PlacementMove) else "stack move"
            x = move.position[0]
            y = move.position[1]
            print(index, type, ' at (', x, ',', y, ')')
            index += 1
        while True:
            user_input = input('Enter the number correlating to the move you would like to make: ')
            try:
                index = int(user_input)
                if 0 <= index <= len(moves) - 1:
                    break
                else:
                    print("Please enter a valid number!")
            except:
                print("Please enter a number!")
        return moves[index]


def main():
    board = blank_board()
    play_game(board, User(PieceColor.WHITE), User(PieceColor.BLACK))


if __name__ == "__main__":
    main()
