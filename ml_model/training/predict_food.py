"""
Predict food class from an image using the trained CNN.

Loads model from ml_model/saved_models/food_cnn/ and returns
class name (and optional nutrient lookup key).
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

SAVED_MODEL_DIR = PROJECT_ROOT / "ml_model" / "saved_models" / "food_cnn"


def predict_food_from_image(
    image_path: str | Path,
    model_dir: Optional[Path] = None,
) -> Tuple[str, float]:
    """
    Run food classification on a single image.

    Args:
        image_path: Path to JPEG/PNG image.
        model_dir: Directory containing model.keras and class_names.txt.

    Returns:
        (class_name, confidence). class_name can be used for nutrient lookup
        (e.g. normalize to food_name_normalized: lowercase, spaces).
    """
    import tensorflow as tf
    from ml_model.training.food_cnn import load_saved_model, IMG_SIZE

    model_dir = Path(model_dir or SAVED_MODEL_DIR)
    model, class_names = load_saved_model(model_dir)
    if not class_names:
        return "unknown", 0.0

    img = tf.io.read_file(str(image_path))
    img = tf.io.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    img = tf.expand_dims(img, 0)

    logits = model.predict(img, verbose=0)
    idx = int(np.argmax(logits[0]))
    conf = float(logits[0][idx])
    name = class_names[idx] if idx < len(class_names) else "unknown"
    return name, conf
