# Thành viên 2 – Alpha-Beta & Depth Pruning (AI Cờ vua)

**Phạm vi:** Tuần 1–4 theo kế hoạch phân công nhóm 4 người. Tập trung **thuật toán tìm kiếm**, không thay thế bộ luật của thành viên 1 hay Value Network của thành viên 3.

## 1. Cấu trúc

```
ThanhVien2_AlphaBeta_HoanChinh/
├── alpha_beta.py            # Alpha-Beta, depth limit, Move Ordering, ID, Quiescence, TT
├── demo.py                  # Chạy thử MiniMax / Alpha-Beta / bản nâng cao
├── benchmark.py             # Đo số nút + thời gian; xuất CSV, PNG, Markdown
├── integration_example.py   # Cách nhóm gọi API + cách tích hợp Value Network
├── tests/
│   └── test_search.py       # Kiểm tra hành vi và so sánh điểm với MiniMax
├── outputs/                 # Sinh kết quả sau khi chạy benchmark
├── requirements.txt
├── README.md
├── RUN_WINDOWS.bat         # Chạy cài đặt / test / demo / benchmark trên Windows
├── VERIFICATION.md        # Phân biệt kiểm tra đã chạy và phần cần xác minh
└── Bao_cao_Thanh_vien_2.docx
```

## 2. Môi trường

- Windows 10/11, Python **3.10 trở lên** (khuyến nghị Python 3.11), VS Code.
- Cài thư viện `chess` (python-chess) và `matplotlib`.
- RAM 8 GB vẫn dùng được với depth 2–3. Depth lớn hơn có thể chạy lâu.

## 3. Chạy trên VS Code / PowerShell

Mở thư mục dự án, rồi chạy các lệnh (hoặc nhấp đúp `RUN_WINDOWS.bat` để cài, thử và chạy nhanh):

```powershell
py -m pip install -r requirements.txt
py demo.py --depth 3
py -m unittest discover -s tests -v
py benchmark.py --depths 1 2 3 --positions start italian
```

Nếu máy không có lệnh `py`, dùng `python` thay cho `py`. Tránh thêm file ảo `.venv` vào ZIP nộp nhóm.

**Để chạy nhanh ban đầu:** `py demo.py --depth 2` và `py benchmark.py --depths 1 2`.

Kết quả benchmark tự sinh trong thư mục `outputs/`:
- `benchmark.csv`: vị trí, độ sâu, thuật toán, điểm, nodes, cutoffs, giây.
- `benchmark_nodes.png`: đồ thị số nút duyệt.
- `benchmark_summary.md`: bảng giảm số nút tính từ dữ liệu thật.

**Không điền số liệu chạy giả:** Những tệp này chỉ tồn tại sau khi thực thi chương trình trên máy có cài thư viện.

## 4. Nhiệm vụ theo từng tuần

| Tuần | Công việc | File |
|---|---|---|
| 1 | Alpha-Beta, giới hạn độ sâu; so sánh với MiniMax | `alpha_beta.py`, `demo.py` |
| 2 | Move Ordering, Iterative Deepening, Quiescence, Transposition Table | `alpha_beta.py` |
| 3 | Tích hợp Value Network từ TV3 | `integration_example.py` |
| 4 | Benchmark, biểu đồ số nút / thời gian / báo cáo | `benchmark.py`, `Bao_cao_Thanh_vien_2.docx` |

## 5. Giao ước ghép nhóm

```python
import chess
from alpha_beta import search, get_move, AlphaBetaAI

board = chess.Board()
move = search(board, depth=3)  # chess.Move hoặc None
# KHÔNG tự push vào board; người gọi chịu trách nhiệm điều khiển ván.
if move is not None:
    board.push(move)
```

- `board` là `chess.Board` từ **thư viện chess**, không phải kiểu dữ liệu tự định nghĩa của nhóm. Nếu thành viên 1 viết một lớp cờ riêng, cần một lớp chuyển đổi tương đương.
- Khi có mạng Value Network của thành viên 3, đưa hàm đánh giá vào:

```python
from alpha_beta import AlphaBetaAI
from value_network import evaluate as value_evaluate  # do TV3 thống nhất tên

ai = AlphaBetaAI(evaluator=value_evaluate)
move = ai.search(board, 3)
```

**Ràng buộc bắt buộc với TV3**: `value_evaluate(board)` trả về số thực từ `-1` đến `1`, **theo phía sắp đi**. Nếu TV3 trả điểm theo quân trắng, cần đổi dấu nếu lượt quân đen; nếu trả xác suất `[0, 1]`, phải chuyển sang `[-1, 1]` và xử lý góc nhìn đúng trước khi truyền.

## 6. Cách chứng minh Alpha-Beta tốt hơn MiniMax

- MiniMax và Alpha-Beta dùng **cùng độ sâu**, **cùng hàm chấm điểm**, **cùng vị trí**, **cùng thứ tự nước đi**.
- Tắt mọi tối ưu khác ở cả hai cấu hình để chỉ đo hiệu quả **cắt nhánh**.
- Vì Alpha-Beta lược bỏ các nhánh không thể thay đổi quyết định, kết quả điểm tối ưu phải trùng MiniMax; số nút duyệt thường ít hơn hoặc bằng.
- Nhánh nâng cao tính thêm quiescence nên **không** so số nút trực tiếp với cấu hình cơ bản mà không phân biệt.

## 7. Lưu ý kỹ thuật

- Hạn chế quiescence đến `qdepth` để chạy được trên laptop phổ thông. Khi đang bị chiếu tại giới hạn, xét một lượt thoát chiếu rồi chấm tĩnh để tránh đứng yên sai luật.
- TT sử dụng chuỗi FEN; FEN không lưu đầy đủ lịch sử lặp vị trí, nên đây là mô hình học thuật chưa xử lý toàn bộ luật hòa lặp 5 lần trong mọi ngữ cảnh lịch sử. Mỗi lần gọi `search` bảng TT được xóa.
- Ở các vị trí cân bằng, những nước đi đồng điểm có thể khác nhau dù điểm MiniMax và Alpha-Beta bằng nhau.
- Thành viên 2 **không triển khai AlphaGo đầy đủ**; mô-đun là một engine tìm kiếm Alpha-Beta kết hợp vào kiến trúc chung của đề tài.

## 8. Nộp cho nhóm trưởng

Gửi trọn thư mục này hoặc ZIP. Sau khi chạy được các lệnh, gửi thêm `outputs/benchmark.csv`, `outputs/benchmark_nodes.png` và `outputs/benchmark_summary.md` cho nhóm trưởng. Không nộp `__pycache__`, `.venv`, các file thừa.
