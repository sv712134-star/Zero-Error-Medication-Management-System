"""FastAPI server for prescription digitization service."""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
from pathlib import Path

from prescription_digitizer import PrescriptionDigitizer

# Initialize FastAPI app
app = FastAPI(
    title="Zero-Error Medication Management System",
    description="AI-powered Prescription Digitizer API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize digitizer
digitizer = PrescriptionDigitizer()


# Pydantic models for request/response
class MedicationData(BaseModel):
    """Medication information."""
    drug_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    duration: Optional[str] = None


class PrescriptionResponse(BaseModel):
    """Response model for prescription processing."""
    extraction_id: str
    status: str
    extracted_text: Optional[str] = None
    medications: List[MedicationData] = []
    confidence_score: float
    requires_review: bool
    message: str


class ReviewQueueResponse(BaseModel):
    """Response model for review queue."""
    total_pending: int
    items: List[dict]
    statistics: dict


class ReviewUpdateRequest(BaseModel):
    """Request model for review updates."""
    status: str  # 'approved' or 'rejected'
    notes: str = ""


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "status": "operational",
        "service": "Zero-Error Medication Management System",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "ocr": "ready",
            "ner": "ready",
            "validator": "ready",
            "scoring": "ready"
        }
    }


@app.post("/process", tags=["Prescription Processing"])
async def process_prescription(file: UploadFile = File(...)) -> PrescriptionResponse:
    """
    Process a single prescription image.
    
    - **file**: Prescription image file (JPEG, PNG, BMP)
    
    Returns prescription extraction results with confidence score.
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            # Process prescription
            results = digitizer.process_prescription(tmp_path)
            
            # Extract medication data
            medications = []
            if results.get('ner'):
                for med in results['ner'].get('medications', []):
                    medications.append(MedicationData(
                        drug_name=med.get('drug_name', ''),
                        dosage=med.get('dosage', ''),
                        frequency=med.get('frequency', ''),
                        route=med.get('route', ''),
                        duration=med.get('duration', '')
                    ))
            
            # Extract confidence
            confidence = results.get('confidence_score', {}).get('overall_confidence', 0)
            
            return PrescriptionResponse(
                extraction_id=results.get('extraction_id', ''),
                status='success' if results.get('status') != 'failed' else 'failed',
                extracted_text=results.get('ocr', {}).get('full_text', '')[:500],
                medications=medications,
                confidence_score=confidence,
                requires_review=results.get('requires_review', False),
                message='Prescription processed successfully' if results.get('status') != 'failed' else results.get('error', '')
            )
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-batch", tags=["Prescription Processing"])
async def process_batch(files: List[UploadFile] = File(...)):
    """
    Process multiple prescription images in a batch.
    
    - **files**: List of prescription image files
    
    Returns aggregated results for all processed images.
    """
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Save all uploaded files
        for file in files:
            filepath = os.path.join(temp_dir, file.filename)
            contents = await file.read()
            with open(filepath, 'wb') as f:
                f.write(contents)
        
        # Process batch
        results = digitizer.process_batch(temp_dir)
        
        return {
            "status": "success",
            "summary": {
                "total_processed": results['total_processed'],
                "successful": results['successful'],
                "failed": results['failed'],
                "manual_review_required": results['manual_review_required']
            },
            "extractions": results['extractions']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary directory
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@app.get("/review-queue", tags=["Manual Review"])
async def get_review_queue() -> ReviewQueueResponse:
    """
    Get pending items in manual review queue.
    
    Returns all extractions that require manual verification.
    """
    queue = digitizer.get_review_queue()
    
    return ReviewQueueResponse(
        total_pending=queue['total_pending'],
        items=queue['items'],
        statistics=queue['statistics']
    )


@app.post("/review/{extraction_id}", tags=["Manual Review"])
async def update_review(extraction_id: str, request: ReviewUpdateRequest):
    """
    Update review status for an extraction.
    
    - **extraction_id**: ID of extraction to review
    - **status**: 'approved' or 'rejected'
    - **notes**: Review notes or reason for rejection
    """
    try:
        if request.status.lower() == 'approved':
            digitizer.approve_extraction(extraction_id, request.notes)
        elif request.status.lower() == 'rejected':
            digitizer.reject_extraction(extraction_id, request.notes)
        else:
            raise ValueError(f"Invalid status: {request.status}")
        
        return {
            "status": "success",
            "message": f"Extraction {extraction_id} marked as {request.status}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/extraction/{extraction_id}", tags=["Prescription Processing"])
async def get_extraction(extraction_id: str):
    """
    Get details of a specific extraction.
    
    - **extraction_id**: ID of extraction to retrieve
    """
    # In a real implementation, this would query a database
    return {
        "status": "not_implemented",
        "message": "Database storage required for extraction history"
    }


@app.get("/stats", tags=["Analytics"])
async def get_statistics():
    """Get system statistics and performance metrics."""
    queue = digitizer.get_review_queue()
    
    return {
        "review_queue": queue['statistics'],
        "system_status": "operational",
        "api_version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )
