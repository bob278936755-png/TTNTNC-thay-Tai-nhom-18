# Biên bản kiểm tra kỹ thuật

Trạng thái tại lúc đóng gói:

- **Đã kiểm tra:** `python -m compileall` trên toàn bộ mã Python, không có lỗi cú pháp.
- **Đã kiểm tra:** logic Negamax và Alpha-Beta bằng bàn cờ mô phỏng có cấu trúc cây 3 nhánh và evaluator có giá trị xác định. Ở depth 1–4, điểm Minimax bằng điểm Alpha-Beta và Alpha-Beta không duyệt nhiều nút hơn; ở depth 3 và 4 có cắt nhánh.
- **Chưa kiểm tra được trong môi trường đóng gói:** toàn bộ bài kiểm thử `tests/test_search.py`, demo và benchmark **với thư viện python-chess thật**, vì thư viện này không có sẵn và môi trường không truy cập được nguồn cài đặt.
- **Chưa có số liệu benchmark trên cờ vua thật**. Không đưa số nút hoặc thời gian mô phỏng vào báo cáo như số liệu đo thật.
- **Chưa tích hợp Value Network thật** vì chưa nhận mã/trọng số của Thành viên 3; giao diện tích hợp đã chuẩn bị trong `integration_example.py`.

Để hoàn tất kiểm tra bằng bàn cờ thật trên máy cá nhân:

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py demo.py --depth 3
py benchmark.py --depths 1 2 3 --positions start italian
```

Chỉ khi các lệnh chạy thành công mới xác nhận chương trình đạt bài kiểm thử và sử dụng số liệu kết quả của `outputs/` cho báo cáo nhóm.
