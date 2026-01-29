"""
Component 3: Intake Verification System - Comprehensive Examples
Demonstrates all features of the multi-modal intake verification pipeline.
"""

import numpy as np
from src.intake_verification.object_detection import PillDetector, PillTracker
from src.intake_verification.pose_estimation import HandPoseEstimator, HandMotionAnalyzer
from src.intake_verification.action_recognition import ActionRecognizer, SwallowingDetector
from src.intake_verification.verification_engine import VerificationEngine, IntakeStatus
from src.intake_verification.data_processing import (
    VideoLoader, FrameProcessor, MultiModalDataAggregator, TemporalFeatureCache
)
from src.intake_verification import IntakeVerifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_pill_detection():
    """Example 1: Pill Detection with YOLOv8"""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 1: Pill Detection")
    logger.info("="*60)
    
    # Initialize detector
    detector = PillDetector(model_name='yolov8n', confidence_threshold=0.5)
    
    # Create synthetic frame for demonstration
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    logger.info(f"Frame shape: {frame.shape}")
    
    # Detect pills
    detections = detector.detect(frame, frame_id=0)
    logger.info(f"Detected {len(detections)} pills")
    
    for det in detections:
        logger.info(f"  Pill at ({det.center_x:.0f}, {det.center_y:.0f}), "
                   f"confidence: {det.confidence:.2f}")
    
    print("✓ Pill detection example complete\n")


def example_2_pill_tracking():
    """Example 2: Pill Tracking Across Frames"""
    logger.info("="*60)
    logger.info("EXAMPLE 2: Pill Tracking")
    logger.info("="*60)
    
    # Initialize tracker
    tracker = PillTracker(iou_threshold=0.3, max_gap=5)
    
    # Simulate detections across frames
    from src.intake_verification.object_detection import PillDetection
    
    frame_detections = []
    for frame_id in range(10):
        # Simulate pill moving down the image
        x = 320 + np.random.normal(0, 5)
        y = 100 + frame_id * 30 + np.random.normal(0, 5)
        
        detection = PillDetection(
            frame_id=frame_id,
            x1=x-20, y1=y-20, x2=x+20, y2=y+20,
            confidence=0.8 + np.random.normal(0, 0.05),
            class_id=0, class_name='pill',
            center_x=x, center_y=y,
            width=40, height=40
        )
        frame_detections.append(detection)
    
    # Track
    for det in frame_detections:
        tracker.update([det])
    
    trajectories = tracker.finish()
    logger.info(f"Generated {len(trajectories)} trajectories")
    
    for traj in trajectories:
        logger.info(f"  Trajectory: {traj.total_frames} frames, "
                   f"movement: {traj.movement_distance:.0f} pixels, "
                   f"confidence: {traj.avg_confidence:.2f}")
    
    print("✓ Pill tracking example complete\n")


def example_3_hand_pose_estimation():
    """Example 3: Hand Pose Estimation with MediaPipe"""
    logger.info("="*60)
    logger.info("EXAMPLE 3: Hand Pose Estimation")
    logger.info("="*60)
    
    # Initialize estimator
    estimator = HandPoseEstimator(
        static_image_mode=False,
        max_hands=2,
        min_detection_confidence=0.5
    )
    
    # Create synthetic frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Estimate poses
    poses = estimator.estimate(frame, frame_id=0)
    logger.info(f"Detected {len(poses)} hands")
    
    for pose in poses:
        logger.info(f"  Hand: {pose.hand_side.value}, "
                   f"keypoints: {len(pose.keypoints)}, "
                   f"confidence: {pose.avg_confidence:.2f}, "
                   f"near_mouth: {pose.is_near_mouth}")
    
    print("✓ Hand pose estimation example complete\n")


