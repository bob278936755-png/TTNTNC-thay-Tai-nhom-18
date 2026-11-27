"""Unit tests cho Value Network pipeline (Tuần 2-4).

Chạy:  pytest tests/ -v  (từ thư mục ``member3_Value_Network``)
"""
import random

import chess
import numpy as np
import pytest

from evaluation.encoding import board_to_tensor, centipawns_to_target
from evaluation.data_pipeline import generate_synthetic_data, augment_horizontal_flip
from evaluation.handcrafted import evaluate as heuristic_evaluate


# ======================================================================
# ENCODING
# ======================================================================

class TestEncoding:
    """Kiểm tra mã hoá bàn cờ → Tensor."""

    def test_shape(self):
        t = board_to_tensor(chess.Board())
        assert t.shape == (8, 8, 12)
        assert t.dtype == np.float32

    def test_start_position_piece_count(self):
        """Thế khai cuộc phải có đúng 32 ô = 1 (32 quân)."""
        t = board_to_tensor(chess.Board())
        assert int(t.sum()) == 32

    def test_empty_board(self):
        """Bàn cờ chỉ có 2 Vua → 2 ô = 1."""
        b = chess.Board("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
        t = board_to_tensor(b)
        assert int(t.sum()) == 2

    def test_no_overlap(self):
        """Mỗi ô chỉ có tối đa 1 quân → tối đa 1 kênh = 1 tại mỗi (row, col)."""
        t = board_to_tensor(chess.Board())
        assert t.max() == 1.0
        for r in range(8):
            for c in range(8):
                assert t[r, c].sum() <= 1.0


class TestCentipawns:
    """Kiểm tra hàm chuẩn hoá centipawn."""

    def test_zero_is_zero(self):
        assert centipawns_to_target(0.0, chess.WHITE) == pytest.approx(0.0)
        assert centipawns_to_target(0.0, chess.BLACK) == pytest.approx(0.0)

    def test_positive_cp_white(self):
        """Trắng lợi +400cp → giá trị dương khi Trắng đi."""
        v = centipawns_to_target(400.0, chess.WHITE)
        assert v > 0.5

    def test_positive_cp_black(self):
        """Trắng lợi +400cp → giá trị ÂM khi Đen đi (Đen đang bất lợi)."""
        v = centipawns_to_target(400.0, chess.BLACK)
        assert v < -0.5

    def test_range(self):
        for cp in [-2000, -500, -100, 0, 100, 500, 2000]:
            v = centipawns_to_target(cp, chess.WHITE)
            assert -1.0 <= v <= 1.0


# ======================================================================
# DATA PIPELINE
# ======================================================================

class TestDataPipeline:
    """Kiểm tra pipeline tạo dữ liệu."""

    def test_synthetic_shape(self):
        X, y = generate_synthetic_data(num_games=10, seed=0)
        assert X.ndim == 4
        assert X.shape[1:] == (8, 8, 12)
        assert y.ndim == 2
        assert y.shape[1] == 1
        assert len(X) == len(y)
        assert len(X) > 0

    def test_synthetic_range(self):
        _, y = generate_synthetic_data(num_games=20, seed=1)
        assert y.min() >= -1.0
        assert y.max() <= 1.0

    def test_augmentation_doubles(self):
        X, y = generate_synthetic_data(num_games=10, seed=2)
        n = len(X)
        X2, y2 = augment_horizontal_flip(X, y)
        assert len(X2) == 2 * n
        assert len(y2) == 2 * n

    def test_augmentation_preserves_labels(self):
        """Lật trục dọc không thay đổi nhãn."""
        X, y = generate_synthetic_data(num_games=5, seed=3)
        _, y2 = augment_horizontal_flip(X, y)
        # Tổng nhãn gốc nhân 2 phải bằng tổng nhãn augmented
        assert np.sum(y) * 2 == pytest.approx(np.sum(y2), abs=1e-5)


# ======================================================================
# HỢP ĐỒNG GIAO DIỆN (không cần TensorFlow)
# ======================================================================

class TestHeuristicContract:
    """Đảm bảo hàm heuristic Tuần 1 vẫn hoạt động đúng."""

    def test_start_balanced(self):
        assert heuristic_evaluate(chess.Board()) == pytest.approx(0.0, abs=1e-9)

    def test_range(self):
        rng = random.Random(42)
        for _ in range(50):
            b = chess.Board()
            for _ in range(rng.randint(0, 40)):
                moves = list(b.legal_moves)
                if not moves:
                    break
                b.push(rng.choice(moves))
            v = heuristic_evaluate(b)
            assert -1.0 <= v <= 1.0

    def test_checkmate(self):
        b = chess.Board()
        for san in ("f3", "e5", "g4", "Qh4#"):
            b.push_san(san)
        assert b.is_checkmate()
        assert heuristic_evaluate(b) == -1.0
