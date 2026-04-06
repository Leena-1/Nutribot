# Performance Optimization Guide - Nutribot

## Overview

This document outlines all performance optimizations implemented for the Nutribot mobile app and FastAPI backend to achieve **sub-3-second response times**.

---

## 🚀 Flutter Side Optimizations

### 1. Image Compression (`lib/services/image_service.dart`)

**What it does:**
- Compresses images to max 720x720px resolution
- Reduces quality to 70% (JPEG)
- Typically reduces image size by 60-80%

**Usage:**
```dart
final compressedBytes = await ImageService.compressImage(xfile);
```

**Benefits:**
- Faster upload times (smaller payload)
- Reduced bandwidth usage
- Lower server processing time

### 2. Response Caching (`lib/services/cache_service.dart`)

**What it does:**
- Caches API responses using SHA-256 hash of image/food name
- 24-hour cache expiry
- Prevents redundant API calls for identical inputs

**Usage:**
```dart
// Automatically handled in ApiService
final result = await _api.predictFood(imageBytes: compressedBytes, useCache: true);
```

**Benefits:**
- Instant responses for cached items
- Reduced server load
- Offline-like experience for repeated queries

### 3. Network Optimization (`lib/services/api_service.dart`)

**Features:**
- **Timeout handling**: 30-second timeout per request
- **Retry mechanism**: Up to 2 retries with exponential backoff
- **Error handling**: Graceful SocketException and HttpException handling

**Benefits:**
- More reliable network calls
- Better user experience during network issues
- Automatic recovery from transient failures

### 4. Improved Loading States (`lib/screens/scan_screen.dart`)

**Features:**
- Status messages: "Compressing image...", "Uploading image...", "Analyzing nutrients..."
- Visual progress indicators
- Better error display with styled containers

**Benefits:**
- Users know what's happening
- Perceived performance improvement
- Better error communication

---

## ⚡ Backend Optimizations

### 1. Image Preprocessing (`backend/services/image_processor.py`)

**What it does:**
- Resizes images to 720x720px before ML processing
- Converts to RGB format
- Enhances contrast slightly (10% boost)
- Optimizes JPEG quality

**Benefits:**
- Faster ML inference (smaller input)
- Reduced memory usage
- Better OCR accuracy

### 2. Async FastAPI Endpoints (`backend/api/routes.py`)

**What it does:**
- All heavy operations run in thread pools
- Non-blocking I/O for image processing
- Async model inference

**Key optimizations:**
```python
# Model loading in thread pool
_food_model, _class_names = await loop.run_in_executor(
    None, load_saved_model, FOOD_CNN_DIR
)

# Image preprocessing in thread pool
optimized_image = await loop.run_in_executor(
    None, preprocess_image, content
)

# ML inference in thread pool
logits = await loop.run_in_executor(
    None, lambda: _food_model.predict(img, verbose=0)
)
```

**Benefits:**
- Server can handle multiple requests concurrently
- No blocking of event loop
- Better scalability

### 3. Optimized Response Size

**What it does:**
- Returns only necessary fields
- Removes redundant data
- Efficient JSON serialization

**Response structure:**
```json
{
  "food_name": "Apple",
  "detected_from_image": true,
  "nutrients": {...},
  "disease_suitability": {...},
  "diet_type": "Vegan",
  "recommendation_notes": "..."
}
```

---

## 📦 New Dependencies

### Flutter (`pubspec.yaml`)
```yaml
flutter_image_compress: ^2.3.0  # Image compression
shared_preferences: ^2.2.2       # Local caching
crypto: ^3.0.3                   # Cache key generation
```

### Python (`requirements.txt`)
```txt
Pillow>=10.0.0  # Image processing
```

**Installation:**
```bash
# Flutter
cd mobile_app
flutter pub get

# Python
pip install -r requirements.txt
```

---

## 🎯 Performance Targets & Results

### Target Metrics
- **Image upload**: < 1 second (compressed)
- **Backend processing**: < 2 seconds
- **Total response time**: < 3 seconds

### Expected Improvements
1. **Image compression**: 60-80% size reduction → 3-5x faster uploads
2. **Caching**: Instant responses for cached items (0ms)
3. **Async processing**: 2-3x better concurrent request handling
4. **Image preprocessing**: 30-40% faster ML inference

---

## 🔧 Implementation Steps

