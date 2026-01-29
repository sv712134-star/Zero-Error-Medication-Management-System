# Installation and Setup Guide

## Zero-Error Medication Management System

### System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: 2GB+ for models and data
- **OS**: Windows, macOS, or Linux
- **GPU** (Optional): CUDA 11.8+ for GPU acceleration

### Step-by-Step Installation

#### 1. **Clone or Extract Project**

Extract the project to your desired location.

#### 2. **Create Virtual Environment**

```bash
# Navigate to project directory
cd medication-management-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### 3. **Install Dependencies**

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

This installs:
- **Image Processing**: OpenCV, Pillow
- **OCR**: EasyOCR, PaddleOCR
- **NER**: Transformers, PyTorch
- **Validation**: Requests, FuzzyWuzzy
- **API**: FastAPI, Uvicorn
- **Testing**: Pytest

#### 4. **Configure Environment**

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings (optional)
# API keys for Google Vision or Azure Form Recognizer
```

#### 5. **Create Required Directories**

```bash
mkdir -p data/drug_cache
mkdir -p logs
mkdir -p data/batch_prescriptions
```

### Configuration

#### Main Configuration File: `configs/config.yaml`

Key settings:

```yaml
# OCR Settings
ocr:
  backend: easyocr  # or paddleocr
  use_gpu: false    # Set to true if GPU available

# NER Settings  
ner:
  use_clinical_bert: true  # Use clinical BERT for better results
  
# Thresholds
scoring:
  manual_review_threshold: 0.70
```

### First Run

#### Test Basic Functionality

```bash
# Run examples
python examples.py
```

This will execute:
1. Basic prescription processing
2. Component testing
3. Database validation
4. Confidence scoring
5. Data processing utilities
6. Batch processing
7. Performance monitoring

#### Start API Server

```bash
# Start FastAPI server
python api_server.py
```

Server will be available at: `http://localhost:8000`

### API Documentation

Once server is running, access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_preprocessing.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Using the System

#### Basic Usage

```python
from prescription_digitizer import PrescriptionDigitizer

# Initialize
digitizer = PrescriptionDigitizer()

# Process single prescription
results = digitizer.process_prescription('path/to/prescription.jpg')

# Check results
if results['status'] != 'failed':
    print(f"Extracted Medications: {results['ner']['medications']}")
    print(f"Confidence: {results['confidence_score']['overall_confidence']:.2%}")
```

#### API Usage

```bash
# Process single prescription via API
curl -X POST http://localhost:8000/process \
  -F "file=@prescription.jpg"

# Get manual review queue
curl http://localhost:8000/review-queue

# Approve an extraction
curl -X POST http://localhost:8000/review/extraction_id \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "notes": "Verified"}'
```

### GPU Setup (Optional)

For faster processing with GPU:

#### NVIDIA GPU (CUDA)

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update config
# In config.yaml or .env:
USE_GPU=true
```

#### Verify GPU Usage

```python
import torch
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"GPU Count: {torch.cuda.device_count()}")
print(f"GPU Name: {torch.cuda.get_device_name(0)}")
```

### Troubleshooting

#### Issue: `easyocr` download fails

**Solution**: Download models manually
```bash
python -c "import easyocr; reader = easyocr.Reader(['en'])"
```

#### Issue: Memory error with large batches

**Solution**: Process smaller batches or reduce image resolution in config

#### Issue: API port already in use

**Solution**: Use different port
```bash
python api_server.py --port 8001
```

#### Issue: Drug database connection fails

**Solution**: API will use cached data. Update cache manually:
```bash
python -c "from src.validation import DatabaseValidator; db = DatabaseValidator(); db.validate_drug_name('Aspirin')"
```

### Production Deployment

#### Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "api_server.py"]
```

Build and run:
```bash
docker build -t medication-system .
docker run -p 8000:8000 medication-system
```

#### Using Gunicorn (Production ASGI)

```bash
pip install gunicorn

gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app
```

### Performance Optimization

1. **GPU Acceleration**: Set `use_gpu: true` for 3-5x speedup
2. **Batch Processing**: Use `/process-batch` endpoint for multiple images
3. **Caching**: Drug database is automatically cached
4. **Model Optimization**: Use smaller OCR models if needed

### Data Privacy

- Prescription images are processed locally by default
- Optional: Configure cloud OCR backends for specific features
- Drug data is cached locally with optional encryption
- Consider HIPAA compliance for healthcare deployment

### Maintenance

#### Clear Cache

```bash
rm -rf data/drug_cache/*
rm -rf logs/*
```

#### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Next Steps

1. **Process prescriptions** using the provided examples
2. **Set up manual review** workflow for low-confidence extractions
3. **Integrate with your system** via API
4. **Monitor performance** using built-in statistics

### Support & Resources

- **Documentation**: See [README.md](README.md)
- **Examples**: Run [examples.py](examples.py)
- **API Docs**: Access Swagger UI when API server is running
- **Configuration**: Edit [configs/config.yaml](configs/config.yaml)

### Architecture Overview

```
User Input (Image)
    ↓
Image Preprocessing
    ↓
OCR Extraction (EasyOCR/PaddleOCR)
    ↓
Text Cleaning & Splitting
    ↓
NER Entity Recognition
    ↓
Pattern Matching (Dosage, Frequency, etc.)
    ↓
Database Validation (FDA/RxNav)
    ↓
Confidence Scoring
    ↓
Manual Review Queue (if needed)
    ↓
Structured Output
```

---

**Ready to start?** Run `python examples.py` or `python api_server.py` to begin!
