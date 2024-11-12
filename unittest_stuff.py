import unittest
from final_sos_version import Game, Team, Board, Square

class TestSOSDetection(unittest.TestCase):

    def setUp(self):
        # setting up a sample game instance with a 5x5 board
        root = None  # placeholder since we're not using the GUI in tests
        self.game = Game(root)
        self.game.board_size = 5
        self.game.board = Board(root, self.game.board_size, self.game.board_size, lambda x, y: None)

    def place_letter(self, row, col, letter):
        # helper to simulate placing a letter on the board
        square = self.game.board.get_square(row, col)
        square.mark(letter, self.game.team_save if letter == "S" else self.game.team_souls)

    def test_sos_detection_horizontal(self):
        # testing horizontal sos detection
        self.place_letter(2, 1, "S")
        self.place_letter(2, 2, "O")
        self.place_letter(2, 3, "S")
        self.assertEqual(self.game.check_sos(2, 2, "O"), 1)

    def test_sos_detection_vertical(self):
        # testing vertical sos detection
        self.place_letter(1, 2, "S")
        self.place_letter(2, 2, "O")
        self.place_letter(3, 2, "S")
        self.assertEqual(self.game.check_sos(2, 2, "O"), 1)

    def test_sos_detection_diagonal_top_left_to_bottom_right(self):
        # testing diagonal sos detection from top-left to bottom-right
        self.place_letter(0, 0, "S")
        self.place_letter(1, 1, "O")
        self.place_letter(2, 2, "S")
        self.assertEqual(self.game.check_sos(1, 1, "O"), 1)

    def test_sos_detection_diagonal_bottom_left_to_top_right(self):
        # testing diagonal sos detection from bottom-left to top-right
        self.place_letter(3, 1, "S")
        self.place_letter(2, 2, "O")
        self.place_letter(1, 3, "S")
        self.assertEqual(self.game.check_sos(2, 2, "O"), 1)

    def test_sos_multiple_detections(self):
        # testing multiple sos detections around a single point
        self.place_letter(2, 1, "S")
        self.place_letter(2, 2, "O")
        self.place_letter(2, 3, "S")
        self.place_letter(1, 2, "S")
        self.place_letter(3, 2, "S")
        # should detect two "SOS" formations with (2, 2) as the center
        self.assertEqual(self.game.check_sos(2, 2, "O"), 2)

    def test_sos_no_detection(self):
        # testing that no sos is detected if the pattern is incomplete
        self.place_letter(0, 0, "S")
        self.place_letter(0, 1, "O")
        # no third "S" to complete an "SOS"
        self.assertEqual(self.game.check_sos(0, 1, "O"), 0)

if __name__ == "__main__":
    unittest.main()
