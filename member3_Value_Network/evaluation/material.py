"""Vật chất (1/3/3/5/9) và các hàm tiện ích dùng chung."""
import math
import chess

PIECE_VALUES = {
    chess.PAWN: 1.0,
    chess.KNIGHT: 3.0,
    chess.BISHOP: 3.0,
    chess.ROOK: 5.0,
    chess.QUEEN: 9.0,
}

# Tổng giá trị quân (không tính Tốt) của hai bên ở thế khai cuộc: 2 * 31
_MAX_NON_PAWN = 62.0

# tanh(x / K): chênh 4 Tốt ~ 0.76
NORMALIZE_K = 4.0


def material_balance(board: chess.Board) -> float:
    """Chênh lệch vật chất (Trắng - Đen), đơn vị Tốt."""
    total = 0.0
    for piece_type, value in PIECE_VALUES.items():
        white = len(board.pieces(piece_type, chess.WHITE))
        black = len(board.pieces(piece_type, chess.BLACK))
        total += value * (white - black)
    return total


def game_phase(board: chess.Board) -> float:
    """1.0 = trung cuộc (nhiều quân), 0.0 = tàn cuộc (ít quân)."""
    non_pawn = 0.0
    for piece_type, value in PIECE_VALUES.items():
        if piece_type == chess.PAWN:
            continue
        non_pawn += value * (
            len(board.pieces(piece_type, chess.WHITE))
            + len(board.pieces(piece_type, chess.BLACK))
        )
    return min(1.0, non_pawn / _MAX_NON_PAWN)


def normalize(score: float, k: float = NORMALIZE_K) -> float:
    """Ép điểm (đơn vị Tốt) về [-1, 1] bằng tanh."""
    return max(-1.0, min(1.0, math.tanh(score / k)))


def material_eval(board: chess.Board) -> float:
    """Chỉ riêng vật chất, chuẩn hóa, góc nhìn bên đang đi."""
    score = material_balance(board)
    if board.turn == chess.BLACK:
        score = -score
    return normalize(score)
