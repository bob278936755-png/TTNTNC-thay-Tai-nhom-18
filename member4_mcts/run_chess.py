import chess
from chess_adapter import choose_chess_move


def main():
    board = chess.Board()
    print('Ban co ban dau:')
    print(board)
    move, stats = choose_chess_move(
        board, simulations=40, rollout_plies=48, seed=42,
    )
    print('\nAI chon nuoc:', move.uci())
    print('Co hop le:', move in board.legal_moves)
    print('So mo phong:', stats.simulations)
    print('So nut tao:', stats.nodes_created)
    print('Thoi gian:', round(stats.elapsed_seconds, 3), 'giay')
    board.push(move)
    print('\nBan co sau khi AI di:')
    print(board)


if __name__ == '__main__':
    main()
