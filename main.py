from Tak import Tak
from UserAgent import User

BOARD_LENGTH = 5
NUM_STONES = 21
NUM_CAPSTONES = 1

game = Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES)
game.play_game(User(), User())
