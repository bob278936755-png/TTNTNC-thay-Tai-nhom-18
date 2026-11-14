import pytest
import tictactoe_game as g

winner, moves, minimax, best_move = g.winner, g.moves, g.minimax, g.best_move


def make(s):
    """Dựng bàn cờ từ chuỗi: 'XX.|.O.|...' (dấu . là ô trống)."""
    return [' ' if c == '.' else c for c in s.replace('|', '')]


LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]


def test_loaded_the_right_module():
    assert "tictactoe_game" in g.__file__


# ---------- 1. Hàm phụ trợ ----------
@pytest.mark.parametrize("line", LINES)
@pytest.mark.parametrize("p", ['X', 'O'])
def test_winner_detects_all_8_lines(line, p):
    b = [' '] * 9
    for i in line:
        b[i] = p
    assert winner(b) == p


def test_winner_none_on_empty_and_draw():
    assert winner(make('...|...|...')) is None
    assert winner(make('XOX|XOO|OXX')) is None


def test_moves():
    assert moves(make('...|...|...')) == list(range(9))
    assert moves(make('XXX|OO.|...')) == [5, 6, 7, 8]
    assert moves(make('XOX|XOO|OXX')) == []


# ---------- 2. Giá trị MiniMax tính tay được ----------
def test_minimax_terminal_values():
    assert minimax(make('XXX|OO.|...'), 'O') == +1
    assert minimax(make('OOO|XX.|X..'), 'X') == -1
    assert minimax(make('XOX|XOO|OXX'), 'X') == 0


def test_minimax_one_move_to_win():
    assert minimax(make('XX.|OO.|...'), 'X') == +1
    assert minimax(make('XX.|OO.|...'), 'O') == -1


# ---------- 3. best_move chọn đúng nước ----------
def test_takes_winning_move():
    assert best_move(make('XX.|OO.|...'), 'X') == 2


def test_blocks_opponent_win():
    assert best_move(make('XX.|.O.|...'), 'O') == 2


def test_best_move_returns_empty_cell():
    b = make('XO.|.X.|..O')
    assert best_move(b, 'X') in moves(b)


def test_best_move_does_not_modify_board():
    b = make('XO.|.X.|..O')
    before = list(b)
    best_move(b, 'X')
    assert b == before


# ---------- 4. Test vét cạn: không bao giờ thua ----------
def ai_never_loses(b, ai, turn):
    w = winner(b)
    if w:
        return w == ai
    if not moves(b):
        return True
    other = 'O' if ai == 'X' else 'X'
    if turn == ai:
        m = best_move(b, ai)
        b[m] = ai
        ok = ai_never_loses(b, ai, other)
        b[m] = ' '
        return ok
    for m in moves(b):
        b[m] = other
        ok = ai_never_loses(b, ai, ai)
        b[m] = ' '
        if not ok:
            return False
    return True


def test_x_never_loses():
    assert ai_never_loses([' '] * 9, 'X', 'X')


def test_o_never_loses():
    assert ai_never_loses([' '] * 9, 'O', 'X')