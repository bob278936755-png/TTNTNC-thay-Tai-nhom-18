"""Cơ động: số ô mà Mã, Tượng, Xe, Hậu kiểm soát được (không tính ô quân mình)."""
import chess

MOBILITY_WEIGHT = 0.03  # đơn vị Tốt trên mỗi ô

_PIECES = (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)


def _side_mobility(board: chess.Board, color: chess.Color) -> int:
    own = board.occupied_co[color]
    count = 0
    for piece_type in _PIECES:
        for sq in board.pieces(piece_type, color):
            count += chess.popcount(board.attacks_mask(sq) & ~own)
    return count


def mobility_score(board: chess.Board) -> float:
    """Điểm cơ động (Trắng - Đen), đơn vị Tốt."""
    diff = _side_mobility(board, chess.WHITE) - _side_mobility(board, chess.BLACK)
    return MOBILITY_WEIGHT * diff
