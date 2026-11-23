from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, tanh
from typing import Callable

try:
    import chess
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Can cai python-chess: python -m pip install python-chess"
    ) from exc

from mcts import MCTSAgent, SearchStats

ValueFn = Callable[[chess.Board, str], float]

# Gia tri quan de luong gia do neu rollout chua ket thuc.
PIECE_VALUES = {
    chess.PAWN: 1.0,
    chess.KNIGHT: 3.0,
    chess.BISHOP: 3.0,
    chess.ROOK: 5.0,
    chess.QUEEN: 9.0,
    chess.KING: 0.0,
}


def material_value(board: chess.Board, player: str) -> float:
    """Gia tri [-1, 1] cua trang thai theo player; khong phai engine co vua."""
    if player not in ("W", "B"):
        raise ValueError("player phai la 'W' hoac 'B'.")
    diff = 0.0
    for piece_type, value in PIECE_VALUES.items():
        diff += value * (
            len(board.pieces(piece_type, chess.WHITE))
            - len(board.pieces(piece_type, chess.BLACK))
        )
    if player == "B":
        diff = -diff
    return tanh(diff / 8.0)


@dataclass
class ChessState:
    board: chess.Board
    remaining_plies: int = 48
    value_fn: ValueFn = material_value

    def __post_init__(self):
        if self.remaining_plies < 0:
            raise ValueError("remaining_plies khong duoc am.")

    @property
    def current_player(self) -> str:
        return "W" if self.board.turn == chess.WHITE else "B"

    def is_terminal(self) -> bool:
        # Gioi han rollout la diem dung *danh gia*, khong phai vong co ket thuc.
        return self.board.is_game_over(claim_draw=True) or self.remaining_plies == 0

    def legal_moves(self) -> list[str]:
        if self.is_terminal():
            return []
        return [move.uci() for move in self.board.legal_moves]

    def play(self, move: str) -> "ChessState":
        if self.is_terminal():
            raise ValueError("Khong the di tiep tu trang thai da ket thuc.")
        try:
            parsed = chess.Move.from_uci(move)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"UCI khong hop le: {move}") from exc
        if parsed not in self.board.legal_moves:
            raise ValueError(f"Nuoc di khong hop le: {move}")
        new_board = self.board.copy(stack=True)
        new_board.push(parsed)
        return ChessState(new_board, self.remaining_plies - 1, self.value_fn)

    def reward(self, player: str) -> float:
        """Diem [0,1]: thang=1, hoa=.5, thua=0, chua xong thi luong gia."""
        if player not in ("W", "B"):
            raise ValueError("player phai la 'W' hoac 'B'.")
        if not self.is_terminal():
            raise ValueError("Chi danh gia khi game ket thuc hoac het gioi han rollout.")
        outcome = self.board.outcome(claim_draw=True)
        if outcome is not None:
            if outcome.winner is None:
                return 0.5
            winning_player = "W" if outcome.winner == chess.WHITE else "B"
            return 1.0 if player == winning_player else 0.0
        value = float(self.value_fn(self.board, player))
        if not -1.0 <= value <= 1.0:
            raise ValueError("value_fn phai tra gia tri thuoc [-1, 1].")
        return (value + 1.0) / 2.0


def choose_chess_move(
    board: chess.Board,
    simulations: int = 40,
    rollout_plies: int = 48,
    seed: int | None = 42,
    exploration: float = sqrt(2),
    value_fn: ValueFn = material_value,
) -> tuple[chess.Move, SearchStats]:

    if rollout_plies < 1:
        raise ValueError("rollout_plies phai >= 1.")
    if board.is_game_over(claim_draw=True):
        raise ValueError("Van co da ket thuc.")
    state = ChessState(board.copy(stack=True), rollout_plies, value_fn)
    agent = MCTSAgent(simulations=simulations, exploration=exploration, seed=seed)
    chosen_uci = agent.get_move(state)
    move = chess.Move.from_uci(chosen_uci)
    if move not in board.legal_moves:
        raise AssertionError("MCTS dua ra nuoc di khong hop le.")
    assert agent.last_stats is not None
    return move, agent.last_stats
