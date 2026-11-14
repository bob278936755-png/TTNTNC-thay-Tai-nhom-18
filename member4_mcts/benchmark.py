"""Thực nghiệm 100 ván MCTS vs Random cho cả hai màu X và O."""
import argparse
import random
from mcts import MCTSAgent
from tictactoe import TicTacToeState


def match(mcts_as: str, games: int, simulations: int, seed: int) -> dict:
    rng = random.Random(seed)
    agent = MCTSAgent(simulations=simulations, seed=seed)
    result = {'Thắng': 0, 'Hòa': 0, 'Thua': 0}
    time_total = 0.0
    nodes_total = 0
    mcts_moves = 0

    for _ in range(games):
        state = TicTacToeState()
        while not state.is_terminal():
            if state.current_player == mcts_as:
                move = agent.get_move(state)
                time_total += agent.last_stats.elapsed_seconds
                nodes_total += agent.last_stats.nodes_created
                mcts_moves += 1
            else:
                move = rng.choice(state.legal_moves())
            state = state.play(move)

        if state.winner() == mcts_as:
            result['Thắng'] += 1
        elif state.winner() is None:
            result['Hòa'] += 1
        else:
            result['Thua'] += 1

    result['Tổng số ván'] = games
    result['Số mô phỏng mỗi nước'] = simulations
    result['Số lượt MCTS đã đi'] = mcts_moves
    result['Trung bình giây/nước'] = round(time_total / mcts_moves, 4) if mcts_moves else 0
    result['Trung bình số nút tạo/nước'] = round(nodes_total / mcts_moves, 2) if mcts_moves else 0
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Đối đầu MCTS và Random Player trên Tic-Tac-Toe')
    parser.add_argument('--games', type=int, default=100)
    parser.add_argument('--simulations', type=int, default=300)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    if args.games < 1 or args.simulations < 1:
        parser.error('--games và --simulations phải là số nguyên dương')

    for side in ('X', 'O'):
        print(f'\n=== MCTS chơi {side} / Random chơi {"O" if side == "X" else "X"} ===')
        for k, v in match(side, args.games, args.simulations, args.seed + (0 if side == 'X' else 1000)).items():
            print(f'{k}: {v}')
