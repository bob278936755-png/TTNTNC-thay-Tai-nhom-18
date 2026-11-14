import chess

PIECE_VALUE = {chess.PAWN:1, chess.KNIGHT:3, chess.BISHOP:3,
               chess.ROOK:5, chess.QUEEN:9, chess.KING:0}
MATE = 1000
NODES = 0

def material(board):
    """Điểm vật chất theo góc nhìn Trắng (hàm tạm, TV3 sẽ thay thế)."""
    s = 0
    for piece, v in PIECE_VALUE.items():
        s += v * (len(board.pieces(piece, chess.WHITE))
                  - len(board.pieces(piece, chess.BLACK)))
    return s

def minimax(board, depth, maximizing):
    global NODES
    NODES += 1
    if board.is_checkmate():                      # kiểm tra TRƯỚC depth == 0
        # Bên đang đến lượt bị chiếu hết. Cộng depth để ưu tiên chiếu hết SỚM.
        return -(MATE + depth) if maximizing else (MATE + depth)
    if board.is_game_over():                      # hết nước đi, thiếu quân, lặp thế...
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

def best_move(board, depth):
    white = board.turn == chess.WHITE             # Trắng là Max, Đen là Min
    best, best_score = None, None
    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, not white)
        board.pop()
        if best_score is None or (score > best_score if white else score < best_score):
            best, best_score = move, score
    return best