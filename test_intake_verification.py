"""
Component 3: Intake Verification System - Test Suite
Validates all modules and integration points.
"""

import unittest
import numpy as np
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestIntakeVerificationStructure(unittest.TestCase):
    """Test project structure and setup"""
    
    def test_directory_structure(self):
        """Test all required directories exist"""
        base_path = Path('src/intake_verification')
        
        required_dirs = [
            'object_detection',
            'pose_estimation',
            'action_recognition',
            'verification_engine',
            'data_processing',
            'utils'
        ]
        
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            self.assertTrue(dir_path.exists(), f"Directory missing: {dir_path}")
            logger.info(f"✓ Directory exists: {dir_name}")
    
    def test_configuration_file(self):
        """Test configuration file exists and is valid"""
        config_path = Path('configs/component_3_config.yaml')
        self.assertTrue(config_path.exists(), f"Config file missing: {config_path}")
        
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        self.assertIn('models', config)
        self.assertIn('verification', config)
        self.assertIn('processing', config)
        logger.info("✓ Configuration file valid")


class TestObjectDetection(unittest.TestCase):
    """Test pill detection and tracking"""
    
    def test_pill_detection_initialization(self):
        """Test PillDetector initialization"""
        from src.intake_verification.object_detection import PillDetector
        
        detector = PillDetector(model_name='yolov8n', confidence_threshold=0.5)
        self.assertIsNotNone(detector)
        logger.info("✓ PillDetector initialized")
    
    def test_pill_tracker_initialization(self):
        """Test PillTracker initialization"""
        from src.intake_verification.object_detection import PillTracker
        
        tracker = PillTracker(iou_threshold=0.3, max_gap=5)
        self.assertIsNotNone(tracker)
        logger.info("✓ PillTracker initialized")
    
    def test_pill_detection_dataclass(self):
        """Test PillDetection dataclass"""
        from src.intake_verification.object_detection import PillDetection
        
        detection = PillDetection(
            frame_id=0,
            x1=100, y1=100, x2=200, y2=200,
            confidence=0.9,
            class_id=0,
            class_name='pill',
            center_x=150,
            center_y=150,
            width=100,
            height=100
        )
        
        data = detection.to_dict()
        self.assertIn('bbox', data)
        self.assertIn('center', data)
        self.assertIn('confidence', data)
        logger.info("✓ PillDetection dataclass working")


class TestPoseEstimation(unittest.TestCase):
    """Test hand pose estimation"""
    
    def test_hand_pose_estimator_initialization(self):
        """Test HandPoseEstimator initialization"""
        from src.intake_verification.pose_estimation import HandPoseEstimator
        
        estimator = HandPoseEstimator(
            static_image_mode=False,
            max_hands=2,
            min_detection_confidence=0.5
        )
        self.assertIsNotNone(estimator)
        logger.info("✓ HandPoseEstimator initialized")
    
    def test_hand_side_enum(self):
        """Test HandSide enum"""
        from src.intake_verification.pose_estimation import HandSide
        
        self.assertEqual(HandSide.LEFT.value, 'left')
        self.assertEqual(HandSide.RIGHT.value, 'right')
        logger.info("✓ HandSide enum working")
    
    def test_hand_keypoint(self):
        """Test HandKeypoint dataclass"""
        from src.intake_verification.pose_estimation import HandKeypoint
        
        kp1 = HandKeypoint(x=100, y=150, z=0.5, confidence=0.9,
                          landmark_id=0, name='WRIST')
        kp2 = HandKeypoint(x=110, y=160, z=0.5, confidence=0.9,
                          landmark_id=1, name='THUMB_CMC')
        
        distance = kp1.distance_to(kp2)
        self.assertGreater(distance, 0)
        logger.info("✓ HandKeypoint working")
    
    def test_hand_motion_analyzer(self):
        """Test HandMotionAnalyzer"""
        from src.intake_verification.pose_estimation import (
            HandMotionAnalyzer, HandPose, HandSide, HandKeypoint
        )
        
        analyzer = HandMotionAnalyzer()
        self.assertIsNotNone(analyzer)
        logger.info("✓ HandMotionAnalyzer initialized")


