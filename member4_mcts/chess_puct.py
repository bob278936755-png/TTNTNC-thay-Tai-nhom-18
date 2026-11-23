
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Callable, Mapping

import chess
from chess_adapter import material_value

PolicyValueFn = Callable[[chess.Board], tuple[Mapping[str, float], float]]


def baseline_policy_value(board: chess.Board) -> tuple[dict[str, float], float]:
    """Baseline: prior dong deu, value dua vao chenh lech quan (khong phai DNN)."""
    moves = [m.uci() for m in board.legal_moves]
    player = 'W' if board.turn == chess.WHITE else 'B'
    return {move: 1.0 for move in moves}, material_value(board, player)


def normalize_policy(weights: Mapping[str, float], legal_uci: list[str]) -> dict[str, float]:
    """Chi lay nuoc hop le, xu ly prior am/NaN/vo cuc, fallback uniform."""
    if not legal_uci:
        return {}
    safe = {}
    for uci in legal_uci:
        try:
            value = float(weights.get(uci, 0.0))
        except (TypeError, ValueError, OverflowError):
            value = 0.0
        safe[uci] = value if math.isfinite(value) and value > 0 else 0.0
    total = sum(safe.values())
    if not math.isfinite(total) or total <= 0:
        return {uci: 1.0 / len(legal_uci) for uci in legal_uci}
    return {uci: safe[uci] / total for uci in legal_uci}


@dataclass
class _Node:
    move_uci: str | None
    prior: float
    to_play: bool
    visits: int = 0
    value_sum: float = 0.0  # Goc nhin nguoi sap di tai nut nay
    children: dict[str, '_Node'] = field(default_factory=dict)


def _terminal_value(board: chess.Board) -> float:
    """Ket qua [−1,1] tu goc nhin ben sap di; chi goi neu van ket thuc."""
    outcome = board.outcome(claim_draw=True)
    if outcome is None:
        raise ValueError('Chua phai trang thai ket thuc.')
    if outcome.winner is None:
        return 0.0
    return 1.0 if outcome.winner == board.turn else -1.0


def _evaluate(board: chess.Board, fn: PolicyValueFn) -> tuple[dict[str, float], float]:
    weights, value = fn(board)
    value = float(value)
    if not math.isfinite(value) or not -1.0 <= value <= 1.0:
        raise ValueError('Value Network phai tra value huu han trong [-1, 1].')
    legal = [move.uci() for move in board.legal_moves]
    return normalize_policy(weights, legal), value


def _expand(node: _Node, board: chess.Board, priors: dict[str, float]) -> None:
    node.children = {
        uci: _Node(move_uci=uci, prior=prob, to_play=not board.turn)
        for uci, prob in priors.items()
    }


def _pick_child(node: _Node, c_puct: float, rng: random.Random) -> _Node:
    scale = math.sqrt(max(1, node.visits))
    def score(child: _Node) -> float:
        # child.value_sum theo goc nhin DOI THU, nen khi chon phai doi dau.
        q = -(child.value_sum / child.visits) if child.visits else 0.0
        u = c_puct * child.prior * scale / (1 + child.visits)
        return q + u
    scored = [(child, score(child)) for child in node.children.values()]
    top = max(value for _, value in scored)
    ties = [child for child, value in scored if abs(value - top) <= 1e-12]
    return rng.choice(ties)


@dataclass(frozen=True)
class PUCTStats:
    move_uci: str
    simulations: int
    nodes_created: int
    elapsed_seconds: float
    visits_by_move: dict[str, int]
    policy_by_move: dict[str, float]


def choose_puct_move(
    board: chess.Board,
    simulations: int = 80,
    c_puct: float = 1.5,
    max_tree_depth: int = 10,
    policy_value_fn: PolicyValueFn | None = None,
    seed: int | None = 42,
) -> tuple[chess.Move, PUCTStats]:
    """PUCT: prior o canh, value o la; khong thay doi board dau vao.

    Khi chua co network, su dung prior dong deu + material evaluation baseline.
    max_tree_depth tinh tu the co hien tai (so nua nuoc di).
    """
    if simulations < 1 or max_tree_depth < 1:
        raise ValueError('simulations va max_tree_depth phai >= 1.')
    if not math.isfinite(c_puct) or c_puct < 0:
        raise ValueError('c_puct phai la so huu han khong am.')
    if board.is_game_over(claim_draw=True):
        raise ValueError('Khong the tim nuoc di khi van da ket thuc.')

    fn = policy_value_fn or baseline_policy_value
    rng = random.Random(seed)
    start = time.perf_counter()
    root = _Node(None, prior=1.0, to_play=board.turn)
    priors, _ = _evaluate(board.copy(stack=True), fn)
    _expand(root, board, priors)
    nodes_created = 1 + len(root.children)

    for _ in range(simulations):
        current = board.copy(stack=True)
        node = root
        path = [root]
        depth = 0
        # Di xuong nhanh PUCT; dung o nut chua tham hoac den gioi han.
        while node.children and depth < max_tree_depth:
            child = _pick_child(node, c_puct, rng)
            current.push_uci(child.move_uci)
            node = child
            path.append(node)
            depth += 1
            if node.visits == 0:
                break
        if current.is_game_over(claim_draw=True):
            value = _terminal_value(current)
        else:
            priors, value = _evaluate(current, fn)
            if depth < max_tree_depth and not node.children:
                _expand(node, current, priors)
                nodes_created += len(node.children)
        # Node giu value theo nguoi sap di; moi cap luot doi dau.
        for visited in reversed(path):
            visited.visits += 1
            visited.value_sum += value
            value = -value

    best = max(root.children.values(), key=lambda c: (
        c.visits, -(c.value_sum / c.visits) if c.visits else -float('inf'), c.prior,
    ))
    visits = {uci: child.visits for uci, child in root.children.items()}
    total_visits = sum(visits.values())
    policy = {uci: n / total_visits for uci, n in visits.items()}
    move = chess.Move.from_uci(best.move_uci)
    if move not in board.legal_moves:
        raise AssertionError('PUCT chon nuoc khong hop le.')
    return move, PUCTStats(best.move_uci, simulations, nodes_created,
                           time.perf_counter() - start, visits, policy)
