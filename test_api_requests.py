"""
Comprehensive Test Script for Unified API Endpoints
Tests all 7 endpoints with sample data and various scenarios
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import numpy as np

# API Configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "v1"
API_BASE = f"{BASE_URL}/api/{API_VERSION}"

# Color codes for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def create_sample_image(width=640, height=480, text="Sample Prescription"):
    """Create a sample image for testing"""
    img = Image.new('RGB', (width, height), color='white')
    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def create_sample_video(duration_seconds=5, fps=30):
    """Create a sample video file for testing"""
    # For simplicity, we'll create a dummy video file
    # In real scenario, this would be actual video data
    video_data = b"DUMMY_VIDEO_DATA_" * 1000
    return BytesIO(video_data)

def test_health_endpoint():
    """Test 1: GET /health - Check system status"""
    print_header("Test 1: Health Check Endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        print_info(f"Request: GET {API_BASE}/health")
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False

def test_analyze_prescription():
    """Test 2: POST /analyze-prescription - Analyze prescription image"""
    print_header("Test 2: Analyze Prescription Endpoint")
    
    try:
        # Create sample prescription image
        image_file = create_sample_image(640, 480, "Sample Prescription")
        
        files = {
            'file': ('prescription.jpg', image_file, 'image/jpeg')
        }
        data = {
            'patient_id': 'PAT-001',
            'notes': 'Sample prescription for testing'
        }
        
        print_info(f"Request: POST {API_BASE}/analyze-prescription")
        print_info(f"Patient ID: {data['patient_id']}")
        print_info(f"File: prescription.jpg (sample image)")
        
        response = requests.post(f"{API_BASE}/analyze-prescription", files=files, data=data)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print_success("Prescription analysis request submitted")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2))
            return result.get('workflow_id'), True
        else:
            print_error(f"Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return None, False

def test_verify_pill(workflow_id=None):
    """Test 3: POST /verify-pill - Verify pill authenticity"""
    print_header("Test 3: Verify Pill Endpoint")
    
    try:
        # Create sample pill image
        image_file = create_sample_image(640, 480, "Sample Pill")
        
        files = {
            'file': ('pill.jpg', image_file, 'image/jpeg')
        }
        data = {
            'patient_id': 'PAT-001',
            'medication_id': 'MED-001'
        }
        
        print_info(f"Request: POST {API_BASE}/verify-pill")
        print_info(f"Patient ID: {data['patient_id']}")
        print_info(f"Medication ID: {data['medication_id']}")
        print_info(f"File: pill.jpg (sample image)")
        
        response = requests.post(f"{API_BASE}/verify-pill", files=files, data=data)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print_success("Pill verification request submitted")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2))
            return result.get('workflow_id'), True
        else:
            print_error(f"Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return None, False

def test_verify_intake(workflow_id=None):
    """Test 4: POST /verify-intake - Verify medication intake"""
    print_header("Test 4: Verify Intake Endpoint")
    
    try:
        # Create sample video file
        video_file = create_sample_video(5, 30)
        
        files = {
            'file': ('intake.mp4', video_file, 'video/mp4')
        }
        data = {
            'patient_id': 'PAT-001',
            'medication_id': 'MED-001'
        }
        
        print_info(f"Request: POST {API_BASE}/verify-intake")
        print_info(f"Patient ID: {data['patient_id']}")
        print_info(f"Medication ID: {data['medication_id']}")
        print_info(f"File: intake.mp4 (sample video)")
        
        response = requests.post(f"{API_BASE}/verify-intake", files=files, data=data)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print_success("Intake verification request submitted")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2))
            return result.get('workflow_id'), True
        else:
            print_error(f"Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return None, False

def test_complete_verification(workflow_id=None):
    """Test 5: POST /complete-verification - Complete entire workflow"""
    print_header("Test 5: Complete Verification Endpoint")
    
    try:
        # Create sample files
        prescription_file = create_sample_image(640, 480, "Prescription")
        pill_file = create_sample_image(640, 480, "Pill")
        intake_file = create_sample_video(5, 30)
        
        files = {
            'prescription': ('prescription.jpg', prescription_file, 'image/jpeg'),
            'pill': ('pill.jpg', pill_file, 'image/jpeg'),
            'intake': ('intake.mp4', intake_file, 'video/mp4')
        }
        data = {
            'patient_id': 'PAT-001',
            'medication_id': 'MED-001',
            'notes': 'Complete workflow test'
        }
        
        print_info(f"Request: POST {API_BASE}/complete-verification")
        print_info(f"Patient ID: {data['patient_id']}")
        print_info(f"Medication ID: {data['medication_id']}")
        print_info(f"Files: prescription.jpg, pill.jpg, intake.mp4")
        
        response = requests.post(f"{API_BASE}/complete-verification", files=files, data=data)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print_success("Complete verification workflow submitted")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2))
            return result.get('workflow_id'), True
        else:
            print_error(f"Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return None, False

def test_get_result(workflow_id):
    """Test 6: GET /result/{workflow_id} - Retrieve verification result"""
    print_header("Test 6: Get Result Endpoint")
    
    if not workflow_id:
        print_warning("No workflow_id provided, skipping test")
        return False
    
    try:
        print_info(f"Request: GET {API_BASE}/result/{workflow_id}")
        print_info(f"Workflow ID: {workflow_id}")
        
        response = requests.get(f"{API_BASE}/result/{workflow_id}")
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print_success("Result retrieved successfully")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2))
            return True
        elif response.status_code == 404:
            print_warning("Result not found (still processing or invalid ID)")
            return False
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def test_get_report(workflow_id):
    """Test 7: GET /report/{workflow_id} - Retrieve verification report"""
    print_header("Test 7: Get Report Endpoint")
    
    if not workflow_id:
        print_warning("No workflow_id provided, skipping test")
        return False
    
    try:
        print_info(f"Request: GET {API_BASE}/report/{workflow_id}")
        print_info(f"Workflow ID: {workflow_id}")
        
        response = requests.get(f"{API_BASE}/report/{workflow_id}")
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Check if it's a file or JSON
            if 'application/pdf' in response.headers.get('content-type', ''):
                print_success("PDF report retrieved successfully")
                # Save the PDF
                with open(f"report_{workflow_id}.pdf", "wb") as f:
                    f.write(response.content)
                print_info(f"Report saved to: report_{workflow_id}.pdf")
                return True
            else:
                result = response.json()
                print_success("Report retrieved successfully")
                print(f"\nResponse:")
                print(json.dumps(result, indent=2))
                return True
        elif response.status_code == 404:
            print_warning("Report not found (still processing or invalid ID)")
            return False
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print_header("ZERO-ERROR MEDICATION MANAGEMENT SYSTEM - API TEST SUITE")
    
    print_info(f"Target API: {BASE_URL}")
    print_info(f"Testing at: {datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Health check
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print_error("API server is not responding. Stopping tests.")
        return
    
    time.sleep(1)
    
    # Test 2: Analyze Prescription
    workflow_id_1, status_2 = test_analyze_prescription()
    time.sleep(1)
    
    # Test 3: Verify Pill
    workflow_id_2, status_3 = test_verify_pill(workflow_id_1)
    time.sleep(1)
    
    # Test 4: Verify Intake
    workflow_id_3, status_4 = test_verify_intake(workflow_id_2)
    time.sleep(1)
    
    # Test 5: Complete Verification
    workflow_id_4, status_5 = test_complete_verification()
    time.sleep(1)
    
    # Use workflow_id_4 from complete verification as it's the most complete
    workflow_id = workflow_id_4 or workflow_id_1 or workflow_id_2 or workflow_id_3
    
    # Test 6: Get Result
    status_6 = test_get_result(workflow_id)
    time.sleep(1)
    
    # Test 7: Get Report
    status_7 = test_get_report(workflow_id)
    
    # Summary
    print_header("TEST SUMMARY")
    
    tests = [
        ("Health Check", health_ok),
        ("Analyze Prescription", status_2),
        ("Verify Pill", status_3),
        ("Verify Intake", status_4),
        ("Complete Verification", status_5),
        ("Get Result", status_6),
        ("Get Report", status_7)
    ]
    
    passed = sum(1 for _, status in tests if status)
    total = len(tests)
    
    for test_name, status in tests:
        if status:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results: {Colors.GREEN}{passed}/{total}{Colors.END} tests passed")
    
    if passed == total:
        print_success("All tests passed!")
    else:
        print_warning(f"{total - passed} test(s) failed")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
