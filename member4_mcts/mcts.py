"""MCTS thuần: Selection (UCT) -> Expansion -> Rollout -> Backpropagation.

Không phụ thuộc luật Tic-Tac-Toe. Dùng được cho trò chơi hai người chơi,
luân phiên lượt, kết quả xác định, nếu trạng thái cài đặt đúng giao diện.
"""
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Protocol


class GameState(Protocol):
    current_player: str

    def is_terminal(self) -> bool: ...
    def legal_moves(self) -> list[int]: ...
    def play(self, move: int) -> 'GameState': ...
    def reward(self, player: str) -> float: ...


@dataclass
class Node:
    state: GameState
    parent: Node | None = None
    move: int | None = None
    children: list[Node] = field(default_factory=list)
    visits: int = 0
    reward_sum: float = 0.0
    untried_moves: list[int] = field(init=False)

    def __post_init__(self):
        self.untried_moves = self.state.legal_moves()

    def uct(self, exploration: float) -> float:
        if self.visits == 0:
            return float('inf')
        if self.parent is None:
            raise ValueError('Nút gốc không có UCT từ nút cha.')
        exploit = self.reward_sum / self.visits
        explore = exploration * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploit + explore


@dataclass(frozen=True)
class SearchStats:
    move: int
    simulations: int
    nodes_created: int
    elapsed_seconds: float
    visits_by_move: dict[int, int]


class MCTSAgent:
    def __init__(self, simulations: int = 500,
                 exploration: float = math.sqrt(2), seed: int | None = None):
        if simulations < 1:
            raise ValueError('Số mô phỏng phải >= 1.')
        if exploration < 0:
            raise ValueError('Hệ số khám phá không được âm.')
        self.simulations = simulations
        self.exploration = exploration
        self.rng = random.Random(seed)
        self.last_stats: SearchStats | None = None

    def get_move(self, state: GameState) -> int:
        if state.is_terminal():
            raise ValueError('Ván đã kết thúc, không còn nước đi.')

        root = Node(state)
        nodes_created = 1
        start = time.perf_counter()

        for _ in range(self.simulations):
            node = root

            # 1. Selection: nếu đã mở hết các con, chọn nhánh UCT cao nhất.
            while not node.state.is_terminal() and not node.untried_moves:
                node = max(node.children, key=lambda child: child.uct(self.exploration))

            # 2. Expansion: mở rộng một nước đi hợp lệ chưa thử.
            if not node.state.is_terminal() and node.untried_moves:
                move = self.rng.choice(node.untried_moves)
                node.untried_moves.remove(move)
                child = Node(node.state.play(move), parent=node, move=move)
                node.children.append(child)
                node = child
                nodes_created += 1

            # 3. Simulation (rollout): chọn ngẫu nhiên đến hết ván.
            final_state = node.state
            while not final_state.is_terminal():
                final_state = final_state.play(self.rng.choice(final_state.legal_moves()))

            # 4. Backpropagation: ghi nhận kết quả theo người đã đi tại nút cha.
            # Quan trọng: ở nút đối thủ, đánh giá theo góc nhìn đối thủ,
            # không được luôn lấy góc nhìn của X hay của nút gốc.
            while node is not None:
                node.visits += 1
                player = (node.parent.state.current_player if node.parent
                          else root.state.current_player)
                node.reward_sum += final_state.reward(player)
                node = node.parent

        # Chọn nước đi được mô phỏng nhiều nhất (robust child).
        best = max(root.children, key=lambda child: (child.visits, child.reward_sum / child.visits))
        self.last_stats = SearchStats(
            move=best.move,
            simulations=self.simulations,
            nodes_created=nodes_created,
            elapsed_seconds=time.perf_counter() - start,
            visits_by_move={child.move: child.visits for child in root.children},
        )
        return best.move
