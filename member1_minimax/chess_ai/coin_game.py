def minimax(n, maximizing):
    """Trả về +1 nếu máy (Max) thắng, -1 nếu thua, theo chơi tối ưu."""
    if n == 0:
        # Người vừa bốc xu cuối đã thắng. Người đang đến lượt là bên THUA.
        return -1 if maximizing else +1

    scores = [minimax(n - take, not maximizing)
              for take in (1, 2, 3) if take <= n]
    return max(scores) if maximizing else min(scores)

def best_take(n):
    """Chọn số xu cần bốc cho máy."""
    best, best_score = None, -2
    for take in (1, 2, 3):
        if take <= n:
            score = minimax(n - take, False)   # sau nước của máy là lượt đối thủ
            if score > best_score:
                best, best_score = take, score
    return best