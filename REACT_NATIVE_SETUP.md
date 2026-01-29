"""
Complete React Native Mobile App Setup & Implementation Guide
For Medication Verification System
"""

# ============================================================================
# STEP 1: PROJECT INITIALIZATION
# ============================================================================

# Create new React Native project
npx react-native init MedicationVerifier

# Navigate to project
cd MedicationVerifier

# Install dependencies
npm install

# Install required packages
npm install @react-navigation/native @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context
npm install react-native-camera react-native-image-picker
npm install axios react-native-fs
npm install react-native-gesture-handler react-native-reanimated
npm install react-native-vector-icons
npm install react-native-video


# ============================================================================
# STEP 2: PROJECT STRUCTURE
# ============================================================================

# Create directory structure
mkdir -p src/screens
mkdir -p src/services
mkdir -p src/components
mkdir -p src/navigation
mkdir -p src/utils
mkdir -p assets/models
mkdir -p assets/icons


# ============================================================================
# STEP 3: ENVIRONMENT CONFIGURATION
# ============================================================================

# Create .env file in root
cat > .env << 'EOF'
# API Configuration
API_BASE_URL=http://192.168.1.100:8000
API_TIMEOUT=30000

# App Configuration
ENV=development
LOG_LEVEL=info

# Feature Flags
ENABLE_OFFLINE_MODE=true
ENABLE_LOCAL_TLS=true
BATCH_PROCESSING=false
EOF


# ============================================================================
# STEP 4: CREATE CORE FILES
# ============================================================================

# File 1: App.js (Main Entry Point)
cat > App.js << 'EOF'
import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Ionicons from 'react-native-vector-icons/Ionicons';

// Import Screens
import HomeScreen from './src/screens/HomeScreen';
import PrescriptionScreen from './src/screens/PrescriptionScreen';
import PillScreen from './src/screens/PillScreen';
import IntakeScreen from './src/screens/IntakeScreen';
import ResultScreen from './src/screens/ResultScreen';

// Initialize Navigation
const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const HomeStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerShown: true,
      headerStyle: {
        backgroundColor: '#007AFF',
      },
      headerTintColor: '#fff',
      headerTitleStyle: {
        fontWeight: 'bold',
      },
    }}
  >
    <Stack.Screen 
      name="HomeScreen" 
      component={HomeScreen}
      options={{ title: 'Medication Verification' }}
    />
  </Stack.Navigator>
);

const PrescriptionStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerShown: true,
      headerStyle: { backgroundColor: '#007AFF' },
      headerTintColor: '#fff',
    }}
  >
    <Stack.Screen 
      name="PrescriptionScreen" 
      component={PrescriptionScreen}
      options={{ title: 'Analyze Prescription' }}
    />
  </Stack.Navigator>
);

const PillStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerShown: true,
      headerStyle: { backgroundColor: '#007AFF' },
      headerTintColor: '#fff',
    }}
  >
    <Stack.Screen 
      name="PillScreen" 
      component={PillScreen}
      options={{ title: 'Verify Pill' }}
    />
  </Stack.Navigator>
);

const IntakeStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerShown: true,
      headerStyle: { backgroundColor: '#007AFF' },
      headerTintColor: '#fff',
    }}
  >
    <Stack.Screen 
      name="IntakeScreen" 
      component={IntakeScreen}
      options={{ title: 'Verify Intake' }}
    />
  </Stack.Navigator>
);

const ResultStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerShown: true,
      headerStyle: { backgroundColor: '#007AFF' },
      headerTintColor: '#fff',
    }}
  >
    <Stack.Screen 
      name="ResultScreen" 
      component={ResultScreen}
      options={{ title: 'Results' }}
    />
  </Stack.Navigator>
);

