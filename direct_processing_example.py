#!/usr/bin/env python
"""
Simple Direct Prescription Processing - No Network Dependencies
Demonstrates pattern matching and data processing without OCR/API calls
"""

from src.ner.pattern_matcher import PatternMatcher
from src.validation.confidence_scorer import ConfidenceScorer
from utils import DataProcessor

print("\n" + "="*80)
print("PRESCRIPTION PROCESSING - DIRECT EXTRACTION EXAMPLES")
print("="*80 + "\n")

# ============================================================================
# Example: Direct Pattern Extraction
# ============================================================================

print("[EXAMPLE] Direct Pattern Extraction from Text")
print("-"*80)

matcher = PatternMatcher()

prescriptions = [
    "Amoxicillin 500mg orally twice daily for 7 days",
    "Ibuprofen 400mg every 6 hours as needed for pain",
    "Metformin 1000mg twice daily with meals",
    "Aspirin 325mg once daily for heart disease prevention",
]

for i, rx_text in enumerate(prescriptions, 1):
    print(f"\n[Prescription {i}]")
    print(f"Text: {rx_text}")
    
    # Extract all patterns
    extracted = matcher.extract_all(rx_text)
    
    print(f"Extracted Information:")
    dosages = extracted.get('dosages', [])
    if dosages:
        print(f"  Dosage:       {dosages[0]['full_text']} (at position {dosages[0]['position']})")
    print(f"  Frequency:    {extracted.get('frequency', 'Not specified')}")
    print(f"  Route:        {extracted.get('route', 'Not specified')}")
    print(f"  Duration:     {extracted.get('duration', 'Not specified')}")
    if extracted.get('instructions'):
        print(f"  Instructions: {extracted.get('instructions', [])}")

# ============================================================================
# Example: Confidence Scoring
# ============================================================================

print("\n\n[EXAMPLE] Confidence Scoring")
print("-"*80)

scorer = ConfidenceScorer()

scenarios = [
    ("High Confidence", 0.96, 0.94, 0.92),
    ("Medium Confidence", 0.75, 0.70, 0.65),
    ("Low Confidence", 0.55, 0.50, 0.45),
]

for scenario_name, ocr_conf, ner_conf, val_conf in scenarios:
    score = scorer.calculate_confidence(f"rx_{scenario_name}", ocr_conf, ner_conf, val_conf)
    
    print(f"\n{scenario_name}:")
    print(f"  Component Scores:")
    print(f"    - OCR Confidence:        {ocr_conf:.2%}")
    print(f"    - NER Confidence:        {ner_conf:.2%}")
    print(f"    - Validation Confidence: {val_conf:.2%}")
    print(f"  Result:")
    print(f"    - Overall Confidence: {score.overall_confidence:.2%}")
    print(f"    - Formula: (0.40 * {ocr_conf}) + (0.35 * {ner_conf}) + (0.25 * {val_conf})")
    print(f"    - Manual Review Needed: {'YES' if score.requires_manual_review else 'NO'}")

# ============================================================================
# Example: Data Processing
# ============================================================================

print("\n\n[EXAMPLE] Data Processing & Normalization")
print("-"*80)

processor = DataProcessor()

print("\nProcessing Medications:")

meds = [
    ("amoxicillin", "500mg", "twice daily"),
    ("ibuprofen", "400mg", "every 6 hours"),
    ("metformin", "1000mg", "twice daily"),
    ("aspirin", "325mg", "once daily"),
]

for drug_name, dosage, frequency in meds:
    record = processor.create_medication_record(
        drug_name=drug_name,
        dosage=dosage,
        frequency=frequency,
        route="oral"
    )
    
    print(f"\n  Raw Input:")
    print(f"    {drug_name} | {dosage} | {frequency}")
    print(f"  Normalized Output:")
    print(f"    {record['drug_name']} | {record['dosage']} | {record['frequency']}")

# ============================================================================
# Example: Complete Workflow
# ============================================================================

print("\n\n[EXAMPLE] Complete Prescription Processing Workflow")
print("-"*80)

print(f"\nScenario: Processing a prescription for a patient")

# Step 1: Text Input
print("\nStep 1: Input prescription text")
rx_text = "Amoxicillin 500mg orally twice daily for 7 days with food"
print(f"  Text: {rx_text}")

# Step 2: Pattern Extraction
print("\nStep 2: Extract medication information")
matcher = PatternMatcher()
extracted = matcher.extract_all(rx_text)
dosages = extracted.get('dosages', [])
dosage_text = dosages[0]['full_text'] if dosages else 'N/A'
print(f"  Drug: Amoxicillin")
print(f"  Dosage: {dosage_text}")
print(f"  Frequency: {extracted.get('frequency')}")
print(f"  Route: {extracted.get('route')}")
print(f"  Duration: {extracted.get('duration')}")
if extracted.get('instructions'):
    print(f"  Instructions: {extracted.get('instructions')}")

# Step 3: Calculate Confidence
print("\nStep 3: Calculate confidence score")
scorer = ConfidenceScorer()
score = scorer.calculate_confidence("workflow_rx", 0.95, 0.92, 0.88)
print(f"  Overall Confidence: {score.overall_confidence:.2%}")
print(f"  Quality: {'APPROVED' if not score.requires_manual_review else 'NEEDS REVIEW'}")

# Step 4: Process Data
print("\nStep 4: Normalize and standardize data")
processor = DataProcessor()
record = processor.create_medication_record(
    drug_name="amoxicillin",
    dosage="500mg",
    frequency="twice daily",
    route="oral"
)
print(f"  Medication Record:")
print(f"    - Drug: {record['drug_name']}")
print(f"    - Dosage: {record['dosage']}")
print(f"    - Frequency: {record['frequency']} (BID = twice daily)")
print(f"    - Route: {record['route'].upper() if record['route'] else 'N/A'}")

# Step 5: Output
print("\nStep 5: Ready for API/Database submission")
print(f"  Status: READY")
print(f"  Fields: Complete and normalized")
print(f"  Quality: High confidence")

# ============================================================================
# Summary
# ============================================================================

print("\n\n" + "="*80)
print("SUMMARY")
print("="*80)

print("\nDirect Processing Components Available:")
print("  1. PatternMatcher - Extract dosage, frequency, route, duration, instructions")
print("  2. ConfidenceScorer - Calculate weighted confidence scores")
print("  3. DataProcessor - Normalize drug names and standardize frequencies")
print("\nUsage Example:")
print("""
  from src.ner.pattern_matcher import PatternMatcher
  
  matcher = PatternMatcher()
  result = matcher.extract_all('Amoxicillin 500mg twice daily')
  
  print(result['dosages'])      # [{'value': '500', 'unit': 'mg', ...}]
  print(result['frequency'])    # 'Twice daily'
""")

print("\nFull System Components (with network dependencies):")
print("  - PrescriptionDigitizer: Full pipeline orchestrator")
print("  - OCREngine: EasyOCR/PaddleOCR for text extraction")
print("  - NERExtractor: Named entity recognition")
print("  - DatabaseValidator: FDA drug validation")
print("  - REST API: FastAPI server at localhost:8000")

print("\n" + "="*80)
print("Processing Examples Completed Successfully")
print("="*80 + "\n")
