#!/usr/bin/env python3
"""
Production Model Training with 15,000+ Cases Per Model
Multi-Input Processing: Images, Text, Tabular Data, Time-Series
Target: 90%+ accuracy on all models
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from torchvision.models import efficientnet_b0, densenet121, resnet50
from torchvision.models import EfficientNet_B0_Weights, DenseNet121_Weights, ResNet50_Weights
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
import pickle
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = Path("data/production")
MODELS_DIR = Path("backend/models/weights")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 0.0001

print("=" * 80)
print("PRODUCTION MODEL TRAINING")
print(f"Device: {DEVICE}")
print(f"Target: 90%+ accuracy with 15,000+ cases per model")
print("Multi-Input: Images, Text, Tabular, Time-Series")
print("=" * 80)

results = {}

# ============================================================================
# MULTI-INPUT DATASET CLASSES
# ============================================================================

class MultiModalDataset(Dataset):
    """Base class for multi-modal medical data"""
    def __init__(self, data_dir, transform=None):
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.samples = []
        self.labels = []
        
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        raise NotImplementedError

class ImageDataset(MultiModalDataset):
    """For image-based models (Dermatology, Respiratory, Orthopedics)"""
    def __init__(self, image_paths, labels, transform=None):
        super().__init__(None, transform)
        self.image_paths = image_paths
        self.labels = labels
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

class TimeSeriesDataset(MultiModalDataset):
    """For time-series data (Cardiology ECG)"""
    def __init__(self, signals, labels):
        super().__init__(None, None)
        self.signals = signals
        self.labels = labels
        
    def __len__(self):
        return len(self.signals)
    
    def __getitem__(self, idx):
        signal = torch.FloatTensor(self.signals[idx])
        label = self.labels[idx]
        return signal, label

class TabularDataset(MultiModalDataset):
    """For tabular clinical data (Gastro, General Medicine)"""
    def __init__(self, features, labels):
        super().__init__(None, None)
        self.features = features
        self.labels = labels
        
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        features = torch.FloatTensor(self.features[idx])
        label = self.labels[idx]
        return features, label

# ============================================================================
# ADVANCED MODEL ARCHITECTURES
# ============================================================================

class ECGResNet1D(nn.Module):
    """1D ResNet for ECG time-series data"""
    def __init__(self, num_classes=5, input_channels=12):
        super().__init__()
        
        self.conv1 = nn.Conv1d(input_channels, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm1d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool1d(kernel_size=3, stride=2, padding=1)
        
        # Residual blocks
        self.layer1 = self._make_layer(64, 64, 2)
        self.layer2 = self._make_layer(64, 128, 2, stride=2)
        self.layer3 = self._make_layer(128, 256, 2, stride=2)
        self.layer4 = self._make_layer(256, 512, 2, stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(512, num_classes)
        
    def _make_layer(self, in_channels, out_channels, blocks, stride=1):
        layers = []
        layers.append(nn.Conv1d(in_channels, out_channels, 3, stride, 1))
        layers.append(nn.BatchNorm1d(out_channels))
        layers.append(nn.ReLU(inplace=True))
        
        for _ in range(1, blocks):
            layers.append(nn.Conv1d(out_channels, out_channels, 3, 1, 1))
            layers.append(nn.BatchNorm1d(out_channels))
            layers.append(nn.ReLU(inplace=True))
        
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        
        return x

class ClinicalMLP(nn.Module):
    """Multi-layer perceptron for clinical tabular data"""
    def __init__(self, input_dim, num_classes, hidden_dims=[512, 256, 128]):
        super().__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU(inplace=True))
            layers.append(nn.Dropout(0.3))
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, num_classes))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)

# ============================================================================
# TRAINING FUNCTION
# ============================================================================

def train_model(model, train_loader, val_loader, epochs=20, lr=0.0001, model_name="model"):
    """Train a PyTorch model with validation"""
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', patience=3, factor=0.5)
    
    best_acc = 0
    best_model_state = None
    patience_counter = 0
    max_patience = 5
    
    print(f"\nTraining {model_name}...")
    print(f"Train samples: {len(train_loader.dataset)}, Val samples: {len(val_loader.dataset)}")
    
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        for batch_idx, (data, target) in enumerate(pbar):
            data, target = data.to(DEVICE), target.to(DEVICE)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(output.data, 1)
            train_total += target.size(0)
            train_correct += (predicted == target).sum().item()
            
            pbar.set_postfix({'loss': train_loss/(batch_idx+1), 'acc': 100.*train_correct/train_total})
        
        train_acc = 100. * train_correct / train_total
        
        # Validation phase
        model.eval()
        val_correct = 0
        val_total = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(DEVICE), target.to(DEVICE)
                output = model(data)
                _, predicted = torch.max(output.data, 1)
                val_total += target.size(0)
                val_correct += (predicted == target).sum().item()
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(target.cpu().numpy())
        
        val_acc = 100. * val_correct / val_total
        
        print(f"Epoch {epoch+1}: Train Acc: {train_acc:.2f}%, Val Acc: {val_acc:.2f}%")
        
        # Learning rate scheduling
        scheduler.step(val_acc)
        
        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            best_model_state = model.state_dict().copy()
            patience_counter = 0
            print(f"  → New best accuracy: {best_acc:.2f}%")
        else:
            patience_counter += 1
            if patience_counter >= max_patience:
                print(f"  → Early stopping at epoch {epoch+1}")
                break
    
    # Load best model
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    
    # Final evaluation
    model.eval()
    val_correct = 0
    val_total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for data, target in val_loader:
            data, target = data.to(DEVICE), target.to(DEVICE)
            output = model(data)
            _, predicted = torch.max(output.data, 1)
            val_total += target.size(0)
            val_correct += (predicted == target).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(target.cpu().numpy())
    
    final_acc = 100. * val_correct / val_total
    
    print(f"\n{model_name} Final Results:")
    print(f"  Best Validation Accuracy: {best_acc:.2f}%")
    print(f"  Final Validation Accuracy: {final_acc:.2f}%")
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(all_labels, all_preds))
    
    return best_acc

# ============================================================================
# DATA TRANSFORMS
# ============================================================================

transform_train = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

transform_val = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

print("\n✓ Configuration complete")
print(f"✓ Device: {DEVICE}")
print(f"✓ Batch size: {BATCH_SIZE}")
print(f"✓ Epochs: {EPOCHS}")
print(f"✓ Learning rate: {LEARNING_RATE}")
print("\nReady to train models!")
print("\nNote: Run individual model training scripts for each organ")

