#!/usr/bin/env python3
"""
MedAI-Pro: Medical Dataset Downloader (Simplified)
Generates/downloads medical datasets for all 7 models
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import random
import io
import sys

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
LOGS_DIR = PROJECT_ROOT / "outputs" / "logs"

# Create directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "dataset_download_log.txt"

def log_download(message):
    """Log download progress"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = f"[{timestamp}] {message}"
    print(log_text, file=sys.stdout)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_text + '\n')
    except Exception as e:
        print(f"Warning: Could not write to log: {e}")

# ============================================================================
# CARDIOLOGY DATASETS
# ============================================================================

def download_cardiology_datasets():
    """Download/generate cardiology ECG datasets"""
    log_download("[CARDIOLOGY] Generating ECG datasets...")
    
    try:
        cardio_dir = DATA_DIR / "cardiology"
        cardio_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic ECG data
        # Simulate MIT-BIH and PTB-XL datasets
        n_samples = 2500  # ~2500 ECG records
        n_features = 250  # Time series length
        n_classes = 5     # Arrhythmia classes
        
        ecg_data = np.random.randn(n_samples, n_features).astype(np.float32)
        ecg_labels = np.random.randint(0, n_classes, n_samples)
        
        np.save(cardio_dir / "ecg_data.npy", ecg_data)
        np.save(cardio_dir / "ecg_labels.npy", ecg_labels)
        
        log_download(f"[CARDIOLOGY] Generated {n_samples} ECG records")
        log_download(f"[CARDIOLOGY] Saved to: {cardio_dir}")
        
        return True
    except Exception as e:
        log_download(f"[CARDIOLOGY] ERROR: {str(e)}")
        return False

# ============================================================================
# DERMATOLOGY DATASETS
# ============================================================================

def download_dermatology_datasets():
    """Download/generate dermatology image datasets"""
    log_download("[DERMATOLOGY] Generating skin lesion datasets...")
    
    try:
        derm_dir = DATA_DIR / "dermatology"
        derm_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic image data
        n_samples = 3000  # ~3000 skin lesion images
        height, width = 224, 224
        channels = 3
        n_classes = 8
        
        # ISIC-like data
        images = np.random.randint(0, 256, (n_samples, height, width, channels), dtype=np.uint8)
        labels = np.random.randint(0, n_classes, n_samples)
        
        np.save(derm_dir / "isic_images.npy", images)
        np.save(derm_dir / "isic_labels.npy", labels)
        
        log_download(f"[DERMATOLOGY] Generated {n_samples} skin lesion images")
        log_download(f"[DERMATOLOGY] Saved to: {derm_dir}")
        
        return True
    except Exception as e:
        log_download(f"[DERMATOLOGY] ERROR: {str(e)}")
        return False

# ============================================================================
# RESPIRATORY DATASETS
# ============================================================================

def download_respiratory_datasets():
    """Download/generate respiratory imaging datasets"""
    log_download("[RESPIRATORY] Generating chest X-ray datasets...")
    
    try:
        resp_dir = DATA_DIR / "respiratory"
        resp_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic X-ray data
        n_samples = 2000  # ~2000 chest X-rays
        height, width = 256, 256
        channels = 3
        
        images = np.random.randint(0, 256, (n_samples, height, width, channels), dtype=np.uint8)
        labels = np.random.randint(0, 2, n_samples)  # Binary: Normal vs Pneumonia
        
        np.save(resp_dir / "pneumonia_images.npy", images)
        np.save(resp_dir / "pneumonia_labels.npy", labels)
        
        log_download(f"[RESPIRATORY] Generated {n_samples} chest X-ray images")
        log_download(f"[RESPIRATORY] Saved to: {resp_dir}")
        
        return True
    except Exception as e:
        log_download(f"[RESPIRATORY] ERROR: {str(e)}")
        return False

# ============================================================================
# ORTHOPEDICS DATASETS
# ============================================================================

def download_orthopedics_datasets():
    """Download/generate orthopedics imaging datasets"""
    log_download("[ORTHOPEDICS] Generating bone X-ray datasets...")
    
    try:
        ortho_dir = DATA_DIR / "orthopedics"
        ortho_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic X-ray data
        n_samples = 2000  # ~2000 bone X-rays
        height, width = 256, 256
        channels = 3
        
        images = np.random.randint(0, 256, (n_samples, height, width, channels), dtype=np.uint8)
        labels = np.random.randint(0, 2, n_samples)  # Binary: Normal vs Fracture
        
        np.save(ortho_dir / "mura_images.npy", images)
        np.save(ortho_dir / "mura_labels.npy", labels)
        
        log_download(f"[ORTHOPEDICS] Generated {n_samples} bone X-ray images")
        log_download(f"[ORTHOPEDICS] Saved to: {ortho_dir}")
        
        return True
    except Exception as e:
        log_download(f"[ORTHOPEDICS] ERROR: {str(e)}")
        return False

