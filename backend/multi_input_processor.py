"""
Multi-Input Processor for MedAI-Pro
Supports: Audio, Image, Text, Medical Readings, Medical Documents, IOT Signals
Integrates with User Profile: Age, Blood Group, Gender, Height, Weight, Medical History
"""

import torch
import numpy as np
from PIL import Image
import io
import base64
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import librosa
import soundfile as sf
import PyPDF2
import docx
from transformers import AutoTokenizer, AutoModel
import cv2
from sklearn.preprocessing import StandardScaler
import pickle

class MultiInputProcessor:
    """Process multiple input types for medical diagnosis"""
    
    def __init__(self, models_dir: str = "backend/models/weights"):
        self.models_dir = Path(models_dir)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load tokenizer for text processing
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        
        # Scalers for different input types
        self.scalers = {}
        self._load_scalers()
    
    def _load_scalers(self):
        """Load pre-trained scalers"""
        scaler_files = self.models_dir.glob("*_scaler.pkl")
        for scaler_file in scaler_files:
            organ = scaler_file.stem.replace("_scaler", "")
            with open(scaler_file, 'rb') as f:
                self.scalers[organ] = pickle.load(f)
    
    # ========================================================================
    # IMAGE PROCESSING
    # ========================================================================
    
    def process_image(self, image_data: Union[str, bytes, Image.Image]) -> torch.Tensor:
        """
        Process medical images (X-rays, dermoscopy, etc.)
        Supports: JPG, PNG, DICOM
        """
        # Convert to PIL Image
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                # Base64 encoded
                image_data = base64.b64decode(image_data.split(',')[1])
                image = Image.open(io.BytesIO(image_data))
            else:
                # File path
                image = Image.open(image_data)
        elif isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        else:
            image = image_data
        
        # Convert to RGB
        image = image.convert('RGB')
        
        # Resize to 224x224 (standard for medical imaging)
        image = image.resize((224, 224))
        
        # Convert to tensor
        image_array = np.array(image) / 255.0
        image_tensor = torch.FloatTensor(image_array).permute(2, 0, 1)
        
        # Normalize (ImageNet stats)
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        image_tensor = (image_tensor - mean) / std
        
        return image_tensor.unsqueeze(0).to(self.device)
    
    # ========================================================================
    # AUDIO PROCESSING
    # ========================================================================
    
    def process_audio(self, audio_data: Union[str, bytes, np.ndarray]) -> torch.Tensor:
        """
        Process medical audio (heart sounds, lung sounds, voice)
        Supports: WAV, MP3, OGG
        """
        # Load audio
        if isinstance(audio_data, str):
            audio, sr = librosa.load(audio_data, sr=22050)
        elif isinstance(audio_data, bytes):
            audio, sr = sf.read(io.BytesIO(audio_data))
        else:
            audio = audio_data
            sr = 22050
        
        # Extract features
        # 1. Mel-frequency cepstral coefficients (MFCCs)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
        
        # 2. Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        
        # 3. Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio)
        
        # Combine features
        features = np.vstack([mfccs, spectral_centroid, spectral_rolloff, zcr])
        
        # Pad or truncate to fixed length (500 frames)
        if features.shape[1] < 500:
            features = np.pad(features, ((0, 0), (0, 500 - features.shape[1])), mode='constant')
        else:
            features = features[:, :500]
        
        # Convert to tensor
        features_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
        
        return features_tensor
    
    # ========================================================================
    # TEXT PROCESSING
    # ========================================================================
    
    def process_text(self, text: str) -> torch.Tensor:
        """
        Process medical text (symptoms, medical history, reports)
        """
        # Tokenize
        encoded = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=512,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoded['input_ids'].to(self.device),
            'attention_mask': encoded['attention_mask'].to(self.device)
        }
    
    # ========================================================================
    # MEDICAL READINGS PROCESSING (ECG, EEG, etc.)
    # ========================================================================
    
    def process_medical_readings(self, readings: Union[Dict, np.ndarray, List]) -> torch.Tensor:
        """
        Process medical device readings (ECG, EEG, blood pressure, etc.)
        Supports: Time-series data, multi-channel signals
        """
        # Convert to numpy array
        if isinstance(readings, dict):
            # ECG format: {'lead_I': [...], 'lead_II': [...], ...}
            if 'lead_I' in readings or 'lead_1' in readings:
                # 12-lead ECG
                leads = []
                for i in range(1, 13):
                    lead_name = f'lead_{i}' if f'lead_{i}' in readings else f'lead_{["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"][i-1]}'
                    if lead_name in readings:
                        leads.append(readings[lead_name])
                signal = np.array(leads)
            else:
                # Generic readings
                signal = np.array(list(readings.values()))
        elif isinstance(readings, list):
            signal = np.array(readings)
        else:
            signal = readings
        
        # Ensure 2D (channels x samples)
        if signal.ndim == 1:
            signal = signal.reshape(1, -1)
        
        # Pad or truncate to fixed length (5000 samples)
        if signal.shape[1] < 5000:
            signal = np.pad(signal, ((0, 0), (0, 5000 - signal.shape[1])), mode='constant')
        else:
            signal = signal[:, :5000]
        
        # Normalize
        signal = (signal - signal.mean()) / (signal.std() + 1e-8)
        
        # Convert to tensor
        signal_tensor = torch.FloatTensor(signal).unsqueeze(0).to(self.device)
        
        return signal_tensor
    
    # ========================================================================
    # MEDICAL DOCUMENTS PROCESSING (PDF, DOCX)
    # ========================================================================
    
    def process_medical_document(self, document_data: Union[str, bytes]) -> str:
        """
        Extract text from medical documents (PDF, DOCX)
        """
        text = ""
        
        if isinstance(document_data, str):
            # File path
            if document_data.endswith('.pdf'):
                with open(document_data, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
            elif document_data.endswith('.docx'):
                doc = docx.Document(document_data)
                text = '\n'.join([para.text for para in doc.paragraphs])
        else:
            # Bytes
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(document_data))
                for page in pdf_reader.pages:
                    text += page.extract_text()
            except:
                try:
                    doc = docx.Document(io.BytesIO(document_data))
                    text = '\n'.join([para.text for para in doc.paragraphs])
                except:
                    text = document_data.decode('utf-8', errors='ignore')
        
        return text
    
    # ========================================================================
    # IOT SIGNALS PROCESSING
    # ========================================================================
    
    def process_iot_signals(self, signals: Dict[str, Any]) -> torch.Tensor:
        """
        Process IoT medical device signals
        Supports: Wearables, sensors, continuous monitoring devices
        """
        features = []
        
        # Extract features from different sensors
        if 'heart_rate' in signals:
            features.extend(self._extract_time_series_features(signals['heart_rate']))
        
        if 'blood_pressure' in signals:
            if isinstance(signals['blood_pressure'], dict):
                features.append(signals['blood_pressure'].get('systolic', 0))
                features.append(signals['blood_pressure'].get('diastolic', 0))
            else:
                features.append(signals['blood_pressure'])
        
        if 'temperature' in signals:
            features.append(signals['temperature'])
        
        if 'oxygen_saturation' in signals:
            features.append(signals['oxygen_saturation'])
        
        if 'steps' in signals:
            features.append(signals['steps'])
        
        if 'sleep_hours' in signals:
            features.append(signals['sleep_hours'])
        
        # Convert to tensor
        features_array = np.array(features, dtype=np.float32)
        features_tensor = torch.FloatTensor(features_array).unsqueeze(0).to(self.device)
        
        return features_tensor
    
    def _extract_time_series_features(self, time_series: List[float]) -> List[float]:
        """Extract statistical features from time series"""
        ts = np.array(time_series)
        return [
            np.mean(ts),
            np.std(ts),
            np.min(ts),
            np.max(ts),
            np.median(ts)
        ]
    
    # ========================================================================
    # USER PROFILE INTEGRATION
    # ========================================================================
    
    def process_user_profile(self, profile: Dict[str, Any]) -> torch.Tensor:
        """
        Process user profile data
        Fields: age, blood_group, gender, height, weight, medical_history, current_conditions
        """
        features = []
        
        # Age
        features.append(profile.get('age', 0))
        
        # Gender (one-hot encoding)
        gender = profile.get('gender', 'unknown').lower()
        features.append(1 if gender == 'male' else 0)
        features.append(1 if gender == 'female' else 0)
        features.append(1 if gender == 'other' else 0)
        
        # Blood group (one-hot encoding)
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        blood_group = profile.get('blood_group', 'unknown')
        for bg in blood_groups:
            features.append(1 if blood_group == bg else 0)
        
        # Height (cm)
        features.append(profile.get('height', 0))
        
        # Weight (kg)
        features.append(profile.get('weight', 0))
        
        # BMI (calculated)
        height_m = profile.get('height', 0) / 100
        weight_kg = profile.get('weight', 0)
        bmi = weight_kg / (height_m ** 2) if height_m > 0 else 0
        features.append(bmi)
        
        # Medical history (count of conditions)
        medical_history = profile.get('medical_history', [])
        features.append(len(medical_history) if isinstance(medical_history, list) else 0)
        
        # Current conditions (count)
        current_conditions = profile.get('current_conditions', [])
        features.append(len(current_conditions) if isinstance(current_conditions, list) else 0)
        
        # Convert to tensor
        features_array = np.array(features, dtype=np.float32)
        features_tensor = torch.FloatTensor(features_array).unsqueeze(0).to(self.device)
        
        return features_tensor
    
    # ========================================================================
    # COMBINED PROCESSING
    # ========================================================================
    
    def process_combined_input(self, 
                               image: Optional[Any] = None,
                               audio: Optional[Any] = None,
                               text: Optional[str] = None,
                               medical_readings: Optional[Any] = None,
                               document: Optional[Any] = None,
                               iot_signals: Optional[Dict] = None,
                               user_profile: Optional[Dict] = None) -> Dict[str, torch.Tensor]:
        """
        Process multiple input types simultaneously
        Returns dictionary of processed tensors
        """
        processed = {}
        
        if image is not None:
            processed['image'] = self.process_image(image)
        
        if audio is not None:
            processed['audio'] = self.process_audio(audio)
        
        if text is not None:
            processed['text'] = self.process_text(text)
        
        if medical_readings is not None:
            processed['medical_readings'] = self.process_medical_readings(medical_readings)
        
        if document is not None:
            doc_text = self.process_medical_document(document)
            processed['document_text'] = self.process_text(doc_text)
        
        if iot_signals is not None:
            processed['iot_signals'] = self.process_iot_signals(iot_signals)
        
        if user_profile is not None:
            processed['user_profile'] = self.process_user_profile(user_profile)
        
        return processed

