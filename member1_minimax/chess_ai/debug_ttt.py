import tictactoe_game as g

print("File đang dùng:", g.__file__)

def make(s):
    return [' ' if c == '.' else c for c in s.replace('|', '')]

# X đang có 2 ô hàng trên, đến lượt X: phải thắng ở ô 2
print("1. minimax:", g.minimax(make('XX.|OO.|...'), 'X'), " (đúng = 1)")
print("2. X thắng ở ô:", g.best_move(make('XX.|OO.|...'), 'X'), " (đúng = 2)")

# X sắp thắng ở ô 2, đến lượt O: phải chặn ô 2
print("3. O chặn ở ô:", g.best_move(make('XX.|.O.|...'), 'O'), " (đúng = 2)")

# bàn không bị thay đổi sau khi tìm kiếm
b = make('XO.|.X.|..O'); before = list(b)
g.best_move(b, 'X')
print("4. bàn còn nguyên:", b == before, " (đúng = True)")