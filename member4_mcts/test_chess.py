"""Chay: python -m unittest -v test_chess.py (can python-chess)."""
import unittest
import chess
from chess_adapter import ChessState, choose_chess_move, material_value


class ChessAdapterTests(unittest.TestCase):
    def test_initial_legal_moves(self):
        s = ChessState(chess.Board())
        self.assertEqual(s.current_player, 'W')
        self.assertEqual(len(s.legal_moves()), 20)
        self.assertIn('e2e4', s.legal_moves())

    def test_play_does_not_mutate_input(self):
        board = chess.Board()
        s = ChessState(board)
        s2 = s.play('e2e4')
        self.assertEqual(s2.current_player, 'B')
        self.assertEqual(s.current_player, 'W')
        self.assertEqual(board.fen(), chess.STARTING_FEN)
        self.assertEqual(s2.remaining_plies, 47)

    def test_illegal_move(self):
        s = ChessState(chess.Board())
        with self.assertRaises(ValueError):
            s.play('e2e5')

    def test_checkmate_rewards(self):
        board = chess.Board()
        for move in ('f2f3', 'e7e5', 'g2g4', 'd8h4'):
            board.push_uci(move)
        self.assertTrue(board.is_checkmate())
        s = ChessState(board)
        self.assertTrue(s.is_terminal())
        self.assertEqual(s.reward('B'), 1.0)
        self.assertEqual(s.reward('W'), 0.0)
        self.assertEqual(s.legal_moves(), [])

    def test_draw_reward(self):
        # The classic king/queen stalemate position.
        board = chess.Board('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1')
        self.assertTrue(board.is_stalemate())
        s = ChessState(board)
        self.assertEqual(s.reward('B'), 0.5)
        self.assertEqual(s.reward('W'), 0.5)

    def test_rollout_cutoff_uses_evaluation(self):
        s = ChessState(chess.Board(), remaining_plies=0)
        self.assertTrue(s.is_terminal())
        self.assertEqual(s.reward('W'), 0.5)
        self.assertEqual(s.reward('B'), 0.5)
        self.assertEqual(material_value(chess.Board(), 'W'), 0.0)

    def test_mcts_returns_legal_move_and_preserves_board(self):
        board = chess.Board()
        original = board.fen()
        move, stats = choose_chess_move(board, simulations=4, rollout_plies=8, seed=42)
        self.assertIn(move, board.legal_moves)
        self.assertEqual(board.fen(), original)
        self.assertEqual(stats.simulations, 4)
        self.assertGreaterEqual(stats.nodes_created, 2)

    def test_terminal_board_fails_cleanly(self):
        board = chess.Board()
        for move in ('f2f3', 'e7e5', 'g2g4', 'd8h4'):
            board.push_uci(move)
        with self.assertRaises(ValueError):
            choose_chess_move(board)


if __name__ == '__main__':
    unittest.main()
