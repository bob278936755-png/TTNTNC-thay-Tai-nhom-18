"""Pipeline thu thập & tiền xử lý dữ liệu huấn luyện Value Network.

Ba nguồn dữ liệu (theo thứ tự ưu tiên triển khai):
  1. ``generate_synthetic_data``  — dữ liệu tổng hợp từ ván chơi ngẫu nhiên,
     dán nhãn bằng hàm heuristic Tuần 1.  Dùng để kiểm thử pipeline ngay lập tức.
  2. ``load_pgn_data``  — đọc file PGN từ Lichess, lấy kết quả ván đấu làm nhãn.
  3. ``load_stockfish_data``  — dùng Stockfish chấm centipawn cho mỗi thế cờ
     (chính xác nhất nhưng tốn thời gian, chạy offline).

Tất cả đều trả về ``(X, y)`` với:
  - ``X``: mảng ``np.float32`` shape ``(N, 8, 8, 12)``
  - ``y``: mảng ``np.float32`` shape ``(N, 1)``  — giá trị trong [-1, 1]
"""
import os
import random

import chess
import chess.pgn
import numpy as np

from .encoding import board_to_tensor, centipawns_to_target
from .handcrafted import evaluate as heuristic_evaluate


# ---------------------------------------------------------------------------
# 1. Dữ liệu tổng hợp (Synthetic) — sẵn sàng ngay, không cần file ngoài
# ---------------------------------------------------------------------------

def generate_synthetic_data(
    num_games: int = 200,
    max_plies: int = 60,
    sample_every: int = 2,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Tạo dữ liệu tổng hợp bằng cách chơi ngẫu nhiên rồi dán nhãn heuristic.

    Parameters
    ----------
    num_games : int
        Số ván chơi ngẫu nhiên.
    max_plies : int
        Số nước đi tối đa mỗi ván.
    sample_every : int
        Lấy mẫu mỗi ``sample_every`` nước để tránh các thế cờ quá tương đồng.
    seed : int
        Hạt giống bộ sinh ngẫu nhiên (tái lập kết quả).

    Returns
    -------
    X : np.ndarray  shape (N, 8, 8, 12)
    y : np.ndarray  shape (N, 1)
    """
    rng = random.Random(seed)
    tensors: list[np.ndarray] = []
    targets: list[float] = []

    for _ in range(num_games):
        board = chess.Board()
        ply = 0
        while ply < max_plies:
            moves = list(board.legal_moves)
            if not moves or board.is_game_over():
                break
            board.push(rng.choice(moves))
            ply += 1

            if ply % sample_every == 0:
                tensors.append(board_to_tensor(board))
                targets.append(heuristic_evaluate(board))

    X = np.array(tensors, dtype=np.float32)
    y = np.array(targets, dtype=np.float32).reshape(-1, 1)
    return X, y


# ---------------------------------------------------------------------------
# 2. Dữ liệu PGN từ Lichess / FICS / CCRL
# ---------------------------------------------------------------------------

def load_pgn_data(
    pgn_path: str,
    max_games: int = 500,
    sample_every: int = 4,
) -> tuple[np.ndarray, np.ndarray]:
    """Đọc file PGN và lấy nhãn từ kết quả ván đấu (1-0 / 0-1 / 1/2-1/2).

    Với mỗi thế cờ trung cuộc, nhãn là:
      +1.0 nếu bên đang đi thắng ván đó,
      -1.0 nếu thua,
       0.0 nếu hòa.
    """
    result_map = {"1-0": 1.0, "0-1": -1.0, "1/2-1/2": 0.0}
    tensors: list[np.ndarray] = []
    targets: list[float] = []

    with open(pgn_path, encoding="utf-8", errors="replace") as pgn_file:
        game_count = 0
        while game_count < max_games:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            result_str = game.headers.get("Result", "*")
            if result_str not in result_map:
                continue
            result_white = result_map[result_str]
            game_count += 1

            board = game.board()
            ply = 0
            for move in game.mainline_moves():
                board.push(move)
                ply += 1
                if ply < 10 or ply % sample_every != 0:
                    continue
                tensors.append(board_to_tensor(board))
                v = result_white if board.turn == chess.WHITE else -result_white
                targets.append(v)

    X = np.array(tensors, dtype=np.float32) if tensors else np.empty((0, 8, 8, 12), dtype=np.float32)
    y = np.array(targets, dtype=np.float32).reshape(-1, 1)
    return X, y


# ---------------------------------------------------------------------------
# 3. Data Augmentation: lật bàn cờ theo trục dọc (a↔h)
# ---------------------------------------------------------------------------

def augment_horizontal_flip(
    X: np.ndarray, y: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Nhân đôi dữ liệu bằng phản xạ gương qua trục dọc.

    Giá trị thế cờ V(s) không đổi khi lật cột a↔h vì cờ vua
    gần đối xứng qua trục giữa (ngoại trừ nhập thành).
    """
    X_flip = np.flip(X, axis=2).copy()     # lật trục cột (file)
    X_aug = np.concatenate([X, X_flip], axis=0)
    y_aug = np.concatenate([y, y], axis=0)

    idx = np.arange(len(X_aug))
    np.random.shuffle(idx)
    return X_aug[idx], y_aug[idx]
