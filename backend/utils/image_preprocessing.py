from __future__ import annotations

import io
from typing import Tuple

import numpy as np
from PIL import Image


MODEL_INPUT_SIZE: Tuple[int, int] = (224, 224)


def load_rgb(image_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def resize_to_model(img: Image.Image, size: Tuple[int, int] = MODEL_INPUT_SIZE) -> Image.Image:
    return img.resize(size, Image.Resampling.LANCZOS)


def to_numpy_uint8(img: Image.Image) -> np.ndarray:
    return np.asarray(img, dtype=np.uint8)


def mobilenetv2_input_from_bytes(image_bytes: bytes, size: Tuple[int, int] = MODEL_INPUT_SIZE) -> np.ndarray:
    """
    Produce a MobileNetV2-compatible input tensor (H,W,3) float32 in [-1, 1].
    Equivalent to `tf.keras.applications.mobilenet_v2.preprocess_input` on uint8 0..255.
    """
    img = resize_to_model(load_rgb(image_bytes), size=size)
    arr = np.asarray(img, dtype=np.float32)
    # MobileNetV2 preprocess: scale to [-1, 1]
    arr = (arr / 127.5) - 1.0
    return arr

