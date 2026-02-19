"""
Dataset preprocessing pipeline for AI Food Nutrition & Disease Risk Prediction.

Exposes:
- run_pipeline: Run full clean + merge + unified table generation
- get_config: Get current preprocessing config
"""

from ml_model.preprocessing.merge_pipeline import run_pipeline
from ml_model.preprocessing.config import get_config

__all__ = ["run_pipeline", "get_config"]
