"""Environment configuration for the medication management system."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_VISION_API_KEY = os.getenv('GOOGLE_VISION_API_KEY', '')
AZURE_FORM_RECOGNIZER_KEY = os.getenv('AZURE_FORM_RECOGNIZER_KEY', '')

# System Configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG_MODE = ENVIRONMENT == 'development'

# Paths
DATA_DIR = os.getenv('DATA_DIR', 'data')
LOG_DIR = os.getenv('LOG_DIR', 'logs')
CACHE_DIR = os.getenv('CACHE_DIR', 'data/cache')

# GPU Configuration
USE_GPU = os.getenv('USE_GPU', 'false').lower() == 'true'
DEVICE = 'cuda' if USE_GPU else 'cpu'

# Model Configuration
OCR_BACKEND = os.getenv('OCR_BACKEND', 'easyocr')
USE_CLINICAL_BERT = os.getenv('USE_CLINICAL_BERT', 'true').lower() == 'true'

# Thresholds
MANUAL_REVIEW_THRESHOLD = float(os.getenv('MANUAL_REVIEW_THRESHOLD', '0.7'))
HIGH_CONFIDENCE_THRESHOLD = float(os.getenv('HIGH_CONFIDENCE_THRESHOLD', '0.85'))
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.85'))

# API Configuration
RX_NAV_API_BASE = "https://rxnav.nlm.nih.gov/REST"
DAILYMED_API_BASE = "https://dailymed.nlm.nih.gov/dailymed"

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
