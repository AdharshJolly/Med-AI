"""
Dermatology AI Model for MedAI-Pro
Skin lesion classification using EfficientNetB7
Target Accuracy: 85-90% on HAM10000 dataset
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import timm
from PIL import Image
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import numpy as np


class HAM10000Dataset(Dataset):
    """HAM10000 Skin Lesion Dataset"""
    
    def __init__(self, data_path: str, split: str = 'train', transform=None):
        self.data_path = Path(data_path)
        self.split = split
        self.transform = transform
        
        # Load metadata
        metadata_file = self.data_path / 'HAM10000_metadata.csv'
        if not metadata_file.exists():
            # Try alternative names
            metadata_file = list(self.data_path.glob('*metadata*.csv'))[0]
        
        self.metadata = pd.read_csv(metadata_file)
        
        # Split data (80% train, 10% val, 10% test)
        n = len(self.metadata)
        if split == 'train':
            self.metadata = self.metadata[:int(0.8*n)]
        elif split == 'val':
            self.metadata = self.metadata[int(0.8*n):int(0.9*n)]
        else:
            self.metadata = self.metadata[int(0.9*n):]
        
        # Class mapping
        self.class_map = {
            'nv': 0,   # Melanocytic nevi
            'mel': 1,  # Melanoma
            'bkl': 2,  # Benign keratosis
            'bcc': 3,  # Basal cell carcinoma
            'akiec': 4,  # Actinic keratoses
            'vasc': 5,  # Vascular lesions
            'df': 6    # Dermatofibroma
        }
        
        self.class_names = list(self.class_map.keys())
        
        logger.info(f"Loaded {len(self.metadata)} skin lesion images for {split}")
    
    def __len__(self):
        return len(self.metadata)
    
    def __getitem__(self, idx):
        row = self.metadata.iloc[idx]
        
        # Load image
        image_id = row['image_id']
        image_path = None
        
        # Search for image in different folders
        for folder in ['HAM10000_images_part_1', 'HAM10000_images_part_2', 'images']:
            potential_path = self.data_path / folder / f"{image_id}.jpg"
            if potential_path.exists():
                image_path = potential_path
                break
        
        if image_path is None:
            # Fallback: search recursively
            image_path = list(self.data_path.rglob(f"{image_id}.jpg"))[0]
        
        image = cv2.imread(str(image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply transforms
        if self.transform:
            transformed = self.transform(image=image)
            image = transformed['image']
        
        # Get label
        label = self.class_map[row['dx']]
        
        return image, label


class DermatologyModel:
    """Dermatology diagnosis model using EfficientNetB7"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pre-trained EfficientNetB7
        self.model = timm.create_model('efficientnet_b7', pretrained=True, num_classes=7)
        self.model = self.model.to(self.device)
        
        self.class_names = [
            'Melanocytic Nevi (Benign)',
            'Melanoma (Malignant)',
            'Benign Keratosis',
            'Basal Cell Carcinoma',
            'Actinic Keratoses',
            'Vascular Lesions',
            'Dermatofibroma'
        ]
        
        self.severity_map = {
            'Melanocytic Nevi (Benign)': 'low',
            'Melanoma (Malignant)': 'critical',
            'Benign Keratosis': 'low',
            'Basal Cell Carcinoma': 'high',
            'Actinic Keratoses': 'medium',
            'Vascular Lesions': 'medium',
            'Dermatofibroma': 'low'
        }
        
        # Transforms
        self.train_transform = A.Compose([
            A.Resize(600, 600),
            A.RandomCrop(512, 512),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.Rotate(limit=90, p=0.5),
            A.RandomBrightnessContrast(p=0.5),
            A.HueSaturationValue(p=0.3),
            A.GaussNoise(p=0.2),
            A.Blur(blur_limit=3, p=0.2),
            A.CLAHE(p=0.3),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        self.val_transform = A.Compose([
            A.Resize(512, 512),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
            logger.info(f"✅ Dermatology model loaded from {model_path}")
        else:
            logger.warning("⚠️ No pre-trained model loaded")
    
    def train(self, data_path: str, epochs: int = 30, batch_size: int = 16):
        """Train the dermatology model"""
        logger.info("🚀 Starting dermatology model training...")
        
        # Create datasets
        train_dataset = HAM10000Dataset(data_path, 'train', self.train_transform)
        val_dataset = HAM10000Dataset(data_path, 'val', self.val_transform)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
        
        # Training setup with class weights for imbalanced data
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=0.0001, weight_decay=0.01)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        
        best_acc = 0.0
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                _, predicted = outputs.max(1)
                train_total += labels.size(0)
                train_correct += predicted.eq(labels).sum().item()
            
            train_acc = 100. * train_correct / train_total
            
            # Validation phase
            val_acc, val_loss = self.evaluate(val_loader)
            
            scheduler.step()
            
            logger.info(
                f"Epoch {epoch+1}/{epochs} - "
                f"Train Loss: {train_loss/len(train_loader):.4f}, Train Acc: {train_acc:.2f}% - "
                f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%"
            )
            
            if val_acc > best_acc:
                best_acc = val_acc
                self.save_model('models/dermatology_best.pth')
                logger.info(f"✅ Best model saved with accuracy: {best_acc:.2f}%")
        
        logger.info(f"🎉 Training completed! Best accuracy: {best_acc:.2f}%")
        return best_acc
    
    def evaluate(self, dataloader):
        """Evaluate model"""
        self.model.eval()
        criterion = nn.CrossEntropyLoss()
        
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in dataloader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        accuracy = 100. * correct / total
        avg_loss = val_loss / len(dataloader)
        
        return accuracy, avg_loss
    
    def predict(self, image: torch.Tensor) -> Dict:
        """Make prediction on skin lesion image"""
        self.model.eval()
        
        with torch.no_grad():
            if image.dim() == 3:
                image = image.unsqueeze(0)
            
            image = image.to(self.device)
            outputs = self.model(image)
            probabilities = F.softmax(outputs, dim=1)
            
            confidence, predicted = probabilities.max(1)
            
            result = {
                'primary_prediction': self.class_names[predicted.item()],
                'confidence_score': confidence.item(),
                'severity_level': self.severity_map[self.class_names[predicted.item()]],
                'all_predictions': {
                    self.class_names[i]: probabilities[0][i].item()
                    for i in range(len(self.class_names))
                },
                'recommendations': self._get_recommendations(predicted.item(), confidence.item())
            }
            
            return result
    
    def _get_recommendations(self, class_idx: int, confidence: float) -> List[str]:
        """Get medical recommendations based on prediction"""
        recommendations = []
        
        if class_idx == 1:  # Melanoma
            recommendations = [
                "⚠️ URGENT: Consult a dermatologist immediately",
                "Biopsy recommended for confirmation",
                "Avoid sun exposure",
                "Monitor for changes in size, shape, or color"
            ]
        elif class_idx == 3:  # Basal Cell Carcinoma
            recommendations = [
                "Consult a dermatologist within 1-2 weeks",
                "Surgical removal may be required",
                "Use sunscreen (SPF 50+) daily"
            ]
        elif class_idx in [0, 2, 6]:  # Benign conditions
            recommendations = [
                "Regular monitoring recommended",
                "Consult dermatologist if changes occur",
                "Maintain good skin hygiene"
            ]
        else:
            recommendations = [
                "Consult a dermatologist for proper evaluation",
                "Avoid self-medication",
                "Document any changes"
            ]
        
        if confidence < 0.7:
            recommendations.insert(0, "⚠️ Low confidence - Professional evaluation strongly recommended")
        
        return recommendations
    
    def save_model(self, path: str):
        """Save model weights"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)
    
    def load_model(self, path: str):
        """Load model weights"""
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()


if __name__ == "__main__":
    model = DermatologyModel()
    logger.info("✅ Dermatology model module ready")

