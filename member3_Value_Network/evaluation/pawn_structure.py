"""Cấu trúc Tốt: Tốt chồng, Tốt cô lập, Tốt thông."""
import chess

DOUBLED_PENALTY = 0.30
ISOLATED_PENALTY = 0.25
# Thưởng Tốt thông theo hàng tương đối (0 = hàng xuất phát ... 7 = hàng phong cấp)
PASSED_BONUS = (0.0, 0.0, 0.10, 0.20, 0.40, 0.80, 1.40, 0.0)


def _side_structure(board: chess.Board, color: chess.Color) -> float:
    own = list(board.pieces(chess.PAWN, color))
    enemy = list(board.pieces(chess.PAWN, not color))
    own_files = [chess.square_file(s) for s in own]
    score = 0.0

    # Tốt chồng
    for f in set(own_files):
        n = own_files.count(f)
        if n > 1:
            score -= DOUBLED_PENALTY * (n - 1)

    for sq in own:
        f = chess.square_file(sq)
        r = chess.square_rank(sq)

        # Tốt cô lập: không có Tốt mình ở hai cột kề
        if (f - 1) not in own_files and (f + 1) not in own_files:
            score -= ISOLATED_PENALTY

        # Tốt thông: không Tốt địch nào ở cột này/cột kề phía trước
        blocked = False
        for esq in enemy:
            if abs(chess.square_file(esq) - f) > 1:
                continue
            er = chess.square_rank(esq)
            if (color == chess.WHITE and er > r) or (color == chess.BLACK and er < r):
                blocked = True
                break
        if not blocked:
            rel_rank = r if color == chess.WHITE else 7 - r
            score += PASSED_BONUS[rel_rank]

    return score


def pawn_structure_score(board: chess.Board) -> float:
    """Điểm cấu trúc Tốt (Trắng - Đen), đơn vị Tốt."""
    return _side_structure(board, chess.WHITE) - _side_structure(board, chess.BLACK)
