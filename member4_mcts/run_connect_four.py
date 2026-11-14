"""Minh họa lựa chọn nước Connect Four bằng MCTS."""
from mcts import MCTSAgent
from connect_four import ConnectFourState


def from_moves(moves: list[int]) -> ConnectFourState:
    board = ConnectFourState()
    for col in moves:
        board = board.play(col)
    return board


def demo(title: str, state: ConnectFourState, simulations: int = 300):
    agent = MCTSAgent(simulations=simulations, seed=42)
    print(f'\n=== {title} ===')
    print(state.show())
    print('Lượt:', state.current_player)
    move = agent.get_move(state)
    stats = agent.last_stats
    print('MCTS chọn cột:', move)
    print(f'Mô phỏng: {stats.simulations}; Nút tạo: {stats.nodes_created}; '
          f'Thời gian: {stats.elapsed_seconds:.3f} giây')
    print('Số lượt thăm theo cột:', dict(sorted(stats.visits_by_move.items())))
    print('Sau nước đi:\n' + state.play(move).show())


if __name__ == '__main__':
    demo('Bàn cờ rỗng', ConnectFourState())
    # X có 3 quân thẳng đứng ở cột 3, tới lượt X: đánh cột 3 thắng ngay.
    demo('X có thể thắng ngay tại cột 3', from_moves([3, 2, 3, 2, 3, 4]), 800)
