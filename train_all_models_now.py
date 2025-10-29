#!/usr/bin/env python3
"""
Complete Production Training Script
Trains all 7 models with downloaded datasets
Target: 90%+ accuracy
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from sklearn.preprocessing import StandardScaler, LabelEncoder

# Results dictionary for storing model accuracies
results = {}

# Ensure DEVICE is defined before use
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Results dictionary for storing model accuracies
results = {}
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb
import lightgbm as lgb
from tqdm import tqdm
import pickle
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = Path("data/real")
MODELS_DIR = Path("backend/models/weights")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("PRODUCTION MODEL TRAINING - ALL 7 MODELS")
print(f"Device: {DEVICE}")
print("=" * 80)

# 2. DERMATOLOGY - Skin Lesion Classification
print("\n" + "=" * 80)
print("2. TRAINING DERMATOLOGY MODEL")
print("=" * 80)
try:
    derm_dir = DATA_DIR / "dermatology"
    image_paths = []
    labels = []
    # HAM10000
    ham_dir = derm_dir / "ham10000"
    if ham_dir.exists():
        ham_images = list(ham_dir.glob("**/*.jpg"))
        image_paths.extend(ham_images)
        labels.extend([0] * len(ham_images))
        print(f"✓ HAM10000: {len(ham_images):,} images")
    # ISIC 2019
    isic_dir = derm_dir / "isic2019"
    if isic_dir.exists():
        isic_images = list(isic_dir.glob("**/*.jpg"))
        image_paths.extend(isic_images)
        labels.extend([1] * len(isic_images))
        print(f"✓ ISIC 2019: {len(isic_images):,} images")
    # Melanoma
    melanoma_dir = derm_dir / "melanoma"
    if melanoma_dir.exists():
        melanoma_images = list(melanoma_dir.glob("**/*.jpg"))
        image_paths.extend(melanoma_images)
        labels.extend([2] * len(melanoma_images))
        print(f"✓ Melanoma: {len(melanoma_images):,} images")

    if len(image_paths) > 0:
        print(f"Total images: {len(image_paths):,}")
        X_train, X_test, y_train, y_test = train_test_split(
            image_paths, labels, test_size=0.2, random_state=42, stratify=labels
        )
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        class ImageDataset(Dataset):
            def __init__(self, paths, labels, transform):
                self.paths = paths
                self.labels = labels
                self.transform = transform
            def __len__(self):
                return len(self.paths)
            def __getitem__(self, idx):
                try:
                    img = Image.open(self.paths[idx]).convert('RGB')
                    img = self.transform(img)
                    return img, self.labels[idx]
                except:
                    return torch.zeros(3, 224, 224), self.labels[idx]
        train_dataset = ImageDataset(X_train, y_train, transform)
        test_dataset = ImageDataset(X_test, y_test, transform)
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=0)
        print("Loading EfficientNet-B0...")
        model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, 3)
        model = model.to(DEVICE)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.0001)
        print("Training model...")
        for epoch in range(5):
            model.train()
            train_loss = 0
            for images, labels_batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/5"):
                images, labels_batch = images.to(DEVICE), labels_batch.to(DEVICE)
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels_batch)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            print(f"Epoch {epoch+1}/5 - Loss: {train_loss/len(train_loader):.4f}")
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels_batch in test_loader:
                images, labels_batch = images.to(DEVICE), labels_batch.to(DEVICE)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels_batch.size(0)
                correct += (predicted == labels_batch).sum().item()
        accuracy = 100 * correct / total
        model_path = MODELS_DIR / "dermatology_model.pth"
        torch.save(model.state_dict(), model_path)
        results['dermatology'] = accuracy
        print(f"✓ Dermatology Model: {accuracy:.2f}% accuracy")
        print(f"✓ Saved to {model_path}")
    else:
        print("✗ No dermatology images found")
        results['dermatology'] = 0.0
except Exception as e:
    print(f"✗ Dermatology training failed: {e}")
    results['dermatology'] = 0.0
        
        results['dermatology'] = accuracy
        print(f"✓ Dermatology Model: {accuracy:.2f}% accuracy")
        print(f"✓ Saved to {model_path}")
    else:
        print("✗ No dermatology images found")
        results['dermatology'] = 0.0

except Exception as e:
    print(f"✗ Dermatology training failed: {e}")
    results['dermatology'] = 0.0

# ============================================================================
# 3. RESPIRATORY - Chest X-ray Classification
# ============================================================================
print("\n" + "=" * 80)
print("3. TRAINING RESPIRATORY MODEL")
print("=" * 80)

try:
    resp_dir = DATA_DIR / "respiratory"
    
    # Collect all images
    image_paths = []
    labels = []
    
    # Pneumonia
    pneumonia_dir = resp_dir / "pneumonia"
    if pneumonia_dir.exists():
        pneumonia_images = list(pneumonia_dir.glob("**/*.jpeg"))
        image_paths.extend(pneumonia_images)
        labels.extend([0] * len(pneumonia_images))
        print(f"✓ Pneumonia: {len(pneumonia_images):,} images")
    
    # COVID-19
    covid_dir = resp_dir / "covid19"
    if covid_dir.exists():
        covid_images = list(covid_dir.glob("**/*.png"))
        image_paths.extend(covid_images)
        labels.extend([1] * len(covid_images))
        print(f"✓ COVID-19: {len(covid_images):,} images")
    
    if len(image_paths) > 0:
        print(f"Total images: {len(image_paths):,}")

