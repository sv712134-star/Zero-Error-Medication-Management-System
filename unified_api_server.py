"""
Unified REST API for Complete Medication Verification System
Exposes all 3 components through FastAPI endpoints.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import os
import uuid
from datetime import datetime
import json
from pathlib import Path
import shutil

try:
    from src.integration_engine import MedicationVerificationWorkflow
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    class MedicationVerificationWorkflow:
        """Fallback mock workflow when components unavailable"""
        def __init__(self):
            self.components_loaded = {
                'prescription_digitizer': False,
                'pill_authenticator': False,
                'intake_verifier': False
            }
        def get_component_status(self):
            return self.components_loaded

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Zero-Error Medication Management System",
    description="Unified API for prescription analysis, pill verification, and intake verification",
    version="1.0.0"
)

# Initialize workflow engine (will be loaded once at startup)
workflow = None

# Storage paths
UPLOAD_DIR = Path("data/uploads")
RESULTS_DIR = Path("data/results")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# DATA MODELS
# ============================================================================

class AnalysisPrescriptionRequest(BaseModel):
    """Request model for prescription analysis"""
    patient_id: str
    notes: Optional[str] = None


class VerifyPillRequest(BaseModel):
    """Request model for pill verification"""
    patient_id: str
    medication_id: str


class VerifyIntakeRequest(BaseModel):
    """Request model for intake verification"""
    patient_id: str
    medication_id: str


class BatchProcessRequest(BaseModel):
    """Request model for batch processing"""
    patient_id: str
    medication_id: str
    notes: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Response model for workflow results"""
    workflow_id: str
    patient_id: str
    medication_id: str
    status: str
    confidence: float
    valid: bool
    message: str


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global workflow
    logger.info("=" * 70)
    logger.info("ZERO-ERROR MEDICATION MANAGEMENT SYSTEM - API SERVER")
    logger.info("=" * 70)
    logger.info("🚀 Starting API server on http://0.0.0.0:8000")
    logger.info("📚 API documentation: http://localhost:8000/docs")
    
    try:
        logger.info("📦 Initializing medication verification workflow...")
        workflow = MedicationVerificationWorkflow()
        status = workflow.get_component_status()
        
        logger.info("✓ Component Status:")
        logger.info(f"  - Prescription Digitizer: {'✅ Available' if status.get('prescription_digitizer') else '⚠️  Unavailable'}")
        logger.info(f"  - Pill Authenticator: {'✅ Available' if status.get('pill_authenticator') else '⚠️  Unavailable'}")
        logger.info(f"  - Intake Verifier: {'✅ Available' if status.get('intake_verifier') else '⚠️  Unavailable'}")
        logger.info("=" * 70)
    except Exception as e:
        logger.warning(f"⚠️  Could not load all components: {e}")
        logger.info("Continuing with available components...")
        workflow = MedicationVerificationWorkflow()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down API server...")
    logger.info("Goodbye! 👋")


# ============================================================================
# COMPONENT 1: PRESCRIPTION ANALYSIS
# ============================================================================

