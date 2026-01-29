"""
Example usage of the medication management system.
Demonstrates different ways to use the prescription digitizer.
"""

import os
from prescription_digitizer import PrescriptionDigitizer
from src.preprocessing.image_processor import ImageProcessor
from src.ocr.ocr_engine import OCREngine
from src.ner.pattern_matcher import PatternMatcher
from src.validation.database_validator import DatabaseValidator
from src.validation.confidence_scorer import ConfidenceScorer
from utils import logger, perf_monitor, DataProcessor


print("\n" + "="*80)
print("PRESCRIPTION DIGITIZER - DIRECT PROCESSING EXAMPLES")
print("="*80 + "\n")


# ============================================================================
# EXAMPLE 1: Direct Pattern Matching
# ============================================================================

def example_1_direct_pattern_matching():
    """Example 1: Direct pattern extraction without OCR."""
    print("[EXAMPLE 1] Direct Pattern Matching")
    print("-"*80)
    
    matcher = PatternMatcher()
    
    test_prescriptions = [
        "Amoxicillin 500mg orally twice daily for 7 days",
        "Ibuprofen 400mg every 6 hours as needed",
        "Metformin 1000mg twice daily with meals",
    ]
    
    for prescription in test_prescriptions:
        extracted = matcher.extract_all(prescription)
        
        print(f"\nInput: {prescription}")
        print(f"  Dosages: {extracted.get('dosages')}")
        print(f"  Frequency: {extracted.get('frequency')}")
        print(f"  Route: {extracted.get('route')}")
        print(f"  Duration: {extracted.get('duration')}")


# ============================================================================
# EXAMPLE 2: Full Pipeline with Main Application
# ============================================================================

def example_2_full_pipeline():
    """Example 2: Full prescription processing pipeline."""
    print("\n\n[EXAMPLE 2] Full Pipeline Processing")
    print("-"*80)
    
    print("\nInitializing PrescriptionDigitizer...")
    digitizer = PrescriptionDigitizer()
    print("  OK - Digitizer initialized\n")
    
    # Example prescription image
    test_image = "data/sample_prescription.jpg"
    
    if os.path.exists(test_image):
        print(f"Processing image: {test_image}")
        results = digitizer.process_prescription(test_image)
        
        print(f"  Extraction ID: {results['extraction_id']}")
        if results.get('ocr'):
            print(f"  OCR Confidence: {results['ocr'].get('confidence', 0):.2%}")
        if results.get('ner'):
            print(f"  Medications Found: {results['ner'].get('num_medications', 0)}")
        if results.get('confidence_score'):
            score = results['confidence_score']
            print(f"  Overall Confidence: {score['overall_confidence']:.2%}")
            print(f"  Requires Review: {'Yes' if results.get('requires_review') else 'No'}")
    else:
        print(f"Note: Sample image not found at {test_image}")
        print("      In production, provide path to actual prescription image")
        print("      The system is ready to process real prescription images")


# ============================================================================
# EXAMPLE 3: Confidence Scoring
# ============================================================================

def example_3_confidence_scoring():
    """Example 3: Confidence scoring and review queue."""
    print("\n\n[EXAMPLE 3] Confidence Scoring & Review Management")
    print("-"*80)
    
    scorer = ConfidenceScorer()
    
    # High-confidence extraction
    print("\nHigh-Confidence Extraction:")
    high = scorer.calculate_confidence("rx_high", 0.96, 0.94, 0.92)
    print(f"  OCR: 96%, NER: 94%, Validation: 92%")
    print(f"  Overall: {high.overall_confidence:.2%}")
    print(f"  Requires Review: {high.requires_manual_review}")
    
    # Low-confidence extraction
    print("\nLow-Confidence Extraction:")
    low = scorer.calculate_confidence("rx_low", 0.55, 0.50, 0.45)
    print(f"  OCR: 55%, NER: 50%, Validation: 45%")
    print(f"  Overall: {low.overall_confidence:.2%}")
    print(f"  Requires Review: {low.requires_manual_review}")
    
    # Get review queue
    print("\nReview Queue Status:")
    queue = scorer.get_review_queue()
    print(f"  Total Items: {queue['total_items']}")
    print(f"  Low Confidence Items: {queue['low_confidence_count']}")


