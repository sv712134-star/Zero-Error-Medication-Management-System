"""
Component 2: Visual Pill Authenticator - Complete Example

Demonstrates:
1. Dataset creation and management
2. Data augmentation
3. Model initialization
4. Feature extraction
5. Training setup
6. Inference and predictions
"""

import logging
import torch
from pathlib import Path
from PIL import Image
import numpy as np

# Import from pill authenticator
from src.pill_authenticator import (
    PillDatasetLoader,
    DataAugmentor,
    PillClassifier,
    PillFeatureExtractor
)
from src.pill_authenticator.training import PillModelTrainer, ModelEvaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_dataset_management():
    """Example 1: Dataset Management"""
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: Dataset Management")
    logger.info("=" * 60)
    
    # Initialize dataset loader
    loader = PillDatasetLoader(data_dir="data/pill_database")
    
    # Example: Add a pill to database
    # In practice, you would add real pill images
    logger.info(f"Current dataset size: {len(loader.metadata)} pills")
    
    # Get statistics
    stats = loader.get_statistics()
    logger.info(f"Dataset statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    return loader


def example_2_data_augmentation():
    """Example 2: Data Augmentation Pipeline"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 2: Data Augmentation")
    logger.info("=" * 60)
    
    augmentor = DataAugmentor(image_size=(224, 224), use_advanced=True)
    
    # Create a dummy image for demonstration
    dummy_img = Image.new('RGB', (256, 256), color='red')
    
    # Test different augmentation strategies
    logger.info("Testing augmentation strategies:")
    
    # 1. Rotations
    rotated = augmentor.rotate_image(dummy_img, angles=[90, 180, 270])
    logger.info(f"  - Rotation: Generated {len(rotated)} rotated versions")
    
    # 2. Lighting variations
    lit = augmentor.vary_lighting(dummy_img)
    logger.info(f"  - Lighting: Generated {len(lit)} variations")
    
    # 3. Background changes
    bg = augmentor.change_background(dummy_img)
    logger.info(f"  - Backgrounds: Generated {len(bg)} variations")
    
    # 4. Augmentation batch
    batch = augmentor.create_augmentation_batch(
        dummy_img,
        include_original=True,
        rotations=True,
        lighting=True,
        backgrounds=False,
        noise=False
    )
    logger.info(f"  - Batch augmentation: Generated {len(batch)} total images")
    
    return augmentor


def example_3_model_initialization():
    """Example 3: Model Initialization"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 3: Model Initialization and Architecture")
    logger.info("=" * 60)
    
    # Initialize classifier
    classifier = PillClassifier(
        num_shapes=10,      # 10 shape categories
        num_colors=20,      # 20 color categories
        num_imprints=500,   # 500 imprint categories
        backbone="efficientnet",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    
    logger.info(f"Model Architecture:")
    logger.info(f"  - Backbone: EfficientNet-B4")
    logger.info(f"  - Shape classes: 10")
    logger.info(f"  - Color classes: 20")
    logger.info(f"  - Imprint classes: 500")
    logger.info(f"  - Device: {classifier.device}")
    
    # Test forward pass
    dummy_input = torch.randn(2, 3, 224, 224).to(classifier.device)
    predictions = classifier.predict(dummy_input, return_probabilities=True)
    
    logger.info(f"\nPrediction outputs:")
    for key, val in predictions.items():
        if "pred" in key:
            logger.info(f"  - {key}: shape {val.shape}")
    
    return classifier


def example_4_feature_extraction():
    """Example 4: Feature Extraction"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 4: Comprehensive Feature Extraction")
    logger.info("=" * 60)
    
    # Create extractor (with optional model)
    extractor = PillFeatureExtractor(
        model_classifier=None,  # Can be set to a PillClassifier
        use_shape_detector=True,
        use_color_analyzer=True,
        use_imprint_extractor=True,
        use_size_calibrator=True
    )
    
    # Create a sample pill-like image
    pill_img = Image.new('RGB', (256, 256), color='blue')
    
    # Extract features
    features = extractor.extract_features(pill_img)
    
    logger.info(f"Extracted Features:")
    logger.info(f"  - Shape: {features.shape} (confidence: {features.shape_confidence:.2f})")
    logger.info(f"  - Color: {features.color} (confidence: {features.color_confidence:.2f})")
    logger.info(f"  - Imprint: {features.imprint_text} (confidence: {features.imprint_confidence:.2f})")
    logger.info(f"  - Estimated Size: {features.estimated_size_mm} mm")
    
    return extractor


def example_5_training_setup():
    """Example 5: Training Pipeline Setup"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 5: Training Pipeline Setup")
    logger.info("=" * 60)
    
    # Initialize model
    classifier = PillClassifier(
        num_shapes=10,
        num_colors=20,
        num_imprints=500,
        backbone="efficientnet"
    )
    
    # Initialize trainer
    trainer = PillModelTrainer(
        model=classifier,
        device="cuda" if torch.cuda.is_available() else "cpu",
        learning_rate=1e-4,
        weight_decay=1e-5,
        use_scheduler=True,
        checkpoint_dir="checkpoints/pill_authenticator"
    )
    
    logger.info("Trainer initialized with:")
    logger.info(f"  - Learning rate: 1e-4")
    logger.info(f"  - Weight decay: 1e-5")
    logger.info(f"  - Learning rate scheduler: Cosine Annealing")
    logger.info(f"  - Early stopping patience: 20 epochs")
    logger.info(f"  - Checkpoint directory: checkpoints/pill_authenticator")
    
    logger.info("\nTo train:")
    logger.info("  trainer.fit(train_loader, val_loader, num_epochs=50)")
    
    return trainer


