#!/usr/bin/env python3
"""
Simplified Dataset Download Script for MedAI-Pro
Downloads medical datasets with minimal dependencies
"""

import os
import sys
import zipfile
import requests
from pathlib import Path
from tqdm import tqdm
import json

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def print_info(text):
    print(f"{YELLOW}ℹ{RESET} {text}")

def download_file(url, destination, description="Downloading"):
    """Download a file with progress bar"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as f, tqdm(
            desc=description,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                pbar.update(size)
        
        return True
    except Exception as e:
        print_error(f"Download failed: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """Extract a zip file"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        print_error(f"Extraction failed: {e}")
        return False

def generate_synthetic_data(data_dir, dataset_name, num_samples=5000):
    """Generate synthetic medical data"""
    import numpy as np
    import pandas as pd
    
    print_info(f"Generating {num_samples} synthetic samples for {dataset_name}...")
    
    if dataset_name == "gastroenterology":
        # Generate GI symptoms data
        symptoms = ['abdominal_pain', 'nausea', 'vomiting', 'diarrhea', 'constipation', 
                   'bloating', 'heartburn', 'blood_in_stool', 'weight_loss', 'fever']
        
        data = {symptom: np.random.randint(0, 2, num_samples) for symptom in symptoms}
        data['age'] = np.random.randint(18, 80, num_samples)
        data['duration_days'] = np.random.randint(1, 30, num_samples)
        
        # Generate labels
        conditions = ['GERD', 'IBS', 'Gastritis', 'Ulcer', 'Colitis', 'Normal']
        data['diagnosis'] = np.random.choice(conditions, num_samples)
        
        df = pd.DataFrame(data)
        output_path = data_dir / dataset_name / 'synthetic_data.csv'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print_success(f"Generated {num_samples} GI samples at {output_path}")
        
    elif dataset_name == "general":
        # Generate general medicine data
        symptoms = ['fever', 'cough', 'fatigue', 'headache', 'body_ache', 
                   'sore_throat', 'runny_nose', 'shortness_of_breath', 'chills', 'loss_of_taste']
        
        data = {symptom: np.random.randint(0, 2, num_samples) for symptom in symptoms}
        data['age'] = np.random.randint(18, 80, num_samples)
        data['temperature'] = np.random.uniform(97.0, 103.0, num_samples)
        data['heart_rate'] = np.random.randint(60, 120, num_samples)
        
        # Generate labels
        conditions = ['Flu', 'COVID-19', 'Common Cold', 'Pneumonia', 'Bronchitis', 'Healthy']
        data['diagnosis'] = np.random.choice(conditions, num_samples)
        
        df = pd.DataFrame(data)
        output_path = data_dir / dataset_name / 'synthetic_data.csv'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print_success(f"Generated {num_samples} general medicine samples at {output_path}")
    
    return True

def download_ptbxl(data_dir):
    """Download PTB-XL ECG dataset"""
    print_header("Downloading PTB-XL ECG Dataset")
    
    ptbxl_dir = data_dir / 'cardiology' / 'ptb-xl'
    ptbxl_dir.mkdir(parents=True, exist_ok=True)
    
    url = "https://physionet.org/static/published-projects/ptb-xl/ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3.zip"
    zip_path = data_dir / 'ptb-xl.zip'
    
    print_info("Downloading PTB-XL dataset (800 MB)...")
    print_info("This may take 10-30 minutes depending on your internet speed")
    
    if download_file(url, zip_path, "PTB-XL"):
        print_success("Download complete!")
        print_info("Extracting files...")
        
        if extract_zip(zip_path, ptbxl_dir):
            print_success(f"PTB-XL dataset extracted to {ptbxl_dir}")
            zip_path.unlink()  # Delete zip file
            return True
    
    return False

