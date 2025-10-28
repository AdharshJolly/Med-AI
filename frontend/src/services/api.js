/**
 * API Service for MedAI-Pro with Clerk Authentication
 * Axios client with Clerk token integration and error handling
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add Clerk token
api.interceptors.request.use(
  async (config) => {
    try {
      // Get token from Clerk
      const token = await window.Clerk?.session?.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      if (status === 401) {
        // Unauthorized - redirect to home
        window.location.href = '/';
      } else if (status === 403) {
        console.error('Access forbidden:', data.message);
      } else if (status === 500) {
        console.error('Server error:', data.message);
      }
    } else if (error.request) {
      console.error('No response from server');
    } else {
      console.error('Request error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Profile API calls
export const createUserProfile = (profileData) => api.post('/api/profile/create', profileData);
export const getUserProfile = (userId) => api.get(`/api/profile/${userId}`);
export const updateUserProfile = (profileData) => api.put('/api/profile/update', profileData);
export const getMedicalSummary = (userId) => api.get(`/api/profile/medical-summary/${userId}`);

// Diagnosis API calls
export const submitDiagnosis = (diagnosisData) => api.post('/api/diagnosis/analyze', diagnosisData);
export const getDiagnosisHistory = (userId) => api.get(`/api/diagnosis/history/${userId}`);
export const getDiagnosisById = (diagnosisId) => api.get(`/api/diagnosis/${diagnosisId}`);
export const uploadDiagnosisFile = (formData) => api.post('/api/diagnosis/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});

// Chat API calls
export const sendChatMessage = (message, userId) => api.post('/api/chat/message', { message, user_id: userId });
export const getChatHistory = (userId) => api.get(`/api/chat/history/${userId}`);
export const analyzeSentiment = (message) => api.post('/api/chat/sentiment', { message });
export const translateMessage = (message, targetLanguage) => api.post('/api/chat/translate', { message, target_language: targetLanguage });
export const speechToText = (audioBlob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob);
  return api.post('/api/chat/speech-to-text', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
export const textToSpeech = (text, language = 'en') => api.post('/api/chat/text-to-speech', { text, language }, {
  responseType: 'blob',
});

// Maps API calls
export const getNearbyFacilities = (location, facilityType = 'hospital', radius = 5000) => {
  return api.post('/api/maps/nearby', { location, facility_type: facilityType, radius });
};
export const searchFacilities = (query, location) => api.post('/api/maps/search', { query, location });
export const getFacilityDetails = (placeId) => api.get(`/api/maps/facility/${placeId}`);

// AI Insights API calls
export const getDashboardInsights = (userId) => api.post('/api/insights/dashboard', { user_id: userId });
export const getDiagnosisInsights = (diagnosisData) => api.post('/api/insights/diagnosis', diagnosisData);
export const getHistoryInsights = (diagnosisId) => api.post(`/api/insights/history/${diagnosisId}`);
export const getHealthTrends = (userId) => api.get(`/api/insights/trends/${userId}`);

// Contact API calls
export const submitContactForm = (formData) => api.post('/api/contact/submit', formData);

// Health data API calls
export const getHealthStats = (userId) => api.get(`/api/health/stats/${userId}`);
export const getRecentDiagnoses = (userId, limit = 5) => api.get(`/api/health/recent/${userId}?limit=${limit}`);

export default api;

