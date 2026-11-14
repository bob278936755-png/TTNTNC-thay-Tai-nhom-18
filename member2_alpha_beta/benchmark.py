"""Benchmark so sánh công bằng: kết quả thực tế được tạo khi CHẠY mã.

Ví dụ:
    py benchmark.py
    py benchmark.py --depths 1 2 3 --positions start italian
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import chess
from alpha_beta import make_basic_ai, make_minimax_ai

POSITIONS = {
    "start": None,
    # Ruy Lopez sau 1.e4 e5 2.Nf3 Nc6 3.Bb5 a6
    "ruy_lopez": "r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4",
    # Vị trí có trao đổi quân để đo ảnh hưởng của cắt nhánh
    "italian": "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
}


def run_benchmark(depths: list[int], positions: list[str], folder: Path) -> list[dict]:
    folder.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for name in positions:
        for depth in depths:
            for algo_name, engine in [("MiniMax", make_minimax_ai()),
                                      ("Alpha-Beta", make_basic_ai())]:
                board = chess.Board(POSITIONS[name]) if POSITIONS[name] else chess.Board()
                before = board.fen()
                move = engine.search(board, depth)
                assert board.fen() == before
                assert move is None or move in board.legal_moves
                stat = engine.stats
                row = {
                    "position": name,
                    "depth": depth,
                    "algorithm": algo_name,
                    "best_move_uci": move.uci() if move else "none",
                    "score": round(engine.last_score or 0.0, 6),
                    "nodes": stat.nodes,
                    "cutoffs": stat.cutoffs,
                    "time_seconds": round(stat.seconds, 6),
                }
                rows.append(row)
                print(row)

    csv_path = folder / "benchmark.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    # Chỉ so sánh số nút, thời gian là thông số phụ thuộc vào máy chạy.
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Không có matplotlib: đã xuất CSV, bỏ qua biểu đồ.")
    else:
        # Vẽ nhóm cột theo vị trí và độ sâu.
        labels = [f"{name}\nd={depth}" for name in positions for depth in depths]
        minimax_nodes = [r["nodes"] for r in rows if r["algorithm"] == "MiniMax"]
        ab_nodes = [r["nodes"] for r in rows if r["algorithm"] == "Alpha-Beta"]
        x = list(range(len(labels)))
        fig, ax = plt.subplots(figsize=(max(8, len(labels) * 1.3), 5))
        ax.bar([i - 0.18 for i in x], minimax_nodes, width=0.36, label="MiniMax")
        ax.bar([i + 0.18 for i in x], ab_nodes, width=0.36, label="Alpha-Beta")
        ax.set_xticks(x, labels)
        ax.set_ylabel("Số nút tìm kiếm chính")
        ax.set_title("Benchmark: cùng evaluator, depth, thứ tự nước đi")
        ax.legend()
        fig.tight_layout()
        fig.savefig(folder / "benchmark_nodes.png", dpi=160)
        plt.close(fig)

    # Tóm tắt tự động theo dữ liệu chạy thật, không điền số liệu mẫu.
    lines = ["# Kết quả benchmark (tạo khi chạy chương trình)", "",
             "Cấu hình: MiniMax và Alpha-Beta đều tắt các tối ưu khác.",
             "Số nút không gồm nút gốc; chỉ tính cây tìm kiếm chính.", "",
             "| Vị trí | Depth | MiniMax nodes | Alpha-Beta nodes | Giảm (%) |",
             "|---|---:|---:|---:|---:|"]
    for i in range(0, len(rows), 2):
        mm, ab = rows[i], rows[i+1]
        reduction = (100.0 * (mm["nodes"] - ab["nodes"]) / mm["nodes"]
                     if mm["nodes"] else 0.0)
        lines.append(f"| {mm['position']} | {mm['depth']} | {mm['nodes']} | {ab['nodes']} | {reduction:.2f}% |")
    lines += ["", "Kết luận: số nút cắt giảm phụ thuộc vị trí, evaluator, độ sâu và thứ tự nước đi."]
    (folder / "benchmark_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nĐã xuất dữ liệu vào: {folder.resolve()}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depths", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--positions", nargs="+", choices=list(POSITIONS),
                        default=["start", "italian"])
    parser.add_argument("--out", default="outputs", help="Thư mục xuất kết quả")
    args = parser.parse_args()
    if not args.depths or any(d < 1 for d in args.depths):
        parser.error("Mọi depth phải >= 1")
    run_benchmark(args.depths, args.positions, Path(args.out))


if __name__ == "__main__":
    main()
