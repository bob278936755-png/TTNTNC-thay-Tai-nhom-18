import pytest
from coin_game import minimax, best_take

LOSING = [4, 8, 12, 16, 20]                     # n chia hết cho 4
WINNING = [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15]


# ---------- 1. Điều kiện dừng ----------
def test_base_case_max_to_move_loses():
    # Hết xu và đến lượt Max: đối thủ đã bốc xu cuối nên Max thua
    assert minimax(0, True) == -1


def test_base_case_min_to_move_wins():
    assert minimax(0, False) == +1


# ---------- 2. Thế nhỏ tính tay được ----------
@pytest.mark.parametrize("n", [1, 2, 3])
def test_can_take_all_and_win(n):
    # Còn 1-3 xu: bốc hết là thắng ngay
    assert minimax(n, True) == +1


def test_four_coins_is_lost():
    # Bốc 1, 2, 3 đều để lại 3, 2, 1 xu cho đối thủ bốc hết
    assert minimax(4, True) == -1


# ---------- 3. Quy luật chia hết cho 4 ----------
@pytest.mark.parametrize("n", LOSING)
def test_multiples_of_four_are_losing(n):
    assert minimax(n, True) == -1


@pytest.mark.parametrize("n", WINNING)
def test_other_positions_are_winning(n):
    assert minimax(n, True) == +1


# ---------- 4. Đối xứng Max / Min ----------
@pytest.mark.parametrize("n", range(0, 16))
def test_symmetry_between_max_and_min(n):
    # Cùng một thế, đổi bên thì điểm phải đảo dấu
    assert minimax(n, True) == -minimax(n, False)


# ---------- 5. best_take chọn đúng nước ----------
@pytest.mark.parametrize("n", WINNING)
def test_best_take_leaves_multiple_of_four(n):
    take = best_take(n)
    assert 1 <= take <= 3
    assert (n - take) % 4 == 0


@pytest.mark.parametrize("n", LOSING)
def test_best_take_is_legal_even_when_losing(n):
    take = best_take(n)
    assert take in (1, 2, 3)


def test_best_take_never_exceeds_remaining():
    assert best_take(1) == 1
    assert best_take(2) in (1, 2)


def test_best_take_with_no_coins_returns_none():
    assert best_take(0) is None


# ---------- 6. Test vét cạn: AI đã thắng được thì không thua ----------
def ai_always_wins(n, ai_turn):
    """Đối thủ thử MỌI nước đi; AI luôn đi best_take. Trả True nếu AI thắng mọi nhánh."""
    if n == 0:
        return not ai_turn                      # người vừa bốc xu cuối thắng;
                                                # nếu đang là lượt AI thì AI thua
    if ai_turn:
        return ai_always_wins(n - best_take(n), False)
    return all(ai_always_wins(n - take, True)
               for take in (1, 2, 3) if take <= n)


@pytest.mark.parametrize("n", WINNING)
def test_ai_moving_first_from_winning_position_never_loses(n):
    assert ai_always_wins(n, ai_turn=True)


@pytest.mark.parametrize("n", LOSING)
def test_ai_loses_against_perfect_opponent_from_losing_position(n):
    # Thế thua mà đối thủ chơi hoàn hảo thì AI không thể thắng
    assert not ai_always_wins(n, ai_turn=True)