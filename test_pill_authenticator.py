"""
Quick test to verify Component 2 modules are working correctly
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported"""
    logger.info("Testing imports...")
    
    try:
        from src.pill_authenticator import (
            PillDatasetLoader,
            DataAugmentor,
            PillClassifier,
            PillFeatureExtractor
        )
        logger.info("✓ Main modules imported successfully")
        
        from src.pill_authenticator.training import PillModelTrainer, ModelEvaluator
        logger.info("✓ Training modules imported successfully")
        
        from src.pill_authenticator.feature_extraction import (
            ShapeDetector,
            ColorAnalyzer,
            ImprintExtractor,
            SizeCalibrator
        )
        logger.info("✓ Feature extraction modules imported successfully")
        
        return True
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return False


def test_dataset_loader():
    """Test dataset loader initialization"""
    logger.info("\nTesting PillDatasetLoader...")
    
    try:
        from src.pill_authenticator import PillDatasetLoader
        
        loader = PillDatasetLoader(data_dir="data/pill_database")
        logger.info(f"✓ Dataset loader initialized")
        logger.info(f"  - Current pills in database: {len(loader.metadata)}")
        logger.info(f"  - Data directory: {loader.data_dir}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False


def test_augmentor():
    """Test data augmentor"""
    logger.info("\nTesting DataAugmentor...")
    
    try:
        from src.pill_authenticator import DataAugmentor
        from PIL import Image
        
        augmentor = DataAugmentor(image_size=(224, 224))
        logger.info(f"✓ DataAugmentor initialized")
        
        # Test with dummy image
        dummy_img = Image.new('RGB', (256, 256), color='blue')
        
        # Test rotation
        rotated = augmentor.rotate_image(dummy_img, angles=[90, 180])
        logger.info(f"  - Rotation test: {len(rotated)} rotated images")
        
        # Test lighting
        lit = augmentor.vary_lighting(dummy_img)
        logger.info(f"  - Lighting test: {len(lit)} lighting variations")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False


def test_model_classifier():
    """Test model classifier"""
    logger.info("\nTesting PillClassifier...")
    
    try:
        import torch
        from src.pill_authenticator import PillClassifier
        
        classifier = PillClassifier(
            num_shapes=10,
            num_colors=20,
            num_imprints=500,
            backbone="efficientnet"
        )
        logger.info(f"✓ PillClassifier initialized")
        logger.info(f"  - Backbone: efficientnet")
        logger.info(f"  - Device: {classifier.device}")
        
        # Test forward pass
        dummy_input = torch.randn(2, 3, 224, 224).to(classifier.device)
        predictions = classifier.predict(dummy_input)
        logger.info(f"  - Forward pass successful")
        logger.info(f"  - Output keys: {list(predictions.keys())}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False


def test_feature_extractor():
    """Test feature extractor"""
    logger.info("\nTesting PillFeatureExtractor...")
    
    try:
        from src.pill_authenticator import PillFeatureExtractor
        from PIL import Image
        
        extractor = PillFeatureExtractor()
        logger.info(f"✓ PillFeatureExtractor initialized")
        
        # Test with dummy image
        dummy_img = Image.new('RGB', (256, 256), color='red')
        features = extractor.extract_features(dummy_img)
        
        logger.info(f"  - Features extracted:")
        logger.info(f"    - Shape: {features.shape} (confidence: {features.shape_confidence:.2f})")
        logger.info(f"    - Color: {features.color} (confidence: {features.color_confidence:.2f})")
        logger.info(f"    - Size estimate: {features.estimated_size_mm}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False


def test_trainer():
    """Test trainer initialization"""
    logger.info("\nTesting PillModelTrainer...")
    
    try:
        from src.pill_authenticator import PillClassifier
        from src.pill_authenticator.training import PillModelTrainer
        
        classifier = PillClassifier()
        trainer = PillModelTrainer(
            model=classifier,
            learning_rate=1e-4,
            weight_decay=1e-5
        )
        logger.info(f"✓ PillModelTrainer initialized")
        logger.info(f"  - Learning rate: 1e-4")
        logger.info(f"  - Checkpoint directory: {trainer.checkpoint_dir}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False


def test_directory_structure():
    """Verify directory structure"""
    logger.info("\nVerifying directory structure...")
    
    required_dirs = [
        "src/pill_authenticator",
        "src/pill_authenticator/dataset",
        "src/pill_authenticator/models",
        "src/pill_authenticator/augmentation",
        "src/pill_authenticator/feature_extraction",
        "src/pill_authenticator/training",
        "data/pill_database"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        logger.info(f"  {status} {dir_path}")
        all_exist = all_exist and exists
    
    return all_exist


def test_config_file():
    """Test configuration file"""
    logger.info("\nVerifying configuration...")
    
    config_path = Path("src/pill_authenticator/config.yaml")
    
    if config_path.exists():
        logger.info(f"✓ Configuration file found: {config_path}")
        return True
    else:
        logger.error(f"✗ Configuration file not found: {config_path}")
        return False


def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("COMPONENT 2 - MODULE VERIFICATION TEST")
    logger.info("=" * 60)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Configuration File", test_config_file),
        ("Module Imports", test_imports),
        ("PillDatasetLoader", test_dataset_loader),
        ("DataAugmentor", test_augmentor),
        ("PillClassifier", test_model_classifier),
        ("PillFeatureExtractor", test_feature_extractor),
        ("PillModelTrainer", test_trainer),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✓ All tests passed! Component 2 is ready to use.")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
