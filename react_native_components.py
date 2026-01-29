"""
React Native Mobile App - Core Components
Complete medication verification app components
"""

# App.js - Main entry point
app_js = '''
import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Ionicons from 'react-native-vector-icons/Ionicons';

import HomeScreen from './src/screens/HomeScreen';
import PrescriptionScreen from './src/screens/PrescriptionScreen';
import PillScreen from './src/screens/PillScreen';
import IntakeScreen from './src/screens/IntakeScreen';
import ResultScreen from './src/screens/ResultScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  useEffect(() => {
    // Initialize app on startup
    initializeApp();
  }, []);

  const initializeApp = async () => {
    // Load TFLite models
    // Request permissions
    // Initialize storage
  };

  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: true,
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;
            
            if (route.name === 'Home') {
              iconName = focused ? 'home' : 'home-outline';
            } else if (route.name === 'Prescription') {
              iconName = focused ? 'document' : 'document-outline';
            } else if (route.name === 'Pill') {
              iconName = focused ? 'pulse' : 'pulse-outline';
            } else if (route.name === 'Intake') {
              iconName = focused ? 'videocam' : 'videocam-outline';
            } else if (route.name === 'Results') {
              iconName = focused ? 'checkmark-circle' : 'checkmark-circle-outline';
            }
            
            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#2196F3',
          tabBarInactiveTintColor: '#888888',
        })}
      >
        <Tab.Screen name="Home" component={HomeScreen} />
        <Tab.Screen name="Prescription" component={PrescriptionScreen} />
        <Tab.Screen name="Pill" component={PillScreen} />
        <Tab.Screen name="Intake" component={IntakeScreen} />
        <Tab.Screen name="Results" component={ResultScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
'''

# HomeScreen.js
home_screen = '''
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { checkAPIHealth } from '../services/api';

export default function HomeScreen({ navigation }) {
  const [apiStatus, setApiStatus] = useState('unknown');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const status = await checkAPIHealth();
      setApiStatus(status ? 'connected' : 'disconnected');
    } catch (error) {
      setApiStatus('error');
    }
    setLoading(false);
  };

  const workflows = [
    {
      title: 'Prescription Analysis',
      description: 'Capture and analyze prescription image',
      icon: '📋',
      screen: 'Prescription',
      color: '#FFE5B4',
    },
    {
      title: 'Pill Verification',
      description: 'Verify pill shape, color, and imprint',
      icon: '💊',
      screen: 'Pill',
      color: '#FFB6C1',
    },
    {
      title: 'Intake Verification',
      description: 'Record and verify medication intake',
      icon: '🎥',
      screen: 'Intake',
      color: '#87CEEB',
    },
    {
      title: 'View Results',
      description: 'Check verification results and reports',
      icon: '✅',
      screen: 'Results',
      color: '#90EE90',
    },
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Medication Verifier</Text>
        <Text style={styles.subtitle}>Zero-Error Verification System</Text>
      </View>

      {/* Status */}
      <View style={styles.statusCard}>
        {loading ? (
          <ActivityIndicator size="large" color="#2196F3" />
        ) : (
          <>
            <Text style={styles.statusLabel}>API Status:</Text>
            <Text style={[
              styles.statusValue,
              { color: apiStatus === 'connected' ? '#4CAF50' : '#F44336' }
            ]}>
              {apiStatus.toUpperCase()}
            </Text>
          </>
        )}
      </View>

      {/* Workflow Cards */}
      <View style={styles.workflowsContainer}>
        {workflows.map((workflow, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.workflowCard, { backgroundColor: workflow.color }]}
            onPress={() => navigation.navigate(workflow.screen)}
          >
            <Text style={styles.icon}>{workflow.icon}</Text>
            <Text style={styles.workflowTitle}>{workflow.title}</Text>
            <Text style={styles.workflowDescription}>{workflow.description}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Info */}
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>How It Works</Text>
        <Text style={styles.infoText}>
          1. Capture prescription image{\'\\n'}
          2. Verify pill identification{\'\\n'}
          3. Record medication intake{\'\\n'}
          4. Get comprehensive verification report
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 20,
    paddingTop: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  subtitle: {
    fontSize: 14,
    color: '#E3F2FD',
    marginTop: 5,
  },
  statusCard: {
    backgroundColor: '#FFFFFF',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    elevation: 3,
  },
  statusLabel: {
    fontSize: 14,
    color: '#666666',
  },
  statusValue: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 5,
  },
  workflowsContainer: {
    padding: 10,
  },
  workflowCard: {
    margin: 10,
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  icon: {
    fontSize: 40,
    marginBottom: 10,
  },
  workflowTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  workflowDescription: {
    fontSize: 12,
    color: '#666666',
    textAlign: 'center',
  },
  infoCard: {
    backgroundColor: '#FFFFFF',
    margin: 15,
    padding: 15,
    borderRadius: 10,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  infoText: {
    fontSize: 13,
    color: '#666666',
    lineHeight: 20,
  },
});
'''

