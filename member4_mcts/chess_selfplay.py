from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import chess
from chess_puct import PolicyValueFn, choose_puct_move


@dataclass
class SelfPlayStep:
    ply: int
    fen: str
    player: str
    chosen_uci: str
    visits_by_move: dict[str, int]
    policy_by_move: dict[str, float]
    result: str = '*'  # * = chua biet ket qua thuc
    value_target: int | None = None


@dataclass
class SelfPlayResult:
    board: chess.Board
    steps: list[SelfPlayStep]
    result: str
    finished_by_rules: bool


def play_self_game(
    board: chess.Board | None = None,
    simulations: int = 12,
    max_plies: int = 12,
    max_tree_depth: int = 6,
    policy_value_fn: PolicyValueFn | None = None,
) -> SelfPlayResult:
    if max_plies < 1:
        raise ValueError('max_plies phai >= 1.')
    playing = chess.Board() if board is None else board.copy(stack=True)
    steps: list[SelfPlayStep] = []
    while len(steps) < max_plies and not playing.is_game_over(claim_draw=True):
        player = 'W' if playing.turn == chess.WHITE else 'B'
        move, stats = choose_puct_move(
            playing, simulations=simulations, max_tree_depth=max_tree_depth,
            policy_value_fn=policy_value_fn, seed=42 + len(steps),
        )
        steps.append(SelfPlayStep(len(steps) + 1, playing.fen(), player, move.uci(),
                                  stats.visits_by_move, stats.policy_by_move))
        playing.push(move)

    finished = playing.is_game_over(claim_draw=True)
    result = playing.result(claim_draw=True) if finished else '*'
    for step in steps:
        step.result = result
        if finished:
            if result == '1/2-1/2':
                step.value_target = 0
            else:
                white_won = (result == '1-0')
                step.value_target = 1 if (step.player == 'W') == white_won else -1
    return SelfPlayResult(playing, steps, result, finished)


def save_selfplay_csv(result: SelfPlayResult, path: str | Path) -> None:
    """CSV co the doc sau nay de train: (state, pi, z)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'ply', 'fen', 'player', 'chosen_uci', 'visits_json',
            'policy_json', 'game_result', 'value_target'
        ])
        writer.writeheader()
        for step in result.steps:
            writer.writerow({
                'ply': step.ply, 'fen': step.fen, 'player': step.player,
                'chosen_uci': step.chosen_uci,
                'visits_json': json.dumps(step.visits_by_move, sort_keys=True),
                'policy_json': json.dumps(step.policy_by_move, sort_keys=True),
                'game_result': step.result,
                'value_target': '' if step.value_target is None else step.value_target,
            })
