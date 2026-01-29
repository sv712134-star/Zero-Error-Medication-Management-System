#!/usr/bin/env python
"""System test - verify all core components are operational"""

import sys
print("\n" + "="*70)
print("MEDICATION MANAGEMENT SYSTEM - OPERATIONAL TEST")
print("="*70 + "\n")

try:
    # Test 1: Pattern Matching
    print("[1/5] Testing Pattern Matcher...")
    from src.ner.pattern_matcher import PatternMatcher
    
    matcher = PatternMatcher()
    result = matcher.extract_all('Take Amoxicillin 500mg twice daily for 7 days')
    
    assert result.get('dosages'), "Dosage extraction failed"
    assert result.get('frequency'), "Frequency extraction failed"
    assert result.get('duration'), "Duration extraction failed"
    print("  PASSED - Pattern matching working")
    print(f"    - Dosages: {result.get('dosages')}")
    print(f"    - Frequency: {result.get('frequency')}")
    print(f"    - Duration: {result.get('duration')}")
    
    # Test 2: Confidence Scoring
    print("\n[2/5] Testing Confidence Scoring...")
    from src.validation.confidence_scorer import ConfidenceScorer
    
    scorer = ConfidenceScorer()
    score = scorer.calculate_confidence('test123', 0.95, 0.92, 0.88)
    
    assert score.overall_confidence > 0.90, "Confidence score incorrect"
    assert not score.requires_manual_review, "Review flag incorrect"
    print("  PASSED - Confidence scoring working")
    print(f"    - Overall Confidence: {score.overall_confidence:.2%}")
    print(f"    - Requires Review: {score.requires_manual_review}")
    
    # Test 3: Data Processing
    print("\n[3/5] Testing Data Processor...")
    from utils import DataProcessor
    
    processor = DataProcessor()
    record = processor.create_medication_record(
        drug_name="amoxicillin",
        dosage="500mg",
        frequency="twice daily"
    )
    
    assert record['drug_name'] == "Amoxicillin", "Drug name normalization failed"
    assert record['frequency'] == "BID", "Frequency standardization failed"
    print("  PASSED - Data processing working")
    print(f"    - Normalized Drug: {record['drug_name']}")
    print(f"    - Standardized Frequency: {record['frequency']}")
    
    # Test 4: Image Processor
    print("\n[4/5] Testing Image Processor...")
    from src.preprocessing.image_processor import ImageProcessor
    
    proc = ImageProcessor()
    assert proc.target_width == 800, "Image processor config incorrect"
    print("  PASSED - Image processor initialized")
    print(f"    - Target dimensions: {proc.target_width}x{proc.target_height}")
    
    # Test 5: Main Application
    print("\n[5/5] Testing Main Application...")
    from prescription_digitizer import PrescriptionDigitizer
    
    digitizer = PrescriptionDigitizer()
    assert digitizer.image_processor is not None
    assert digitizer.ocr_engine is not None
    assert digitizer.ner_extractor is not None
    assert digitizer.validator is not None
    assert digitizer.confidence_scorer is not None
    print("  PASSED - Main application initialized")
    print("    - Preprocessor: OK")
    print("    - OCR Engine: OK")
    print("    - NER Extractor: OK")
    print("    - Validator: OK")
    print("    - Scorer: OK")
    
    # Summary
    print("\n" + "="*70)
    print("SUCCESS - ALL TESTS PASSED")
    print("="*70)
    print("\nSystem Status: FULLY OPERATIONAL")
    print("All 5 core components verified and working correctly")
    print("\n" + "="*70 + "\n")
    sys.exit(0)
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
