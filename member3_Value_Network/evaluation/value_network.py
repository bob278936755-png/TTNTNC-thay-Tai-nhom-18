"""Kiến trúc CNN / ResNet Value Network cho AI Cờ vua.

Hai phiên bản:
  1. ``build_baseline_cnn``   — CNN 3 tầng đơn giản (Tuần 2)
  2. ``build_resnet_value_net`` — Deep Residual Network kiểu AlphaZero (Tuần 3)

Cả hai đều:
  - Nhận đầu vào  (8, 8, 12)
  - Trả ra 1 giá trị kích hoạt ``tanh``  → [-1, 1]
  - Dùng MSE loss (vì bài toán hồi quy giá trị liên tục)
"""
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, regularizers


# ======================================================================
# Tuần 2: Baseline CNN
# ======================================================================

def build_baseline_cnn(input_shape: tuple = (8, 8, 12)) -> models.Model:
    """Mạng CNN 3 tầng cơ bản — dùng kiểm thử pipeline và làm baseline.

    Kiến trúc:
      Conv 64 → BN → ReLU
      Conv 128 → BN → ReLU
      Conv 128 → BN → ReLU
      Flatten → Dense 128 ReLU → Dense 1 tanh
    """
    inputs = layers.Input(shape=input_shape, name="board_input")

    x = layers.Conv2D(64, (3, 3), padding="same", activation="relu")(inputs)
    x = layers.BatchNormalization()(x)

    x = layers.Conv2D(128, (3, 3), padding="same", activation="relu")(inputs)
    x = layers.BatchNormalization()(x)

    x = layers.Conv2D(128, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)

    x = layers.Flatten()(x)
    x = layers.Dense(128, activation="relu")(x)
    outputs = layers.Dense(1, activation="tanh", name="value_output")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="Baseline_CNN")
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-3),
        loss="mean_squared_error",
        metrics=["mae"],
    )
    return model


# ======================================================================
# Tuần 3: Residual Value Network (AlphaZero-style)
# ======================================================================

def _residual_block(
    x: tf.Tensor, filters: int, l2: float = 1e-4,
) -> tf.Tensor:
    """Khối tàn dư: 2 × (Conv → BN → ReLU) + skip connection."""
    shortcut = x

    x = layers.Conv2D(
        filters, (3, 3), padding="same", use_bias=False,
        kernel_regularizer=regularizers.l2(l2),
    )(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)

    x = layers.Conv2D(
        filters, (3, 3), padding="same", use_bias=False,
        kernel_regularizer=regularizers.l2(l2),
    )(x)
    x = layers.BatchNormalization()(x)

    x = layers.add([shortcut, x])
    x = layers.ReLU()(x)
    return x


def build_resnet_value_net(
    input_shape: tuple = (8, 8, 12),
    num_res_blocks: int = 4,
    filters: int = 128,
    l2: float = 1e-4,
    dropout: float = 0.3,
    lr: float = 5e-4,
) -> models.Model:
    """Deep Residual Value Network — phiên bản tinh chỉnh chống overfitting.

    Kiến trúc:
      Initial Conv 128 → BN → ReLU
      N × Residual Block (mặc định 4)
      Value Head: Conv 1×1 32 → BN → ReLU → Flatten
                  → Dense 128 ReLU + Dropout → Dense 1 tanh

    Regularization:
      - L2 weight decay trên tất cả Conv layers
      - Batch Normalization sau mỗi Conv
      - Dropout ở tầng Fully Connected
    """
    inputs = layers.Input(shape=input_shape, name="board_input")

    # --- Initial convolution ---
    x = layers.Conv2D(
        filters, (3, 3), padding="same", use_bias=False,
        kernel_regularizer=regularizers.l2(l2),
    )(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)

    # --- Residual tower ---
    for _ in range(num_res_blocks):
        x = _residual_block(x, filters, l2)

    # --- Value head ---
    x = layers.Conv2D(32, (1, 1), padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.Flatten()(x)

    x = layers.Dense(
        128, activation="relu",
        kernel_regularizer=regularizers.l2(l2),
    )(x)
    x = layers.Dropout(dropout)(x)

    outputs = layers.Dense(1, activation="tanh", name="value_output")(x)

    model = models.Model(
        inputs=inputs, outputs=outputs,
        name="Residual_Value_Net",
    )
    model.compile(
        optimizer=optimizers.Adam(learning_rate=lr),
        loss="mean_squared_error",
        metrics=["mae"],
    )
    return model
