from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

from backend.config import get_settings
from backend.models.food import FoodPrediction
from backend.utils.errors import ModelNotLoadedError
from backend.utils.image_preprocessing import mobilenetv2_input_from_bytes


class FoodMapping:
    def __init__(self, mapping_path: Optional[Path] = None):
        s = get_settings()
        self._path = Path(mapping_path or s.food_mapping_path)
        self._mapping: Optional[Dict[str, str]] = None

    def _load(self) -> Dict[str, str]:
        if self._mapping is not None:
            return self._mapping
        if not self._path.exists():
            self._mapping = {}
            return self._mapping
        try:
            self._mapping = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            self._mapping = {}
        return self._mapping

    def map_to_nutrition_name(self, class_name: str) -> str:
        """
        Map a model class label to a nutrition lookup key.
        Falls back to a cleaned, space-separated form.
        """
        m = self._load()
        key = (class_name or "").strip()
        if not key:
            return ""
        mapped = m.get(key)
        if mapped:
            return mapped
        # common training labels use underscores
        return key.replace("_", " ").strip().lower()


class FoodClassifierService:
    def __init__(self, *, model_dir: Optional[Path] = None):
        s = get_settings()
        self._model_dir = Path(model_dir or s.food_model_dir)
        self._model = None
        self._class_names: Optional[list[str]] = None
        self._load_lock = asyncio.Lock()

    async def _ensure_loaded(self) -> None:
        if self._model is not None and self._class_names is not None:
            return
        if not self._model_dir.exists():
            raise ModelNotLoadedError(details={"path": str(self._model_dir)})

        async with self._load_lock:
            if self._model is not None and self._class_names is not None:
                return

            def _load():
                import tensorflow as tf  # noqa: F401
                from ml_model.training.food_cnn import load_saved_model

                return load_saved_model(self._model_dir)

            loop = asyncio.get_event_loop()
            model, class_names = await loop.run_in_executor(None, _load)
            self._model = model
            self._class_names = class_names or []

    async def predict(self, image_bytes: bytes) -> FoodPrediction:
        await self._ensure_loaded()
        if self._model is None or not self._class_names:
            raise ModelNotLoadedError("Food model is loaded but class names are missing.")

        img_arr = mobilenetv2_input_from_bytes(image_bytes)  # (224,224,3) float32 [-1,1]

        def _infer(arr: np.ndarray) -> Tuple[str, float]:
            import tensorflow as tf

            x = tf.constant(arr, dtype=tf.float32)
            x = tf.expand_dims(x, 0)
            probs = self._model.predict(x, verbose=0)[0]
            idx = int(np.argmax(probs))
            conf = float(probs[idx]) if idx < len(probs) else 0.0
            label = self._class_names[idx] if idx < len(self._class_names) else "unknown"
            return label, conf

        loop = asyncio.get_event_loop()
        label, conf = await loop.run_in_executor(None, _infer, img_arr)
        return FoodPrediction(class_name=label, confidence=conf)

