"""
Orthopedics AI Model for MedAI-Pro
Bone fracture detection using ResNet50
Target Accuracy: 85-90% on MURA dataset
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import models
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import pandas as pd


class MURADataset(Dataset):
    """MURA Bone Fracture Dataset"""
    
    def __init__(self, data_path: str, split: str = 'train', transform=None):
        self.data_path = Path(data_path)
        self.split = split
        self.transform = transform
        
        # Load image paths and labels
        csv_file = self.data_path / f'{split}_image_paths.csv'
        if csv_file.exists():
            df = pd.read_csv(csv_file, header=None, names=['path'])
            self.images = df['path'].tolist()
            self.labels = [1 if 'positive' in p else 0 for p in self.images]
        else:
            # Fallback: scan directory
            self.images = []
            self.labels = []
            for label_dir in ['positive', 'negative']:
                label = 1 if label_dir == 'positive' else 0
                search_dir = self.data_path / split / label_dir
                if search_dir.exists():
                    for img_path in search_dir.rglob('*.png'):
                        self.images.append(str(img_path))
                        self.labels.append(label)
        
        logger.info(f"Loaded {len(self.images)} bone X-ray images for {split}")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = cv2.imread(self.images[idx])
        if image is None:
            image = cv2.imread(self.images[idx], cv2.IMREAD_GRAYSCALE)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if self.transform:
            transformed = self.transform(image=image)
            image = transformed['image']
        
        return image, self.labels[idx]


class OrthopedicsModel:
    """Orthopedics diagnosis model using ResNet50"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pre-trained ResNet50
        self.model = models.resnet50(pretrained=True)
        self.model.fc = nn.Linear(self.model.fc.in_features, 2)
        self.model = self.model.to(self.device)
        
        self.class_names = ['Normal', 'Fracture/Abnormality']
        self.severity_map = {'Normal': 'low', 'Fracture/Abnormality': 'high'}
        
        # Transforms
        self.train_transform = A.Compose([
            A.Resize(256, 256),
            A.RandomCrop(224, 224),
            A.HorizontalFlip(p=0.5),
            A.Rotate(limit=10, p=0.3),
            A.RandomBrightnessContrast(p=0.3),
            A.CLAHE(p=0.5),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        self.val_transform = A.Compose([
            A.Resize(224, 224),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
            logger.info(f"✅ Orthopedics model loaded from {model_path}")
    
    def train(self, data_path: str, epochs: int = 20, batch_size: int = 32):
        """Train the orthopedics model"""
        logger.info("🚀 Starting orthopedics model training...")
        
        train_dataset = MURADataset(data_path, 'train', self.train_transform)
        val_dataset = MURADataset(data_path, 'valid', self.val_transform)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0001)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
        
        best_acc = 0.0
        
        for epoch in range(epochs):
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
            val_acc, val_loss = self.evaluate(val_loader)
            
            scheduler.step()
            
            logger.info(f"Epoch {epoch+1}/{epochs} - Train Acc: {train_acc:.2f}% - Val Acc: {val_acc:.2f}%")
            
            if val_acc > best_acc:
                best_acc = val_acc
                self.save_model('models/orthopedics_best.pth')
        
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
        
        return 100. * correct / total, val_loss / len(dataloader)
    
    def predict(self, image: torch.Tensor) -> Dict:
        """Make prediction on bone X-ray"""
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
                'recommendations': self._get_recommendations(predicted.item())
            }
            
            return result
    
    def _get_recommendations(self, class_idx: int) -> List[str]:
        """Get medical recommendations"""
        if class_idx == 1:  # Fracture
            return [
                "Consult an orthopedic specialist immediately",
                "Immobilize the affected area",
                "Apply ice to reduce swelling",
                "Avoid weight-bearing on affected limb",
                "CT scan may be required for detailed assessment"
            ]
        else:
            return [
                "Bone structure appears normal",
                "Maintain bone health with calcium and vitamin D",
                "Regular exercise recommended"
            ]
    
    def save_model(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)
    
    def load_model(self, path: str):
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()


if __name__ == "__main__":
    model = OrthopedicsModel()
    logger.info("✅ Orthopedics model module ready")

