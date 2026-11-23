from __future__ import annotations

import csv
from pathlib import Path
import chess
from chess_adapter import choose_chess_move
from chess_puct import choose_puct_move
from chess_selfplay import play_self_game, save_selfplay_csv

POSITIONS = {
    'initial': chess.STARTING_FEN,
    'check': '4k3/8/8/8/8/8/4r3/4K3 w - - 0 1',
    'promotion': '7k/P7/8/8/8/8/8/K7 w - - 0 1',
    'middlegame': 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3',
}


def main():
    target = Path(__file__).resolve().parent / 'results'
    target.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, fen in POSITIONS.items():
        board = chess.Board(fen)
        for algo in ('UCT_rollout', 'PUCT_material'):
            if algo == 'UCT_rollout':
                move, st = choose_chess_move(board, simulations=20, rollout_plies=16, seed=42)
            else:
                move, st = choose_puct_move(board, simulations=20, max_tree_depth=6)
            rows.append({
                'position': name, 'algorithm': algo, 'move_uci': move.uci(),
                'legal': move in board.legal_moves, 'simulations': st.simulations,
                'nodes_created': st.nodes_created,
                'elapsed_seconds': f'{st.elapsed_seconds:.6f}',
            })
            print(f'{name:12s} {algo:14s} move={move.uci():5s} '
                  f'legal={move in board.legal_moves} time={st.elapsed_seconds:.3f}s')
    with (target / 'benchmark_chess.csv').open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    game = play_self_game(simulations=4, max_plies=8, max_tree_depth=4)
    save_selfplay_csv(game, target / 'selfplay_chess.csv')
    print(f'\nSelf-play: {len(game.steps)} plies, result={game.result}, '
          f'finished_by_rules={game.finished_by_rules}')
    print('CSV da luu:', target)
    if not game.finished_by_rules:
        print('CHU Y: Van dung som; value_target de trong, khong ghi la hoa.')


if __name__ == '__main__':
    main()