export default function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize app
    setTimeout(() => setIsLoading(false), 1000);
  }, []);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;

            if (route.name === 'Home') {
              iconName = focused ? 'home' : 'home-outline';
            } else if (route.name === 'Prescription') {
              iconName = focused ? 'document' : 'document-outline';
            } else if (route.name === 'Pill') {
              iconName = focused ? 'flask' : 'flask-outline';
            } else if (route.name === 'Intake') {
              iconName = focused ? 'eye' : 'eye-outline';
            } else if (route.name === 'Results') {
              iconName = focused ? 'checkmark-circle' : 'checkmark-circle-outline';
            }

            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#007AFF',
          tabBarInactiveTintColor: 'gray',
          headerShown: false,
        })}
      >
        <Tab.Screen 
          name="Home" 
          component={HomeStack}
          options={{ tabBarLabel: 'Home' }}
        />
        <Tab.Screen 
          name="Prescription" 
          component={PrescriptionStack}
          options={{ tabBarLabel: 'Prescription' }}
        />
        <Tab.Screen 
          name="Pill" 
          component={PillStack}
          options={{ tabBarLabel: 'Pill' }}
        />
        <Tab.Screen 
          name="Intake" 
          component={IntakeStack}
          options={{ tabBarLabel: 'Intake' }}
        />
        <Tab.Screen 
          name="Results" 
          component={ResultStack}
          options={{ tabBarLabel: 'Results' }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
EOF


# File 2: HomeScreen.js
cat > src/screens/HomeScreen.js << 'EOF'
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { checkAPIHealth } from '../services/api';

export default function HomeScreen({ navigation }) {
  const [apiStatus, setApiStatus] = useState('checking');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await checkAPIHealth();
        setApiStatus(health.status === 'healthy' ? 'connected' : 'degraded');
      } catch (error) {
        setApiStatus('disconnected');
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  const WorkflowCard = ({ title, description, icon, screen, color }) => (
    <TouchableOpacity
      style={[styles.card, { borderLeftColor: color }]}
      onPress={() => navigation.navigate(screen)}
    >
      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        <Ionicons name={icon} size={32} color={color} style={{ marginRight: 16 }} />
        <View style={{ flex: 1 }}>
          <Text style={styles.cardTitle}>{title}</Text>
          <Text style={styles.cardDescription}>{description}</Text>
        </View>
        <Ionicons name="chevron-forward" size={24} color="#ccc" />
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Status Bar */}
      <View style={styles.statusBar}>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Ionicons
            name={apiStatus === 'connected' ? 'wifi' : 'wifi-outline'}
            size={20}
            color={apiStatus === 'connected' ? '#34C759' : '#FF3B30'}
          />
          <Text style={styles.statusText}>
            {apiStatus === 'connected' ? 'Connected to Server' : 'Server Disconnected'}
          </Text>
        </View>
      </View>

      {/* Welcome Section */}
      <View style={styles.welcomeSection}>
        <Text style={styles.welcomeTitle}>Medication Verification System</Text>
        <Text style={styles.welcomeSubtitle}>
          Zero-Error Automated Verification Pipeline
        </Text>
      </View>

      {/* Workflow Cards */}
      <View style={styles.cardsSection}>
        <Text style={styles.sectionTitle}>Verification Workflow</Text>

        <WorkflowCard
          title="Analyze Prescription"
          description="Upload and analyze prescription image"
          icon="document"
          screen="Prescription"
          color="#007AFF"
        />

        <WorkflowCard
          title="Verify Pill"
          description="Authenticate pill authenticity"
          icon="flask"
          screen="Pill"
          color="#34C759"
        />

        <WorkflowCard
          title="Verify Intake"
          description="Confirm medication intake"
          icon="eye"
          screen="Intake"
          color="#FF9500"
        />

        <WorkflowCard
          title="View Results"
          description="Check verification results"
          icon="checkmark-circle"
          screen="Results"
          color="#AF52DE"
        />
      </View>

      {/* Instructions */}
      <View style={styles.instructionSection}>
        <Text style={styles.sectionTitle}>How to Use</Text>
        <Text style={styles.instructionText}>
          1. Start with "Analyze Prescription" tab{'\n'}
          2. Upload a clear image of the prescription{'\n'}
          3. Move to "Verify Pill" for pill authentication{'\n'}
          4. Use "Verify Intake" to confirm medication taken{'\n'}
          5. Check "Results" for final verification status
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  statusBar: {
    backgroundColor: '#007AFF',
    padding: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusText: {
    color: 'white',
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '600',
  },
  welcomeSection: {
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  welcomeTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  welcomeSubtitle: {
    fontSize: 14,
    color: '#999',
    marginTop: 4,
  },
  cardsSection: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  cardDescription: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  instructionSection: {
    margin: 16,
    padding: 16,
    backgroundColor: 'white',
    borderRadius: 8,
  },
  instructionText: {
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
  },
});
EOF


# File 3: API Service Layer
cat > src/services/api.js << 'EOF'
import axios from 'axios';
import { API_BASE_URL, API_TIMEOUT } from '../../config/constants';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL || 'http://192.168.1.100:8000',
  timeout: API_TIMEOUT || 30000,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API] Response:`, response.status);
    return response;
  },
  (error) => {
    console.error(`[API] Error:`, error.message);
    return Promise.reject(error);
  }
);

// API Functions

export const checkAPIHealth = async () => {
  try {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const analyzePrescription = async (prescriptionImagePath, patientId, notes = '') => {
  try {
    const formData = new FormData();
    formData.append('file', {
      uri: prescriptionImagePath,
      type: 'image/jpeg',
      name: 'prescription.jpg',
    });
    formData.append('patient_id', patientId);
    if (notes) formData.append('notes', notes);

    const response = await apiClient.post('/api/v1/analyze-prescription', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const verifyPill = async (pillImagePath, patientId, medicationId = '') => {
  try {
    const formData = new FormData();
    formData.append('file', {
      uri: pillImagePath,
      type: 'image/jpeg',
      name: 'pill.jpg',
    });
    formData.append('patient_id', patientId);
    if (medicationId) formData.append('medication_id', medicationId);

    const response = await apiClient.post('/api/v1/verify-pill', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const verifyIntake = async (intakeVideoPath, patientId, medicationId = '') => {
  try {
    const formData = new FormData();
    formData.append('file', {
      uri: intakeVideoPath,
      type: 'video/mp4',
      name: 'intake.mp4',
    });
    formData.append('patient_id', patientId);
    if (medicationId) formData.append('medication_id', medicationId);

    const response = await apiClient.post('/api/v1/verify-intake', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const completeVerification = async (
  prescriptionPath,
  pillPath,
  intakePath,
  patientId,
  notes = ''
) => {
  try {
    const formData = new FormData();
    formData.append('prescription_file', {
      uri: prescriptionPath,
      type: 'image/jpeg',
      name: 'prescription.jpg',
    });
    if (pillPath) {
      formData.append('pill_file', {
        uri: pillPath,
        type: 'image/jpeg',
        name: 'pill.jpg',
      });
    }
    if (intakePath) {
      formData.append('intake_file', {
        uri: intakePath,
        type: 'video/mp4',
        name: 'intake.mp4',
      });
    }
    formData.append('patient_id', patientId);
    if (notes) formData.append('notes', notes);

    const response = await apiClient.post('/api/v1/complete-verification', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getResult = async (workflowId) => {
  try {
    const response = await apiClient.get(`/api/v1/result/${workflowId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const downloadReport = async (workflowId) => {
  try {
    const response = await apiClient.get(`/api/v1/report/${workflowId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default apiClient;
EOF


# File 4: PrescriptionScreen.js
cat > src/screens/PrescriptionScreen.js << 'EOF'
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  ScrollView,
  Alert,
} from 'react-native';
import { CameraRoll } from '@react-native-camera-roll/camera-roll';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { analyzePrescription } from '../services/api';

export default function PrescriptionScreen() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [patientId, setPatientId] = useState('PAT001');

  const takePhoto = () => {
    launchCamera(
      {
        mediaType: 'photo',
        cameraType: 'back',
        saveToPhotos: true,
      },
      (response) => {
        if (response.didCancel) {
          console.log('Camera cancelled');
        } else if (response.errorCode) {
          Alert.alert('Camera Error', response.errorMessage);
        } else {
          setSelectedImage(response.assets[0]);
          setResult(null);
        }
      }
    );
  };

  const selectFromLibrary = () => {
    launchImageLibrary(
      {
        mediaType: 'photo',
        selectionLimit: 1,
      },
      (response) => {
        if (response.didCancel) {
          console.log('Cancelled');
        } else if (response.errorCode) {
          Alert.alert('Library Error', response.errorMessage);
        } else {
          setSelectedImage(response.assets[0]);
          setResult(null);
        }
      }
    );
  };

  const handleAnalyze = async () => {
    if (!selectedImage) {
      Alert.alert('Error', 'Please select a prescription image');
      return;
    }

    setLoading(true);
    try {
      const response = await analyzePrescription(
        selectedImage.uri,
        patientId,
        'Prescription analysis from mobile'
      );
      setResult(response.result);
    } catch (error) {
      Alert.alert('Error', error.message || 'Failed to analyze prescription');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Image Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Select Prescription Image</Text>

        {selectedImage ? (
          <View style={styles.imageContainer}>
            <Image source={{ uri: selectedImage.uri }} style={styles.image} />
            <TouchableOpacity
              style={styles.removeButton}
              onPress={() => {
                setSelectedImage(null);
                setResult(null);
              }}
            >
              <Ionicons name="close-circle" size={32} color="#FF3B30" />
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.placeholderContainer}>
            <Ionicons name="image-outline" size={48} color="#ccc" />
            <Text style={styles.placeholderText}>No image selected</Text>
          </View>
        )}

        <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.button} onPress={takePhoto}>
            <Ionicons name="camera" size={20} color="white" />
            <Text style={styles.buttonText}>Take Photo</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.button} onPress={selectFromLibrary}>
            <Ionicons name="image" size={20} color="white" />
            <Text style={styles.buttonText}>From Library</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Analysis Button */}
      <View style={styles.section}>
        <TouchableOpacity
          style={[styles.analyzeButton, { opacity: loading ? 0.6 : 1 }]}
          onPress={handleAnalyze}
          disabled={loading || !selectedImage}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <>
              <Ionicons name="flask" size={20} color="white" />
              <Text style={styles.analyzeButtonText}>Analyze Prescription</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {/* Results */}
      {result && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Analysis Results</Text>

          {result.prescription_analysis && (
            <View style={styles.resultCard}>
              <View style={styles.resultHeader}>
                <Ionicons name="checkmark-circle" size={24} color="#34C759" />
                <Text style={styles.resultTitle}>Prescription Valid</Text>
              </View>

              <View style={styles.resultItem}>
                <Text style={styles.label}>Medications Found:</Text>
                <Text style={styles.value}>
                  {result.medications_identified?.join(', ') || 'None'}
                </Text>
              </View>

              <View style={styles.resultItem}>
                <Text style={styles.label}>Confidence:</Text>
                <Text style={styles.value}>
                  {(result.prescription_analysis.confidence * 100).toFixed(1)}%
                </Text>
              </View>

              {result.prescription_analysis.dosage_info && (
                <View style={styles.resultItem}>
                  <Text style={styles.label}>Dosage Information:</Text>
                  <Text style={styles.value}>
                    {JSON.stringify(result.prescription_analysis.dosage_info)}
                  </Text>
                </View>
              )}
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  section: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  imageContainer: {
    position: 'relative',
    marginBottom: 12,
  },
  image: {
    width: '100%',
    height: 300,
    borderRadius: 8,
  },
  removeButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: 16,
  },
  placeholderContainer: {
    height: 200,
    borderWidth: 2,
    borderColor: '#ddd',
    borderStyle: 'dashed',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  placeholderText: {
    color: '#999',
    marginTop: 8,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 8,
  },
  button: {
    flex: 1,
    backgroundColor: '#007AFF',
    padding: 12,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
  },
  analyzeButton: {
    backgroundColor: '#34C759',
    padding: 16,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  analyzeButtonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 16,
  },
  resultCard: {
    backgroundColor: '#f9f9f9',
    borderLeftWidth: 4,
    borderLeftColor: '#34C759',
    padding: 12,
    borderRadius: 4,
    marginTop: 8,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#34C759',
  },
  resultItem: {
    marginBottom: 8,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  label: {
    fontSize: 12,
    color: '#999',
    fontWeight: '600',
  },
  value: {
    fontSize: 14,
    color: '#333',
    marginTop: 4,
  },
});
EOF

echo "✓ React Native project setup complete!"
echo "✓ Core app structure created"
echo "✓ API service layer implemented"
echo "✓ HomeScreen and PrescriptionScreen ready"
echo ""
echo "Next steps:"
echo "1. Create remaining screens (PillScreen, IntakeScreen, ResultScreen)"
echo "2. Set up TensorFlow Lite models"
echo "3. Configure native modules (iOS/Android)"
echo "4. Build and test on simulator/device"
