"""
Respiratory AI Model for MedAI-Pro
Chest X-ray pneumonia detection using DenseNet121
Target Accuracy: 85-90% on Chest X-Ray dataset
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import models
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


class ChestXRayDataset(Dataset):
    """Chest X-Ray Pneumonia Dataset"""
    
    def __init__(self, data_path: str, split: str = 'train', transform=None):
        self.data_path = Path(data_path)
        self.split = split
        self.transform = transform
        
        # Load images from directory structure
        split_dir = self.data_path / split
        self.images = []
        self.labels = []
        
        for class_idx, class_name in enumerate(['NORMAL', 'PNEUMONIA']):
            class_dir = split_dir / class_name
            if class_dir.exists():
                for img_path in class_dir.glob('*.jpeg'):
                    self.images.append(str(img_path))
                    self.labels.append(class_idx)
        
        logger.info(f"Loaded {len(self.images)} chest X-ray images for {split}")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = cv2.imread(self.images[idx])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if self.transform:
            transformed = self.transform(image=image)
            image = transformed['image']
        
        label = self.labels[idx]
        return image, label


class RespiratoryModel:
    """Respiratory diagnosis model using DenseNet121"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pre-trained DenseNet121
        self.model = models.densenet121(pretrained=True)
        self.model.classifier = nn.Linear(self.model.classifier.in_features, 2)
        self.model = self.model.to(self.device)
        
        self.class_names = ['Normal', 'Pneumonia']
        self.severity_map = {'Normal': 'low', 'Pneumonia': 'high'}
        
        # Transforms
        self.train_transform = A.Compose([
            A.Resize(256, 256),
            A.RandomCrop(224, 224),
            A.HorizontalFlip(p=0.5),
            A.Rotate(limit=15, p=0.3),
            A.RandomBrightnessContrast(p=0.3),
            A.GaussNoise(p=0.2),
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
            logger.info(f"✅ Respiratory model loaded from {model_path}")
    
    def train(self, data_path: str, epochs: int = 25, batch_size: int = 32):
        """Train the respiratory model"""
        logger.info("🚀 Starting respiratory model training...")
        
        train_dataset = ChestXRayDataset(data_path, 'train', self.train_transform)
        val_dataset = ChestXRayDataset(data_path, 'val', self.val_transform)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0001)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', patience=3)
        
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
            
            scheduler.step(val_acc)
            
            logger.info(f"Epoch {epoch+1}/{epochs} - Train Acc: {train_acc:.2f}% - Val Acc: {val_acc:.2f}%")
            
            if val_acc > best_acc:
                best_acc = val_acc
                self.save_model('models/respiratory_best.pth')
        
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
        """Make prediction on chest X-ray"""
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
        if class_idx == 1:  # Pneumonia
            return [
                "Consult a pulmonologist immediately",
                "Chest X-ray confirmation recommended",
                "Complete blood count (CBC) test advised",
                "Rest and adequate hydration",
                "Monitor temperature and oxygen levels"
            ]
        else:
            return [
                "Lungs appear normal",
                "Maintain respiratory health",
                "Regular check-ups recommended"
            ]
    
    def save_model(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)

    def load_model(self, path: str):
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()

    def generate_cam(self, image_path: str, save_path: Optional[str] = None) -> Tuple[np.ndarray, Dict]:
        """
        Generate Class Activation Mapping (CAM) visualization for chest X-ray

        Args:
            image_path: Path to chest X-ray image
            save_path: Optional path to save CAM visualization

        Returns:
            Tuple of (CAM heatmap, prediction results)
        """
        # Load and preprocess image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Apply CLAHE enhancement
        lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

        # Resize and normalize
        resized = cv2.resize(enhanced, (224, 224))
        normalized = resized.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        normalized = (normalized - mean) / std

        # Convert to tensor
        input_tensor = torch.from_numpy(normalized).permute(2, 0, 1).unsqueeze(0).to(self.device)

        # Get prediction
        self.model.eval()
        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            prediction = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][prediction].item()

        # Generate CAM using Grad-CAM
        self.model.zero_grad()

        # Forward pass
        features = []
        def hook_fn(module, input, output):
            features.append(output)

        # Register hook on last convolutional layer
        target_layer = self.model.features[-1]
        handle = target_layer.register_forward_hook(hook_fn)

        # Forward pass with gradient
        output = self.model(input_tensor)
        handle.remove()

        # Backward pass
        self.model.zero_grad()
        class_score = output[0, prediction]
        class_score.backward()

        # Get gradients and features
        gradients = target_layer.weight.grad
        feature_map = features[0]

        # Calculate weights
        weights = torch.mean(gradients, dim=(2, 3), keepdim=True)

        # Generate CAM
        cam = torch.sum(weights * feature_map, dim=1).squeeze()
        cam = F.relu(cam)
        cam = cam.cpu().numpy()

        # Normalize CAM
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        cam = cv2.resize(cam, (image.shape[1], image.shape[0]))

        # Create heatmap
        heatmap = cm.jet(cam)[:, :, :3]
        heatmap = (heatmap * 255).astype(np.uint8)

        # Overlay heatmap on original image
        overlay = cv2.addWeighted(image, 0.6, heatmap, 0.4, 0)

        # Save visualization if path provided
        if save_path:
            plt.figure(figsize=(15, 5))

            plt.subplot(1, 3, 1)
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            plt.title('Original X-Ray')
            plt.axis('off')

            plt.subplot(1, 3, 2)
            plt.imshow(cam, cmap='jet')
            plt.title('Class Activation Map')
            plt.axis('off')

            plt.subplot(1, 3, 3)
            plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
            plt.title(f'Prediction: {self.classes[prediction]} ({confidence:.2%})')
            plt.axis('off')

            plt.tight_layout()
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"CAM visualization saved to {save_path}")

        # Prepare results
        results = {
            "prediction": self.classes[prediction],
            "confidence": confidence,
            "affected_regions": self._identify_affected_regions(cam),
            "cam_available": True
        }

        return overlay, results

    def _identify_affected_regions(self, cam: np.ndarray, threshold: float = 0.7) -> List[str]:
        """
        Identify affected lung regions from CAM

        Args:
            cam: Class activation map
            threshold: Threshold for high activation

        Returns:
            List of affected regions
        """
        regions = []
        h, w = cam.shape

        # Divide into regions
        left_upper = cam[:h//2, :w//2]
        right_upper = cam[:h//2, w//2:]
        left_lower = cam[h//2:, :w//2]
        right_lower = cam[h//2:, w//2:]

        # Check activation in each region
        if np.mean(left_upper) > threshold:
            regions.append("Left upper lobe")
        if np.mean(right_upper) > threshold:
            regions.append("Right upper lobe")
        if np.mean(left_lower) > threshold:
            regions.append("Left lower lobe")
        if np.mean(right_lower) > threshold:
            regions.append("Right lower lobe")

        if not regions:
            regions.append("No specific region highlighted")

        return regions


def calculate_cam_visualization(model: RespiratoryModel, image_path: str, save_path: Optional[str] = None):
    """
    Standalone function to calculate CAM visualization

    Args:
        model: Trained respiratory model
        image_path: Path to chest X-ray image
        save_path: Optional path to save visualization

    Returns:
        Tuple of (overlay image, prediction results)
    """
    return model.generate_cam(image_path, save_path)



# Orchestrator-compatible training function
def train_model(data_path: str, epochs: int = 25, batch_size: int = 32) -> dict:
    """Train RespiratoryModel and return accuracy in a dict."""
    model = RespiratoryModel()
    acc = model.train(data_path, epochs=epochs, batch_size=batch_size)
    return {"accuracy": acc}

if __name__ == "__main__":
    model = RespiratoryModel()
    logger.info("✅ Respiratory model module ready with CAM visualization")

