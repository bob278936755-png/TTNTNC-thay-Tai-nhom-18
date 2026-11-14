"""Benchmark Connect Four: MCTS đối đầu người chơi chọn cột ngẫu nhiên."""
from __future__ import annotations

import argparse
import random
import time

from connect_four import ConnectFourState
from mcts import MCTSAgent


def match(mcts_as: str, games: int, simulations: int, seed: int) -> dict:
    rng = random.Random(seed + 100000)
    agent = MCTSAgent(simulations=simulations, seed=seed)
    results = {'Thắng': 0, 'Hòa': 0, 'Thua': 0}
    seconds = 0.0
    nodes = 0
    agent_moves = 0
    start = time.perf_counter()

    for _ in range(games):
        state = ConnectFourState()
        while not state.is_terminal():
            if state.current_player == mcts_as:
                move = agent.get_move(state)
                seconds += agent.last_stats.elapsed_seconds
                nodes += agent.last_stats.nodes_created
                agent_moves += 1
            else:
                move = rng.choice(state.legal_moves())
            state = state.play(move)

        winner = state.winner()
        if winner == mcts_as:
            results['Thắng'] += 1
        elif winner is None:
            results['Hòa'] += 1
        else:
            results['Thua'] += 1

    return {
        **results,
        'Tổng số ván': games,
        'Mô phỏng mỗi nước': simulations,
        'Số nước MCTS đã đánh': agent_moves,
        'Trung bình giây/nước MCTS': round(seconds / agent_moves, 4) if agent_moves else 0,
        'Trung bình nút tạo/nước': round(nodes / agent_moves, 2) if agent_moves else 0,
        'Tổng thời gian benchmark (giây)': round(time.perf_counter() - start, 2),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MCTS đấu Random Player trong Connect Four')
    parser.add_argument('--games', type=int, default=10, help='Số ván cho mỗi màu')
    parser.add_argument('--simulations', type=int, default=150, help='Mô phỏng cho mỗi nước MCTS')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    if args.games < 1 or args.simulations < 1:
        parser.error('--games và --simulations phải là số nguyên dương')

    for side in ('X', 'O'):
        print(f'\n=== Connect Four: MCTS = {side}, Random = {"O" if side == "X" else "X"} ===')
        result = match(side, args.games, args.simulations,
                       args.seed if side == 'X' else args.seed + 1000)
        for key, value in result.items():
            print(f'{key}: {value}')