# ============================================================================
# GASTROENTEROLOGY DATASETS
# ============================================================================

def download_gastroenterology_datasets():
    """Download/generate gastroenterology datasets"""
    log_download("[GASTROENTEROLOGY] Generating GI disease datasets...")
    
    try:
        gastro_dir = DATA_DIR / "gastroenterology"
        gastro_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic clinical data
        n_samples = 800
        n_features = 25
        
        data = {
            f'feature_{i}': np.random.randn(n_samples) for i in range(n_features)
        }
        data['label'] = np.random.randint(0, 6, n_samples)
        
        df = pd.DataFrame(data)
        df.to_csv(gastro_dir / "gastro_clinical.csv", index=False)
        
        log_download(f"[GASTROENTEROLOGY] Generated {n_samples} clinical records")
        log_download(f"[GASTROENTEROLOGY] Saved to: {gastro_dir}")
        
        return True
    except Exception as e:
        log_download(f"[GASTROENTEROLOGY] ERROR: {str(e)}")
        return False

# ============================================================================
# GENERAL MEDICINE DATASETS
# ============================================================================

def download_general_medicine_datasets():
    """Download/generate general medicine datasets"""
    log_download("[GENERAL_MEDICINE] Generating multi-disease datasets...")
    
    try:
        general_dir = DATA_DIR / "general_medicine"
        general_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic clinical data
        n_samples = 1000
        n_features = 30
        
        data = {
            f'feature_{i}': np.random.randn(n_samples) for i in range(n_features)
        }
        data['label'] = np.random.randint(0, 5, n_samples)
        
        df = pd.DataFrame(data)
        df.to_csv(general_dir / "heart_disease.csv", index=False)
        
        log_download(f"[GENERAL_MEDICINE] Generated {n_samples} clinical records")
        log_download(f"[GENERAL_MEDICINE] Saved to: {general_dir}")
        
        return True
    except Exception as e:
        log_download(f"[GENERAL_MEDICINE] ERROR: {str(e)}")
        return False

# ============================================================================
# ROUTER DATASETS
# ============================================================================

def download_router_datasets():
    """Download/generate medical text routing datasets"""
    log_download("[ROUTER] Generating medical text datasets...")
    
    try:
        router_dir = DATA_DIR / "router"
        router_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic medical text data
        symptoms = [
            "chest pain and shortness of breath",
            "skin rash and itching",
            "persistent cough and fever",
            "joint pain and swelling",
            "digestive issues and bloating",
            "headache and fatigue"
        ]
        
        organs = ["cardiology", "dermatology", "respiratory", "orthopedics", "gastroenterology", "general"]
        
        n_samples = 2000
        texts = []
        labels = []
        
        for _ in range(n_samples):
            symptom = random.choice(symptoms)
            organ_idx = organs.index(random.choice(organs))
            texts.append(symptom)
            labels.append(organ_idx)
        
        df = pd.DataFrame({
            'text': texts,
            'label': labels
        })
        df.to_csv(router_dir / "medical_text_routing.csv", index=False)
        
        log_download(f"[ROUTER] Generated {n_samples} medical text samples")
        log_download(f"[ROUTER] Saved to: {router_dir}")
        
        return True
    except Exception as e:
        log_download(f"[ROUTER] ERROR: {str(e)}")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main download function"""
    log_download("="*80)
    log_download("MEDAI-PRO: MEDICAL DATASET DOWNLOADER")
    log_download("="*80)
    
    log_download("\nStarting dataset generation for all 7 specialties...\n")
    
    results = {
        'cardiology': download_cardiology_datasets(),
        'dermatology': download_dermatology_datasets(),
        'respiratory': download_respiratory_datasets(),
        'orthopedics': download_orthopedics_datasets(),
        'gastroenterology': download_gastroenterology_datasets(),
        'general_medicine': download_general_medicine_datasets(),
        'router': download_router_datasets(),
    }
    
    # Summary
    log_download("\n" + "="*80)
    log_download("DATASET GENERATION COMPLETE")
    log_download("="*80)
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for specialty, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        log_download(f"[{status}] {specialty}")
    
    log_download(f"\nTotal: {success_count}/{total_count} datasets ready")
    log_download(f"Data location: {DATA_DIR}")
    log_download(f"Log file: {LOG_FILE}")
    log_download("="*80)

if __name__ == "__main__":
    main()
