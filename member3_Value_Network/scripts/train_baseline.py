"""TUẦN 2 — Thu thập dữ liệu & huấn luyện Baseline CNN Value Network.

Chạy:  python -m scripts.train_baseline  (từ thư mục ``member3_Value_Network``)

Kết quả:
  - In ``model.summary()``
  - Huấn luyện 5 epoch trên dữ liệu synthetic
  - Lưu mô hình ra ``checkpoints/value_net_baseline.keras``
"""
import os
import sys

# Cho phép import package ``evaluation`` khi chạy bằng ``python -m scripts.train_baseline``
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from evaluation.data_pipeline import generate_synthetic_data
from evaluation.value_network import build_baseline_cnn

CHECKPOINT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checkpoints"
)


def main() -> None:
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    # --- 1. Tạo dữ liệu synthetic ---
    print("[Tuần 2] Tạo dữ liệu synthetic (ván ngẫu nhiên + nhãn heuristic)...")
    X_train, y_train = generate_synthetic_data(num_games=300, seed=42)
    print(f"  → Số mẫu: {X_train.shape[0]}  |  Shape: {X_train.shape}")

    # --- 2. Xây dựng mô hình ---
    print("[Tuần 2] Khởi tạo Baseline CNN Value Network...")
    model = build_baseline_cnn()
    model.summary()

    # --- 3. Huấn luyện ---
    print("[Tuần 2] Huấn luyện 5 epochs...")
    model.fit(X_train, y_train, epochs=5, batch_size=64, validation_split=0.2)

    # --- 4. Lưu ---
    save_path = os.path.join(CHECKPOINT_DIR, "value_net_baseline.keras")
    model.save(save_path)
    print(f"[Tuần 2] ✓ Đã lưu mô hình: {save_path}")


if __name__ == "__main__":
    main()
