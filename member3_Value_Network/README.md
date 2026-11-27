# AI Cờ vua – Nhóm 18 · Thành viên 3: Position Evaluation & Value Network

Môn Trí tuệ Nhân tạo Nâng cao. Phần của Thành viên 3: chấm điểm thế cờ dở dang.

## Giao diện chung (hợp đồng giữa các thành viên)

```python
# Tuần 1: Hàm heuristic thủ công
from evaluation import evaluate
evaluate(board: chess.Board) -> float   # trong [-1, 1], góc nhìn BÊN ĐANG ĐI

# Tuần 3: Value Network (thay thế / bổ sung cho evaluate)
from evaluation.inference import load_value_network, value_net_evaluate
load_value_network("checkpoints/value_net_finetuned.keras")
value_net_evaluate(board: chess.Board) -> float   # trong [-1, 1], góc nhìn BÊN ĐANG ĐI
```

- `+1`: bên đang đi thắng chắc, `-1`: bên đang đi bị chiếu hết, `0`: cân bằng/hòa.
- Dùng được trực tiếp trong negamax: không cần đổi dấu theo màu quân.

## Cấu trúc thư mục

```
member3_Value_Network/
├── evaluation/              # Package chính
│   ├── __init__.py
│   ├── handcrafted.py       # [Tuần 1] Hàm đánh giá 5 yếu tố
│   ├── material.py          # Vật chất & hàm tiện ích
│   ├── pst.py               # Piece-square tables
│   ├── king_safety.py       # An toàn Vua
│   ├── mobility.py          # Cơ động
│   ├── pawn_structure.py    # Cấu trúc Tốt
│   ├── encoding.py          # [Tuần 2] Mã hoá Board → Tensor 8×8×12
│   ├── data_pipeline.py     # [Tuần 2] Thu thập & tiền xử lý dữ liệu
│   ├── value_network.py     # [Tuần 2-3] Kiến trúc CNN / ResNet
│   └── inference.py         # [Tuần 3] Wrapper suy luận (hợp đồng giao tiếp)
├── scripts/
│   ├── demo_eval.py         # [Tuần 1] Demo hàm heuristic
│   ├── train_baseline.py    # [Tuần 2] Huấn luyện Baseline CNN
│   ├── train_resnet.py      # [Tuần 3] Huấn luyện ResNet + chống overfitting
│   └── benchmark.py         # [Tuần 4] Benchmark, đối đầu, báo cáo
├── tests/
│   ├── test_evaluation.py   # [Tuần 1] Tests hàm heuristic
│   └── test_value_network.py # [Tuần 2-4] Tests encoding, data, hợp đồng
├── checkpoints/             # (git-ignored) Nơi lưu model .keras
├── requirements.txt
├── .gitignore
└── README.md
```

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy từng tuần

```bash
# Tuần 1: Demo hàm heuristic
python -m scripts.demo_eval

# Tuần 2: Huấn luyện Baseline CNN
python -m scripts.train_baseline

# Tuần 3: Huấn luyện ResNet (chống overfitting)
python -m scripts.train_resnet

# Tuần 4: Benchmark & Báo cáo
python -m scripts.benchmark

# Chạy toàn bộ tests
pytest tests/ -v
```

## Hướng dẫn tích hợp cho Thành viên 2 & 4

### Thành viên 2 (Alpha-Beta Pruning)

```python
from evaluation.inference import load_value_network, value_net_evaluate

load_value_network("member3_Value_Network/checkpoints/value_net_finetuned.keras")

# Tại leaf node (depth == 0) trong Alpha-Beta:
score = value_net_evaluate(board)  # thay cho evaluate(board)
```

**Khuyến nghị**: dùng Transposition Table để cache điểm đã tính.

### Thành viên 4 (MCTS / AlphaZero)

```python
from evaluation.inference import load_value_network, value_net_evaluate

load_value_network("member3_Value_Network/checkpoints/value_net_finetuned.keras")

# Trong MCTS, thay thế random rollout bằng:
value = value_net_evaluate(leaf_board)  # → backpropagate Q(s,a)
```

## Tiến độ

- [x] Tuần 1: hàm đánh giá thủ công (vật chất, piece-square, an toàn Vua, cơ động, cấu trúc Tốt)
- [x] Tuần 2: dữ liệu tổng hợp + Baseline CNN Value Network
- [x] Tuần 3: ResNet, Data Augmentation, L2/Dropout/EarlyStopping, hàm hợp đồng
- [x] Tuần 4: benchmark tốc độ, tương quan, đối đầu, báo cáo tổng kết
