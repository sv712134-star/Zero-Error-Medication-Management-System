# Complete System Architecture & Deployment Guide

## 🎯 System Overview

```
Zero-Error Medication Management System
├─ Component 1: Prescription Digitizer (OCR + NER)
├─ Component 2: Pill Authenticator (Vision + Deep Learning)
├─ Component 3: Intake Verification (Pose + Action Recognition)
├─ Integration Engine (Workflow Orchestration)
├─ Unified API Server (FastAPI)
└─ React Native Mobile App (iOS/Android)
```

---

## 📱 Backend Server Deployment

### Quick Start (Local Development)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Download ML models (first run)
python -c "from src.ocr.ocr_engine import OCREngine; OCREngine('easyocr')"
python -c "from src.ner.ner_extractor import NERExtractor; NERExtractor()"

# 3. Start unified API server
python unified_api_server.py

# 4. Server running at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Docker Deployment

**Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p data/uploads data/results data/models

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "unified_api_server.py"]
```

**Build & Run:**
```bash
# Build image
docker build -t medication-verifier:latest .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  medication-verifier:latest

# With GPU support
docker run --gpus all -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  medication-verifier:latest
```

### Cloud Deployment (AWS)

**Using EC2:**
```bash
# 1. Launch EC2 instance (t3.xlarge recommended)
# Ubuntu 22.04 LTS

# 2. Connect and install
sudo apt-get update
sudo apt-get install -y python3.10 python3-pip git

# 3. Clone repository
git clone https://github.com/your-repo/medication-verifier.git
cd medication-verifier

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create systemd service
sudo tee /etc/systemd/system/medication-api.service > /dev/null <<EOF
[Unit]
Description=Medication Verification API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/medication-verifier
ExecStart=/usr/bin/python3 unified_api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 6. Enable and start service
sudo systemctl enable medication-api
sudo systemctl start medication-api

# 7. Check status
sudo systemctl status medication-api

# 8. View logs
sudo journalctl -u medication-api -f
```

**Using ECS (Elastic Container Service):**
```bash
# 1. Push image to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag medication-verifier:latest \
  <account>.dkr.ecr.us-east-1.amazonaws.com/medication-verifier:latest

docker push <account>.dkr.ecr.us-east-1.amazonaws.com/medication-verifier:latest

# 2. Create ECS task definition
# (Use AWS Console or update task-definition.json)

# 3. Create ECS service
aws ecs create-service --cluster medication-cluster \
  --service-name medication-api \
  --task-definition medication-verifier:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}

# 4. Set up load balancer
# (Configure Application Load Balancer in EC2 console)
```

---

## 📲 Mobile App Deployment

### iOS Deployment

**Prerequisites:**
- Mac with Xcode 14+
- Apple Developer Account ($99/year)
- iOS 13+ device

**Build Steps:**
```bash
# 1. Navigate to iOS directory
cd MedicationVerifier/ios

# 2. Install pods
pod install

# 3. Go back to project root
cd ..

# 4. Update bundle identifier and team ID
# In Xcode: Project > Signing & Capabilities > Team

# 5. Build for device
xcodebuild -workspace ios/MedicationVerifier.xcworkspace \
  -scheme MedicationVerifier \
  -configuration Release \
  -derivedDataPath build \
  -destination generic/platform=iOS

# 6. Archive for App Store
xcodebuild -workspace ios/MedicationVerifier.xcworkspace \
  -scheme MedicationVerifier \
  -configuration Release \
  -archivePath build/MedicationVerifier.xcarchive \
  archive

# 7. Export for distribution
xcodebuild -exportArchive \
  -archivePath build/MedicationVerifier.xcarchive \
  -exportOptionsPlist ios/ExportOptions.plist \
  -exportPath build/ipa

# 8. Upload to App Store Connect
# Open App Store Connect > Select app > TestFlight > Build > Upload .ipa
```

**App Store Submission:**
```
1. Create app in App Store Connect
2. Fill in app details:
   - App Name: Medication Verifier
   - Category: Medical
   - Content Rating: No content restrictions
   - Privacy Policy: Link to privacy policy
