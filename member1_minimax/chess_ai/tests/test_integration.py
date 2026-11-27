import sys
from pathlib import Path
import chess
import pytest

from chess_minimax import minimax, search as minimax_search

# ROOT_DIR trỏ tới thư mục gốc TTNTNC-thay-Tai-nhom-18
ROOT_DIR = Path(__file__).resolve().parents[3]
MEMBER2_DIR = ROOT_DIR / "member2_alpha_beta"

alpha_beta_files = list(MEMBER2_DIR.rglob("alpha_beta.py"))
if alpha_beta_files:
    alpha_beta_dir = str(alpha_beta_files[0].parent)
    if alpha_beta_dir not in sys.path:
        sys.path.insert(0, alpha_beta_dir)

try:
    from alpha_beta import search as alphabeta_search  # type: ignore
except ImportError:
    alphabeta_search = None


# Các thế có nước đi tối ưu DUY NHẤT -> bắt buộc trùng đúng nước đi
TACTICAL_FENS = [
    "6k1/5ppp/8/8/8/8/8/4R1K1 w - - 0 1",  # Mate in 1 Trắng (e1e8)
    "4r1k1/8/8/8/8/8/5PPP/6K1 b - - 0 1",  # Mate in 1 Đen (e8e1)
    "4k3/8/8/3q4/8/8/8/3RK3 w - - 0 1",   # Ăn Hậu miễn phí (d1d5)
]

# Các thế khai cuộc / trung cuộc có nhiều nước đồng điểm vật chất -> so sánh điểm MiniMax
GENERAL_FENS = [
    chess.STARTING_FEN,
    "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    "r2q1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 4 7",
]


def _minimax_value_of_move(board: chess.Board, move: chess.Move, depth: int) -> float:
    """Tính điểm MiniMax của một nước đi cụ thể ở độ sâu depth."""
    white = board.turn == chess.WHITE
    b = board.copy()
    b.push(move)
    return minimax(b, depth - 1, not white)


@pytest.mark.skipif(
    alphabeta_search is None,
    reason="Chưa tích hợp module Alpha-Beta của Thành viên 2",
)
@pytest.mark.parametrize("fen", TACTICAL_FENS)
@pytest.mark.parametrize("depth", [2, 3])
def test_minimax_matches_alphabeta_tactical(fen, depth):
    board = chess.Board(fen)
    move_mm = minimax_search(board.copy(), depth=depth)
    move_ab = alphabeta_search(board.copy(), depth=depth)

    assert move_mm == move_ab


@pytest.mark.skipif(
    alphabeta_search is None,
    reason="Chưa tích hợp module Alpha-Beta của Thành viên 2",
)
@pytest.mark.parametrize("fen", GENERAL_FENS)
@pytest.mark.parametrize("depth", [2, 3])
def test_minimax_matches_alphabeta_score(fen, depth):
    board = chess.Board(fen)
    move_mm = minimax_search(board.copy(), depth=depth)
    move_ab = alphabeta_search(board.copy(), depth=depth)

    assert move_mm in board.legal_moves
    assert move_ab in board.legal_moves

    score_mm = _minimax_value_of_move(board, move_mm, depth)
    score_ab = _minimax_value_of_move(board, move_ab, depth)
    assert score_mm == pytest.approx(score_ab, abs=1e-6)