"""Chạy: py -m unittest discover -s tests -v"""
import unittest
import chess
from alpha_beta import (AlphaBetaAI, evaluate, get_move,
                        make_basic_ai, make_minimax_ai, search)


class TestAlphaBeta(unittest.TestCase):
    def test_legal_move_does_not_modify_board(self):
        board = chess.Board()
        before_fen, before_stack = board.fen(), list(board.move_stack)
        for algo in (make_minimax_ai(), make_basic_ai(), AlphaBetaAI()):
            move = algo.search(board, 2)
            self.assertIn(move, board.legal_moves)
            self.assertEqual(board.fen(), before_fen)
            self.assertEqual(board.move_stack, before_stack)

    def test_default_api(self):
        board = chess.Board()
        self.assertIn(search(board, 1), board.legal_moves)
        self.assertIn(get_move(board), board.legal_moves)

    def test_already_mated_returns_none(self):
        board = chess.Board("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1")
        self.assertTrue(board.is_checkmate())
        self.assertIsNone(AlphaBetaAI().search(board, 3))

    def test_stalemate_returns_none(self):
        board = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        self.assertTrue(board.is_stalemate())
        self.assertIsNone(AlphaBetaAI().search(board, 3))

    def test_depth_limit(self):
        with self.assertRaises(ValueError):
            AlphaBetaAI().search(chess.Board(), 0)

    def test_minimax_and_alpha_beta_same_score(self):
        boards = [chess.Board(),
                  chess.Board("r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4")]
        for board in boards:
            before = board.fen()
            for depth in (1, 2, 3):
                minimax = make_minimax_ai()
                ab = make_basic_ai()
                minimax.search(board, depth)
                ab.search(board, depth)
                self.assertAlmostEqual(minimax.last_score, ab.last_score)
                self.assertLessEqual(ab.stats.nodes, minimax.stats.nodes)
                self.assertEqual(before, board.fen())

    def test_evaluation_is_from_side_to_move(self):
        board = chess.Board()
        self.assertEqual(evaluate(board), 0.0)
        board.remove_piece_at(chess.D8)  # Black loses the queen.
        board.turn = chess.WHITE
        self.assertGreater(evaluate(board), 0)
        board.turn = chess.BLACK
        self.assertLess(evaluate(board), 0)

    def test_custom_evaluator_is_used(self):
        call_count = [0]

        def evaluator(board):
            call_count[0] += 1
            return 0.25

        ai = AlphaBetaAI(evaluator=evaluator, quiescence=False)
        ai.search(chess.Board(), 1)
        self.assertGreater(call_count[0], 0)

    def test_quiescence_in_check_is_safe(self):
        board = chess.Board("4k3/8/8/8/8/8/4r3/4K3 w - - 0 1")
        self.assertTrue(board.is_check())
        before = board.fen()
        ai = AlphaBetaAI(qdepth=0)
        move = ai.search(board, 1)
        self.assertIn(move, board.legal_moves)
        self.assertEqual(before, board.fen())


if __name__ == "__main__":
    unittest.main()
