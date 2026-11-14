"""Luật chơi Tic-Tac-Toe, tách biệt với thuật toán MCTS."""
from dataclasses import dataclass
from typing import Optional

WINNING_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


@dataclass(frozen=True)
class TicTacToeState:
    """Bàn cờ bất biến; lượt hiện tại luôn nằm trong current_player."""
    board: tuple[str, ...] = (' ',) * 9
    current_player: str = 'X'

    def __post_init__(self):
        if len(self.board) != 9 or any(v not in ('X', 'O', ' ') for v in self.board):
            raise ValueError('Bàn cờ phải có 9 ô, chỉ nhận X, O hoặc dấu cách.')
        if self.current_player not in ('X', 'O'):
            raise ValueError('current_player phải là X hoặc O.')

    def winner(self) -> Optional[str]:
        for a, b, c in WINNING_LINES:
            if self.board[a] != ' ' and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def is_terminal(self) -> bool:
        return self.winner() is not None or ' ' not in self.board

    def legal_moves(self) -> list[int]:
        if self.is_terminal():
            return []
        return [i for i, v in enumerate(self.board) if v == ' ']

    def play(self, move: int) -> 'TicTacToeState':
        if move not in self.legal_moves():
            raise ValueError(f'Nước đi không hợp lệ: {move}')
        new_board = list(self.board)
        new_board[move] = self.current_player
        next_player = 'O' if self.current_player == 'X' else 'X'
        return TicTacToeState(tuple(new_board), next_player)

    def reward(self, player: str) -> float:
        """Giá trị cuối ván theo góc nhìn player: thắng=1, hòa=0.5, thua=0."""
        if not self.is_terminal():
            raise ValueError('Chưa thể đánh giá thưởng khi ván chưa kết thúc.')
        winner = self.winner()
        if winner is None:
            return 0.5
        return 1.0 if winner == player else 0.0

    def show(self) -> str:
        labels = [v if v != ' ' else str(i) for i, v in enumerate(self.board)]
        return '\n---+---+---\n'.join(
            ' ' + ' | '.join(labels[i:i + 3]) for i in (0, 3, 6)
        )
