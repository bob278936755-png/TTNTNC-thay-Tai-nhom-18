"""Chạy demo đơn giản: py demo.py hoặc py demo.py --depth 3."""
import argparse
import chess
from alpha_beta import AlphaBetaAI, make_basic_ai, make_minimax_ai


def main():
    parser = argparse.ArgumentParser(description="Demo Alpha-Beta - thành viên 2")
    parser.add_argument("--depth", type=int, default=3,
                        help="Độ sâu tìm kiếm; depth=2 chạy nhanh hơn")
    parser.add_argument("--fen", type=str, default=None,
                        help="Vị trí cờ dạng FEN, bỏ trống là ban đầu")
    args = parser.parse_args()
    board = chess.Board(args.fen) if args.fen else chess.Board()
    before = board.fen()
    print("BÀN CỜ:")
    print(board)
    print("\nFEN:", before)
    print(f"\nSO SÁNH CÙNG DEPTH={args.depth}, CÙNG EVALUATOR:")
    print(f"{'Thuật toán':<20} {'Nước đi':<10} {'Số nút':>10} {'Cắt nhánh':>12} {'Giây':>10}")
    for name, engine in [
        ("MiniMax", make_minimax_ai()),
        ("Alpha-Beta", make_basic_ai()),
        ("Alpha-Beta nâng cao", AlphaBetaAI()),
    ]:
        move = engine.search(board, args.depth)
        assert board.fen() == before, "LỖI: board bị thay đổi!"
        assert move is None or move in board.legal_moves
        stats = engine.stats
        print(f"{name:<20} {str(move):<10} {stats.nodes:>10} {stats.cutoffs:>12} {stats.seconds:>10.4f}")
        if name == "Alpha-Beta nâng cao":
            print(f"  Quiescence nodes={stats.qnodes}, TT hits={stats.tt_hits}, score={engine.last_score}")
    print("\nPASS: nước đi hợp lệ và bàn cờ gốc không thay đổi.")


if __name__ == "__main__":
    main()
