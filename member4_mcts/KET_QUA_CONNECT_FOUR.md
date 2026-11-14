# Kết quả kiểm thử MCTS trên Connect Four

## 1. Phạm vi

- Thuật toán: MCTS thuần, Selection bằng UCT, Expansion, random rollout, Backpropagation.
- Game: Connect Four 7 cột × 6 hàng, X đi trước; đánh bằng cách chọn cột 0–6.
- Giữ nguyên lõi `mcts.py` từ sprint Tic-Tac-Toe; luật Connect Four ở `connect_four.py`.
- Python 3; chỉ dùng thư viện chuẩn.

## 2. Kiểm thử tự động

Chạy: `python -m unittest -v test_mcts.py test_connect_four.py`

**21/21 bài kiểm thử đạt (OK)**, gồm 8 bài cũ của Tic-Tac-Toe/MCTS và 13 bài mới về luật Connect Four, các tình huống chiến thuật và MCTS.

Các trường hợp quan trọng: quân rơi xuống ô thấp nhất, không vượt cột, từ chối cột đầy, thắng ngang/dọc/chéo, không được đánh sau khi kết thúc, MCTS chọn được nước hợp lệ, thắng ngay và chặn đối thủ trong những thế cờ kiểm thử.

## 3. Benchmark với Random Player

Lệnh: `python benchmark_connect_four.py --games 100 --simulations 150 --seed 42`

| MCTS cầm | Thắng | Hòa | Thua | TB thời gian/nước MCTS (giây) | TB nút tạo/nước |
|---|---:|---:|---:|---:|---:|
| X | 100 | 0 | 0 | 0,0158 | 142,41 |
| O | 100 | 0 | 0 | 0,0146 | 141,85 |

- Tổng 200 ván (100 với MCTS đi trước, 100 với MCTS đi sau).
- Nút tạo là **nút trong cây MCTS**, không tính từng trạng thái mô phỏng ngẫu nhiên.
- Thời gian đo trong môi trường chạy thử, có thể khác trên máy người dùng.
- Kết quả phụ thuộc seed, số mô phỏng và đối thủ; **không chứng minh** MCTS luôn thắng hay là thuật toán tối ưu.

## 4. Đã xong và chưa xong

**Đã xong:** MCTS thuần + UCT + random rollout, thử nghiệm hai trò chơi (Tic-Tac-Toe và Connect Four), test và benchmark ngẫu nhiên.

**Chưa xong:** Policy/Value Network, PUCT, vòng lặp tự chơi để huấn luyện, dùng `python-chess` cho cờ vua, đối đầu với các thuật toán khác trong benchmark tổng nhóm.
