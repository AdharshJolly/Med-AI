"""
Multi-Modal Medical Data Preprocessor for MedAI-Pro
Handles preprocessing for ECG signals, medical images, text, and tabular data
"""

import numpy as np
import pandas as pd
import cv2
from PIL import Image
import torch
import torchvision.transforms as transforms
from scipy import signal
from scipy.ndimage import zoom
import wfdb
from typing import Tuple, Dict, List, Union, Optional
import albumentations as A
from albumentations.pytorch import ToTensorV2
import librosa
from loguru import logger


class ECGPreprocessor:
    """Preprocess ECG signals for cardiology model"""
    
    def __init__(self, target_length: int = 5000, sampling_rate: int = 500):
        self.target_length = target_length
        self.sampling_rate = sampling_rate
    
    def load_ecg(self, file_path: str) -> np.ndarray:
        """Load ECG from WFDB format"""
        try:
            record = wfdb.rdrecord(file_path)
            ecg_signal = record.p_signal
            return ecg_signal
        except Exception as e:
            logger.error(f"Error loading ECG: {e}")
            return None
    
    def denoise(self, ecg_signal: np.ndarray) -> np.ndarray:
        """Remove noise from ECG signal"""
        # Bandpass filter (0.5-40 Hz)
        nyquist = self.sampling_rate / 2
        low = 0.5 / nyquist
        high = 40 / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, ecg_signal, axis=0)
        return filtered
    
    def normalize(self, ecg_signal: np.ndarray) -> np.ndarray:
        """Normalize ECG signal"""
        mean = np.mean(ecg_signal, axis=0)
        std = np.std(ecg_signal, axis=0)
        normalized = (ecg_signal - mean) / (std + 1e-8)
        return normalized
    
    def resample(self, ecg_signal: np.ndarray) -> np.ndarray:
        """Resample ECG to target length"""
        current_length = ecg_signal.shape[0]
        if current_length != self.target_length:
            zoom_factor = self.target_length / current_length
            resampled = zoom(ecg_signal, (zoom_factor, 1), order=1)
            return resampled
        return ecg_signal
    
    def preprocess(self, ecg_data: Union[str, np.ndarray]) -> torch.Tensor:
        """Complete ECG preprocessing pipeline"""
        # Load if file path
        if isinstance(ecg_data, str):
            ecg_signal = self.load_ecg(ecg_data)
        else:
            ecg_signal = ecg_data
        
        if ecg_signal is None:
            return None
        
        # Preprocessing steps
        ecg_signal = self.denoise(ecg_signal)
        ecg_signal = self.normalize(ecg_signal)
        ecg_signal = self.resample(ecg_signal)
        
        # Convert to tensor
        ecg_tensor = torch.FloatTensor(ecg_signal).permute(1, 0)  # (channels, length)
        return ecg_tensor


