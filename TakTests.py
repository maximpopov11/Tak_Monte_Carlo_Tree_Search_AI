from copy import deepcopy
import unittest

from Constants import BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES
from Tak import Tak, GameState, PieceColor, PieceType, Piece, PlacementMove, StackMove, Direction


class run_tests(unittest.TestCase):
    """Run all tests for Tak"""

    def __init__(self):
        self.test_play_game()
        self.test_result()
        # TODO terminal_test
        # TODO: test stack moving onto wall crushes wall
        # TODO: test stack moving onto capstone illegal

    def test_play_game(self):
        """Test that play_game does not throw an exception by having agents make the first move listed"""
        class Agent:
            def query(self, state):
                return state.moves[0]

        agent = Agent()
        Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES).play_game(agent, agent)

    def test_result(self):
        """Test result in a series of situations"""
        initial = Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES).initial
        board = initial.board
        for i in range(3):
            board[0][0].append(Piece(PieceColor.WHITE, PieceType.TILE, (0, 0, 2 * i)))
            board[0][0].append(Piece(PieceColor.BLACK, PieceType.TILE, (0, 0, 2 * i + 1)))
        # placement
        piece1 = Piece(PieceColor.WHITE, PieceType.TILE, (0, 1, 0))
        move1 = PlacementMove((0, 1), piece1)
        board1 = deepcopy(board)
        board1[1][0].append(piece1)
        # long stack move
        move2 = StackMove((0, 0), Direction.RIGHT, [1, 1, 1, 1])
        board2 = deepcopy(board)
        board2[0][4].append(board2[0][0].pop())
        board2[0][3].append(board2[0][0].pop())
        board2[0][2].append(board2[0][0].pop())
        board2[0][1].append(board2[0][0].pop())
        # short stack move
        move3 = StackMove((0, 0), Direction.RIGHT, [3, 2])
        board3 = deepcopy(board)
        board2[0][2].appendleft(board2[0][0].pop())
        board2[0][2].appendleft(board2[0][0].pop())
        board2[0][1].appendleft(board2[0][0].pop())
        board2[0][1].appendleft(board2[0][0].pop())
        board2[0][1].appendleft(board2[0][0].pop())
        moves = [move1, move2, move3]
        state = GameState(to_move=PieceColor.WHITE, board=board, moves=moves)
        self.assertEqual(board1, Tak.result(initial, state, move1).board)
        self.assertEqual(board2, Tak.result(initial, state, move2).board)
        self.assertEqual(board3, Tak.result(initial, state, move3).board)


run_tests()
