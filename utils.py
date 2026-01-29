"""Utility functions for the medication management system."""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import os


class Logger:
    """Custom logger for the system."""

    def __init__(self, name: str, log_file: str = None):
        """Initialize logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)


class JSONEncoder:
    """Custom JSON encoder for complex objects."""

    @staticmethod
    def encode(obj: Any) -> str:
        """Encode object to JSON."""
        return json.dumps(obj, default=str, indent=2)

    @staticmethod
    def decode(json_str: str) -> Dict:
        """Decode JSON string."""
        return json.loads(json_str)


class DataProcessor:
    """Process and format medication data."""

    @staticmethod
    def format_dosage(value: str, unit: str) -> str:
        """Format dosage consistently."""
        unit = unit.lower().strip()
        return f"{value}{unit}".replace(' ', '')

    @staticmethod
    def normalize_drug_name(name: str) -> str:
        """Normalize drug name to standard format."""
        return name.strip().lower().title()

    @staticmethod
    def standardize_frequency(frequency: str) -> str:
        """Convert frequency to standard format."""
        freq_map = {
            'once daily': 'OD',
            'twice daily': 'BID',
            'three times daily': 'TID',
            'four times daily': 'QID',
            'as needed': 'PRN'
        }
        
        freq_lower = frequency.lower().strip()
        return freq_map.get(freq_lower, frequency)

    @staticmethod
    def create_medication_record(drug_name: str, 
                                dosage: str = "",
                                frequency: str = "",
                                route: str = "",
                                duration: str = "") -> Dict:
        """Create structured medication record."""
        return {
            'drug_name': DataProcessor.normalize_drug_name(drug_name),
            'dosage': dosage,
            'frequency': DataProcessor.standardize_frequency(frequency),
            'route': route,
            'duration': duration,
            'created_at': datetime.now().isoformat()
        }


class PerformanceMonitor:
    """Monitor system performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = {}
        self.start_times = {}

    def start_timer(self, metric_name: str):
        """Start timing a metric."""
        self.start_times[metric_name] = datetime.now()

    def end_timer(self, metric_name: str) -> float:
        """End timing and record metric."""
        if metric_name in self.start_times:
            duration = (datetime.now() - self.start_times[metric_name]).total_seconds()
            
            if metric_name not in self.metrics:
                self.metrics[metric_name] = []
            
            self.metrics[metric_name].append(duration)
            return duration
        
        return 0.0

    def get_average(self, metric_name: str) -> float:
        """Get average time for a metric."""
        if metric_name in self.metrics:
            values = self.metrics[metric_name]
            return sum(values) / len(values) if values else 0.0
        return 0.0

    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics."""
        stats = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                stats[metric_name] = {
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
        
        return stats


# Global logger instance
logger = Logger("MedicationSystem", log_file="logs/medication_system.log")

# Global performance monitor
perf_monitor = PerformanceMonitor()


def log_extraction(extraction_id: str, status: str, details: Dict = None):
    """Log extraction details."""
    message = f"[{extraction_id}] Status: {status}"
    if details:
        message += f" | {details}"
    
    if status == "error":
        logger.error(message)
    elif status == "warning":
        logger.warning(message)
    else:
        logger.info(message)
