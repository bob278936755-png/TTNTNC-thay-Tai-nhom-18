"""Luật Connect Four (4 quân liên tiếp), dùng chung mcts.MCTSAgent.

Bàn cờ gồm 7 cột x 6 hàng. Mỗi cột là tuple quân tính từ ĐÁY LÊN.
Nước đi là số cột 0..6. Trạng thái bất biến, không cần thư viện ngoài.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

COLS = 7
ROWS = 6
DIRECTIONS = ((1, 0), (0, 1), (1, 1), (1, -1))


@dataclass(frozen=True)
class ConnectFourState:
    columns: tuple[tuple[str, ...], ...] = ((),) * COLS
    current_player: str = 'X'
    # (cột, độ cao tính từ đáy) của nước vừa đi; giúp dò thắng nhanh hơn.
    last_move: tuple[int, int] | None = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        if len(self.columns) != COLS:
            raise ValueError(f'Bàn cờ phải gồm {COLS} cột.')
        if any(len(col) > ROWS or any(token not in ('X', 'O') for token in col)
               for col in self.columns):
            raise ValueError('Mỗi cột tối đa 6 quân, mỗi quân là X hoặc O.')
        if self.current_player not in ('X', 'O'):
            raise ValueError('current_player phải là X hoặc O.')
        if self.last_move is not None:
            col, height = self.last_move
            if not (0 <= col < COLS and 0 <= height < len(self.columns[col])):
                raise ValueError('last_move nằm ngoài các ô đã đánh.')

    def _piece(self, col: int, height: int) -> str | None:
        if 0 <= col < COLS and 0 <= height < len(self.columns[col]):
            return self.columns[col][height]
        return None

    def _has_four_through(self, col: int, height: int) -> bool:
        token = self._piece(col, height)
        if token is None:
            return False
        for dc, dh in DIRECTIONS:
            count = 1
            for sign in (-1, 1):
                c, h = col + sign * dc, height + sign * dh
                while self._piece(c, h) == token:
                    count += 1
                    c += sign * dc
                    h += sign * dh
            if count >= 4:
                return True
        return False

    @cached_property
    def _winner(self) -> str | None:
        if self.last_move is not None:
            col, height = self.last_move
            if self._has_four_through(col, height):
                return self.columns[col][height]
            return None
        # Hỗ trợ cả trạng thái dựng thủ công không có last_move.
        for col in range(COLS):
            for height in range(len(self.columns[col])):
                if self._has_four_through(col, height):
                    return self.columns[col][height]
        return None

    def winner(self) -> str | None:
        return self._winner

    def is_terminal(self) -> bool:
        return self.winner() is not None or all(len(col) == ROWS for col in self.columns)

    def legal_moves(self) -> list[int]:
        if self.is_terminal():
            return []
        return [col for col in range(COLS) if len(self.columns[col]) < ROWS]

    def play(self, move: int) -> 'ConnectFourState':
        if move not in self.legal_moves():
            raise ValueError(f'Nước đi không hợp lệ: {move}. Chọn cột 0..6 chưa đầy.')
        columns = list(self.columns)
        height = len(columns[move])
        columns[move] = columns[move] + (self.current_player,)
        next_player = 'O' if self.current_player == 'X' else 'X'
        return ConnectFourState(tuple(columns), next_player, (move, height))

    def reward(self, player: str) -> float:
        """Kết thúc: thắng=1, hòa=0.5, thua=0 từ góc nhìn player."""
        if player not in ('X', 'O'):
            raise ValueError('Người chơi phải là X hoặc O.')
        if not self.is_terminal():
            raise ValueError('Không thể chấm điểm khi ván chưa kết thúc.')
        winner = self.winner()
        return 0.5 if winner is None else (1.0 if winner == player else 0.0)

    def show(self) -> str:
        rows = []
        for height in range(ROWS - 1, -1, -1):
            rows.append('| ' + ' '.join(self._piece(c, height) or '.' for c in range(COLS)) + ' |')
        return '\n'.join(['  0 1 2 3 4 5 6', *rows, '  -------------'])
