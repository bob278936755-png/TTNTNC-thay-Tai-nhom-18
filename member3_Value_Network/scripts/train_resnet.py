"""TUẦN 3 — Tinh chỉnh ResNet Value Network + Data Augmentation + Chống Overfitting.

Chạy:  python -m scripts.train_resnet  (từ thư mục ``member3_Value_Network``)

Kết quả:
  - Huấn luyện ResNet trên dữ liệu augmented
  - Early Stopping + ReduceLR + ModelCheckpoint
  - Lưu mô hình tốt nhất ra ``checkpoints/value_net_finetuned.keras``
  - Demo hàm ``value_net_evaluate`` (hợp đồng giao tiếp)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from tensorflow.keras import callbacks as cb

from evaluation.data_pipeline import generate_synthetic_data, augment_horizontal_flip
from evaluation.value_network import build_resnet_value_net
from evaluation.inference import load_value_network, value_net_evaluate

import chess

CHECKPOINT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checkpoints"
)


def main() -> None:
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    save_path = os.path.join(CHECKPOINT_DIR, "value_net_finetuned.keras")

    # --- 1. Dữ liệu + Data Augmentation ---
    print("[Tuần 3] Tạo dữ liệu synthetic...")
    X_raw, y_raw = generate_synthetic_data(num_games=400, seed=123)
    print(f"  → Mẫu gốc : {X_raw.shape[0]}")

    X_train, y_train = augment_horizontal_flip(X_raw, y_raw)
    print(f"  → Sau augmentation (lật trục dọc): {X_train.shape[0]} mẫu")

    # --- 2. Xây dựng ResNet ---
    print("[Tuần 3] Khởi tạo Residual Value Network (4 blocks, L2, Dropout)...")
    model = build_resnet_value_net(num_res_blocks=4, dropout=0.3)
    model.summary()

    # --- 3. Callbacks chống Overfitting ---
    custom_callbacks = [
        cb.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True,
            verbose=1,
        ),
        cb.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=2, min_lr=1e-6,
            verbose=1,
        ),
        cb.ModelCheckpoint(
            save_path, monitor="val_loss", save_best_only=True, verbose=1,
        ),
    ]

    # --- 4. Huấn luyện ---
    print("[Tuần 3] Huấn luyện (tối đa 20 epochs, EarlyStopping)...")
    history = model.fit(
        X_train, y_train,
        epochs=20,
        batch_size=64,
        validation_split=0.2,
        callbacks=custom_callbacks,
    )

    # --- 5. Demo hàm hợp đồng giao tiếp ---
    print("\n[Tuần 3] Kiểm tra hàm value_net_evaluate (hợp đồng giao tiếp):")
    load_value_network(save_path)

    test_cases = {
        "Thế khai cuộc":    chess.Board(),
        "Trắng hơn Hậu":   chess.Board("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        "Đen hơn Xe":       chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/1NBQKBN1 w - - 0 1"),
    }
    for name, board in test_cases.items():
        v = value_net_evaluate(board)
        print(f"  {name:20s} → {v:+.4f}")

    print(f"\n[Tuần 3] ✓ Mô hình đã lưu: {save_path}")
    print("[Tuần 3] ✓ Hàm value_net_evaluate(board) sẵn sàng bàn giao cho TV2 & TV4.")


if __name__ == "__main__":
    main()
