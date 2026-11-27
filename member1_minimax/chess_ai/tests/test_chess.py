import chess
import pytest
import chess_minimax as cm

best_move, minimax, material = cm.best_move, cm.minimax, cm.material
from chess_minimax import evaluate, get_move, search

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



def test_api_return_types():
    board = chess.Board()

    score = evaluate(board)
    assert isinstance(score, (int, float))
    assert -1.0 <= score <= 1.0

    move_search = search(board, depth=2)
    assert isinstance(move_search, chess.Move)
    assert move_search in board.legal_moves

    move_agent = get_move(board)
    assert isinstance(move_agent, chess.Move)
    assert move_agent in board.legal_moves


def test_board_not_mutated_after_search():
    """Đảm bảo đệ quy luôn gọi board.pop(), không làm hỏng bàn cờ gốc."""
    board = chess.Board()
    fen_before = board.fen()

    _ = search(board, depth=2)

    assert board.fen() == fen_before


@pytest.mark.parametrize("depth", [1, 2])
def test_mate_in_1_white(depth):
    # Thế chiếu hết hàng cuối cho Trắng: Re8# (e1e8)
    board = chess.Board("6k1/5ppp/8/8/8/8/8/4R1K1 w - - 0 1")
    best_move = search(board, depth=depth)
    assert best_move == chess.Move.from_uci("e1e8")


@pytest.mark.parametrize("depth", [1, 2])
def test_mate_in_1_black(depth):
    # Thế chiếu hết hàng cuối cho Đen: Re1# (e8e1)
    board = chess.Board("4r1k1/8/8/8/8/8/5PPP/6K1 b - - 0 1")
    best_move = search(board, depth=depth)
    assert best_move == chess.Move.from_uci("e8e1")


def test_captures_free_queen():
    # Xe Trắng d1 ăn Hậu Đen d5 không mất gì (d1d5)
    board = chess.Board("4k3/8/8/3q4/8/8/8/3RK3 w - - 0 1")
    best_move = search(board, depth=2)
    assert best_move == chess.Move.from_uci("d1d5")


@pytest.mark.parametrize(
    "fen",
    [
        chess.STARTING_FEN,
        "4k3/8/8/3Q4/8/8/8/4K3 w - - 0 1",  # Trắng hơn 1 Hậu, Trắng đi
        "4k3/8/8/3q4/8/8/8/4K3 b - - 0 1",  # Đen hơn 1 Hậu, Đen đi
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    ],
)
def test_evaluate_bounds_and_symmetry(fen):
    board = chess.Board(fen)
    score = evaluate(board)

    # 1. Luôn nằm trong [-1, 1]
    assert -1.0 <= score <= 1.0

    # 2. Đổi lượt đi trên cùng thế cờ -> điểm phải đảo dấu
    flipped_turn = board.copy()
    flipped_turn.turn = not board.turn
    assert evaluate(flipped_turn) == pytest.approx(-score, abs=1e-6)

    # 3. Lật màu quân + lật lượt đi (board.mirror()) -> góc nhìn bên đang đi giữ nguyên
    mirrored = board.mirror()
    assert evaluate(mirrored) == pytest.approx(score, abs=1e-6)



def test_draw_stalemate_evaluates_to_zero():
    # Đen hết nước đi (stalemate)
    board = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    assert board.is_stalemate()
    assert evaluate(board) == pytest.approx(0.0, abs=1e-6)


def test_draw_insufficient_material():
    # Chỉ còn 2 Vua -> hòa
    board = chess.Board("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    assert board.is_insufficient_material()
    assert evaluate(board) == pytest.approx(0.0, abs=1e-6)


def test_draw_threefold_repetition():
    # Tạo lặp thế 3 lần bằng cách đi Mã qua lại
    board = chess.Board()
    moves = ["g1f3", "g8f6", "f3g1", "f6g8", "g1f3", "g8f6", "f3g1", "f6g8"]
    for uci in moves:
        board.push_uci(uci)

    assert board.can_claim_threefold_repetition()
    assert board.is_game_over(claim_draw=True)
    assert evaluate(board) == pytest.approx(0.0, abs=1e-6)