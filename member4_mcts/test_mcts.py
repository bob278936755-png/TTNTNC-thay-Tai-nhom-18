"""Chạy kiểm thử: python -m unittest -v test_mcts.py"""
import unittest
from mcts import MCTSAgent
from tictactoe import TicTacToeState


class TestTicTacToe(unittest.TestCase):
    def test_board_empty(self):
        game = TicTacToeState()
        self.assertEqual(game.legal_moves(), list(range(9)))
        self.assertFalse(game.is_terminal())
        self.assertEqual(game.current_player, 'X')

    def test_move_is_immutable_and_alternates(self):
        before = TicTacToeState()
        after = before.play(4)
        self.assertEqual(before.board[4], ' ')
        self.assertEqual(after.board[4], 'X')
        self.assertEqual(after.current_player, 'O')
        with self.assertRaises(ValueError):
            after.play(4)

    def test_win(self):
        game = TicTacToeState(('X', 'X', 'X', 'O', 'O', ' ', ' ', ' ', ' '), 'O')
        self.assertTrue(game.is_terminal())
        self.assertEqual(game.winner(), 'X')
        self.assertEqual(game.reward('X'), 1.0)
        self.assertEqual(game.reward('O'), 0.0)
        self.assertEqual(game.legal_moves(), [])

    def test_draw(self):
        game = TicTacToeState(('X', 'O', 'X', 'X', 'O', 'O', 'O', 'X', 'X'), 'O')
        self.assertTrue(game.is_terminal())
        self.assertIsNone(game.winner())
        self.assertEqual(game.reward('X'), 0.5)


class TestMCTS(unittest.TestCase):
    def test_legal_move(self):
        state = TicTacToeState()
        agent = MCTSAgent(simulations=250, seed=2)
        self.assertIn(agent.get_move(state), state.legal_moves())
        self.assertEqual(agent.last_stats.simulations, 250)
        self.assertEqual(sum(agent.last_stats.visits_by_move.values()), 250)

    def test_forced_win_one_move(self):
        state = TicTacToeState(('X', 'X', ' ', 'O', 'O', ' ', ' ', ' ', ' '), 'X')
        agent = MCTSAgent(simulations=1500, seed=42)
        self.assertEqual(agent.get_move(state), 2)

    def test_forced_block(self):
        # O đang đe dọa thắng tại ô 2, X phải chặn.
        state = TicTacToeState(('O', 'O', ' ', 'X', ' ', ' ', 'X', ' ', ' '), 'X')
        agent = MCTSAgent(simulations=2000, seed=7)
        self.assertEqual(agent.get_move(state), 2)

    def test_terminal_not_playable(self):
        state = TicTacToeState(('X', 'X', 'X', 'O', 'O', ' ', ' ', ' ', ' '), 'O')
        with self.assertRaises(ValueError):
            MCTSAgent(seed=1).get_move(state)


if __name__ == '__main__':
    unittest.main()