# PrescriptionScreen.js
prescription_screen = '''
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import { analyzePrescription } from '../services/api';

export default function PrescriptionScreen() {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const takePhoto = () => {
    launchCamera({
      mediaType: 'photo',
      cameraType: 'back',
      quality: 1,
    }, (response) => {
      if (response.assets) {
        const asset = response.assets[0];
        setImage({
          uri: asset.uri,
          type: asset.type,
          name: asset.fileName,
        });
        analyzeImage(asset.uri);
      }
    });
  };

  const pickFromLibrary = () => {
    launchImageLibrary({
      mediaType: 'photo',
      quality: 1,
    }, (response) => {
      if (response.assets) {
        const asset = response.assets[0];
        setImage({
          uri: asset.uri,
          type: asset.type,
          name: asset.fileName,
        });
        analyzeImage(asset.uri);
      }
    });
  };

  const analyzeImage = async (uri) => {
    setLoading(true);
    try {
      const result = await analyzePrescription(uri);
      setResult(result);
    } catch (error) {
      Alert.alert('Error', 'Failed to analyze prescription');
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Prescription Analysis</Text>
      
      {image ? (
        <View style={styles.imageContainer}>
          <Image source={{ uri: image.uri }} style={styles.image} />
        </View>
      ) : (
        <View style={styles.placeholder}>
          <Text style={styles.placeholderText}>📋 No image selected</Text>
        </View>
      )}

      <View style={styles.buttonsContainer}>
        <TouchableOpacity style={styles.button} onPress={takePhoto}>
          <Text style={styles.buttonText}>📷 Take Photo</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.button} onPress={pickFromLibrary}>
          <Text style={styles.buttonText}>🖼️ Choose from Library</Text>
        </TouchableOpacity>
      </View>

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2196F3" />
          <Text style={styles.loadingText}>Analyzing prescription...</Text>
        </View>
      )}

      {result && !loading && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>Analysis Result</Text>
          <Text style={styles.resultText}>{JSON.stringify(result, null, 2)}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    padding: 15,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  imageContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    overflow: 'hidden',
    marginBottom: 20,
  },
  image: {
    width: '100%',
    height: 300,
    resizeMode: 'cover',
  },
  placeholder: {
    backgroundColor: '#E0E0E0',
    borderRadius: 10,
    height: 300,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  placeholderText: {
    fontSize: 18,
  },
  buttonsContainer: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 20,
  },
  button: {
    flex: 1,
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  loadingText: {
    marginTop: 10,
    color: '#666666',
  },
  resultContainer: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  resultText: {
    fontSize: 12,
    color: '#666666',
  },
});
'''

# Save files
with open('App.js', 'w') as f:
    f.write(app_js)

with open('src/screens/HomeScreen.js', 'w') as f:
    f.write(home_screen)

with open('src/screens/PrescriptionScreen.js', 'w') as f:
    f.write(prescription_screen)

print("React Native components created successfully")
