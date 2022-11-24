from copy import deepcopy
import unittest

from Constants import BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES
from Tak import Tak, GameState, PieceColor, PieceType, Piece, PlacementMove, StackMove, Direction


class RunTests(unittest.TestCase):
    """Run all tests for Tak"""

    def __init__(self):
        super().__init__()
        self.test_play_game()
        self.test_result()
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
        tak = Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES)
        board = tak.initial.board
        for i in range(3):
            board[0][0].append(Piece(PieceColor.WHITE, PieceType.TILE, (0, 0, 2 * i)))
            board[0][0].append(Piece(PieceColor.BLACK, PieceType.TILE, (0, 0, 2 * i + 1)))
        # placement
        piece1 = Piece(PieceColor.WHITE, PieceType.TILE, (0, 1, 0))
        move1 = PlacementMove((0, 1), piece1)
        board1 = deepcopy(board)
        board1[0][1].append(piece1)
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
        board3[0][2].appendleft(board3[0][0].pop())
        board3[0][2].appendleft(board3[0][0].pop())
        board3[0][1].appendleft(board3[0][0].pop())
        board3[0][1].appendleft(board3[0][0].pop())
        board3[0][1].appendleft(board3[0][0].pop())
        moves = [move1, move2, move3]
        state = GameState(to_move=PieceColor.WHITE, board=board, moves=moves)
        self.__assert_board_equality(board1, tak.result(state, move1).board)
        self.__assert_board_equality(board2, tak.result(state, move2).board)
        self.__assert_board_equality(board3, tak.result(state, move3).board)

    def test_terminal(self):
        board = Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES).initial.board
        board1 = deepcopy(board)
        count1 = 0
        for row in board1:
            for space in row:
                color = PieceColor.WHITE if count1 % 2 == 0 else PieceColor.BLACK
                piece = Piece(color, PieceType.TILE, None)
                space.append(piece)
        tak1 = Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES, board1)
        self.assertTrue(tak1.terminal_test())

        board2 = deepcopy(board)
        for space in board2[0]:
            space.append(Piece(PieceColor.WHITE, PieceType.TILE))
        tak2 = Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES, board2)
        self.assertTrue(tak2.terminal_test())

    def __assert_board_equality(self, expected_board, actual_board):
        """Assert that the expected and actual boards contain the same pieces"""
        for y in range(len(expected_board)):
            for x in range(len(expected_board[y])):
                for i in range(len(expected_board[y][x])):
                    self.assertEqual(expected_board[y][x][i], actual_board[y][x][i])


RunTests()
