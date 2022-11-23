from Constants import BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES
from Tak import Tak
from UserAgent import User

game = Tak(BOARD_LENGTH, NUM_STONES, NUM_CAPSTONES)
game.play_game(User(), User())
