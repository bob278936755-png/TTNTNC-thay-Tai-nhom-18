"""Mã hoá trạng thái bàn cờ thành Tensor đầu vào cho mạng CNN / ResNet.

Tensor kích thước  8 × 8 × 12  (12 mặt phẳng nhị phân):
  - Kênh  0..5  : Tốt, Mã, Tượng, Xe, Hậu, Vua  — quân TRẮNG
  - Kênh  6..11 : Tốt, Mã, Tượng, Xe, Hậu, Vua  — quân ĐEN

Hàng 0 ứng với rank 1 (a1..h1), hàng 7 ứng với rank 8 (a8..h8).
"""
import math

import chess
import numpy as np

# Ánh xạ kiểu quân → chỉ số kênh (0-based, offset +6 cho quân Đen)
_PLANE = {
    chess.PAWN:   0,
    chess.KNIGHT: 1,
    chess.BISHOP: 2,
    chess.ROOK:   3,
    chess.QUEEN:  4,
    chess.KING:   5,
}


def board_to_tensor(board: chess.Board) -> np.ndarray:
    """Chuyển ``chess.Board`` thành mảng ``np.float32`` kích thước (8, 8, 12)."""
    tensor = np.zeros((8, 8, 12), dtype=np.float32)
    for square, piece in board.piece_map().items():
        row = chess.square_rank(square)
        col = chess.square_file(square)
        plane = _PLANE[piece.piece_type]
        if piece.color == chess.BLACK:
            plane += 6
        tensor[row, col, plane] = 1.0
    return tensor


def centipawns_to_target(cp: float, turn: chess.Color) -> float:
    """Chuẩn hóa điểm centipawn về [-1, 1] bằng tanh, theo góc nhìn bên đang đi.

    Quy ước: ``cp`` luôn tính từ góc nhìn Trắng (dương = Trắng lợi).
    Hằng số 400 cp ≈ 4 Tốt → tanh(1) ≈ 0.76 (ưu thế rõ).
    """
    v_white = math.tanh(cp / 400.0)
    return v_white if turn == chess.WHITE else -v_white
