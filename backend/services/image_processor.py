"""
Optimized image preprocessing for OCR and ML inference.
"""

import io
from typing import Tuple
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image(image_bytes: bytes, target_size: Tuple[int, int] = (720, 720)) -> bytes:
    """
    Optimize image before OCR/ML processing:
    - Resize to target size (reduces processing time)
    - Convert to RGB if needed
    - Enhance contrast slightly
    - Return optimized JPEG bytes
    
    Args:
        image_bytes: Raw image bytes
        target_size: Target (width, height) for resizing
        
    Returns:
        Optimized image as JPEG bytes
    """
    try:
        # Load image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed (handles RGBA, P, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if larger than target (maintains aspect ratio)
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Optional: Enhance contrast slightly (can improve OCR)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)  # 10% contrast boost
        
        # Convert back to bytes (JPEG, quality 85)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        # If preprocessing fails, return original
        print(f"Image preprocessing error: {e}")
        return image_bytes


def resize_for_model(image_bytes: bytes, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    Resize image specifically for ML model input.
    Returns numpy array ready for TensorFlow.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        return np.array(img)
    except Exception as e:
        print(f"Model resize error: {e}")
        # Fallback: return black image
        return np.zeros((*target_size, 3), dtype=np.uint8)