### Step 1: Install Dependencies

**Flutter:**
```bash
cd mobile_app
flutter pub get
```

**Python:**
```bash
pip install -r requirements.txt
```

### Step 2: Update Backend URL (if needed)

Edit `mobile_app/lib/services/api_service.dart`:
```dart
const String baseUrl = 'http://YOUR_IP:8000';
```

### Step 3: Test the Optimizations

1. **Test image compression:**
   - Take a photo (should see "Compressing image..." message)
   - Check logs for compression ratio

2. **Test caching:**
   - Analyze same food twice
   - Second time should be instant (cache hit)

3. **Test network retry:**
   - Temporarily disconnect network
   - Should see retry attempts in logs

---

## 🏗️ Architecture Recommendations

### 1. Communication Method
- **Current**: HTTP REST API with multipart/form-data
- **Recommendation**: Keep REST API (simple, works well)
- **Future**: Consider gRPC for even lower latency if needed

### 2. Model Deployment
- **Current**: TensorFlow models loaded in memory
- **Recommendation**: 
  - Use TensorFlow Lite for mobile (on-device inference)
  - Keep server models for complex predictions
  - Consider ONNX Runtime for cross-platform

### 3. Scalable Backend Architecture

**Current (Single Server):**
```
Flutter App → FastAPI Server → ML Models
```

**Recommended (Production):**
```
Flutter App → Load Balancer → FastAPI Servers (multiple)
                              ↓
                         Redis Cache
                              ↓
                         ML Inference Service (GPU)
                              ↓
                         Database (PostgreSQL)
```

**Key components:**
- **Load Balancer**: Distribute requests
- **Redis Cache**: Cache frequent lookups
- **GPU Inference Service**: Faster ML predictions
- **Database**: Store unified food features

### 4. Response Time Optimization Checklist

- ✅ Image compression (client-side)
- ✅ Response caching (client-side)
- ✅ Async FastAPI endpoints
- ✅ Image preprocessing (server-side)
- ✅ Optimized ML inference
- ⏳ **TODO**: Add Redis caching layer
- ⏳ **TODO**: Implement request queuing
- ⏳ **TODO**: Add CDN for static assets

---

## 📊 Monitoring & Debugging

### Flutter Logs
```dart
// Enable debug logging
print('Cache hit for predict_food');
print('Image compressed: ${originalSize} -> ${compressedSize} bytes');
```

### Backend Logs
```python
# Check processing times
import time
start = time.time()
# ... processing ...
print(f"Processing took {time.time() - start:.2f}s")
```

### Performance Testing
```bash
# Test API endpoint
curl -X POST http://localhost:8000/api/predict_food \
  -F "file=@test_image.jpg" \
  -w "\nTime: %{time_total}s\n"
```

---

## 🚨 Troubleshooting

### Issue: Slow image uploads
**Solution**: Check image compression is working (should see compression logs)

### Issue: Cache not working
**Solution**: Verify `shared_preferences` is installed and permissions granted

### Issue: Backend timeout
**Solution**: Increase timeout in `api_service.dart` or optimize backend processing

### Issue: Model loading slow
**Solution**: Pre-load models on server startup (add to `main.py`)

---

## 🔮 Future Optimizations

1. **On-device ML**: Use TensorFlow Lite for food detection
2. **WebSocket**: Real-time updates for long-running predictions
3. **Batch processing**: Process multiple images in one request
4. **Model quantization**: Reduce model size and inference time
5. **CDN integration**: Serve static assets faster
6. **GraphQL**: More efficient data fetching

---

## 📝 Best Practices

1. **Always compress images** before upload
2. **Enable caching** for better UX
3. **Handle errors gracefully** with retry logic
4. **Show loading states** to users
5. **Monitor performance** in production
6. **Test on real devices** (not just emulators)
7. **Use async/await** properly in Flutter
8. **Run heavy operations** in thread pools (backend)

---

## 📚 References

- [Flutter Image Compression](https://pub.dev/packages/flutter_image_compress)
- [FastAPI Async Best Practices](https://fastapi.tiangolo.com/async/)
- [TensorFlow Lite](https://www.tensorflow.org/lite)
- [Redis Caching](https://redis.io/)

---

**Last Updated**: 2026-02-17
**Target Response Time**: < 3 seconds
**Current Status**: ✅ Optimizations Implemented
