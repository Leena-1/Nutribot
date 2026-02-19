"""
CNN model for food image classification (Food-101 style).

Uses transfer learning with MobileNetV2 for mobile-friendly inference.
Output: class index or food name for lookup in unified nutrient table.
"""

import tensorflow as tf
from pathlib import Path
from typing import Optional, Tuple

# Image size expected by the model
IMG_SIZE: Tuple[int, int] = (224, 224)
INPUT_SHAPE: Tuple[int, int, int] = (*IMG_SIZE, 3)


def build_food_cnn(
    num_classes: int,
    input_shape: Tuple[int, int, int] = INPUT_SHAPE,
    trainable_layers: int = 20,
) -> tf.keras.Model:
    """
    Build a food classification model using MobileNetV2 backbone.

    Args:
        num_classes: Number of food classes (e.g. 101 for Food-101).
        input_shape: (height, width, channels).
        trainable_layers: Number of top layers to unfreeze for fine-tuning.

    Returns:
        Compiled Keras Model.
    """
    base = tf.keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
        pooling="avg",
    )
    base.trainable = True
    for layer in base.layers[:-trainable_layers]:
        layer.trainable = False

    inputs = tf.keras.layers.Input(shape=input_shape)
    x = base(inputs, training=False)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def load_saved_model(model_dir: Path) -> Tuple[tf.keras.Model, list]:
    """
    Load a saved Keras model and its class names from model_dir.

    Expects:
        model_dir/model.keras (or model.h5)
        model_dir/class_names.txt (one label per line)

    Returns:
        (model, class_names list)
    """
    model_dir = Path(model_dir)
    for name in ("model.keras", "model.h5", "saved_model.pb"):
        path = model_dir / name if name != "saved_model.pb" else model_dir
        if name == "saved_model.pb" and (path / "saved_model.pb").exists():
            model = tf.keras.models.load_model(path)
            break
        if path.exists():
            model = tf.keras.models.load_model(path)
            break
    else:
        raise FileNotFoundError(f"No model found in {model_dir}")

    class_names_path = model_dir / "class_names.txt"
    if class_names_path.exists():
        class_names = [line.strip() for line in open(class_names_path, encoding="utf-8") if line.strip()]
    else:
        class_names = []

    return model, class_names
