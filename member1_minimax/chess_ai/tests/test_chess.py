import chess
import pytest
import chess_minimax as cm

best_move, minimax, material = cm.best_move, cm.minimax, cm.material


def mv(uci):
    return chess.Move.from_uci(uci)


def test_loaded_the_right_module():
    assert "chess_minimax" in cm.__file__


def test_material_start_position_is_zero():
    assert material(chess.Board()) == 0


def test_mate_in_one():
    b = chess.Board("6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1")
    assert best_move(b, 1) == mv("a1a8")


def test_takes_free_queen():
    b = chess.Board("4k3/8/8/3q4/8/8/8/3RK3 w - - 0 1")
    assert best_move(b, 2) == mv("d1d5")


def test_black_takes_free_queen():
    b = chess.Board("3rk3/8/8/3Q4/8/8/8/4K3 b - - 0 1")
    assert best_move(b, 2) == mv("d8d5")


def test_checkmate_score():
    b = chess.Board()
    for san in ["f3", "e5", "g4", "Qh4#"]:
        b.push_san(san)
    assert minimax(b, 0, True) == -cm.MATE


def test_stalemate_is_zero():
    b = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    assert minimax(b, 3, False) == 0


@pytest.mark.parametrize("fen", [
    chess.STARTING_FEN,
    "6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1",
])
def test_best_move_is_always_legal(fen):
    b = chess.Board(fen)
    assert best_move(b, 2) in b.legal_moves


def test_search_leaves_board_unchanged():
    b = chess.Board()
    fen = b.fen()
    best_move(b, 3)
    assert b.fen() == fen


@pytest.mark.parametrize("depth, expected", [(1, 20), (2, 420), (3, 9322)])
def test_node_count(depth, expected):
    cm.NODES = 0
    best_move(chess.Board(), depth)
    assert cm.NODES == expected