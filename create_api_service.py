"""
API Service Layer for React Native App
Handles all communication with backend
"""

api_service = '''
// src/services/api.js
import axios from 'axios';
import RNFS from 'react-native-fs';

// API configuration
const API_BASE_URL = process.env.API_URL || 'https://api.medicationverifier.com';
const API_TIMEOUT = 30000;

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token from secure storage if needed
    return config;
  },
  (error) => Promise.reject(error)
);

// Error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.message);
    return Promise.reject(error);
  }
);

// ============================================================================
// COMPONENT 1: PRESCRIPTION ANALYSIS
// ============================================================================

export const analyzePrescription = async (imagePath, patientId = 'unknown') => {
  try {
    const formData = new FormData();
    formData.append('file', {
      uri: imagePath,
      type: 'image/jpeg',
      name: 'prescription.jpg',
    });
    formData.append('patient_id', patientId);

    const response = await apiClient.post(
      '/api/v1/analyze-prescription',
      formData
    );

    return response.data;
  } catch (error) {
    throw new Error(`Prescription analysis failed: ${error.message}`);
  }
};

// ============================================================================
// COMPONENT 2: PILL VERIFICATION
// ============================================================================

export const verifyPill = async (
  imagePath,
  patientId = 'unknown',
  medicationId = 'unknown'
) => {
  try {
    const formData = new FormData();
    formData.append('file', {
      uri: imagePath,
      type: 'image/jpeg',
      name: 'pill.jpg',
    });
    formData.append('patient_id', patientId);
    formData.append('medication_id', medicationId);

    const response = await apiClient.post(
      '/api/v1/verify-pill',
      formData
    );

    return response.data;
  } catch (error) {
    throw new Error(`Pill verification failed: ${error.message}`);
  }
};

// ============================================================================
// COMPONENT 3: INTAKE VERIFICATION
// ============================================================================

export const verifyIntake = async (
  videoPath,
  patientId = 'unknown',
  medicationId = 'unknown'
) => {
  try {
    const formData = new FormData();
    formData.append('file', {
      uri: videoPath,
      type: 'video/mp4',
      name: 'intake.mp4',
    });
    formData.append('patient_id', patientId);
    formData.append('medication_id', medicationId);

    const response = await apiClient.post(
      '/api/v1/verify-intake',
      formData
    );

    return response.data;
  } catch (error) {
    throw new Error(`Intake verification failed: ${error.message}`);
  }
};

// ============================================================================
// COMPLETE WORKFLOW
// ============================================================================

export const completeVerification = async (
  prescriptionPath,
  pillPath,
  videoPath,
  patientId = 'unknown'
) => {
  try {
    const formData = new FormData();
    
    // Prescription is required
    formData.append('prescription_file', {
      uri: prescriptionPath,
      type: 'image/jpeg',
      name: 'prescription.jpg',
    });
    
    // Pill image is optional
    if (pillPath) {
      formData.append('pill_file', {
        uri: pillPath,
        type: 'image/jpeg',
        name: 'pill.jpg',
      });
    }
    
    // Intake video is optional
    if (videoPath) {
      formData.append('intake_file', {
        uri: videoPath,
        type: 'video/mp4',
        name: 'intake.mp4',
      });
    }
    
    formData.append('patient_id', patientId);

    const response = await apiClient.post(
      '/api/v1/complete-verification',
      formData
    );

    return response.data;
  } catch (error) {
    throw new Error(`Complete verification failed: ${error.message}`);
  }
};

// ============================================================================
// RETRIEVAL ENDPOINTS
// ============================================================================

export const getResult = async (workflowId) => {
  try {
    const response = await apiClient.get(`/api/v1/result/${workflowId}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to retrieve result: ${error.message}`);
  }
};

export const downloadReport = async (workflowId) => {
  try {
    const response = await apiClient.get(
      `/api/v1/report/${workflowId}`,
      { responseType: 'blob' }
    );
    return response.data;
  } catch (error) {
    throw new Error(`Failed to download report: ${error.message}`);
  }
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const checkAPIHealth = async () => {
  try {
    const response = await apiClient.get('/api/v1/health');
    return response.data.status === 'healthy' || response.data.status === 'degraded';
  } catch (error) {
    return false;
  }
};

export default {
  analyzePrescription,
  verifyPill,
  verifyIntake,
  completeVerification,
  getResult,
  downloadReport,
  checkAPIHealth,
};
'''

# Save API service
with open('src/services/api.js', 'w') as f:
    f.write(api_service)

print("API service layer created: src/services/api.js")