class TestActionRecognition(unittest.TestCase):
    """Test action recognition and swallowing detection"""
    
    def test_action_recognizer_initialization(self):
        """Test ActionRecognizer initialization"""
        from src.intake_verification.action_recognition import ActionRecognizer
        
        recognizer = ActionRecognizer(model_type='3dcnn', confidence_threshold=0.6)
        self.assertIsNotNone(recognizer)
        self.assertEqual(len(recognizer.ACTIONS), 4)
        logger.info("✓ ActionRecognizer initialized")
    
    def test_action_3dcnn_model(self):
        """Test 3D CNN model architecture"""
        from src.intake_verification.action_recognition import Action3DCNN
        import torch
        
        model = Action3DCNN(num_classes=4)
        self.assertIsNotNone(model)
        
        # Test forward pass
        x = torch.randn(1, 3, 16, 224, 224)
        output = model(x)
        self.assertEqual(output.shape, (1, 4))
        logger.info("✓ Action3DCNN model working")
    
    def test_action_lstm_model(self):
        """Test LSTM model architecture"""
        from src.intake_verification.action_recognition import ActionLSTM
        import torch
        
        model = ActionLSTM(input_size=18, hidden_size=256, num_classes=4)
        self.assertIsNotNone(model)
        
        # Test forward pass
        x = torch.randn(1, 30, 18)
        output = model(x)
        self.assertEqual(output.shape, (1, 4))
        logger.info("✓ ActionLSTM model working")
    
    def test_swallowing_detector(self):
        """Test SwallowingDetector"""
        from src.intake_verification.action_recognition import (
            SwallowingDetector, ActionRecognizer
        )
        
        recognizer = ActionRecognizer(model_type='3dcnn')
        detector = SwallowingDetector(recognizer)
        self.assertIsNotNone(detector)
        logger.info("✓ SwallowingDetector initialized")


class TestVerificationEngine(unittest.TestCase):
    """Test verification engine and multi-modal fusion"""
    
    def test_intake_status_enum(self):
        """Test IntakeStatus enum"""
        from src.intake_verification.verification_engine import IntakeStatus
        
        self.assertEqual(IntakeStatus.CONFIRMED.value, 'confirmed')
        self.assertEqual(IntakeStatus.LIKELY.value, 'likely')
        self.assertEqual(IntakeStatus.UNCERTAIN.value, 'uncertain')
        self.assertEqual(IntakeStatus.REJECTED.value, 'rejected')
        logger.info("✓ IntakeStatus enum working")
    
    def test_verification_engine_initialization(self):
        """Test VerificationEngine initialization"""
        from src.intake_verification.verification_engine import VerificationEngine
        
        engine = VerificationEngine()
        self.assertIsNotNone(engine)
        self.assertIn('pill_detection', engine.weights)
        self.assertIn('hand_tracking', engine.weights)
        self.assertIn('action_recognition', engine.weights)
        logger.info("✓ VerificationEngine initialized")
    
    def test_verification_event(self):
        """Test VerificationEvent dataclass"""
        from src.intake_verification.verification_engine import (
            VerificationEvent, IntakeStatus
        )
        
        event = VerificationEvent(
            event_id='test_1',
            timestamp=0.0,
            pill_detection={'detected': True},
            hand_tracking={'detected': True},
            action_recognition={'detected': True},
            modal_confidences={'pill_detection': 0.8, 'hand_tracking': 0.7, 'action_recognition': 0.9},
            final_confidence=0.8,
            status=IntakeStatus.CONFIRMED,
            reasoning=['Test event']
        )
        
        data = event.to_dict()
        self.assertIn('event_id', data)
        self.assertIn('status', data)
        logger.info("✓ VerificationEvent working")
    
    def test_verify_intake(self):
        """Test verification logic"""
        from src.intake_verification.verification_engine import VerificationEngine
        
        engine = VerificationEngine()
        
        result = engine.verify_intake(
            pill_trajectory={'detected': True, 'avg_confidence': 0.85, 'disappearance_frame': 25},
            hand_trajectory={'detected': True, 'avg_confidence': 0.75, 'mouth_contact_frames': [20, 21, 22]},
            action_sequence={'swallow_frames': [(16, 20)], 'avg_confidence': 0.70},
            video_metadata={'duration': 1.0, 'frame_count': 30, 'fps': 30}
        )
        
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.final_status)
        self.assertGreater(result.final_confidence, 0)
        logger.info("✓ Verification logic working")