3. Configure pricing and availability
4. Submit for review
5. Apple reviews (typically 24-48 hours)
6. Launch on App Store
```

### Android Deployment

**Prerequisites:**
- Android Studio 2022.1+
- Android NDK r21+
- Google Play Developer Account ($25, one-time)

**Build Steps:**
```bash
# 1. Generate signing key (first time only)
keytool -genkey -v -keystore medication-verifier.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias medication-verifier \
  -storepass <password> \
  -keypass <password> \
  -dname "CN=Medication Verifier, O=Healthcare, L=City, C=US"

# 2. Copy keystore to android/app
cp medication-verifier.keystore android/app/

# 3. Create gradle.properties in android/
cat >> android/gradle.properties << EOF
MYAPP_RELEASE_STORE_FILE=medication-verifier.keystore
MYAPP_RELEASE_STORE_PASSWORD=<password>
MYAPP_RELEASE_KEY_ALIAS=medication-verifier
MYAPP_RELEASE_KEY_PASSWORD=<password>
EOF

# 4. Update android/app/build.gradle
# Ensure signingConfigs.release is configured

# 5. Build APK
cd android
./gradlew assembleRelease
cd ..

# APK location: android/app/build/outputs/apk/release/app-release.apk

# 6. Build AAB for Play Store
cd android
./gradlew bundleRelease
cd ..

# AAB location: android/app/build/outputs/bundle/release/app-release.aab
```

**Play Store Submission:**
```
1. Create app in Google Play Console
2. Upload AAB (Android App Bundle)
3. Fill in app details:
   - App Name: Medication Verifier
   - Category: Medical
   - Content Rating Questionnaire
   - Privacy Policy: Link to privacy policy
4. Configure pricing and distribution
5. Submit for review
6. Google reviews (typically 2-4 hours)
7. Launch on Play Store
```

---

## 🔒 Security Configuration

### API Authentication

```python
# In unified_api_server.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, encode

security = HTTPBearer()

@app.post("/api/v1/complete-verification")
async def complete_verification(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    # ... other params
):
    token = credentials.credentials
    try:
        payload = decode(token, "SECRET_KEY", algorithms=["HS256"])
        patient_id = payload.get("patient_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### HTTPS/SSL

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Run server with SSL
uvicorn unified_api_server:app \
  --host 0.0.0.0 --port 8443 \
  --ssl-keyfile key.pem \
  --ssl-certfile cert.pem
```

### Data Encryption

```python
from cryptography.fernet import Fernet
import os

# Generate encryption key
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# Encrypt sensitive results before storage
encrypted = cipher.encrypt(json.dumps(result).encode())
with open(f"{result_path}.enc", "wb") as f:
    f.write(encrypted)
```

---

## 📊 Monitoring & Analytics

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# Metrics
request_count = Counter(
    'medication_verifier_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status']
)

request_duration = Histogram(
    'medication_verifier_request_duration_seconds',
    'API request duration',
    ['endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# In request handler
@app.middleware("http")
async def add_metrics(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.labels(
        endpoint=request.url.path,
        method=request.method,
        status=response.status_code
    ).inc()
    
    request_duration.labels(endpoint=request.url.path).observe(duration)
    return response

# Start metrics server
start_http_server(8001)
```

### ELK Stack Logging

```python
import logging
import json
from pythonjsonlogger import jsonlogger

# JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Log workflow events
logger.info("Workflow started", extra={
    "workflow_id": workflow_id,
    "patient_id": patient_id,
    "timestamp": datetime.now().isoformat()
})
```

---

## 🧪 Testing & Validation

### API Testing with Pytest

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unified_api_server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]

