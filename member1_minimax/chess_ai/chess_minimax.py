import chess

PIECE_VALUE = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}
MAX_MATERIAL = 39.0  # 8*1 + 2*3 + 2*3 + 2*5 + 1*9
MATE = 1000
NODES = 0


def material(board: chess.Board) -> int:
    """Điểm vật chất theo góc nhìn Trắng (hàm tạm, TV3 sẽ thay thế)."""
    s = 0
    for piece, v in PIECE_VALUE.items():
        s += v * (
            len(board.pieces(piece, chess.WHITE))
            - len(board.pieces(piece, chess.BLACK))
        )
    return s


def evaluate(board: chess.Board) -> float:
    """Đánh giá thế cờ trong [-1.0, 1.0] theo góc nhìn bên đang đi."""
    if board.is_checkmate():
        return -1.0
    if board.is_game_over(claim_draw=True):
        return 0.0

    raw = material(board) / MAX_MATERIAL
    score = max(-1.0, min(1.0, raw))
    return score if board.turn == chess.WHITE else -score


def minimax(board: chess.Board, depth: int, maximizing: bool) -> float:
    global NODES
    NODES += 1

    if board.is_checkmate():  # kiểm tra TRƯỚC depth == 0
        # Bên đang đến lượt bị chiếu hết. Cộng depth để ưu tiên chiếu hết SỚM.
        return -(MATE + depth) if maximizing else (MATE + depth)
    if board.is_game_over(claim_draw=True):  # hết nước đi, thiếu quân, lặp thế, 50 nước
        return 0
    if depth == 0:
        return material(board)

    best = -float("inf") if maximizing else float("inf")
    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, not maximizing)
        board.pop()
        best = max(best, score) if maximizing else min(best, score)
    return best


def best_move(board: chess.Board, depth: int) -> chess.Move | None:
    global NODES
    NODES = 0

    white = board.turn == chess.WHITE  # Trắng là Max, Đen là Min
    best, best_score = None, None
    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, not white)
        board.pop()
        if best_score is None or (score > best_score if white else score < best_score):
            best, best_score = move, score
    return best


def search(board: chess.Board, depth: int = 3) -> chess.Move | None:
    """Giao diện tìm kiếm thống nhất theo hợp đồng nhóm."""
    return best_move(board, depth)


def get_move(board: chess.Board) -> chess.Move | None:
    """Giao diện đối đầu chuẩn (mốc cơ sở MiniMax depth 3 cho Tuần 4)."""
    return search(board, depth=3)