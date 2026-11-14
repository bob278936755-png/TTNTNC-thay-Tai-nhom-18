import random

import chess
import pytest

from evaluation import evaluate
from evaluation.material import material_balance


def random_positions(n_games=15, max_plies=80, seed=0):
    rng = random.Random(seed)
    boards = []
    for _ in range(n_games):
        b = chess.Board()
        for _ in range(rng.randint(0, max_plies)):
            moves = list(b.legal_moves)
            if not moves:
                break
            b.push(rng.choice(moves))
            boards.append(b.copy(stack=False))
    return boards


POSITIONS = random_positions()


def test_start_position_is_balanced():
    assert evaluate(chess.Board()) == pytest.approx(0.0, abs=1e-9)


def test_checkmate_is_minus_one_for_side_to_move():
    b = chess.Board()
    for san in ("f3", "e5", "g4", "Qh4#"):
        b.push_san(san)
    assert b.is_checkmate()
    assert evaluate(b) == -1.0


def test_stalemate_and_insufficient_material_are_draws():
    stalemate = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    assert stalemate.is_stalemate()
    assert evaluate(stalemate) == 0.0
    assert evaluate(chess.Board("8/8/8/4k3/8/8/4K3/8 w - - 0 1")) == 0.0


def test_range_is_within_minus_one_and_one():
    assert len(POSITIONS) > 100
    for b in POSITIONS:
        assert -1.0 <= evaluate(b) <= 1.0


def test_mirror_gives_same_score():
    """mirror() đổi màu quân VÀ lượt đi -> điểm góc nhìn bên đang đi phải bằng nhau."""
    for b in POSITIONS:
        assert evaluate(b) == pytest.approx(evaluate(b.mirror()), abs=1e-9)


def test_flip_colors_keep_turn_negates_score():
    """Đổi màu quân nhưng giữ nguyên lượt đi -> điểm đổi dấu (evaluate(thế) = -evaluate(thế lật màu))."""
    checked = 0
    for b in POSITIONS:
        if b.is_game_over():
            continue
        flipped = b.mirror()
        flipped.turn = not flipped.turn
        if flipped.is_game_over() or flipped.is_check():
            continue
        assert evaluate(b) == pytest.approx(-evaluate(flipped), abs=1e-9)
        checked += 1
    assert checked > 50


def test_extra_queen_is_clearly_better():
    b = chess.Board("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    assert material_balance(b) == 9.0
    assert evaluate(b) > 0.5
    b.turn = chess.BLACK
    assert evaluate(b) < -0.5  # bên đang đi (Đen) thua Hậu


def test_good_structure_beats_bad_structure():
    good = chess.Board("4k3/pppp4/8/8/8/8/PPPP4/4K3 w - - 0 1")
    bad = chess.Board("4k3/pppp4/8/8/8/P7/P2P2P1/4K3 w - - 0 1")  # Tốt chồng + cô lập
    assert evaluate(good) > evaluate(bad)