def setup_kaggle_datasets(data_dir):
    """Setup instructions for Kaggle datasets"""
    print_header("Kaggle Datasets Setup")
    
    print_info("To download Kaggle datasets, you need to:")
    print_info("1. Create a Kaggle account at https://www.kaggle.com")
    print_info("2. Go to https://www.kaggle.com/settings/account")
    print_info("3. Click 'Create New API Token'")
    print_info("4. Save kaggle.json to ~/.kaggle/ (Linux/Mac) or C:\\Users\\YourName\\.kaggle\\ (Windows)")
    print_info("5. Install kaggle: pip install kaggle")
    print("")
    
    print_info("Required Kaggle datasets:")
    print_info("  - HAM10000: kaggle datasets download -d kmader/skin-cancer-mnist-ham10000")
    print_info("  - Chest X-Ray: kaggle datasets download -d paultimothymooney/chest-xray-pneumonia")
    print_info("  - MURA: kaggle datasets download -d kmader/mura-bone-xrays")
    print("")
    
    # Try to download with kaggle API if available
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        print_success("Kaggle API authenticated!")
        
        # Download HAM10000
        print_info("Downloading HAM10000 (Dermatology)...")
        derm_dir = data_dir / 'dermatology' / 'ham10000'
        derm_dir.mkdir(parents=True, exist_ok=True)
        api.dataset_download_files('kmader/skin-cancer-mnist-ham10000', path=str(derm_dir), unzip=True)
        print_success("HAM10000 downloaded!")
        
        # Download Chest X-Ray
        print_info("Downloading Chest X-Ray (Respiratory)...")
        resp_dir = data_dir / 'respiratory' / 'chest-xray'
        resp_dir.mkdir(parents=True, exist_ok=True)
        api.dataset_download_files('paultimothymooney/chest-xray-pneumonia', path=str(resp_dir), unzip=True)
        print_success("Chest X-Ray downloaded!")
        
        # Download MURA
        print_info("Downloading MURA (Orthopedics)...")
        ortho_dir = data_dir / 'orthopedics' / 'mura'
        ortho_dir.mkdir(parents=True, exist_ok=True)
        api.dataset_download_files('kmader/mura-bone-xrays', path=str(ortho_dir), unzip=True)
        print_success("MURA downloaded!")
        
        return True
        
    except ImportError:
        print_error("Kaggle API not installed. Install with: pip install kaggle")
        return False
    except Exception as e:
        print_error(f"Kaggle download failed: {e}")
        print_info("Please download manually and extract to data/ directory")
        return False

def main():
    print_header("MedAI-Pro Simplified Dataset Download")
    
    # Setup data directory
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    print_info(f"Data directory: {data_dir}")
    print("")
    
    # Track progress
    results = {}
    
    # 1. Download PTB-XL (doesn't require Kaggle)
    try:
        results['ptbxl'] = download_ptbxl(data_dir)
    except Exception as e:
        print_error(f"PTB-XL download failed: {e}")
        results['ptbxl'] = False
    
    # 2. Try Kaggle datasets
    try:
        results['kaggle'] = setup_kaggle_datasets(data_dir)
    except Exception as e:
        print_error(f"Kaggle setup failed: {e}")
        results['kaggle'] = False
    
    # 3. Generate synthetic data (always works)
    print_header("Generating Synthetic Datasets")
    
    try:
        results['gastro'] = generate_synthetic_data(data_dir, 'gastroenterology', 6000)
    except Exception as e:
        print_error(f"Gastro data generation failed: {e}")
        results['gastro'] = False
    
    try:
        results['general'] = generate_synthetic_data(data_dir, 'general', 6000)
    except Exception as e:
        print_error(f"General data generation failed: {e}")
        results['general'] = False
    
    # Summary
    print_header("Download Summary")
    
    for dataset, success in results.items():
        if success:
            print_success(f"{dataset}: Downloaded/Generated")
        else:
            print_error(f"{dataset}: Failed")
    
    print("")
    print_info("Next steps:")
    print_info("1. If Kaggle datasets failed, install kaggle API and configure credentials")
    print_info("2. Run: python simple_train_models.py")
    print("")

if __name__ == "__main__":
    main()

