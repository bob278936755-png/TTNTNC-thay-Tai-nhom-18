import chess
import chess_minimax as cm

print("File đang dùng:", cm.__file__)       # QUAN TRỌNG NHẤT
print("MATE =", cm.MATE)
print("material(thế đầu) =", cm.material(chess.Board()))

b = chess.Board("6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1")
for m in b.legal_moves:
    b.push(m)
    print(m.uci(), cm.minimax(b, 0, False))
    b.pop()
print("best_move =", cm.best_move(b, 1))