# AI Cờ vua – Nhóm 18 · Thành viên 3: Position Evaluation & Value Network

Môn Trí tuệ Nhân tạo Nâng cao. Phần của Thành viên 3: chấm điểm thế cờ dở dang.

## Giao diện chung (hợp đồng giữa các thành viên)

```python
from evaluation import evaluate
evaluate(board: chess.Board) -> float   # trong [-1, 1], góc nhìn BÊN ĐANG ĐI
```

- `+1`: bên đang đi thắng chắc, `-1`: bên đang đi bị chiếu hết, `0`: cân bằng/hòa.
- Dùng được trực tiếp trong negamax: không cần đổi dấu theo màu quân.

## Cài đặt

```bash
pip install -r requirements.txt
pytest -q
```

## Tiến độ

- [x] Tuần 1: hàm đánh giá thủ công (vật chất, piece-square, an toàn Vua, cơ động, cấu trúc Tốt)
- [ ] Tuần 2: dữ liệu Lichess/Stockfish + CNN Value Network
- [ ] Tuần 3: tinh chỉnh, chống overfitting, tích hợp tìm kiếm
- [ ] Tuần 4: benchmark và báo cáo