def example_4_hand_motion_analysis():
    """Example 4: Hand Motion Analysis"""
    logger.info("="*60)
    logger.info("EXAMPLE 4: Hand Motion Analysis")
    logger.info("="*60)
    
    # Create synthetic hand poses
    from src.intake_verification.pose_estimation import HandPose, HandKeypoint, HandSide
    
    poses_list = []
    
    for frame_id in range(15):
        # Simulate hand moving toward mouth
        keypoints = [
            HandKeypoint(x=320 + frame_id*3, y=200 - frame_id*5, z=0.5,
                        confidence=0.9, landmark_id=0, name='WRIST')
        ]
        
        pose = HandPose(
            frame_id=frame_id,
            hand_side=HandSide.RIGHT,
            keypoints=keypoints,
            avg_confidence=0.9,
            is_open=True,
            is_near_face=frame_id > 5,
            is_near_mouth=frame_id > 10
        )
        poses_list.append([pose])
    
    # Analyze motion
    analyzer = HandMotionAnalyzer()
    trajectories = analyzer.track_hand(poses_list)
    
    logger.info(f"Tracked {len(trajectories)} hand trajectories")
    
    for traj in trajectories:
        analysis = analyzer.detect_mouth_approach(traj)
        logger.info(f"  Hand {traj.hand_side.value}: "
                   f"movement_distance: {analysis['movement_distance']:.0f} px, "
                   f"avg_velocity: {analysis['avg_velocity']:.2f} px/frame, "
                   f"mouth_contact: {analysis['detected']}")
    
    print("✓ Hand motion analysis example complete\n")


def example_5_action_recognition():
    """Example 5: Action Recognition (Swallowing Detection)"""
    logger.info("="*60)
    logger.info("EXAMPLE 5: Action Recognition")
    logger.info("="*60)
    
    # Initialize recognizer
    recognizer = ActionRecognizer(model_type='3dcnn', confidence_threshold=0.6)
    
    # Create synthetic frames
    num_frames = 32
    frames = np.random.randint(0, 255, (num_frames, 224, 224, 3), dtype=np.uint8)
    
    logger.info(f"Processing {num_frames} frames for action recognition")
    
    # Predict actions
    classifications = recognizer.predict_3dcnn(frames, frame_stride=4)
    
    logger.info(f"Generated {len(classifications)} action predictions")
    
    for i, classification in enumerate(classifications[:3]):  # Show first 3
        logger.info(f"  Prediction {i}: {classification.action_name}, "
                   f"confidence: {classification.confidence:.2f}, "
                   f"detected: {classification.is_positive}")
    
    # Detect swallowing
    detector = SwallowingDetector(recognizer)
    swallow_result = detector.detect_swallow(frames)
    
    logger.info(f"Swallowing detected: {swallow_result['swallowing_detected']}")
    logger.info(f"Number of swallows: {swallow_result['num_swallows']}")
    
    print("✓ Action recognition example complete\n")


def example_6_verification_engine():
    """Example 6: Multi-Modal Verification Engine"""
    logger.info("="*60)
    logger.info("EXAMPLE 6: Verification Engine")
    logger.info("="*60)
    
    # Initialize engine
    engine = VerificationEngine(weights={
        'pill_detection': 0.30,
        'hand_tracking': 0.25,
        'action_recognition': 0.45
    })
    
    # Simulate results from all modalities
    pill_trajectory = {
        'detected': True,
        'avg_confidence': 0.85,
        'movement_distance': 150,
        'disappearance_frame': 25,
        'num_frames': 8
    }
    
    hand_trajectory = {
        'detected': True,
        'avg_confidence': 0.75,
        'mouth_contact_frames': [20, 21, 22, 23, 24],
        'total_frames': 30
    }
    
    action_sequence = {
        'detected': True,
        'avg_confidence': 0.70,
        'swallow_frames': [(16, 20)]
    }
    
    video_metadata = {
        'duration': 1.0,
        'frame_count': 30,
        'fps': 30
    }
    
    # Verify intake
    result = engine.verify_intake(
        pill_trajectory=pill_trajectory,
        hand_trajectory=hand_trajectory,
        action_sequence=action_sequence,
        video_metadata=video_metadata
    )
    
    logger.info(f"Verification Status: {result.final_status.value}")
    logger.info(f"Final Confidence: {result.final_confidence:.2%}")
    
    # Generate report
    report = engine.generate_report(result)
    logger.info("Report:\n" + report)
    
    print("✓ Verification engine example complete\n")


