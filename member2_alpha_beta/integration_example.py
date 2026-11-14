"""Ví dụ tích hợp phần Thành viên 2 vào chương trình của nhóm.

Khi chưa có Value Network: gọi search(board, depth).
Khi có Value Network: truyền evaluator của Thành viên 3 vào AlphaBetaAI.
"""
import chess
from alpha_beta import AlphaBetaAI, search


def demo_team_api():
    board = chess.Board()
    move = search(board, depth=3)
    if move is not None:
        print("TV2 đề xuất:", move.uci(), "=", board.san(move))
        # Trưởng nhóm / TV1 thực hiện board.push(move) trong logic đấu.


def using_value_network(value_evaluate):
    """value_evaluate(board) -> float trong [-1, 1], theo bên đang đi.

    Dùng sau khi Thành viên 3 cung cấp hàm thật:
        from value_network import evaluate as value_evaluate
        move = using_value_network(value_evaluate)
    """
    board = chess.Board()
    ai = AlphaBetaAI(evaluator=value_evaluate)
    move = ai.search(board, depth=3)
    return move


if __name__ == "__main__":
    demo_team_api()
