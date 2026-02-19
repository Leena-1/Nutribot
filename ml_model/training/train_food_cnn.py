"""
Train the food classification CNN on Food-101 (or a subset).

Usage:
  Place Food-101 data under: datasets/food101/images/
  (Subfolders named by food class, each containing images.)

  python -m ml_model.training.train_food_cnn --epochs 5 --batch_size 32

If Food-101 is not present, run with --dry_run to print expected structure.
"""

import argparse
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tensorflow as tf
from ml_model.training.food_cnn import build_food_cnn, IMG_SIZE

FOOD101_IMAGES = PROJECT_ROOT / "datasets" / "food101" / "images"
SAVED_MODELS_DIR = PROJECT_ROOT / "ml_model" / "saved_models" / "food_cnn"


def get_class_names(images_dir: Path) -> list:
    """Discover class names from subfolder names under images_dir."""
    if not images_dir.exists():
        return []
    return sorted([d.name for d in images_dir.iterdir() if d.is_dir()])


def make_dataset_simple(images_dir: Path, batch_size: int, is_training: bool, subset: str = "train"):
    """Build tf.data.Dataset from images_dir/<class_name>/*.jpg with 80/20 split."""
    class_names = get_class_names(images_dir)
    if not class_names:
        return None, []

    class_to_idx = {n: i for i, n in enumerate(class_names)}
    exts = ("*.jpg", "*.jpeg", "*.png")
    all_paths = []
    for ext in exts:
        all_paths.extend(images_dir.glob(f"*/{ext}"))
    all_paths = [str(p) for p in all_paths]
    if not all_paths:
        return None, class_names

    random.seed(42)
    random.shuffle(all_paths)
    n = len(all_paths)
    train_n = int(n * 0.8)
    paths = all_paths[:train_n] if subset == "train" else all_paths[train_n:]
    labels = [class_to_idx[Path(p).parent.name] for p in paths]

    def decode_and_preprocess(path, label):
        img = tf.io.read_file(path)
        img = tf.io.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, IMG_SIZE)
        img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
        return img, tf.cast(label, tf.int32)

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(decode_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    if is_training:
        ds = ds.shuffle(buffer_size=min(len(paths), 2048), seed=42)
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds, class_names


def main():
    parser = argparse.ArgumentParser(description="Train food CNN on Food-101")
    parser.add_argument("--data_dir", type=str, default=str(FOOD101_IMAGES), help="Path to food101/images")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--dry_run", action="store_true", help="Only print structure and exit")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if args.dry_run:
        print(f"Expected structure: {data_dir}/<class_name>/*.jpg")
        print("Download Food-101 from: https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/")
        return 0

    train_ds, class_names = make_dataset_simple(data_dir, args.batch_size, True, "train")
    val_ds, _ = make_dataset_simple(data_dir, args.batch_size, False, "val")
    if train_ds is None or not class_names:
        print("No data found. Use --dry_run to see expected structure.")
        return 1

    num_classes = len(class_names)
    model = build_food_cnn(num_classes)
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    (SAVED_MODELS_DIR / "class_names.txt").write_text("\n".join(class_names), encoding="utf-8")

    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs)
    model.save(SAVED_MODELS_DIR / "model.keras")
    print(f"Model saved to {SAVED_MODELS_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
