"""Kiểm thử Connect Four và khả năng dùng lại MCTS.
Chạy: python -m unittest -v test_connect_four.py
"""
import unittest
from connect_four import ConnectFourState
from mcts import MCTSAgent


def from_moves(moves):
    board = ConnectFourState()
    for move in moves:
        board = board.play(move)
    return board


class TestConnectFourRules(unittest.TestCase):
    def test_empty_board(self):
        state = ConnectFourState()
        self.assertEqual(state.legal_moves(), list(range(7)))
        self.assertEqual(state.current_player, 'X')
        self.assertFalse(state.is_terminal())
        self.assertIsNone(state.winner())

    def test_gravity_and_immutability(self):
        before = ConnectFourState()
        one = before.play(3)
        two = one.play(3)
        self.assertEqual(before.columns[3], ())
        self.assertEqual(one.columns[3], ('X',))
        self.assertEqual(two.columns[3], ('X', 'O'))
        self.assertEqual(two.current_player, 'X')

    def test_reject_illegal_column(self):
        board = ConnectFourState()
        for col in (-1, 7, 100):
            with self.assertRaises(ValueError):
                board.play(col)

    def test_full_column_not_legal(self):
        board = from_moves([0, 0, 0, 0, 0, 0])
        self.assertNotIn(0, board.legal_moves())
        with self.assertRaises(ValueError):
            board.play(0)

    def test_vertical_win(self):
        board = from_moves([3, 2, 3, 2, 3, 2, 3])
        self.assertTrue(board.is_terminal())
        self.assertEqual(board.winner(), 'X')
        self.assertEqual(board.reward('X'), 1.0)
        self.assertEqual(board.reward('O'), 0.0)
        self.assertEqual(board.legal_moves(), [])
        with self.assertRaises(ValueError):
            board.play(0)

    def test_horizontal_win(self):
        board = from_moves([0, 6, 1, 6, 2, 5, 3])
        self.assertTrue(board.is_terminal())
        self.assertEqual(board.winner(), 'X')

    def test_diagonal_rising_win(self):
        # Độ cao tính từ đáy. Tạo trạng thái kiểm tra có X ở (0,0),(1,1),(2,2),(3,3).
        board = ConnectFourState((
            ('X',), ('O', 'X'), ('O', 'O', 'X'), ('O', 'O', 'O', 'X'), (), (), ()
        ), 'O')
        self.assertEqual(board.winner(), 'X')
        self.assertTrue(board.is_terminal())

    def test_diagonal_falling_win(self):
        board = ConnectFourState((
            ('O', 'O', 'O', 'X'), ('O', 'O', 'X'), ('O', 'X'), ('X',), (), (), ()
        ), 'O')
        self.assertEqual(board.winner(), 'X')

    def test_reward_not_available_before_terminal(self):
        with self.assertRaises(ValueError):
            ConnectFourState().reward('X')

    def test_reject_wrong_shapes(self):
        with self.assertRaises(ValueError):
            ConnectFourState(((),) * 6)
        with self.assertRaises(ValueError):
            ConnectFourState((('X',) * 7,) + ((),) * 6)


class TestMCTSConnectFour(unittest.TestCase):
    def test_mcts_returns_legal_move(self):
        board = ConnectFourState()
        agent = MCTSAgent(simulations=60, seed=42)
        move = agent.get_move(board)
        self.assertIn(move, board.legal_moves())
        self.assertEqual(sum(agent.last_stats.visits_by_move.values()), 60)

    def test_mcts_can_win_immediately(self):
        board = from_moves([3, 2, 3, 2, 3, 4])
        agent = MCTSAgent(simulations=1200, seed=42)
        self.assertEqual(agent.get_move(board), 3)

    def test_mcts_blocks_threat(self):
        board = from_moves([0, 1, 2, 1, 4, 1])
        agent = MCTSAgent(simulations=1400, seed=7)
        self.assertEqual(agent.get_move(board), 1)


if __name__ == '__main__':
    unittest.main()
