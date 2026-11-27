"""TUẦN 4 — Benchmark, đối đầu Heuristic vs Value Network, và báo cáo.

Chạy:  python -m scripts.benchmark  (từ thư mục ``member3_Value_Network``)

Nội dung:
  1. Đo tốc độ suy luận (Nodes Per Second) của cả hai phương pháp
  2. Đo độ tương quan giữa Heuristic và Value Net trên 500 thế cờ ngẫu nhiên
  3. Thi đấu đối kháng: Heuristic (1-ply) vs Value Net (1-ply)
  4. In bảng kết quả tổng hợp cho báo cáo
"""
import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chess
import numpy as np

from evaluation.handcrafted import evaluate as heuristic_evaluate
from evaluation.inference import load_value_network, value_net_evaluate

CHECKPOINT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checkpoints"
)


# ======================================================================
# 1. TẠO CÁC THẾ CỜ NGẪU NHIÊN ĐỂ BENCHMARK
# ======================================================================

def _random_positions(n: int = 500, seed: int = 99) -> list[chess.Board]:
    """Tạo ``n`` thế cờ trung cuộc hợp lệ bằng cách chơi ngẫu nhiên."""
    rng = random.Random(seed)
    boards: list[chess.Board] = []
    while len(boards) < n:
        b = chess.Board()
        for _ in range(rng.randint(8, 50)):
            moves = list(b.legal_moves)
            if not moves or b.is_game_over():
                break
            b.push(rng.choice(moves))
        if not b.is_game_over():
            boards.append(b.copy(stack=False))
    return boards


# ======================================================================
# 2. BENCHMARK TỐC ĐỘ
# ======================================================================

def benchmark_speed(boards: list[chess.Board]) -> dict:
    """Đo tốc độ suy luận (Nodes Per Second) của Heuristic và Value Net."""
    n = len(boards)

    # --- Heuristic ---
    t0 = time.perf_counter()
    for b in boards:
        heuristic_evaluate(b)
    t_heuristic = time.perf_counter() - t0

    # --- Value Net ---
    t0 = time.perf_counter()
    for b in boards:
        value_net_evaluate(b)
    t_value_net = time.perf_counter() - t0

    return {
        "n": n,
        "heuristic_time": t_heuristic,
        "heuristic_nps": n / t_heuristic,
        "value_net_time": t_value_net,
        "value_net_nps": n / t_value_net,
        "speed_ratio": (n / t_heuristic) / (n / t_value_net),
    }


# ======================================================================
# 3. ĐỘ TƯƠNG QUAN GIỮA HEURISTIC VÀ VALUE NET
# ======================================================================

def correlation_analysis(boards: list[chess.Board]) -> dict:
    """Tính điểm tương quan Pearson giữa Heuristic và Value Network."""
    h_scores = np.array([heuristic_evaluate(b) for b in boards])
    v_scores = np.array([value_net_evaluate(b) for b in boards])

    corr = np.corrcoef(h_scores, v_scores)[0, 1]
    mae = np.mean(np.abs(h_scores - v_scores))
    agree_sign = np.mean(np.sign(h_scores) == np.sign(v_scores))

    return {
        "pearson_r": corr,
        "mae": mae,
        "sign_agreement": agree_sign,
    }


# ======================================================================
# 4. ĐỐI ĐẦU: Heuristic vs Value Network (1-ply minimax)
# ======================================================================

def _best_move_1ply(board: chess.Board, eval_fn) -> chess.Move | None:
    """Chọn nước đi tốt nhất bằng 1-ply minimax với hàm đánh giá ``eval_fn``."""
    best_move = None
    best_score = -float("inf")
    for move in board.legal_moves:
        board.push(move)
        # Điểm đối phương sau nước đi → đảo dấu cho ta
        score = -eval_fn(board)
        board.pop()
        if score > best_score:
            best_score = score
            best_move = move
    return best_move


def play_match(
    white_fn, black_fn, max_moves: int = 100,
) -> str:
    """Mô phỏng 1 ván đấu giữa 2 agent. Trả về kết quả PGN."""
    board = chess.Board()
    for _ in range(max_moves * 2):
        if board.is_game_over():
            break
        fn = white_fn if board.turn == chess.WHITE else black_fn
        move = _best_move_1ply(board, fn)
        if move is None:
            break
        board.push(move)
    return board.result()


