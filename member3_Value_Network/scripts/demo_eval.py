"""Chạy thử: python -m scripts.demo_eval  (từ thư mục gốc repo)"""
import chess

from evaluation import evaluate
from evaluation.handcrafted import evaluation_breakdown

POSITIONS = {
    "Khai cuộc": chess.STARTING_FEN,
    "Trắng hơn Hậu": "rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "Chiếu hết (Trắng bị mate)": "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3",
}

if __name__ == "__main__":
    for name, fen in POSITIONS.items():
        b = chess.Board(fen)
        print(f"{name}: evaluate = {evaluate(b):+.3f}")
        for k, v in evaluation_breakdown(b).items():
            print(f"    {k:15s} {v:+.3f}")
