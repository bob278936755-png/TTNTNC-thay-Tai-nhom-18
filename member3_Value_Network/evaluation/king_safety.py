"""An toàn Vua: lá chắn Tốt và áp lực địch quanh Vua (chỉ quan trọng ở trung cuộc)."""
import chess

from .material import game_phase

SHIELD_WEIGHT = 0.15       # mỗi Tốt chắn trực tiếp
SHIELD_FAR_FACTOR = 0.5    # Tốt chắn cách 2 hàng tính nửa điểm
ATTACK_PENALTY = 0.10      # mỗi lượt địch tấn công vào vùng quanh Vua


def _side_safety(board: chess.Board, color: chess.Color) -> float:
    king_sq = board.king(color)
    if king_sq is None:
        return 0.0
    king_file = chess.square_file(king_sq)
    king_rank = chess.square_rank(king_sq)
    forward = 1 if color == chess.WHITE else -1

    shield = 0.0
    for df in (-1, 0, 1):
        f = king_file + df
        if not 0 <= f <= 7:
            continue
        for step in (1, 2):
            r = king_rank + forward * step
            if not 0 <= r <= 7:
                break
            piece = board.piece_at(chess.square(f, r))
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                shield += 1.0 if step == 1 else SHIELD_FAR_FACTOR
                break

    zone = chess.BB_KING_ATTACKS[king_sq] | chess.BB_SQUARES[king_sq]
    attacks = 0
    for sq in chess.scan_forward(zone):
        attacks += len(board.attackers(not color, sq))

    return SHIELD_WEIGHT * shield - ATTACK_PENALTY * attacks


def king_safety_score(board: chess.Board) -> float:
    """Điểm an toàn Vua (Trắng - Đen), đơn vị Tốt, giảm dần về 0 ở tàn cuộc."""
    diff = _side_safety(board, chess.WHITE) - _side_safety(board, chess.BLACK)
    return game_phase(board) * diff
