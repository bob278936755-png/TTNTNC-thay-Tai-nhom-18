"""Chạy thử MCTS trên bàn cờ rỗng và tình huống X có thể thắng ngay."""
from mcts import MCTSAgent
from tictactoe import TicTacToeState


def show_case(title: str, state: TicTacToeState, agent: MCTSAgent):
    print('\n' + title)
    print(state.show())
    move = agent.get_move(state)
    stats = agent.last_stats
    print(f'\nMCTS chọn ô: {move}')
    print(f'Số mô phỏng: {stats.simulations}; số nút tạo: {stats.nodes_created}')
    print(f'Thời gian: {stats.elapsed_seconds:.3f} giây')
    print('Số lượt khảo sát mỗi nước:', dict(sorted(stats.visits_by_move.items())))
    print('\nBàn cờ sau nước đi:')
    print(state.play(move).show())


if __name__ == '__main__':
    agent = MCTSAgent(simulations=1500, seed=42)
    show_case('THỬ NGHIỆM 1: BÀN CỜ RỖNG', TicTacToeState(), agent)
    win_now = TicTacToeState(('X', 'X', ' ', 'O', 'O', ' ', ' ', ' ', ' '), 'X')
    show_case('THỬ NGHIỆM 2: X SẮP THẮNG (ô 2)', win_now, agent)
