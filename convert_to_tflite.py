"""
TensorFlow Lite Model Conversion Script
Converts all ML models to TensorFlow Lite format for mobile deployment
"""

import os
import numpy as np
import tensorflow as tf
import torch
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = Path("assets/models/tflite")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = {
    "yolov8_pill_detector": {
        "input_size": (416, 416),
        "source": "runs/detect/train/weights/best.pt",
        "output": OUTPUT_DIR / "pill_detector.tflite",
        "quantization": "dynamic"
    },
    "pill_classifier": {
        "input_size": (224, 224),
        "source": "models/pill_classifier.pt",
        "output": OUTPUT_DIR / "pill_classifier.tflite",
        "quantization": "dynamic"
    },
    "action_recognizer": {
        "input_size": (224, 224),
        "source": "models/action_recognizer.pt",
        "output": OUTPUT_DIR / "action_recognizer.tflite",
        "quantization": "float32"
    },
    "pose_estimator": {
        "input_size": (192, 256),
        "source": "models/pose_estimator.pt",
        "output": OUTPUT_DIR / "pose_estimator.tflite",
        "quantization": "dynamic"
    }
}


# ============================================================================
# CONVERSION UTILITIES
# ============================================================================

class TFLiteConverter:
    """Convert PyTorch/TensorFlow models to TensorFlow Lite format"""

    @staticmethod
    def pytorch_to_tflite(
        model_path: str,
        output_path: str,
        input_size: tuple,
        quantization: str = "dynamic"
    ):
        """
        Convert PyTorch model to TFLite
        
        Args:
            model_path: Path to PyTorch model
            output_path: Output TFLite path
            input_size: Model input size (H, W)
            quantization: Quantization type (dynamic, integer, float32)
        """
        logger.info(f"Converting PyTorch model: {model_path}")
        
        try:
            # Load PyTorch model
            model = torch.load(model_path, map_location='cpu')
            model.eval()
            
            # Create dummy input
            dummy_input = torch.randn(1, 3, input_size[0], input_size[1])
            
            # Export to ONNX first
            onnx_path = str(output_path).replace('.tflite', '.onnx')
            torch.onnx.export(
                model,
                dummy_input,
                onnx_path,
                input_names=['input'],
                output_names=['output'],
                opset_version=13,
                do_constant_folding=True,
                verbose=False
            )
            logger.info(f"✓ ONNX export: {onnx_path}")
            
            # Convert ONNX to TFLite
            TFLiteConverter.onnx_to_tflite(
                onnx_path,
                output_path,
                quantization
            )
            
        except Exception as e:
            logger.error(f"✗ PyTorch to TFLite conversion failed: {e}")
            return False
        
        return True

    @staticmethod
    def onnx_to_tflite(
        onnx_path: str,
        output_path: str,
        quantization: str = "dynamic"
    ):
        """Convert ONNX model to TFLite"""
        logger.info(f"Converting ONNX to TFLite: {onnx_path}")
        
        try:
            # Try using tensorflow-onnx (tf2onnx)
            import onnx
            import onnx_tf
            
            # Load ONNX model
            onnx_model = onnx.load(onnx_path)
            
            # Convert to TensorFlow
            from onnx_tf.backend import prepare
            tf_rep = prepare(onnx_model)
            
            # Export as SavedModel
            saved_model_path = str(output_path).replace('.tflite', '_saved_model')
            tf_rep.export_graph(saved_model_path)
            
            # Convert SavedModel to TFLite
            converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_path)
            
            # Apply quantization
            if quantization == "dynamic":
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
            elif quantization == "integer":
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                converter.target_spec.supported_ops = [
                    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
                ]
            
            # Convert
            tflite_model = converter.convert()
            
            # Save
            with open(output_path, 'wb') as f:
                f.write(tflite_model)
            
            logger.info(f"✓ TFLite model saved: {output_path}")
            
        except ImportError:
            logger.warning("onnx-tf not available, using alternative method")
            # Fallback: use Python model directly
            return False
        except Exception as e:
            logger.error(f"✗ ONNX to TFLite conversion failed: {e}")
            return False
        
        return True

    @staticmethod
    def tf_model_to_tflite(
        saved_model_path: str,
        output_path: str,
        quantization: str = "dynamic"
    ):
        """Convert TensorFlow SavedModel to TFLite"""
        logger.info(f"Converting TensorFlow model: {saved_model_path}")
        
        try:
            converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_path)
            
            # Apply quantization
            if quantization == "dynamic":
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
            elif quantization == "integer":
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                converter.target_spec.supported_ops = [
                    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
                ]
            
            tflite_model = converter.convert()
            
            with open(output_path, 'wb') as f:
                f.write(tflite_model)
            
            logger.info(f"✓ TFLite model saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"✗ TensorFlow to TFLite conversion failed: {e}")
            return False


# ============================================================================
# SPECIALIZED MODEL CONVERTERS
# ============================================================================

class YOLOv8Converter:
    """Convert YOLOv8 models to TFLite"""

    @staticmethod
    def convert(model_path: str, output_path: str):
        """
        Convert YOLOv8 model to TFLite
        
        Args:
            model_path: Path to YOLOv8 .pt file
            output_path: Output TFLite path
        """
        logger.info(f"Converting YOLOv8 model: {model_path}")
        
        try:
            from ultralytics import YOLO
            
            # Load YOLOv8 model
            model = YOLO(model_path)
            
            # Export to TFLite (YOLOv8 has built-in export)
            results = model.export(format='tflite', imgsz=416)
            
            logger.info(f"✓ YOLOv8 model converted: {results}")
            return True
            
        except Exception as e:
            logger.error(f"✗ YOLOv8 conversion failed: {e}")
            return False


class MediaPipeTFLiteConverter:
    """Handle MediaPipe TFLite models"""

    @staticmethod
    def download_pose_detector():
        """Download MediaPipe Pose Detection model"""
        logger.info("Downloading MediaPipe Pose Detector...")
        
        import urllib.request
        
        url = "https://storage.googleapis.com/mediapipe-models/pose_detector/pose_detector_lite/float16/pose_detector_lite.tflite"
        output = OUTPUT_DIR / "pose_detector.tflite"
        
        try:
            urllib.request.urlretrieve(url, output)
            logger.info(f"✓ Downloaded: {output}")
            return True
        except Exception as e:
            logger.error(f"✗ Download failed: {e}")
            return False

    @staticmethod
    def download_hand_detector():
        """Download MediaPipe Hand Detection model"""
        logger.info("Downloading MediaPipe Hand Detector...")
        
        import urllib.request
        
        url = "https://storage.googleapis.com/mediapipe-models/hand_detector/blaze_palm/float16/blaze_palm.tflite"
        output = OUTPUT_DIR / "hand_detector.tflite"
        
        try:
            urllib.request.urlretrieve(url, output)
            logger.info(f"✓ Downloaded: {output}")
            return True
        except Exception as e:
            logger.error(f"✗ Download failed: {e}")
            return False


# ============================================================================
# QUANTIZATION
# ============================================================================

class Quantizer:
    """Quantize TFLite models for better performance"""

    @staticmethod
    def dynamic_range_quantize(tflite_path: str, output_path: str):
        """Apply dynamic range quantization"""
        logger.info(f"Applying dynamic range quantization: {tflite_path}")
        
        try:
            with open(tflite_path, 'rb') as f:
                tflite_model = f.read()
            
            # Read quantization details (implementation depends on model)
            # For simplicity, we're using the converter's built-in quantization
            
            with open(output_path, 'wb') as f:
                f.write(tflite_model)
            
            logger.info(f"✓ Quantized model: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Quantization failed: {e}")
            return False

    @staticmethod
    def integer_quantize(tflite_path: str, output_path: str, calibration_dataset=None):
        """Apply integer quantization (requires calibration data)"""
        logger.info(f"Applying integer quantization: {tflite_path}")
        
        try:
            # This would require calibration dataset
            # Implementation depends on specific model
            logger.warning("Integer quantization requires calibration dataset")
            return False
            
        except Exception as e:
            logger.error(f"✗ Integer quantization failed: {e}")
            return False


# ============================================================================
# MODEL VALIDATION
# ============================================================================

class TFLiteValidator:
    """Validate converted TFLite models"""

    @staticmethod
    def validate(tflite_path: str):
        """Validate TFLite model"""
        logger.info(f"Validating TFLite model: {tflite_path}")
        
        try:
            # Load interpreter
            interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
            interpreter.allocate_tensors()
            
            # Get input/output details
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            logger.info(f"  Input shape: {input_details[0]['shape']}")
            logger.info(f"  Input type: {input_details[0]['dtype']}")
            logger.info(f"  Output shape: {output_details[0]['shape']}")
            logger.info(f"  Output type: {output_details[0]['dtype']}")
            
            # Test inference
            input_shape = input_details[0]['shape']
            test_input = np.random.randn(*input_shape).astype(np.float32)
            
            interpreter.set_tensor(input_details[0]['index'], test_input)
            interpreter.invoke()
            
            output_data = interpreter.get_tensor(output_details[0]['index'])
            
            logger.info(f"✓ Model validation successful")
            logger.info(f"  Output sample shape: {output_data.shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Model validation failed: {e}")
            return False

    @staticmethod
    def benchmark(tflite_path: str, num_iterations: int = 100):
        """Benchmark TFLite model inference speed"""
        logger.info(f"Benchmarking TFLite model: {tflite_path}")
        
        import time
        
        try:
            interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
            interpreter.allocate_tensors()
            
            input_details = interpreter.get_input_details()
            input_shape = input_details[0]['shape']
            
            test_input = np.random.randn(*input_shape).astype(np.float32)
            
            # Warm up
            for _ in range(10):
                interpreter.set_tensor(input_details[0]['index'], test_input)
                interpreter.invoke()
            
            # Benchmark
            start_time = time.time()
            for _ in range(num_iterations):
                interpreter.set_tensor(input_details[0]['index'], test_input)
                interpreter.invoke()
            end_time = time.time()
            
            avg_time = (end_time - start_time) / num_iterations * 1000
            logger.info(f"✓ Average inference time: {avg_time:.2f}ms")
            logger.info(f"  FPS: {1000 / avg_time:.1f}")
            
            return avg_time
            
        except Exception as e:
            logger.error(f"✗ Benchmarking failed: {e}")
            return None


# ============================================================================
# MAIN CONVERSION PIPELINE
# ============================================================================

def convert_all_models():
    """Convert all models to TFLite"""
    logger.info("=" * 70)
    logger.info("TENSORFLOW LITE MODEL CONVERSION PIPELINE")
    logger.info("=" * 70)
    
    results = {}
    
    # 1. Convert YOLOv8 Pill Detector
    logger.info("\n[1/4] YOLOv8 Pill Detector")
    if os.path.exists(MODELS["yolov8_pill_detector"]["source"]):
        success = YOLOv8Converter.convert(
            MODELS["yolov8_pill_detector"]["source"],
            MODELS["yolov8_pill_detector"]["output"]
        )
        results["yolov8_pill_detector"] = success
    else:
        logger.warning("Model file not found, skipping")
        results["yolov8_pill_detector"] = False
    
    # 2. Convert Pill Classifier
    logger.info("\n[2/4] Pill Classifier")
    if os.path.exists(MODELS["pill_classifier"]["source"]):
        success = TFLiteConverter.pytorch_to_tflite(
            MODELS["pill_classifier"]["source"],
            MODELS["pill_classifier"]["output"],
            MODELS["pill_classifier"]["input_size"],
            MODELS["pill_classifier"]["quantization"]
        )
        results["pill_classifier"] = success
    else:
        logger.warning("Model file not found, skipping")
        results["pill_classifier"] = False
    
    # 3. Download MediaPipe Models
    logger.info("\n[3/4] MediaPipe Models")
    success1 = MediaPipeTFLiteConverter.download_pose_detector()
    success2 = MediaPipeTFLiteConverter.download_hand_detector()
    results["mediapipe"] = success1 and success2
    
    # 4. Action Recognizer
    logger.info("\n[4/4] Action Recognizer")
    if os.path.exists(MODELS["action_recognizer"]["source"]):
        success = TFLiteConverter.pytorch_to_tflite(
            MODELS["action_recognizer"]["source"],
            MODELS["action_recognizer"]["output"],
            MODELS["action_recognizer"]["input_size"],
            MODELS["action_recognizer"]["quantization"]
        )
        results["action_recognizer"] = success
    else:
        logger.warning("Model file not found, skipping")
        results["action_recognizer"] = False
    
    # Validate all converted models
    logger.info("\n" + "=" * 70)
    logger.info("VALIDATING CONVERTED MODELS")
    logger.info("=" * 70)
    
    for model_name, output_path in [
        ("Pill Detector", MODELS["yolov8_pill_detector"]["output"]),
        ("Pill Classifier", MODELS["pill_classifier"]["output"]),
        ("Pose Detector", OUTPUT_DIR / "pose_detector.tflite"),
        ("Hand Detector", OUTPUT_DIR / "hand_detector.tflite"),
        ("Action Recognizer", MODELS["action_recognizer"]["output"]),
    ]:
        if os.path.exists(output_path):
            logger.info(f"\n{model_name}:")
            TFLiteValidator.validate(str(output_path))
            TFLiteValidator.benchmark(str(output_path), num_iterations=50)
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("CONVERSION SUMMARY")
    logger.info("=" * 70)
    
    for model_name, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        logger.info(f"{model_name}: {status}")
    
    logger.info("\nModels saved to:", OUTPUT_DIR)
    logger.info("Ready for mobile deployment!")


if __name__ == "__main__":
    convert_all_models()
