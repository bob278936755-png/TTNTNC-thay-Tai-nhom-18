"""Hàm đánh giá thủ công: ghép 5 yếu tố bằng trọng số.

1. Vật chất            2. Piece-square tables
3. An toàn Vua         4. Cơ động            5. Cấu trúc Tốt
"""
import chess

from .king_safety import king_safety_score
from .material import material_balance, normalize
from .mobility import mobility_score
from .pawn_structure import pawn_structure_score
from .pst import pst_score

WEIGHTS = {
    "material": 1.0,
    "pst": 1.0,
    "king_safety": 1.0,
    "mobility": 1.0,
    "pawn_structure": 1.0,
}

_FEATURES = {
    "material": material_balance,
    "pst": pst_score,
    "king_safety": king_safety_score,
    "mobility": mobility_score,
    "pawn_structure": pawn_structure_score,
}


def evaluation_breakdown(board: chess.Board) -> dict:
    """Điểm từng yếu tố (Trắng - Đen, đơn vị Tốt, đã nhân trọng số). Dùng cho báo cáo/debug."""
    return {name: WEIGHTS[name] * fn(board) for name, fn in _FEATURES.items()}


def evaluate(board: chess.Board) -> float:
    """Điểm thế cờ trong [-1, 1] từ góc nhìn bên đang đi.

    -1.0: bên đang đi bị chiếu hết; 0.0: hòa (hết nước đi không bị chiếu / thiếu quân).
    """
    if board.is_checkmate():
        return -1.0
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0

    white_score = sum(evaluation_breakdown(board).values())
    side_score = white_score if board.turn == chess.WHITE else -white_score
    return normalize(side_score)
