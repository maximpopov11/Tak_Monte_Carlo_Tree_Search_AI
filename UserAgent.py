from Tak import PieceColor, PlacementMove


class User:

    def __init__(self):
        pass

    def query(self, state):
        self.print_state(state)
        return self.get_move(state)

    def print_state(self, state):
        # TODO: implement a nicer user-friendly board view
        for row in state.board:
            for space in row:
                symbol = '_'
                if len(space) > 0:
                    color = space[-1].color
                    symbol = 'W' if color == PieceColor.WHITE else 'B'
                print(symbol, end=' ')
            print()
        pass

    def get_move(self, state):
        # TODO: implement a nicer user-friendly move selection
        index = 0
        for move in state.moves:
            type = "placement move" if isinstance(move, PlacementMove) else "stack move"
            x = move.position[0]
            y = move.position[1]
            print(index, type, ' at (', x, ',', y, ')')
            index += 1
        while True:
            user_input = input('Enter the number correlating to the move you would like to make: ')
            try:
                index = int(user_input)
                if 0 <= index <= len(state.moves) - 1:
                    break
                else:
                    print("Please enter a valid number!")
            except:
                print("Please enter a number!")
        return state.moves[index]
