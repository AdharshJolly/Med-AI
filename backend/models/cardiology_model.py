"""
Cardiology AI Model for MedAI-Pro
ECG-based cardiac arrhythmia classification using EfficientNet 1D-CNN
Target Accuracy: 85-90% on PTB-XL dataset
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
import wfdb
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from loguru import logger
import joblib


class ECGDataset(Dataset):
    """PTB-XL ECG Dataset loader"""
    
    def __init__(self, data_path: str, split: str = 'train'):
        self.data_path = Path(data_path)
        self.split = split
        
        # Load metadata
        self.metadata = pd.read_csv(self.data_path / 'ptbxl_database.csv')
        
        # Filter by split
        if split == 'train':
            self.metadata = self.metadata[self.metadata['strat_fold'] <= 8]
        elif split == 'val':
            self.metadata = self.metadata[self.metadata['strat_fold'] == 9]
        else:  # test
            self.metadata = self.metadata[self.metadata['strat_fold'] == 10]
        
        # Load label mappings
        self.label_map = {
            'NORM': 0,  # Normal
            'MI': 1,    # Myocardial Infarction
            'STTC': 2,  # ST/T Change
            'CD': 3,    # Conduction Disturbance
            'HYP': 4    # Hypertrophy
        }
        
        logger.info(f"Loaded {len(self.metadata)} ECG records for {split}")
    
    def __len__(self):
        return len(self.metadata)
    
    def __getitem__(self, idx):
        row = self.metadata.iloc[idx]
        
        # Load ECG signal
        ecg_path = self.data_path / row['filename_hr']
        record = wfdb.rdrecord(str(ecg_path).replace('.hea', ''))
        ecg_signal = record.p_signal  # Shape: (5000, 12)
        
        # Normalize
        ecg_signal = (ecg_signal - ecg_signal.mean(axis=0)) / (ecg_signal.std(axis=0) + 1e-8)
        
        # Convert to tensor (12 channels, 5000 samples)
        ecg_tensor = torch.FloatTensor(ecg_signal.T)
        
        # Get label
        scp_codes = eval(row['scp_codes'])
        label = 0  # Default to NORM
        for code in scp_codes.keys():
            if code in self.label_map:
                label = self.label_map[code]
                break
        
        return ecg_tensor, label


class EfficientNet1D(nn.Module):
    """1D EfficientNet for ECG classification"""
    
    def __init__(self, num_classes: int = 5, in_channels: int = 12):
        super(EfficientNet1D, self).__init__()
        
        # Stem
        self.stem = nn.Sequential(
            nn.Conv1d(in_channels, 32, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm1d(32),
            nn.SiLU(inplace=True)
        )
        
        # MBConv blocks
        self.blocks = nn.ModuleList([
            self._make_mbconv_block(32, 16, 3, 1, 1),
            self._make_mbconv_block(16, 24, 3, 2, 2),
            self._make_mbconv_block(24, 40, 5, 2, 2),
            self._make_mbconv_block(40, 80, 3, 2, 3),
            self._make_mbconv_block(80, 112, 5, 1, 3),
            self._make_mbconv_block(112, 192, 5, 2, 4),
            self._make_mbconv_block(192, 320, 3, 1, 1)
        ])
        
        # Head
        self.head = nn.Sequential(
            nn.Conv1d(320, 1280, kernel_size=1, bias=False),
            nn.BatchNorm1d(1280),
            nn.SiLU(inplace=True),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(1280, num_classes)
        )
    
    def _make_mbconv_block(self, in_ch, out_ch, kernel_size, stride, num_blocks):
        """Create MBConv block"""
        layers = []
        for i in range(num_blocks):
            layers.append(MBConvBlock(
                in_ch if i == 0 else out_ch,
                out_ch,
                kernel_size,
                stride if i == 0 else 1
            ))
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.stem(x)
        for block in self.blocks:
            x = block(x)
        x = self.head(x)
        return x


class MBConvBlock(nn.Module):
    """Mobile Inverted Bottleneck Convolution Block"""
    
    def __init__(self, in_channels, out_channels, kernel_size, stride, expand_ratio=6):
        super(MBConvBlock, self).__init__()
        
        self.stride = stride
        self.use_residual = (stride == 1 and in_channels == out_channels)
        
        hidden_dim = in_channels * expand_ratio
        
        layers = []
        
        # Expansion
        if expand_ratio != 1:
            layers.extend([
                nn.Conv1d(in_channels, hidden_dim, 1, bias=False),
                nn.BatchNorm1d(hidden_dim),
                nn.SiLU(inplace=True)
            ])
        
        # Depthwise
        layers.extend([
            nn.Conv1d(hidden_dim, hidden_dim, kernel_size, stride,
                     padding=kernel_size//2, groups=hidden_dim, bias=False),
            nn.BatchNorm1d(hidden_dim),
            nn.SiLU(inplace=True)
        ])
        
        # Squeeze-and-Excitation
        layers.append(SEBlock(hidden_dim))
        
        # Projection
        layers.extend([
            nn.Conv1d(hidden_dim, out_channels, 1, bias=False),
            nn.BatchNorm1d(out_channels)
        ])
        
        self.conv = nn.Sequential(*layers)
    
    def forward(self, x):
        if self.use_residual:
            return x + self.conv(x)
        else:
            return self.conv(x)


class SEBlock(nn.Module):
    """Squeeze-and-Excitation block"""
    
    def __init__(self, channels, reduction=4):
        super(SEBlock, self).__init__()
        self.squeeze = nn.AdaptiveAvgPool1d(1)
        self.excitation = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.SiLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        b, c, _ = x.size()
        y = self.squeeze(x).view(b, c)
        y = self.excitation(y).view(b, c, 1)
        return x * y.expand_as(x)


class CardiologyModel:
    """Cardiology diagnosis model wrapper"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = EfficientNet1D(num_classes=5, in_channels=12).to(self.device)
        
        self.class_names = ['Normal', 'Myocardial Infarction', 'ST/T Change',
                           'Conduction Disturbance', 'Hypertrophy']
        
        self.severity_map = {
            'Normal': 'low',
            'Myocardial Infarction': 'critical',
            'ST/T Change': 'medium',
            'Conduction Disturbance': 'high',
            'Hypertrophy': 'medium'
        }
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
            logger.info(f"✅ Cardiology model loaded from {model_path}")
        else:
            logger.warning("⚠️ No pre-trained model loaded. Train the model first.")
    
    def train(self, data_path: str, epochs: int = 50, batch_size: int = 32):
        """Train the cardiology model"""
        logger.info("🚀 Starting cardiology model training...")
        
        # Create datasets
        train_dataset = ECGDataset(data_path, 'train')
        val_dataset = ECGDataset(data_path, 'val')
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
        
        # Training setup
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=0.001, weight_decay=0.01)
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
            
            # Save best model
            if val_acc > best_acc:
                best_acc = val_acc
                self.save_model('models/cardiology_best.pth')
                logger.info(f"✅ Best model saved with accuracy: {best_acc:.2f}%")
        
        logger.info(f"🎉 Training completed! Best accuracy: {best_acc:.2f}%")
        return best_acc
    
    def evaluate(self, dataloader):
        """Evaluate model on validation/test set"""
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
    
    def predict(self, ecg_data: torch.Tensor) -> Dict:
        """Make prediction on ECG data"""
        self.model.eval()
        
        with torch.no_grad():
            if ecg_data.dim() == 2:
                ecg_data = ecg_data.unsqueeze(0)
            
            ecg_data = ecg_data.to(self.device)
            outputs = self.model(ecg_data)
            probabilities = F.softmax(outputs, dim=1)
            
            confidence, predicted = probabilities.max(1)
            
            result = {
                'primary_prediction': self.class_names[predicted.item()],
                'confidence_score': confidence.item(),
                'severity_level': self.severity_map[self.class_names[predicted.item()]],
                'all_predictions': {
                    self.class_names[i]: probabilities[0][i].item()
                    for i in range(len(self.class_names))
                }
            }
            
            return result
    
    def save_model(self, path: str):
        """Save model weights"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)
    
    def load_model(self, path: str):
        """Load model weights"""
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()



# Orchestrator-compatible training function
def train_model(data_path: str, epochs: int = 50, batch_size: int = 32) -> dict:
    """Train CardiologyModel and return accuracy in a dict."""
    model = CardiologyModel()
    acc = model.train(data_path, epochs=epochs, batch_size=batch_size)
    return {"accuracy": acc}

if __name__ == "__main__":
    model = CardiologyModel()
    # model.train('data/cardiology/ptb-xl', epochs=50)
    logger.info("✅ Cardiology model module ready")