class TestVideoProcessing(unittest.TestCase):
    """Test video processing utilities"""
    
    def test_frame_processor(self):
        """Test FrameProcessor"""
        from src.intake_verification.data_processing import FrameProcessor
        
        processor = FrameProcessor()
        
        # Create test frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test resize
        resized = processor.resize(frame, (224, 224))
        self.assertEqual(resized.shape[:2], (224, 224))
        
        # Test normalize
        normalized = processor.normalize(resized)
        self.assertGreaterEqual(normalized.max(), 0)
        self.assertLessEqual(normalized.max(), 1)
        
        logger.info("✓ FrameProcessor working")
    
    def test_multimodal_aggregator(self):
        """Test MultiModalDataAggregator"""
        from src.intake_verification.data_processing import MultiModalDataAggregator
        
        aggregator = MultiModalDataAggregator(num_frames=30)
        
        # Add sample data
        aggregator.add_pill_detection(0, {'center': [320, 200], 'confidence': 0.8})
        aggregator.add_hand_pose(1, {'hand': 'right', 'confidence': 0.7})
        aggregator.add_action_prediction(2, {'action': 'swallowing'})
        
        # Get statistics
        stats = aggregator.get_statistics()
        self.assertGreater(stats['frames_with_pill'], 0)
        
        logger.info("✓ MultiModalDataAggregator working")
    
    def test_temporal_cache(self):
        """Test TemporalFeatureCache"""
        from src.intake_verification.data_processing import TemporalFeatureCache
        
        cache = TemporalFeatureCache(cache_size=10)
        
        # Store and retrieve
        test_feature = np.random.randn(256)
        cache.put('frame_0', test_feature)
        retrieved = cache.get('frame_0')
        
        self.assertIsNotNone(retrieved)
        np.testing.assert_array_almost_equal(test_feature, retrieved)
        
        logger.info("✓ TemporalFeatureCache working")


class TestIntakeVerifier(unittest.TestCase):
    """Test unified IntakeVerifier system"""
    
    def test_intake_verifier_initialization(self):
        """Test IntakeVerifier initialization"""
        from src.intake_verification import IntakeVerifier
        
        verifier = IntakeVerifier(device='cpu')
        
        self.assertIsNotNone(verifier)
        self.assertIsNotNone(verifier.pill_detector)
        self.assertIsNotNone(verifier.hand_estimator)
        self.assertIsNotNone(verifier.action_recognizer)
        self.assertIsNotNone(verifier.verification_engine)
        
        logger.info("✓ IntakeVerifier initialized with all components")
    
    def test_configuration_loading(self):
        """Test configuration loading"""
        from src.intake_verification import IntakeVerifier
        
        verifier = IntakeVerifier(device='cpu')
        
        self.assertIn('models', verifier.config)
        self.assertIn('verification', verifier.config)
        
        logger.info("✓ Configuration loaded correctly")


def run_all_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIntakeVerificationStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestObjectDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestPoseEstimation))
    suite.addTests(loader.loadTestsFromTestCase(TestActionRecognition))
    suite.addTests(loader.loadTestsFromTestCase(TestVerificationEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestVideoProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestIntakeVerifier))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        logger.info("\n✓ ALL TESTS PASSED")
    else:
        logger.error("\n✗ SOME TESTS FAILED")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
