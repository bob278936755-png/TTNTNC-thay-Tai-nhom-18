"""Wrapper suy luận (inference) Value Network — HÀM HỢP ĐỒNG GIAO TIẾP.

Module này cung cấp hàm ``value_net_evaluate(board)`` với giao diện
hoàn toàn tương thích hàm ``evaluate(board)`` của Tuần 1:

    value_net_evaluate(board: chess.Board) -> float   # [-1, 1]

Thành viên 2 (Alpha-Beta) và Thành viên 4 (MCTS) import và gọi trực tiếp:

    from evaluation.inference import load_value_network, value_net_evaluate

Quy trình:
  1. Gọi ``load_value_network(path)`` MỘT LẦN khi khởi động engine.
  2. Sau đó gọi ``value_net_evaluate(board)`` bao nhiêu lần tuỳ ý.
"""
import numpy as np
import chess

from .encoding import board_to_tensor

# Mô hình được cache toàn cục (singleton) để tránh load lại mỗi lần gọi
_MODEL = None


def load_value_network(model_path: str = "value_net_finetuned.keras") -> None:
    """Tải trọng số mô hình từ file ``.keras`` / ``.h5``.

    Phải gọi hàm này trước khi sử dụng ``value_net_evaluate``.
    """
    global _MODEL
    # Import muộn để tránh lỗi khi TensorFlow chưa cài
    import tensorflow as tf
    _MODEL = tf.keras.models.load_model(model_path)
    print(f"[Thành viên 3] Đã load Value Network từ: {model_path}")


def value_net_evaluate(board: chess.Board) -> float:
    """Đánh giá thế cờ bằng Value Network.

    Returns
    -------
    float
        Giá trị trong [-1.0, 1.0] từ góc nhìn bên ĐANG ĐI (``board.turn``).

        - ``-1.0`` : bên đang đi bị chiếu hết / thua rõ.
        - `` 0.0`` : cân bằng / hòa.
        - ``+1.0`` : bên đang đi thắng rõ.

    Raises
    ------
    RuntimeError
        Nếu chưa gọi ``load_value_network()``.
    """
    if _MODEL is None:
        raise RuntimeError(
            "Chưa load mô hình! Gọi load_value_network(path) trước."
        )

    # --- Các trạng thái kết thúc: trả luôn, không cần mạng ---
    if board.is_checkmate():
        return -1.0
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0
    if board.can_claim_draw():
        return 0.0

    # --- Mã hoá & suy luận ---
    tensor = board_to_tensor(board)
    batch = np.expand_dims(tensor, axis=0)              # (1, 8, 8, 12)
    prediction = _MODEL(batch, training=False).numpy()   # (1, 1)
    return float(np.clip(prediction[0, 0], -1.0, 1.0))
