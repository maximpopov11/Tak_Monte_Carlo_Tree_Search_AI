from Constants import BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES
from Tak import Tak


def run_tests():
    """Run all tests for Tak"""
    test_play_game()


def test_play_game():
    """Test that play_game does not throw an exception by having agents make the first move listed"""

    class Agent:
        def query(self, state):
            return state.moves[0]

    agent = Agent()
    Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES).play_game(agent, agent)


run_tests()
