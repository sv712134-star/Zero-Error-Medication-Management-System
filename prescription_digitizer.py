"""
Main prescription digitizer application.
Orchestrates the complete pipeline: preprocessing, OCR, NER, and validation.
"""

import os
import uuid
from typing import Optional, Dict
from datetime import datetime
from dataclasses import asdict

from src.preprocessing.image_processor import ImageProcessor
from src.ocr.ocr_engine import OCREngine
from src.ner.ner_extractor import NERExtractor
from src.ner.pattern_matcher import PatternMatcher
from src.validation.database_validator import DatabaseValidator
from src.validation.confidence_scorer import ConfidenceScorer, ReviewStatus


class PrescriptionDigitizer:
    """Main application for prescription digitization."""

    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        Initialize prescription digitizer with all components.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.image_processor = ImageProcessor(
            target_width=self.config.get('preprocessing', {}).get('target_width', 800),
            target_height=self.config.get('preprocessing', {}).get('target_height', 600)
        )
        
        self.ocr_engine = OCREngine(
            primary_backend=self.config.get('ocr', {}).get('backend', 'easyocr'),
            languages=self.config.get('ocr', {}).get('languages', ['en']),
            use_gpu=self.config.get('ocr', {}).get('use_gpu', False)
        )
        
        self.ner_extractor = NERExtractor(
            use_clinical_bert=self.config.get('ner', {}).get('use_clinical_bert', True),
            use_gpu=self.config.get('ner', {}).get('use_gpu', False)
        )
        
        self.pattern_matcher = PatternMatcher()
        
        self.validator = DatabaseValidator(
            cache_dir=self.config.get('validation', {}).get('cache_dir', 'data/drug_cache')
        )
        
        self.confidence_scorer = ConfidenceScorer(
            ocr_weight=self.config.get('scoring', {}).get('ocr_weight', 0.4),
            ner_weight=self.config.get('scoring', {}).get('ner_weight', 0.35),
            validation_weight=self.config.get('scoring', {}).get('validation_weight', 0.25),
            manual_review_threshold=self.config.get('scoring', {}).get('manual_review_threshold', 0.7)
        )

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration file."""
        if os.path.exists(config_path):
            import yaml
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return self._default_config()

    def _default_config(self) -> Dict:
        """Default configuration."""
        return {
            'preprocessing': {
                'target_width': 800,
                'target_height': 600
            },
            'ocr': {
                'backend': 'easyocr',
                'languages': ['en'],
                'use_gpu': False
            },
            'ner': {
                'use_clinical_bert': True,
                'use_gpu': False
            },
            'validation': {
                'cache_dir': 'data/drug_cache'
            },
            'scoring': {
                'ocr_weight': 0.4,
                'ner_weight': 0.35,
                'validation_weight': 0.25,
                'manual_review_threshold': 0.7
            }
        }

    def process_prescription(self, image_path: str, 
                            save_intermediate: bool = False) -> Dict:
        """
        Complete prescription digitization pipeline.
        
        Args:
            image_path: Path to prescription image
            save_intermediate: Save intermediate processing results
            
        Returns:
            Complete extraction and validation results
        """
        extraction_id = str(uuid.uuid4())[:8]
        results = {
            'extraction_id': extraction_id,
            'timestamp': datetime.now().isoformat(),
            'image_path': image_path,
            'preprocessing': None,
            'ocr': None,
            'ner': None,
            'patterns': None,
            'validation': None,
            'confidence_score': None,
            'requires_review': False,
            'review_queue_id': None
        }

        try:
            # Step 1: Image Preprocessing
            print(f"[{extraction_id}] Step 1: Image Preprocessing...")
            processed_image = self.image_processor.preprocess_pipeline(image_path)
            
            if processed_image is None:
                raise ValueError("Image preprocessing failed")
            
            results['preprocessing'] = {
                'status': 'success',
                'message': 'Image successfully preprocessed'
            }

            # Save preprocessed image if requested
            if save_intermediate:
                processed_path = f"data/processed_{extraction_id}.jpg"
                self.image_processor.save_image(processed_image, processed_path)
                results['preprocessing']['output_path'] = processed_path

            # Step 2: OCR Text Extraction
            print(f"[{extraction_id}] Step 2: OCR Text Extraction...")
            ocr_results = self.ocr_engine.extract_text(image_path)
            
            if not ocr_results:
                raise ValueError("OCR extraction failed")
            
            extracted_text = self.ocr_engine.get_full_text(ocr_results)
            avg_ocr_confidence = sum(r.confidence for r in ocr_results) / len(ocr_results)
            
            results['ocr'] = {
                'status': 'success',
                'full_text': extracted_text,
                'confidence': avg_ocr_confidence,
                'num_extractions': len(ocr_results),
                'details': [asdict(r) for r in ocr_results[:5]]  # Top 5
            }

            # Step 3: NER and Entity Extraction
            print(f"[{extraction_id}] Step 3: NER Entity Extraction...")
            entities = self.ner_extractor.extract_entities(extracted_text)
            medications = self.ner_extractor.group_entities_into_medications(
                entities, extracted_text
            )
            
            avg_ner_confidence = sum(e.confidence for e in entities) / len(entities) if entities else 0.5
            
            results['ner'] = {
                'status': 'success',
                'num_entities': len(entities),
                'num_medications': len(medications),
                'confidence': avg_ner_confidence,
                'medications': [
                    {
                        'drug_name': m.drug_name,
                        'dosage': m.dosage,
                        'frequency': m.frequency,
                        'route': m.route,
                        'duration': m.duration
                    }
                    for m in medications
                ]
            }

            # Step 4: Pattern Matching
            print(f"[{extraction_id}] Step 4: Pattern Matching...")
            patterns = self.pattern_matcher.extract_all(extracted_text)
            
            results['patterns'] = {
                'status': 'success',
                'dosages': patterns['dosages'],
                'frequency': patterns['frequency'],
                'route': patterns['route'],
                'duration': patterns['duration'],
                'instructions': patterns['instructions']
            }

            # Step 5: Database Validation
            print(f"[{extraction_id}] Step 5: Database Validation...")
            validation_result = {}
            validation_confidence = 0.5
            
            for med in medications:
                if med.drug_name:
                    validation = self.validator.validate_prescription(
                        med.drug_name, med.dosage, med.frequency
                    )
                    validation_result[med.drug_name] = validation
                    
                    # Calculate validation confidence
                    if validation['drug_valid']:
                        validation_confidence = 0.9 if validation['dosage_valid'] else 0.7
            
            results['validation'] = {
                'status': 'success',
                'validations': validation_result,
                'confidence': validation_confidence
            }

            # Step 6: Confidence Scoring
            print(f"[{extraction_id}] Step 6: Confidence Scoring...")
            score = self.confidence_scorer.calculate_confidence(
                extraction_id=extraction_id,
                ocr_confidence=avg_ocr_confidence,
                ner_confidence=avg_ner_confidence,
                validation_confidence=validation_confidence,
                extracted_data={
                    'medications': [asdict(m) for m in medications]
                }
            )
            
            results['confidence_score'] = asdict(score)
            results['requires_review'] = score.requires_manual_review
            
            if score.requires_manual_review:
                results['review_queue_id'] = extraction_id
                print(f"[{extraction_id}] Low confidence ({score.overall_confidence:.2%}) - Added to manual review queue")
            else:
                print(f"[{extraction_id}] High confidence ({score.overall_confidence:.2%}) - Ready for use")

        except Exception as e:
            print(f"[{extraction_id}] Error: {str(e)}")
            results['error'] = str(e)
            results['status'] = 'failed'

        return results

    def get_review_queue(self) -> Dict:
        """Get current manual review queue."""
        pending = self.confidence_scorer.get_pending_reviews()
        
        return {
            'total_pending': len(pending),
            'items': [
                {
                    'extraction_id': item.extraction_id,
                    'confidence': item.overall_confidence,
                    'data': item.extracted_data
                }
                for item in pending
            ],
            'statistics': self.confidence_scorer.get_statistics()
        }

    def approve_extraction(self, extraction_id: str, notes: str = ""):
        """Approve an extraction from review queue."""
        self.confidence_scorer.update_review_status(
            extraction_id, ReviewStatus.APPROVED, notes
        )

    def reject_extraction(self, extraction_id: str, reason: str):
        """Reject an extraction from review queue."""
        self.confidence_scorer.update_review_status(
            extraction_id, ReviewStatus.REJECTED, reason
        )

    def process_batch(self, image_dir: str) -> Dict:
        """
        Process multiple prescription images in a directory.
        
        Args:
            image_dir: Directory containing prescription images
            
        Returns:
            Batch processing results
        """
        results = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'manual_review_required': 0,
            'extractions': []
        }

        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_path = os.path.join(image_dir, filename)
                extraction = self.process_prescription(image_path)
                
                results['total_processed'] += 1
                results['extractions'].append(extraction)
                
                if extraction.get('status') != 'failed':
                    results['successful'] += 1
                    if extraction.get('requires_review'):
                        results['manual_review_required'] += 1
                else:
                    results['failed'] += 1

        return results


def main():
    """Example usage of prescription digitizer."""
    # Initialize digitizer
    digitizer = PrescriptionDigitizer()
    
    # Process a single prescription
    test_image = "data/sample_prescription.jpg"
    if os.path.exists(test_image):
        print("Processing prescription image...")
        results = digitizer.process_prescription(test_image, save_intermediate=True)
        
        print("\n" + "="*50)
        print("PRESCRIPTION DIGITIZATION RESULTS")
        print("="*50)
        print(f"Extraction ID: {results['extraction_id']}")
        print(f"Status: {'Success' if results.get('status') != 'failed' else 'Failed'}")
        
        if results.get('ocr'):
            print(f"\nExtracted Text: {results['ocr'].get('full_text', '')[:100]}...")
            print(f"OCR Confidence: {results['ocr'].get('confidence', 0):.2%}")
        
        if results.get('ner'):
            print(f"\nMedications Found: {results['ner'].get('num_medications', 0)}")
            for med in results['ner'].get('medications', [])[:3]:
                print(f"  - {med['drug_name']}: {med['dosage']} {med['frequency']}")
        
        if results.get('confidence_score'):
            score = results['confidence_score']
            print(f"\nOverall Confidence: {score['overall_confidence']:.2%}")
            print(f"Requires Manual Review: {'Yes' if results.get('requires_review') else 'No'}")
    
    # Check manual review queue
    queue = digitizer.get_review_queue()
    print(f"\n\nManual Review Queue: {queue['total_pending']} items")


if __name__ == "__main__":
    main()