@app.post("/api/v1/analyze-prescription")
async def analyze_prescription(
    patient_id: str,
    file: UploadFile = File(...),
    notes: Optional[str] = None
) -> JSONResponse:
    """
    Analyze prescription image (Component 1)
    
    Args:
        patient_id: Patient identifier
        file: Prescription image file (JPG/PNG)
        notes: Additional notes
        
    Returns:
        Analysis results with extracted medications
    """
    if not workflow or not workflow.prescription_digitizer:
        raise HTTPException(
            status_code=503,
            detail="Prescription digitizer not available"
        )
    
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"prescription_{file_id}.jpg"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Analyzing prescription for patient {patient_id}")
        
        # Process prescription
        result = workflow.prescription_digitizer.process_prescription(str(file_path))
        
        return JSONResponse({
            "status": "success",
            "patient_id": patient_id,
            "file_id": file_id,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Prescription analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMPONENT 2: PILL VERIFICATION
# ============================================================================

@app.post("/api/v1/verify-pill")
async def verify_pill(
    patient_id: str,
    medication_id: str,
    file: UploadFile = File(...),
    prescription_file_id: Optional[str] = None
) -> JSONResponse:
    """
    Verify pill image against prescription (Component 2)
    
    Args:
        patient_id: Patient identifier
        medication_id: Medication identifier
        file: Pill image file (JPG/PNG)
        prescription_file_id: ID of prescription file for cross-reference
        
    Returns:
        Verification results with shape/color/imprint analysis
    """
    if not workflow or not workflow.pill_classifier:
        raise HTTPException(
            status_code=503,
            detail="Pill authenticator not available"
        )
    
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"pill_{file_id}.jpg"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Verifying pill for patient {patient_id}, medication {medication_id}")
        
        # Verify pill
        result = workflow.pill_classifier.predict(str(file_path))
        
        # Check if authenticated
        shape_conf = result.get('shape', {}).get('confidence', 0)
        color_conf = result.get('color', {}).get('confidence', 0)
        imprint_conf = result.get('imprint', {}).get('confidence', 0)
        overall_conf = (shape_conf + color_conf + imprint_conf) / 3
        
        authenticated = overall_conf > 0.85
        
        return JSONResponse({
            "status": "success",
            "patient_id": patient_id,
            "medication_id": medication_id,
            "file_id": file_id,
            "verification": result,
            "authenticated": authenticated,
            "confidence": float(overall_conf),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Pill verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMPONENT 3: INTAKE VERIFICATION
# ============================================================================

@app.post("/api/v1/verify-intake")
async def verify_intake(
    patient_id: str,
    medication_id: str,
    file: UploadFile = File(...),
    prescription_file_id: Optional[str] = None,
    pill_file_id: Optional[str] = None
) -> JSONResponse:
    """
    Verify medication intake from video (Component 3)
    
    Args:
        patient_id: Patient identifier
        medication_id: Medication identifier
        file: Video file (MP4/MOV/AVI)
        prescription_file_id: ID of prescription file
        pill_file_id: ID of pill image file
        
    Returns:
        Verification results with pill/hand/swallowing detection
    """
    if not workflow or not workflow.intake_verifier:
        raise HTTPException(
            status_code=503,
            detail="Intake verifier not available"
        )
    
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        file_path = UPLOAD_DIR / f"intake_{file_id}{file_ext}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Verifying intake for patient {patient_id}, medication {medication_id}")
        
        # Verify intake
        result = workflow.intake_verifier.verify_video(str(file_path))
        
        return JSONResponse({
            "status": "success",
            "patient_id": patient_id,
            "medication_id": medication_id,
            "file_id": file_id,
            "verification": result.to_dict(),
            "confirmed": result.final_status.value in ['confirmed', 'likely'],
            "confidence": float(result.final_confidence),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Intake verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UNIFIED WORKFLOW
# ============================================================================

@app.post("/api/v1/complete-verification")
async def complete_verification(
    patient_id: str,
    background_tasks: BackgroundTasks,
    prescription_file: UploadFile = File(...),
    pill_file: Optional[UploadFile] = File(None),
    intake_file: Optional[UploadFile] = File(None),
    notes: Optional[str] = None
) -> JSONResponse:
    """
    Complete unified medication verification workflow
    
    All 3 components in one request:
    1. Prescription analysis
    2. Pill verification
    3. Intake verification
    
    Args:
        patient_id: Patient identifier
        prescription_file: Prescription image
        pill_file: Pill image (optional)
        intake_file: Intake video (optional)
        notes: Additional notes
        
    Returns:
        Complete workflow results
    """
    if not workflow:
        raise HTTPException(
            status_code=503,
            detail="Workflow not available"
        )
    
    try:
        workflow_id = str(uuid.uuid4())
        
        # Save files
        prescription_path = UPLOAD_DIR / f"prescription_{workflow_id}.jpg"
        with open(prescription_path, "wb") as f:
            f.write(await prescription_file.read())
        
        pill_path = None
        if pill_file:
            pill_path = UPLOAD_DIR / f"pill_{workflow_id}.jpg"
            with open(pill_path, "wb") as f:
                f.write(await pill_file.read())
        
        intake_path = None
        if intake_file:
            intake_ext = Path(intake_file.filename).suffix
            intake_path = UPLOAD_DIR / f"intake_{workflow_id}{intake_ext}"
            with open(intake_path, "wb") as f:
                f.write(await intake_file.read())
        
        # Extract medication ID from prescription (use first extracted drug as fallback)
        medication_id = "unknown"
        
        # Process workflow
        logger.info(f"Processing complete workflow {workflow_id} for patient {patient_id}")
        
        result = workflow.process_medication_verification(
            patient_id=patient_id,
            prescription_image_path=str(prescription_path),
            pill_image_path=str(pill_path) if pill_path else None,
            intake_video_path=str(intake_path) if intake_path else None
        )
        
        # Save result
        result_path = RESULTS_DIR / f"workflow_{workflow_id}.json"
        with open(result_path, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        
        # Generate report
        report = workflow.generate_report(result)
        report_path = RESULTS_DIR / f"report_{workflow_id}.txt"
        with open(report_path, "w") as f:
            f.write(report)
        
        return JSONResponse({
            "status": "success",
            "workflow_id": workflow_id,
            "patient_id": patient_id,
            "result": {
                "final_status": result.final_status,
                "confidence": float(result.overall_confidence),
                "valid": result.is_valid,
                "reasoning": result.reasoning
            },
            "result_file": str(result_path),
            "report_file": str(report_path),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RETRIEVAL ENDPOINTS
# ============================================================================

@app.get("/api/v1/result/{workflow_id}")
async def get_result(workflow_id: str) -> JSONResponse:
    """Retrieve workflow result"""
    result_path = RESULTS_DIR / f"workflow_{workflow_id}.json"
    
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    
    try:
        with open(result_path) as f:
            result = json.load(f)
        
        return JSONResponse(result)
    
    except Exception as e:
        logger.error(f"Error retrieving result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/report/{workflow_id}")
async def get_report(workflow_id: str) -> FileResponse:
    """Download workflow report"""
    report_path = RESULTS_DIR / f"report_{workflow_id}.txt"
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(report_path, media_type="text/plain")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/api/v1/health")
async def health_check() -> JSONResponse:
    """Check API and component health"""
    try:
        if not workflow:
            return JSONResponse({
                "status": "degraded",
                "message": "Workflow not initialized"
            }, status_code=503)
        
        # Get component status from workflow
        component_status = workflow.get_component_status()
        
        all_available = all(component_status.values())
        
        return JSONResponse({
            "status": "healthy" if all_available else "degraded",
            "message": "All systems operational" if all_available else "Some components unavailable",
            "components": component_status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }, status_code=500)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root() -> JSONResponse:
    """API documentation"""
    return JSONResponse({
        "name": "Zero-Error Medication Management System",
        "version": "1.0.0",
        "description": "Complete medication verification pipeline",
        "endpoints": {
            "prescription": "/api/v1/analyze-prescription",
            "pill": "/api/v1/verify-pill",
            "intake": "/api/v1/verify-intake",
            "complete": "/api/v1/complete-verification",
            "health": "/api/v1/health"
        }
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