def test_analyze_prescription():
    with open("test_data/prescription.jpg", "rb") as f:
        response = client.post(
            "/api/v1/analyze-prescription",
            data={"patient_id": "TEST001"},
            files={"file": ("prescription.jpg", f, "image/jpeg")}
        )
    assert response.status_code == 200
    assert "workflow_id" in response.json()
```

### Mobile Testing

```javascript
// __tests__/api.test.js
import * as api from '../src/services/api';

describe('API Service', () => {
  test('should check API health', async () => {
    const health = await api.checkAPIHealth();
    expect(health.status).toBeDefined();
  });

  test('should handle network errors', async () => {
    try {
      await api.analyzePrescription('invalid_path', 'PAT001');
    } catch (error) {
      expect(error).toBeDefined();
    }
  });
});
```

---

## 🚀 Performance Optimization

### Backend Optimization

```python
# Model caching
from functools import lru_cache
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@lru_cache(maxsize=1)
def load_ocr_model():
    from src.ocr.ocr_engine import OCREngine
    return OCREngine('easyocr')

# Batch processing
async def process_batch(files):
    batch_results = []
    for batch in chunks(files, batch_size=4):
        results = await asyncio.gather(
            *[process_file(f) for f in batch]
        )
        batch_results.extend(results)
    return batch_results
```

### Mobile Optimization

```javascript
// Image compression before upload
const compressImage = async (imageUri) => {
  return new Promise((resolve, reject) => {
    ImageResizer.createResizedImage(
      imageUri,
      1024, // width
      1024, // height
      'JPEG',
      80, // quality
      0, // rotation
      null,
      false
    )
      .then(response => resolve(response.uri))
      .catch(err => reject(err));
  });
};

// Local caching
const cacheResult = async (workflowId, result) => {
  await AsyncStorage.setItem(
    `result_${workflowId}`,
    JSON.stringify(result)
  );
};
```

---

## 📋 Maintenance & Operations

### Regular Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/medication-data-$TIMESTAMP.tar.gz data/
# Keep last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Health Monitoring

```bash
# Check server status every 5 minutes
*/5 * * * * curl -f http://localhost:8000/api/v1/health || alert

# Monitor logs
tail -f logs/medication_verifier.log | grep ERROR

# Check disk space
df -h /path/to/data
```

### Scaling Strategy

```
Peak Load Management:
├─ Horizontal Scaling (add servers)
│  └─ Use load balancer (AWS ALB, NGINX)
├─ Vertical Scaling (upgrade server)
│  └─ Increase CPU/RAM
├─ Caching Layer (Redis)
│  └─ Cache model outputs
└─ Async Processing (Celery)
   └─ Queue long-running tasks
```

---

## 🎓 Quick Reference

| Component | Location | Start Command |
|-----------|----------|----------------|
| **Backend API** | `unified_api_server.py` | `python unified_api_server.py` |
| **Prescription Digitizer** | `prescription_digitizer.py` | `from prescription_digitizer import PrescriptionDigitizer` |
| **Pill Authenticator** | `src/pill_authenticator/` | `from src.pill_authenticator import PillAuthenticator` |
| **Intake Verifier** | `src/intake_verification/` | `from src.intake_verification import IntakeVerifier` |
| **Mobile App** | `MedicationVerifier/` | `npx react-native run-ios` or `run-android` |
| **API Docs** | http://localhost:8000/docs | Browser |

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Models timeout | Increase timeout or download manually |
| Out of Memory | Use smaller models or reduce batch size |
| API refused | Check port 8000 is free, firewall rules |
| Mobile crashes | Check logcat (Android) or Xcode (iOS) |
| GPU not detected | Install CUDA toolkit and cuDNN |

---

## 📞 Support & Resources

- API Documentation: `http://localhost:8000/docs`
- GitHub: `https://github.com/your-repo/medication-verifier`
- Issues: `https://github.com/your-repo/medication-verifier/issues`
- Email: `support@example.com`

---

**Last Updated**: 2026-01-17
**Version**: 1.0.0
**Status**: Production Ready ✅