def example_7_video_processing():
    """Example 7: Video Processing Pipeline"""
    logger.info("="*60)
    logger.info("EXAMPLE 7: Video Processing")
    logger.info("="*60)
    
    # Create frame processor
    processor = FrameProcessor()
    
    # Create synthetic frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Resize
    resized = processor.resize(frame, (224, 224), keep_aspect=True)
    logger.info(f"Original: {frame.shape}, Resized: {resized.shape}")
    
    # Normalize
    normalized = processor.normalize(resized)
    logger.info(f"Normalized range: [{normalized.min():.3f}, {normalized.max():.3f}]")
    
    # Enhancement
    enhanced = processor.enhance_contrast(resized, alpha=1.5)
    logger.info(f"Enhanced contrast applied")
    
    # Multi-modal aggregation
    aggregator = MultiModalDataAggregator(num_frames=30)
    
    # Add some sample data
    for frame_id in range(30):
        if frame_id % 3 == 0:
            aggregator.add_pill_detection(frame_id, {
                'frame_id': frame_id,
                'center': [320, 200],
                'confidence': 0.8
            })
        
        if frame_id % 2 == 0:
            aggregator.add_hand_pose(frame_id, {
                'hand': 'right',
                'confidence': 0.7
            })
    
    stats = aggregator.get_statistics()
    logger.info(f"Aggregation stats: {stats}")
    
    # Feature cache
    cache = TemporalFeatureCache(cache_size=10)
    test_features = np.random.randn(256)
    cache.put('frame_0', test_features)
    retrieved = cache.get('frame_0')
    logger.info(f"Feature cache test: stored {test_features.shape}, retrieved {retrieved.shape}")
    
    print("✓ Video processing example complete\n")


def example_8_unified_system():
    """Example 8: Unified Intake Verifier System"""
    logger.info("="*60)
    logger.info("EXAMPLE 8: Unified IntakeVerifier System")
    logger.info("="*60)
    
    # Initialize unified system
    verifier = IntakeVerifier(device='cpu')
    
    logger.info("✓ IntakeVerifier initialized with all components")
    logger.info("  - Pill Detector (YOLOv8)")
    logger.info("  - Hand Pose Estimator (MediaPipe)")
    logger.info("  - Action Recognizer (3D CNN)")
    logger.info("  - Verification Engine (Multi-Modal Fusion)")
    logger.info("  - Video Processing Pipeline")
    
    logger.info("\nSystem ready for video processing")
    logger.info("Usage: verifier.verify_video('path/to/video.mp4')")
    
    print("✓ Unified system example complete\n")


def example_9_realtime_processing():
    """Example 9: Real-Time Processing"""
    logger.info("="*60)
    logger.info("EXAMPLE 9: Real-Time Processing")
    logger.info("="*60)
    
    from src.intake_verification.verification_engine import RealTimeVerifier, VerificationEngine
    
    # Initialize real-time verifier
    engine = VerificationEngine()
    realtime_verifier = RealTimeVerifier(engine)
    
    logger.info("Real-time verifier initialized")
    logger.info(f"Buffer size: {realtime_verifier.max_buffer_size} frames")
    
    # Simulate frame stream
    for frame_id in range(50):
        frame_data = {
            'frame_id': frame_id,
            'pill_center': [320 + frame_id, 200 - frame_id * 2],
            'hand_detected': frame_id > 10,
            'mouth_detected': frame_id > 30
        }
        
        event = realtime_verifier.process_frame(frame_data)
        
        if event:
            logger.info(f"Intake event detected at frame {frame_id}:")
            logger.info(f"  Status: {event.status.value}")
            logger.info(f"  Confidence: {event.final_confidence:.2%}")
    
    print("✓ Real-time processing example complete\n")


def main():
    """Run all examples"""
    logger.info("\n" + "="*60)
    logger.info("COMPONENT 3: INTAKE VERIFICATION SYSTEM")
    logger.info("Comprehensive Examples")
    logger.info("="*60 + "\n")
    
    try:
        example_1_pill_detection()
        example_2_pill_tracking()
        example_3_hand_pose_estimation()
        example_4_hand_motion_analysis()
        example_5_action_recognition()
        example_6_verification_engine()
        example_7_video_processing()
        example_8_unified_system()
        example_9_realtime_processing()
        
        logger.info("\n" + "="*60)
        logger.info("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        logger.info("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Example error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
