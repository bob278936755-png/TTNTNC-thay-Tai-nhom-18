"""Run: python -m unittest -v test_chess_extended.py"""
import csv
import tempfile
import unittest
from pathlib import Path

import chess
from chess_puct import choose_puct_move, normalize_policy
from chess_selfplay import play_self_game, save_selfplay_csv


class AdvancedChessTests(unittest.TestCase):
    def test_policy_normalization(self):
        p = normalize_policy({'e2e4': 5.0, 'd2d4': -1.0, 'g1f3': float('nan')},
                             ['e2e4', 'd2d4', 'g1f3'])
        self.assertAlmostEqual(sum(p.values()), 1.0)
        self.assertEqual(p['e2e4'], 1.0)
        self.assertEqual(p['d2d4'], 0.0)

    def test_policy_fallback(self):
        p = normalize_policy({}, ['e2e4', 'd2d4'])
        self.assertEqual(p, {'e2e4': 0.5, 'd2d4': 0.5})

    def test_puct_legal_and_immutable(self):
        board = chess.Board()
        fen = board.fen()
        move, stats = choose_puct_move(board, simulations=5, max_tree_depth=3)
        self.assertIn(move, board.legal_moves)
        self.assertEqual(board.fen(), fen)
        self.assertEqual(sum(stats.visits_by_move.values()), 5)
        self.assertAlmostEqual(sum(stats.policy_by_move.values()), 1.0)

    def test_network_callback_forced_prior(self):
        board = chess.Board()
        def net(b):
            return {'e2e4': 1.0}, 0.0
        move, stats = choose_puct_move(board, simulations=1, policy_value_fn=net)
        self.assertEqual(move.uci(), 'e2e4')
        self.assertAlmostEqual(stats.policy_by_move['e2e4'], 1.0)

    def test_bad_value_fails(self):
        with self.assertRaises(ValueError):
            choose_puct_move(chess.Board(), simulations=1,
                             policy_value_fn=lambda b: ({}, 1.5))

    def test_check_position_still_legal(self):
        board = chess.Board('4k3/8/8/8/8/8/4r3/4K3 w - - 0 1')
        self.assertTrue(board.is_check())
        move, _ = choose_puct_move(board, simulations=5, max_tree_depth=3)
        self.assertIn(move, board.legal_moves)

    def test_promotion_possible(self):
        board = chess.Board('7k/P7/8/8/8/8/8/K7 w - - 0 1')
        def net(b):
            return {'a7a8q': 100.0}, 0.0
        move, _ = choose_puct_move(board, simulations=1, policy_value_fn=net)
        self.assertEqual(move.uci(), 'a7a8q')

    def test_terminal_board_rejected(self):
        board = chess.Board()
        for move in ('f2f3','e7e5','g2g4','d8h4'):
            board.push_uci(move)
        self.assertTrue(board.is_checkmate())
        with self.assertRaises(ValueError):
            choose_puct_move(board)

    def test_selfplay_does_not_fake_draw(self):
        game = play_self_game(simulations=1, max_plies=2, max_tree_depth=2)
        self.assertFalse(game.finished_by_rules)
        self.assertEqual(game.result, '*')
        self.assertTrue(all(step.value_target is None for step in game.steps))
        self.assertEqual(len(game.steps), 2)

    def test_csv_selfplay(self):
        game = play_self_game(simulations=1, max_plies=1, max_tree_depth=2)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'sample.csv'
            save_selfplay_csv(game, path)
            with path.open(encoding='utf-8-sig', newline='') as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['game_result'], '*')
            self.assertEqual(rows[0]['value_target'], '')


if __name__ == '__main__':
    unittest.main()
