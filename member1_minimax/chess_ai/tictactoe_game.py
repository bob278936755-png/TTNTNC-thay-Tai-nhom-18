WIN_LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def winner(b):
    for i, j, k in WIN_LINES:
        if b[i] != ' ' and b[i] == b[j] == b[k]:
            return b[i]
    return None

def moves(b):
    return [i for i in range(9) if b[i] == ' ']

def minimax(b, player):
    """X là Max. Trả về +1 (X thắng), -1 (O thắng), 0 (hòa)."""
    w = winner(b)
    if w == 'X': return +1
    if w == 'O': return -1
    if not moves(b): return 0

    nxt = 'O' if player == 'X' else 'X'
    scores = []
    for m in moves(b):
        b[m] = player                    # thử đi
        scores.append(minimax(b, nxt))
        b[m] = ' '                       # hoàn tác (bắt buộc!)
    return max(scores) if player == 'X' else min(scores)

def best_move(b, player):
    nxt = 'O' if player == 'X' else 'X'
    best, best_score = None, None
    for m in moves(b):
        b[m] = player
        s = minimax(b, nxt)
        b[m] = ' '
        better = best_score is None or (s > best_score if player == 'X' else s < best_score)
        if better:
            best, best_score = m, s
    return best