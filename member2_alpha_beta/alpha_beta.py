"""Thành viên 2 - Depth Pruning + Alpha-Beta, tương thích python-chess.

Giao ước nhóm:
    search(board: chess.Board, depth: int) -> chess.Move | None
    get_move(board: chess.Board) -> chess.Move | None
    evaluator(board) -> float: điểm theo phía ĐANG đi, trong (-1, 1)

Board đầu vào KHÔNG bị sửa. Trong bàn cờ đã kết thúc, trả None.
"""
from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, Iterable, Optional

import chess

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}
INF = 2.0
MATE_SCORE = 1.0
MAX_STATIC_SCORE = 0.98  # Để chiếu hết luôn có điểm lớn hơn đánh giá tĩnh.


def evaluate(board: chess.Board) -> float:
    """Bản đánh giá vật chất dùng tạm, cho đến khi nhận Value Network (TV3).

    Vật chất: Tốt=1, Mã=3, Tượng=3, Xe=5, Hậu=9.
    Giá trị dương: tốt cho bên đang đến lượt.
    """
    if board.is_checkmate():
        return -MATE_SCORE
    if board.is_game_over(claim_draw=False):
        return 0.0

    white_minus_black = sum(
        weight * (len(board.pieces(piece, chess.WHITE)) -
                  len(board.pieces(piece, chess.BLACK)))
        for piece, weight in PIECE_VALUES.items()
    )
    raw = white_minus_black / 39.0
    return max(-MAX_STATIC_SCORE, min(MAX_STATIC_SCORE,
               raw if board.turn == chess.WHITE else -raw))


@dataclass
class SearchStats:
    nodes: int = 0             # Nút trong cây tìm kiếm chính (không kể nút gốc)
    qnodes: int = 0            # Nút mở rộng quiescence
    cutoffs: int = 0           # Số lần cắt Alpha-Beta
    tt_hits: int = 0           # Số lần dùng bản ghi TT đủ độ sâu
    seconds: float = 0.0
    completed_depth: int = 0


@dataclass
class TTEntry:
    depth: int
    score: float
    flag: str                 # EXACT, LOWER, UPPER
    best_move: Optional[chess.Move]