def tournament(num_games: int = 10) -> dict:
    """Giải đấu: mỗi bên đổi phiên Trắng/Đen."""
    results = {"heuristic_wins": 0, "value_net_wins": 0, "draws": 0}

    for i in range(num_games):
        if i % 2 == 0:
            # Heuristic cầm Trắng
            res = play_match(heuristic_evaluate, value_net_evaluate, max_moves=60)
            if res == "1-0":
                results["heuristic_wins"] += 1
            elif res == "0-1":
                results["value_net_wins"] += 1
            else:
                results["draws"] += 1
        else:
            # Value Net cầm Trắng
            res = play_match(value_net_evaluate, heuristic_evaluate, max_moves=60)
            if res == "1-0":
                results["value_net_wins"] += 1
            elif res == "0-1":
                results["heuristic_wins"] += 1
            else:
                results["draws"] += 1

        print(f"  Ván {i + 1}/{num_games}: {res}")

    return results


# ======================================================================
# 5. IN BÁO CÁO
# ======================================================================

def print_report(speed: dict, corr: dict, tourney: dict) -> None:
    """In bảng tổng kết cho báo cáo nhóm."""
    print("\n" + "=" * 70)
    print("  BÁO CÁO TỔNG KẾT THÀNH VIÊN 3 — TUẦN 4")
    print("=" * 70)

    print("\n┌─── 1. BENCHMARK TỐC ĐỘ ──────────────────────────────────────────┐")
    print(f"│  Số thế cờ kiểm tra : {speed['n']:<10d}                               │")
    print(f"│  Heuristic (Tuần 1) : {speed['heuristic_time']:.4f}s"
          f"  →  {speed['heuristic_nps']:>10.0f} NPS                │")
    print(f"│  Value Net (Tuần 3) : {speed['value_net_time']:.4f}s"
          f"  →  {speed['value_net_nps']:>10.0f} NPS                │")
    print(f"│  Tỷ lệ tốc độ      : Heuristic nhanh gấp ~{speed['speed_ratio']:.1f}×            │")
    print("└───────────────────────────────────────────────────────────────────┘")

    print("\n┌─── 2. ĐỘ TƯƠNG QUAN ──────────────────────────────────────────────┐")
    print(f"│  Pearson r          : {corr['pearson_r']:+.4f}                                   │")
    print(f"│  MAE                : {corr['mae']:.4f}                                    │")
    print(f"│  Đồng dấu (±)      : {corr['sign_agreement'] * 100:.1f}%                                    │")
    print("└───────────────────────────────────────────────────────────────────┘")

    total = tourney["heuristic_wins"] + tourney["value_net_wins"] + tourney["draws"]
    print("\n┌─── 3. KẾT QUẢ ĐỐI ĐẦU ────────────────────────────────────────── ┐")
    print(f"│  Tổng số ván        : {total}                                       │")
    print(f"│  Heuristic thắng    : {tourney['heuristic_wins']}                                        │")
    print(f"│  Value Net thắng    : {tourney['value_net_wins']}                                        │")
    print(f"│  Hòa                : {tourney['draws']}                                        │")
    print("└───────────────────────────────────────────────────────────────────┘")

    print("\n┌─── 4. KẾT LUẬN ───────────────────────────────────────────────────┐")
    print("│  • Hàm heuristic Tuần 1: đánh giá nhanh, phù hợp Alpha-Beta     │")
    print("│    sâu nhiều tầng (Thành viên 2).                                │")
    print("│  • Value Network Tuần 3: đánh giá chính xác hơn, phù hợp        │")
    print("│    MCTS / AlphaZero (Thành viên 4) khi thay thế random rollout.  │")
    print("│  • Cả hai hàm đều tuân thủ hợp đồng evaluate(board) → [-1, 1].  │")
    print("└───────────────────────────────────────────────────────────────────┘")


# ======================================================================
# MAIN
# ======================================================================

def main() -> None:
    model_path = os.path.join(CHECKPOINT_DIR, "value_net_finetuned.keras")

    if not os.path.exists(model_path):
        print(f"[LỖI] Không tìm thấy mô hình: {model_path}")
        print("       Hãy chạy 'python -m scripts.train_resnet' (Tuần 3) trước!")
        sys.exit(1)

    load_value_network(model_path)

    print("\n[Tuần 4] Tạo thế cờ ngẫu nhiên để benchmark...")
    boards = _random_positions(500)

    print("[Tuần 4] Đo tốc độ suy luận...")
    speed = benchmark_speed(boards)

    print("[Tuần 4] Phân tích tương quan Heuristic ↔ Value Net...")
    corr = correlation_analysis(boards[:200])

    print("[Tuần 4] Giải đấu Heuristic vs Value Net (6 ván)...")
    tourney = tournament(num_games=6)

    print_report(speed, corr, tourney)


if __name__ == "__main__":
    main()