def example_6_inference():
    """Example 6: Inference and Predictions"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 6: Inference and Predictions")
    logger.info("=" * 60)
    
    classifier = PillClassifier(
        num_shapes=10,
        num_colors=20,
        num_imprints=500
    )
    
    # Create batch of dummy images
    batch = torch.randn(4, 3, 224, 224).to(classifier.device)
    
    # Make predictions
    predictions = classifier.predict(batch, return_probabilities=True)
    
    logger.info("Inference Results:")
    logger.info(f"  - Batch size: 4")
    
    # Log shape predictions
    shape_probs = predictions["shape_probs"]
    shape_preds = predictions["shape_pred"]
    logger.info(f"  - Shape predictions: {shape_preds.tolist()}")
    logger.info(f"  - Shape confidence range: {shape_probs.max(dim=1).values.mean():.3f}")
    
    # Log color predictions
    color_probs = predictions["color_probs"]
    color_preds = predictions["color_pred"]
    logger.info(f"  - Color predictions: {color_preds.tolist()}")
    logger.info(f"  - Color confidence range: {color_probs.max(dim=1).values.mean():.3f}")
    
    # Log imprint predictions
    imprint_probs = predictions["imprint_probs"]
    imprint_preds = predictions["imprint_pred"]
    logger.info(f"  - Imprint predictions (first 4): {imprint_preds[:4].tolist()}")
    logger.info(f"  - Imprint confidence range: {imprint_probs.max(dim=1).values.mean():.3f}")


def example_7_end_to_end_workflow():
    """Example 7: End-to-End Workflow"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 7: End-to-End Workflow")
    logger.info("=" * 60)
    
    # 1. Initialize dataset
    logger.info("\n1. Initializing dataset...")
    loader = PillDatasetLoader()
    logger.info(f"   - Dataset ready: {len(loader.metadata)} pills")
    
    # 2. Initialize augmentor
    logger.info("\n2. Initializing augmentation pipeline...")
    augmentor = DataAugmentor()
    logger.info("   - Augmentor ready (basic + advanced)")
    
    # 3. Initialize model
    logger.info("\n3. Initializing model...")
    classifier = PillClassifier(
        num_shapes=10,
        num_colors=20,
        num_imprints=500
    )
    logger.info("   - Model ready with multi-task learning heads")
    
    # 4. Initialize feature extractor
    logger.info("\n4. Initializing feature extraction...")
    extractor = PillFeatureExtractor(model_classifier=classifier)
    logger.info("   - Feature extraction ready")
    
    # 5. Initialize trainer
    logger.info("\n5. Initializing training pipeline...")
    trainer = PillModelTrainer(classifier)
    logger.info("   - Trainer ready with multi-task loss")
    
    # 6. Simulate inference
    logger.info("\n6. Running inference on test batch...")
    test_batch = torch.randn(2, 3, 224, 224).to(classifier.device)
    predictions = classifier.predict(test_batch)
    logger.info(f"   - Predictions generated: {list(predictions.keys())}")
    
    logger.info("\n✓ End-to-end workflow completed successfully!")


def main():
    """Run all examples"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║ COMPONENT 2: VISUAL PILL AUTHENTICATOR - EXAMPLES ║")
    logger.info("╚" + "=" * 58 + "╝")
    
    # Run examples
    example_1_dataset_management()
    example_2_data_augmentation()
    example_3_model_initialization()
    example_4_feature_extraction()
    example_5_training_setup()
    example_6_inference()
    example_7_end_to_end_workflow()
    
    logger.info("\n" + "=" * 60)
    logger.info("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    logger.info("=" * 60)
    
    logger.info("\nNext Steps:")
    logger.info("1. Add real pill images to data/pill_database/")
    logger.info("2. Create DataLoader for training")
    logger.info("3. Run trainer.fit() to start training")
    logger.info("4. Monitor validation metrics and early stopping")
    logger.info("5. Evaluate on test set")
    logger.info("6. Integrate with Component 1 (Prescription Digitizer)")


if __name__ == "__main__":
    main()