class AlphaBetaAI:
    """Negamax có cắt Alpha-Beta và tùy chọn các tối ưu tuần 2.

    Khi so sánh công bằng với MiniMax: tắt move ordering, iterative
    deepening, quiescence và TT ở CẢ HAI cấu hình.
    """

    def __init__(
        self,
        evaluator: Callable[[chess.Board], float] = evaluate,
        use_alpha_beta: bool = True,
        move_ordering: bool = True,
        iterative_deepening: bool = True,
        quiescence: bool = True,
        transposition_table: bool = True,
        qdepth: int = 3,
        tt_capacity: int = 50_000,
    ) -> None:
        if qdepth < 0:
            raise ValueError("qdepth phải >= 0")
        if tt_capacity < 1:
            raise ValueError("tt_capacity phải >= 1")
        self.evaluator = evaluator
        self.use_alpha_beta = use_alpha_beta
        self.move_ordering = move_ordering
        self.iterative_deepening = iterative_deepening
        self.quiescence = quiescence and use_alpha_beta
        self.transposition_table = transposition_table and use_alpha_beta
        self.qdepth = qdepth
        self.tt_capacity = tt_capacity
        self.tt: dict[str, TTEntry] = {}
        self.stats = SearchStats()
        self.last_score: Optional[float] = None

    @staticmethod
    def _terminal_score(board: chess.Board) -> Optional[float]:
        if board.is_checkmate():
            return -MATE_SCORE
        if board.is_game_over(claim_draw=False):
            return 0.0
        return None

    def _static(self, board: chess.Board) -> float:
        value = float(self.evaluator(board))
        return max(-MAX_STATIC_SCORE, min(MAX_STATIC_SCORE, value))

    def _order_moves(
        self,
        board: chess.Board,
        moves: Iterable[chess.Move],
        preferred: Optional[chess.Move] = None,
    ) -> list[chess.Move]:
        ordered = list(moves)
        if not self.move_ordering:
            return ordered

        def priority(move: chess.Move) -> int:
            if move == preferred:
                return 100_000
            result = 0
            if move.promotion:
                result += 5_000 + PIECE_VALUES.get(move.promotion, 0) * 100
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                # En-passant: ô đích rỗng nhưng nạn nhân vẫn là Tốt.
                victim_val = PIECE_VALUES[victim.piece_type] if victim else 1
                attacker_val = PIECE_VALUES[attacker.piece_type] if attacker else 0
                result += 1_000 + 10 * victim_val - attacker_val
            return result

        return sorted(ordered, key=priority, reverse=True)

    def _qsearch(
        self, board: chess.Board, alpha: float, beta: float, remaining: int
    ) -> float:
        """Quiescence: ở lá ưu tiên giải chiếu, bắt quân và phong cấp.

        Giới hạn qdepth ngăn chạy quá lâu. Khi đúng giới hạn mà vẫn
        đang bị chiếu, xét thêm 1 lượt thoát chiếu thay vì đứng yên.
        """
        self.stats.qnodes += 1
        terminal = self._terminal_score(board)
        if terminal is not None:
            return terminal

        in_check = board.is_check()
        if not in_check:
            stand_pat = self._static(board)
            if remaining <= 0:
                return stand_pat
            if stand_pat >= beta:
                self.stats.cutoffs += 1
                return stand_pat
            alpha = max(alpha, stand_pat)
            best = stand_pat
            moves = [move for move in board.legal_moves
                     if board.is_capture(move) or move.promotion]
        else:
            # Đang bị chiếu -> không thể dùng 'stand pat'.
            best = -INF
            moves = list(board.legal_moves)

        for move in self._order_moves(board, moves):
            board.push(move)
            try:
                if in_check and remaining <= 0:
                    # Tới giới hạn: kiểm tra kết thúc hoặc chấm tĩnh
                    # SAU khi đã thoát chiếu; không tăng độ sâu thêm.
                    child_terminal = self._terminal_score(board)
                    child_score = (child_terminal if child_terminal is not None
                                   else self._static(board))
                    score = -child_score
                else:
                    score = -self._qsearch(board, -beta, -alpha, remaining - 1)
            finally:
                board.pop()
            best = max(best, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                self.stats.cutoffs += 1
                break
        return best

    def _negamax(self, board: chess.Board, depth: int, alpha: float,
                 beta: float) -> float:
        self.stats.nodes += 1
        terminal = self._terminal_score(board)
        if terminal is not None:
            return terminal
        if depth == 0:
            if self.quiescence:
                return self._qsearch(board, alpha, beta, self.qdepth)
            return self._static(board)

        # Khóa FEN có luật nhập thành, lượt đi, en-passant, đồng hồ 50 nước.
        # Lịch sử lặp lại KHÔNG có trong FEN: giới hạn demo/học phần.
        key = board.fen() if self.transposition_table else ""
        entry = self.tt.get(key) if self.transposition_table else None
        original_alpha, original_beta = alpha, beta
        if entry is not None and entry.depth >= depth:
            self.stats.tt_hits += 1
            if entry.flag == "EXACT":
                return entry.score
            if entry.flag == "LOWER":
                alpha = max(alpha, entry.score)
            elif entry.flag == "UPPER":
                beta = min(beta, entry.score)
            if alpha >= beta:
                return entry.score

        best = -INF
        best_move: Optional[chess.Move] = None
        for move in self._order_moves(board, board.legal_moves,
                                      entry.best_move if entry else None):
            board.push(move)
            try:
                score = -self._negamax(board, depth - 1, -beta, -alpha)
            finally:
                board.pop()

            if score > best:
                best, best_move = score, move
            alpha = max(alpha, score)
            if self.use_alpha_beta and alpha >= beta:
                self.stats.cutoffs += 1
                break

        if self.transposition_table:
            flag = "EXACT"
            if best <= original_alpha:
                flag = "UPPER"
            elif best >= original_beta:
                flag = "LOWER"
            # Giữ bộ nhớ ổn định với máy RAM 8GB.
            if len(self.tt) >= self.tt_capacity:
                self.tt.clear()
            self.tt[key] = TTEntry(depth, best, flag, best_move)
        return best

    def search(self, board: chess.Board, depth: int) -> Optional[chess.Move]:
        """Tìm nước tốt nhất cho bên đang đi, không làm thay đổi board."""
        if depth < 1:
            raise ValueError("depth phải là số nguyên >= 1")
        self.stats = SearchStats()
        self.last_score = None
        self.tt.clear()
        started = time.perf_counter()
        try:
            if self._terminal_score(board) is not None:
                return None

            best_move: Optional[chess.Move] = None
            depths = (range(1, depth + 1) if self.iterative_deepening
                      else (depth,))
            for current_depth in depths:
                alpha, beta = -INF, INF
                best_score = -INF
                current_best: Optional[chess.Move] = None
                previous = self.tt.get(board.fen()) if self.transposition_table else None
                preferred = previous.best_move if previous else best_move
                for move in self._order_moves(board, board.legal_moves, preferred):
                    board.push(move)
                    try:
                        score = -self._negamax(
                            board, current_depth - 1, -beta, -alpha
                        )
                    finally:
                        board.pop()
                    if score > best_score:
                        best_score, current_best = score, move
                    if self.use_alpha_beta:
                        alpha = max(alpha, score)

                best_move = current_best
                self.last_score = best_score
                self.stats.completed_depth = current_depth
                if self.transposition_table and best_move is not None:
                    self.tt[board.fen()] = TTEntry(
                        current_depth, best_score, "EXACT", best_move
                    )
            return best_move
        finally:
            self.stats.seconds = time.perf_counter() - started


def make_basic_ai() -> AlphaBetaAI:
    """Dùng khi demo so sánh công bằng với MiniMax, chỉ có Alpha-Beta."""
    return AlphaBetaAI(
        use_alpha_beta=True, move_ordering=False, iterative_deepening=False,
        quiescence=False, transposition_table=False,
    )


def make_minimax_ai() -> AlphaBetaAI:
    """Negamax không cắt nhánh, tương đương MiniMax trên trò chơi tổng bằng 0."""
    return AlphaBetaAI(
        use_alpha_beta=False, move_ordering=False, iterative_deepening=False,
        quiescence=False, transposition_table=False,
    )


_default_ai = AlphaBetaAI()


def search(board: chess.Board, depth: int) -> Optional[chess.Move]:
    """API thống nhất để nhóm tích hợp."""
    return _default_ai.search(board, depth)


def get_move(board: chess.Board) -> Optional[chess.Move]:
    """API của bộ điều khiển trận đấu; mặc định giới hạn depth=3."""
    return search(board, 3)
