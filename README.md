# Sprint MCTS — Tic-Tac-Toe + Connect Four (Thành viên 4)

**Môn:** Trí tuệ nhân tạo nâng cao — đồ án AI cờ vua (nhóm 4 người).  
**Vai trò:** Thành viên 4 — Monte Carlo Tree Search (MCTS), dự kiến mở rộng sang MCTS + Policy/Value Network và Self-Play.  
**Phạm vi đã viết:** MCTS thuần (UCT + rollout ngẫu nhiên), luật Tic-Tac-Toe và Connect Four, các ví dụ, test và benchmark.  
**Yêu cầu:** Python **3.10+**, không cần thư viện ngoài.

## Cấu trúc

| File | Công dụng |
|---|---|
| `mcts.py` | Lõi MCTS dùng chung cho các trò chơi hai người luân phiên lượt; giữ nguyên từ sprint trước. |
| `tictactoe.py` | Luật và trạng thái Tic-Tac-Toe (3×3). |
| `run_demo.py` | Ví dụ MCTS chọn nước trong Tic-Tac-Toe. |
| `test_mcts.py` | Bộ 8 kiểm thử cũ của Tic-Tac-Toe/MCTS. |
| `benchmark.py` | MCTS đấu Random trên Tic-Tac-Toe. |
| `connect_four.py` | **Mới:** luật Connect Four 7 cột × 6 hàng, đánh vào cột 0–6, quân rơi xuống ô thấp nhất. |
| `run_connect_four.py` | **Mới:** minh họa MCTS chơi Connect Four. |
| `test_connect_four.py` | **Mới:** kiểm thử nước đi, thắng ngang/dọc/chéo, MCTS và chống nước đi sai. |
| `benchmark_connect_four.py` | **Mới:** MCTS đấu Random ở cả hai màu; đo số nút, thời gian và kết quả. |

## Hướng dẫn chạy trong PyCharm

1. Giải nén ZIP, mở **thư mục chứa các file `.py`** bằng PyCharm.
2. Chọn Python Interpreter hợp lệ (Python 3.10 trở lên).
3. Bấm chuột phải file `run_connect_four.py` → **Run** để xem demo.
4. Để chạy các lệnh dưới đây, mở **Terminal** ngay trong thư mục vừa mở.

```bash
# Test cả hai trò chơi
python -m unittest -v test_mcts.py test_connect_four.py

# Demo Connect Four
python run_connect_four.py

# Đối đầu nhanh (10 ván cho mỗi màu, 150 mô phỏng/nước)
python benchmark_connect_four.py

# Nếu muốn 100 ván cho mỗi màu (có thể chạy lâu)
python benchmark_connect_four.py --games 100 --simulations 300 --seed 42

# Vẫn có thể chạy lại phần Tic-Tac-Toe
python run_demo.py
python benchmark.py --games 100 --simulations 300 --seed 42
```

Trên Windows, nếu `python` không nhận lệnh, thử `py` (sau khi đảm bảo đang sử dụng đúng môi trường Python).

## MCTS hoạt động ra sao?

Bốn bước: **Selection** chọn nhánh UCT → **Expansion** mở một nước mới → **Simulation** đánh ngẫu nhiên đến cuối ván → **Backpropagation** cộng số lượt thăm và điểm.  
UCT cân bằng khai thác nước đi đã có kết quả tốt và khám phá nước ít được thử. Thưởng: thắng **1**, hòa **0,5**, thua **0**.  
Kết quả MCTS có tính ngẫu nhiên. Với ngân sách mô phỏng hạn chế, nó **không được bảo đảm** thắng mọi tình huống.

## Giao diện chung & việc của tuần sau

- Cả `TicTacToeState` và `ConnectFourState` đều có `current_player`, `legal_moves()`, `play(move)`, `is_terminal()`, `reward(player)`.
- `MCTSAgent(simulations=300, seed=42).get_move(state)` trả **chỉ số ô 0–8** trong Tic-Tac-Toe và **chỉ số cột 0–6** trong Connect Four.
- `nodes_created`: số nút cây MCTS tạo ra, **không tính** mọi trạng thái trong rollout.
- **Chưa có** Value Network, Policy Network, PUCT, Self-Play huấn luyện hay adapter `python-chess`.
- Khi ghép dự án cờ vua, cần adapter để lời gọi `get_move(board)` nhận `chess.Board` và trả `chess.Move`. Không sử dụng trực tiếp mã cột Connect Four cho cờ vua.
- Trước khi tích hợp Value Network của thành viên 3, cần thống nhất ngữ nghĩa giá trị `[-1, 1]` theo người chơi đang đi.

## Lưu ý thực nghiệm

Nếu muốn so sánh có ý nghĩa, giữ cùng máy tính, số mô phỏng, seed và số ván. Benchmark Connect Four có thể nặng hơn Tic-Tac-Toe nhiều lần. Nên chạy nhanh trước, sau đó tăng dần `--games` và `--simulations`.