class ImagePreprocessor:
    """Preprocess medical images for dermatology, respiratory, and orthopedics models"""
    
    def __init__(self, image_size: Tuple[int, int] = (224, 224), augment: bool = False):
        self.image_size = image_size
        self.augment = augment
        
        # Training augmentations
        self.train_transform = A.Compose([
            A.Resize(image_size[0], image_size[1]),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.3),
            A.Rotate(limit=20, p=0.5),
            A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
            A.Blur(blur_limit=3, p=0.2),
            A.CLAHE(clip_limit=2.0, p=0.3),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        # Validation/inference transforms
        self.val_transform = A.Compose([
            A.Resize(image_size[0], image_size[1]),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image from file"""
        try:
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Apply CLAHE for contrast enhancement"""
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        return enhanced
    
    def remove_artifacts(self, image: np.ndarray) -> np.ndarray:
        """Remove common artifacts from medical images"""
        # Bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(image, 9, 75, 75)
        return filtered
    
    def preprocess(self, image_data: Union[str, np.ndarray], training: bool = False) -> torch.Tensor:
        """Complete image preprocessing pipeline"""
        # Load if file path
        if isinstance(image_data, str):
            image = self.load_image(image_data)
        else:
            image = image_data
        
        if image is None:
            return None
        
        # Apply enhancements
        image = self.enhance_contrast(image)
        image = self.remove_artifacts(image)
        
        # Apply transforms
        if training and self.augment:
            transformed = self.train_transform(image=image)
        else:
            transformed = self.val_transform(image=image)
        
        return transformed['image']


class TextPreprocessor:
    """Preprocess medical text and symptoms for NLP models"""
    
    def __init__(self, max_length: int = 512):
        self.max_length = max_length
        self.medical_stopwords = {
            'patient', 'reports', 'complains', 'states', 'denies', 'admits'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize medical text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep medical notation
        text = ''.join(char if char.isalnum() or char.isspace() or char in '.,;:-/' else ' ' for char in text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_symptoms(self, text: str) -> List[str]:
        """Extract symptom keywords from text"""
        # Common medical symptom keywords
        symptom_keywords = [
            'pain', 'fever', 'cough', 'fatigue', 'nausea', 'vomiting', 'diarrhea',
            'headache', 'dizziness', 'shortness of breath', 'chest pain', 'rash',
            'swelling', 'bleeding', 'weakness', 'numbness', 'tingling', 'itching'
        ]
        
        text_lower = text.lower()
        found_symptoms = [symptom for symptom in symptom_keywords if symptom in text_lower]
        return found_symptoms
    
    def preprocess(self, text: str) -> Dict[str, any]:
        """Complete text preprocessing pipeline"""
        cleaned_text = self.clean_text(text)
        symptoms = self.extract_symptoms(text)
        
        return {
            'cleaned_text': cleaned_text,
            'symptoms': symptoms,
            'length': len(cleaned_text.split())
        }


class TabularPreprocessor:
    """Preprocess tabular medical data for gastroenterology and general models"""
    
    def __init__(self):
        self.scaler_params = {}
        self.categorical_mappings = {}
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in tabular data"""
        # Numeric columns: fill with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col].fillna(df[col].median(), inplace=True)
        
        # Categorical columns: fill with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown', inplace=True)
        
        return df
    
    def encode_categorical(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Encode categorical variables"""
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if fit:
                unique_values = df[col].unique()
                self.categorical_mappings[col] = {val: idx for idx, val in enumerate(unique_values)}
            
            if col in self.categorical_mappings:
                df[col] = df[col].map(self.categorical_mappings[col])
        
        return df
    
    def normalize_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Normalize numeric features"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if fit:
                self.scaler_params[col] = {
                    'mean': df[col].mean(),
                    'std': df[col].std()
                }
            
            if col in self.scaler_params:
                mean = self.scaler_params[col]['mean']
                std = self.scaler_params[col]['std']
                df[col] = (df[col] - mean) / (std + 1e-8)
        
        return df
    
    def preprocess(self, data: Union[pd.DataFrame, Dict], fit: bool = False) -> np.ndarray:
        """Complete tabular preprocessing pipeline"""
        # Convert dict to DataFrame if needed
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()
        
        # Preprocessing steps
        df = self.handle_missing_values(df)
        df = self.encode_categorical(df, fit=fit)
        df = self.normalize_features(df, fit=fit)
        
        return df.values


class MultiModalPreprocessor:
    """Unified preprocessor for all input modalities"""
    
    def __init__(self):
        self.ecg_preprocessor = ECGPreprocessor()
        self.image_preprocessor = ImagePreprocessor()
        self.text_preprocessor = TextPreprocessor()
        self.tabular_preprocessor = TabularPreprocessor()
    
    def preprocess(self, data: Dict[str, any], modality: str) -> any:
        """Route to appropriate preprocessor based on modality"""
        if modality == 'ecg':
            return self.ecg_preprocessor.preprocess(data)
        elif modality == 'image':
            return self.image_preprocessor.preprocess(data)
        elif modality == 'text':
            return self.text_preprocessor.preprocess(data)
        elif modality == 'tabular':
            return self.tabular_preprocessor.preprocess(data)
        else:
            raise ValueError(f"Unknown modality: {modality}")


if __name__ == "__main__":
    # Test preprocessors
    preprocessor = MultiModalPreprocessor()
    logger.info("✅ Multi-modal preprocessor initialized successfully")

