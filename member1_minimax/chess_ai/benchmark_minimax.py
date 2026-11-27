import csv
import random
import time
import chess

import chess_minimax as mm

# Bộ 6 thế cờ đại diện: khai cuộc, trung cuộc, chiến thuật, tàn cuộc
BENCHMARK_FENS = [
    ("Khoi_dau", chess.STARTING_FEN),
    ("Khai_cuoc_1", "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"),
    ("Trung_cuoc_1", "r2q1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 4 7"),
    ("Trung_cuoc_2", "r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P4/2NBPN2/PP3PPP/R1BQ1RK1 w - - 0 8"),
    ("Chien_thuat", "6k1/5ppp/8/8/8/8/8/4R1K1 w - - 0 1"),
    ("Tan_cuoc", "4k3/8/8/3p4/3P4/8/4K3/4R3 w - - 0 1"),
]


def benchmark_by_depth(depths=(1, 2, 3), csv_path="minimax_benchmark.csv"):
    """Đo số nút duyệt và thời gian trung bình theo độ sâu, xuất CSV cho báo cáo."""
    rows = []
    print("=" * 72)
    print(f"{'Depth':<7} | {'Avg Nodes/Move':>15} | {'Avg Time (s)':>14} | {'Nodes/sec':>12}")
    print("-" * 72)

    for depth in depths:
        total_nodes = 0
        total_time = 0.0

        for name, fen in BENCHMARK_FENS:
            board = chess.Board(fen)
            start = time.perf_counter()
            move = mm.search(board, depth=depth)
            elapsed = time.perf_counter() - start
            nodes = mm.NODES

            total_nodes += nodes
            total_time += elapsed
            rows.append({
                "position": name,
                "depth": depth,
                "move": move.uci() if move else "None",
                "nodes": nodes,
                "time_sec": round(elapsed, 6),
            })

        n = len(BENCHMARK_FENS)
        avg_nodes = total_nodes / n
        avg_time = total_time / n
        nps = total_nodes / total_time if total_time > 0 else 0
        print(f"{depth:<7} | {avg_nodes:>15.1f} | {avg_time:>14.4f} | {nps:>12.1f}")

    print("=" * 72)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["position", "depth", "move", "nodes", "time_sec"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Da luu ket qua chi tiet vao: {csv_path}\n")


def random_ai(board: chess.Board) -> chess.Move:
    return random.choice(list(board.legal_moves))


def play_match(ai1_fn, ai2_fn, ai1_name="MiniMax_d3", ai2_name="Random", num_games=10, max_moves=150):
    """Đấu nhiều ván đổi màu luân phiên, ghi nhận Thắng/Hòa/Thua, thời gian và số nút."""
    stats = {"win": 0, "draw": 0, "loss": 0}
    ai1_total_time = 0.0
    ai1_total_nodes = 0
    ai1_moves = 0

    for game_idx in range(num_games):
        board = chess.Board()
        ai1_is_white = (game_idx % 2 == 0)  # Đổi màu luân phiên

        while not board.is_game_over(claim_draw=True) and board.fullmove_number <= max_moves:
            is_ai1_turn = (board.turn == chess.WHITE) == ai1_is_white
            if is_ai1_turn:
                t0 = time.perf_counter()
                move = ai1_fn(board)
                ai1_total_time += time.perf_counter() - t0
                ai1_total_nodes += mm.NODES
                ai1_moves += 1
            else:
                move = ai2_fn(board)

            if move is None:
                break
            board.push(move)

        result = board.result(claim_draw=True)
        if result == "1-0":
            stats["win" if ai1_is_white else "loss"] += 1
        elif result == "0-1":
            stats["loss" if ai1_is_white else "win"] += 1
        else:
            stats["draw"] += 1

    avg_time = ai1_total_time / ai1_moves if ai1_moves else 0
    avg_nodes = ai1_total_nodes / ai1_moves if ai1_moves else 0

    print(f"=== Ket qua {ai1_name} vs {ai2_name} ({num_games} van, doi mau luan phien) ===")
    print(f"Thang: {stats['win']} | Hoa: {stats['draw']} | Thua: {stats['loss']}")
    print(f"Thoi gian TB/nuoc ({ai1_name}): {avg_time:.4f}s | So nut TB/nuoc: {avg_nodes:.1f}")


if __name__ == "__main__":
    # 1. Đo thống kê theo độ sâu 1, 2, 3 (xuất CSV cho TV2 và báo cáo)
    benchmark_by_depth(depths=(1, 2, 3))

    # 2. Đấu thử nghiệm mốc cơ sở MiniMax depth 3 (tăng num_games=50 khi benchmark chính thức)
    play_match(
        ai1_fn=mm.get_move,
        ai2_fn=random_ai,
        ai1_name="MiniMax_depth3",
        ai2_name="Random",
        num_games=4,
    )