# ============================================================================
# EXAMPLE 4: Data Processing & Normalization
# ============================================================================

def example_4_data_processing():
    """Example 4: Data normalization and standardization."""
    print("\n\n[EXAMPLE 4] Data Processing & Normalization")
    print("-"*80)
    
    processor = DataProcessor()
    
    medications = [
        ("amoxicillin", "500mg", "twice daily", "oral"),
        ("ibuprofen", "400mg", "every 6 hours", "oral"),
        ("metformin", "1000mg", "twice daily", "oral"),
    ]
    
    print("\nProcessing Medications:")
    for drug, dosage, freq, route in medications:
        record = processor.create_medication_record(
            drug_name=drug,
            dosage=dosage,
            frequency=freq,
            route=route
        )
        print(f"\n  Input:      {drug} | {dosage} | {freq}")
        print(f"  Normalized: {record['drug_name']} | {record['dosage']} | {record['frequency_standardized']}")


# ============================================================================
# EXAMPLE 5: Database Validation
# ============================================================================

def example_5_database_validation():
    """Example 5: FDA database validation."""
    print("\n\n[EXAMPLE 5] Database Validation")
    print("-"*80)
    
    validator = DatabaseValidator()
    
    test_drugs = ['Amoxicillin', 'Ibuprofen', 'Metformin', 'InvalidDrug123']
    
    print("\nDrug Validation Results:")
    for drug in test_drugs:
        is_valid, normalized = validator.validate_drug_name(drug)
        status = "OK" if is_valid else "INVALID"
        print(f"  {drug:<20} : {status}" + (f" -> {normalized}" if normalized else ""))


# ============================================================================
# EXAMPLE 6: Complete Workflow
# ============================================================================

def example_6_complete_workflow():
    """Example 6: Complete end-to-end workflow."""
    print("\n\n[EXAMPLE 6] Complete Workflow")
    print("-"*80)
    
    print("\nStep 1: Initialize the system")
    digitizer = PrescriptionDigitizer()
    processor = DataProcessor()
    print("  OK")
    
    print("\nStep 2: Extract text from prescription")
    prescription_text = "Amoxicillin 500mg orally twice daily for 7 days"
    print(f"  Input: {prescription_text}")
    
    print("\nStep 3: Pattern matching and NER")
    matcher = PatternMatcher()
    extracted = matcher.extract_all(prescription_text)
    print(f"  Dosage: {extracted.get('dosages')}")
    print(f"  Frequency: {extracted.get('frequency')}")
    print(f"  Duration: {extracted.get('duration')}")
    
    print("\nStep 4: Validate against FDA database")
    validator = DatabaseValidator()
    is_valid, normalized = validator.validate_drug_name("Amoxicillin")
    print(f"  Drug Valid: {is_valid}")
    print(f"  Normalized: {normalized}")
    
    print("\nStep 5: Calculate confidence score")
    scorer = ConfidenceScorer()
    score = scorer.calculate_confidence("rx_workflow", 0.95, 0.92, 0.88)
    print(f"  Overall Confidence: {score.overall_confidence:.2%}")
    print(f"  Manual Review Required: {score.requires_manual_review}")
    
    print("\nStep 6: Process and normalize data")
    record = processor.create_medication_record(
        drug_name="amoxicillin",
        dosage="500mg",
        frequency="twice daily"
    )
    print(f"  Final Record: {record['drug_name']} | {record['dosage']} | {record['frequency_standardized']}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    try:
        # Run all examples
        example_1_direct_pattern_matching()
        example_2_full_pipeline()
        example_3_confidence_scoring()
        example_4_data_processing()
        example_5_database_validation()
        example_6_complete_workflow()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nQuick Reference for Direct Usage:")
        print("  from src.ner.pattern_matcher import PatternMatcher")
        print("  matcher = PatternMatcher()")
        print("  result = matcher.extract_all('Amoxicillin 500mg twice daily')")
        print("\nComponents:")
        print("  - Pattern matching: PatternMatcher()")
        print("  - Full pipeline: PrescriptionDigitizer()")
        print("  - Confidence scoring: ConfidenceScorer()")
        print("  - Data processing: DataProcessor()")
        print("  - FDA validation: DatabaseValidator()")
        print("\nFor REST API Server: python api_server.py")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Example error: {str(e)}")
        import traceback
        traceback.print_exc()
