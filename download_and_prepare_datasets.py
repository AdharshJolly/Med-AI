#!/usr/bin/env python3
"""
MedAI-Pro Dataset Download and Preparation Script
Downloads all 6 medical datasets and prepares them for training
"""

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so 'backend' package can be imported
sys.path.insert(0, str(Path(__file__).parent))

# Prefer importing from the backend package; fall back to adjusting sys.path if necessary
try:
    from backend.utils.dataset_downloader import DatasetDownloader
except Exception:
    # Fallback: add backend directory to sys.path and import using full package path
    backend_utils_path = str(Path(__file__).parent / 'backend' / 'utils')
    if backend_utils_path not in sys.path:
        sys.path.insert(0, backend_utils_path)
    from dataset_downloader import DatasetDownloader

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

def main():
    print_header("MedAI-Pro Dataset Download and Preparation")
    
    # Initialize downloader
    data_dir = Path(__file__).parent / 'data'
    downloader = DatasetDownloader(str(data_dir))
    
    print_info(f"Data directory: {data_dir}")
    print_info("This process may take 30-60 minutes depending on your internet speed")
    print_info("Total download size: ~10-15 GB\n")
    
    # Ask for confirmation
    response = input(f"{YELLOW}Do you want to proceed? (yes/no): {RESET}").strip().lower()
    if response not in ['yes', 'y']:
        print_error("Download cancelled by user")
        return 1
    
    datasets_status = {}
    
    # 1. Download PTB-XL ECG Dataset
    print_header("1/6: Downloading PTB-XL ECG Dataset")
    print_info("Source: PhysioNet")
    print_info("Size: ~2 GB")
    print_info("Description: 21,837 ECG recordings from 18,885 patients")
    try:
        downloader.download_ptbxl()
        print_success("PTB-XL dataset downloaded successfully!")
        datasets_status['PTB-XL'] = True
    except Exception as e:
        print_error(f"Failed to download PTB-XL: {e}")
        datasets_status['PTB-XL'] = False
    
    # 2. Download HAM10000 Skin Lesion Dataset
    print_header("2/6: Downloading HAM10000 Skin Lesion Dataset")
    print_info("Source: Kaggle")
    print_info("Size: ~1 GB")
    print_info("Description: 10,015 dermatoscopic images of skin lesions")
    print_info("Note: Requires Kaggle API credentials (kaggle.json)")
    try:
        downloader.download_ham10000()
        print_success("HAM10000 dataset downloaded successfully!")
        datasets_status['HAM10000'] = True
    except Exception as e:
        print_error(f"Failed to download HAM10000: {e}")
        print_info("Make sure you have kaggle.json in ~/.kaggle/ directory")
        datasets_status['HAM10000'] = False
    
    # 3. Download NIH Chest X-Ray Dataset
    print_header("3/6: Downloading NIH Chest X-Ray Dataset")
    print_info("Source: Kaggle")
    print_info("Size: ~1.2 GB (sample)")
    print_info("Description: Chest X-ray images for pneumonia detection")
    print_info("Note: Requires Kaggle API credentials")
    try:
        downloader.download_chest_xray()
        print_success("NIH Chest X-Ray dataset downloaded successfully!")
        datasets_status['Chest X-Ray'] = True
    except Exception as e:
        print_error(f"Failed to download Chest X-Ray: {e}")
        datasets_status['Chest X-Ray'] = False
    
    # 4. Download MURA Bone X-Ray Dataset
    print_header("4/6: Downloading MURA Bone X-Ray Dataset")
    print_info("Source: Stanford ML Group")
    print_info("Size: ~6 GB")
    print_info("Description: 40,561 musculoskeletal radiographs")
    try:
        downloader.download_mura()
        print_success("MURA dataset downloaded successfully!")
        datasets_status['MURA'] = True
    except Exception as e:
        print_error(f"Failed to download MURA: {e}")
        print_info("You may need to manually download from Stanford ML Group")
        datasets_status['MURA'] = False
    
    # 5. Generate Synthetic GI Dataset
    print_header("5/6: Generating Synthetic GI Dataset")
    print_info("Generating 6,000 synthetic samples")
    print_info("Conditions: 9 GI conditions")
    try:
        downloader.generate_gi_dataset()
        print_success("Synthetic GI dataset generated successfully!")
        datasets_status['GI Synthetic'] = True
    except Exception as e:
        print_error(f"Failed to generate GI dataset: {e}")
        datasets_status['GI Synthetic'] = False
    
    # 6. Generate Synthetic General Medicine Dataset
    print_header("6/6: Generating Synthetic General Medicine Dataset")
    print_info("Generating 6,000 synthetic samples")
    print_info("Conditions: 16 common diseases")
    try:
        downloader.generate_general_medicine_dataset()
        print_success("Synthetic General Medicine dataset generated successfully!")
        datasets_status['General Medicine Synthetic'] = True
    except Exception as e:
        print_error(f"Failed to generate General Medicine dataset: {e}")
        datasets_status['General Medicine Synthetic'] = False
    
    # Summary
    print_header("Download Summary")
    
    successful = sum(1 for status in datasets_status.values() if status)
    total = len(datasets_status)
    
    for dataset, status in datasets_status.items():
        if status:
            print_success(f"{dataset}: Downloaded/Generated")
        else:
            print_error(f"{dataset}: Failed")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{GREEN}Successful: {successful}/{total}{RESET}")
    print(f"{RED}Failed: {total - successful}/{total}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    if successful == total:
        print_success("All datasets downloaded successfully!")
        print_info("You can now proceed to train the models")
        print_info("Run: python train_all_models.py")
        return 0
    elif successful > 0:
        print_info(f"{successful} datasets downloaded successfully")
        print_info("You can train models with available datasets")
        print_error(f"{total - successful} datasets failed - check errors above")
        return 1
    else:
        print_error("All downloads failed - please check your configuration")
        return 2

if __name__ == "__main__":
    sys.exit(main())

