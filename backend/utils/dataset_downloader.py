"""
Automated Dataset Downloader for MedAI-Pro
Downloads all 6 medical datasets required for training organ-specific models
"""

import os
import sys
import zipfile
import tarfile
import gzip
import shutil
from pathlib import Path
from typing import Dict, List
import requests
from tqdm import tqdm
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import wfdb
import pandas as pd
import numpy as np
from loguru import logger

# Configure logger
logger.add("dataset_download.log", rotation="10 MB")

# Dataset configurations
DATASETS_CONFIG = {
    "cardiology": {
        "name": "PTB-XL ECG Dataset",
        "source": "physionet",
        "url": "https://physionet.org/static/published-projects/ptb-xl/ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3.zip",
        "path": "data/cardiology/ptb-xl",
        "size": "~800 MB",
        "records": 21837,
        "description": "12-lead ECG signals for cardiac arrhythmia classification"
    },
    "dermatology": {
        "name": "HAM10000 Skin Lesion Dataset",
        "source": "kaggle",
        "dataset_id": "kmader/skin-cancer-mnist-ham10000",
        "path": "data/dermatology/ham10000",
        "size": "~2.5 GB",
        "records": 10015,
        "description": "Dermatoscopic images of skin lesions (7 classes)"
    },
    "respiratory": {
        "name": "Chest X-Ray Pneumonia Dataset",
        "source": "kaggle",
        "dataset_id": "paultimothymooney/chest-xray-pneumonia",
        "path": "data/respiratory/chest-xray",
        "size": "~2.3 GB",
        "records": 5856,
        "description": "Chest X-ray images for pneumonia detection"
    },
    "orthopedics": {
        "name": "MURA Bone Fracture Dataset",
        "source": "stanford",
        "url": "https://cs.stanford.edu/group/mlgroup/mura-v1.1.zip",
        "path": "data/orthopedics/mura",
        "size": "~40 GB",
        "records": 40561,
        "description": "Musculoskeletal radiographs for abnormality detection"
    },
    "gastroenterology": {
        "name": "GI Symptoms Dataset",
        "source": "synthetic",
        "path": "data/gastroenterology/gi-symptoms",
        "size": "~50 MB",
        "records": 10000,
        "description": "Tabular data for GI condition classification"
    },
    "general": {
        "name": "Multi-Condition Medical Dataset",
        "source": "kaggle",
        "dataset_id": "itachi9604/disease-symptom-description-dataset",
        "path": "data/general/multi-condition",
        "size": "~5 MB",
        "records": 4920,
        "description": "Disease-symptom mapping for general diagnosis"
    }
}


class DatasetDownloader:
    """Automated medical dataset downloader"""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.kaggle_api = None
        
    def setup_kaggle(self):
        """Initialize Kaggle API"""
        try:
            self.kaggle_api = KaggleApi()
            self.kaggle_api.authenticate()
            logger.info("✅ Kaggle API authenticated successfully")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Kaggle authentication failed: {e}")
            logger.info("Please set up Kaggle API credentials: ~/.kaggle/kaggle.json")
            return False
    
    def download_file(self, url: str, destination: Path, chunk_size: int = 8192):
        """Download file with progress bar"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(destination, 'wb') as f, tqdm(
                desc=destination.name,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    size = f.write(chunk)
                    pbar.update(size)
            
            logger.info(f"✅ Downloaded: {destination}")
            return True
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return False
    
    def extract_archive(self, archive_path: Path, extract_to: Path):
        """Extract compressed archives"""
        try:
            extract_to.mkdir(parents=True, exist_ok=True)
            
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix in ['.tar', '.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_to)
            
            logger.info(f"✅ Extracted: {archive_path} -> {extract_to}")
            return True
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return False
    
    def download_ptbxl(self):
        """Download PTB-XL ECG dataset"""
        logger.info("📥 Downloading PTB-XL ECG Dataset...")
        config = DATASETS_CONFIG["cardiology"]
        dataset_path = self.base_path / config["path"]
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        # Download main dataset
        zip_path = dataset_path / "ptbxl.zip"
        if not zip_path.exists():
            self.download_file(config["url"], zip_path)
            self.extract_archive(zip_path, dataset_path)
        
        logger.info(f"✅ PTB-XL dataset ready at {dataset_path}")
        return dataset_path
    
    def download_ham10000(self):
        """Download HAM10000 skin lesion dataset"""
        logger.info("📥 Downloading HAM10000 Skin Lesion Dataset...")
        config = DATASETS_CONFIG["dermatology"]
        dataset_path = self.base_path / config["path"]
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        if not self.kaggle_api:
            if not self.setup_kaggle():
                logger.error("❌ Cannot download HAM10000 without Kaggle API")
                return None
        
        try:
            self.kaggle_api.dataset_download_files(
                config["dataset_id"],
                path=str(dataset_path),
                unzip=True
            )
            logger.info(f"✅ HAM10000 dataset ready at {dataset_path}")
            return dataset_path
        except Exception as e:
            logger.error(f"❌ HAM10000 download failed: {e}")
            return None
    
    def download_chest_xray(self):
        """Download Chest X-Ray pneumonia dataset"""
        logger.info("📥 Downloading Chest X-Ray Pneumonia Dataset...")
        config = DATASETS_CONFIG["respiratory"]
        dataset_path = self.base_path / config["path"]
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        if not self.kaggle_api:
            if not self.setup_kaggle():
                logger.error("❌ Cannot download Chest X-Ray without Kaggle API")
                return None
        
        try:
            self.kaggle_api.dataset_download_files(
                config["dataset_id"],
                path=str(dataset_path),
                unzip=True
            )
            logger.info(f"✅ Chest X-Ray dataset ready at {dataset_path}")
            return dataset_path
        except Exception as e:
            logger.error(f"❌ Chest X-Ray download failed: {e}")
            return None
    
    def download_mura(self):
        """Download MURA bone fracture dataset"""
        logger.info("📥 Downloading MURA Dataset...")
        logger.warning("⚠️ MURA requires Stanford ML Group agreement")
        logger.info("Please download manually from: https://stanfordmlgroup.github.io/competitions/mura/")
        
        config = DATASETS_CONFIG["orthopedics"]
        dataset_path = self.base_path / config["path"]
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        # Create placeholder
        readme = dataset_path / "README.txt"
        readme.write_text(
            "MURA Dataset\n"
            "Please download from: https://stanfordmlgroup.github.io/competitions/mura/\n"
            "Extract to this directory after obtaining access."
        )
        
        return dataset_path
    
    def generate_gi_dataset(self):
        """Generate synthetic GI symptoms dataset"""
        logger.info("📥 Generating GI Symptoms Dataset...")
        config = DATASETS_CONFIG["gastroenterology"]
        dataset_path = self.base_path / config["path"]
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic tabular data
        np.random.seed(42)
        n_samples = 10000
        
        data = {
            'age': np.random.randint(18, 85, n_samples),
            'gender': np.random.choice(['M', 'F'], n_samples),
            'abdominal_pain': np.random.randint(0, 11, n_samples),
            'nausea': np.random.randint(0, 11, n_samples),
            'vomiting': np.random.randint(0, 11, n_samples),
            'diarrhea': np.random.randint(0, 11, n_samples),
            'constipation': np.random.randint(0, 11, n_samples),
            'bloating': np.random.randint(0, 11, n_samples),
            'heartburn': np.random.randint(0, 11, n_samples),
            'weight_loss': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            'blood_in_stool': np.random.choice([0, 1], n_samples, p=[0.85, 0.15]),
            'fever': np.random.choice([0, 1], n_samples, p=[0.75, 0.25]),
            'diagnosis': np.random.choice([
                'GERD', 'IBS', 'Gastritis', 'Peptic Ulcer', 'Crohns Disease',
                'Ulcerative Colitis', 'Celiac Disease', 'Pancreatitis', 'Normal'
            ], n_samples)
        }
        
        df = pd.DataFrame(data)
        df.to_csv(dataset_path / "gi_symptoms.csv", index=False)
        
        logger.info(f"✅ GI Symptoms dataset generated at {dataset_path}")
        return dataset_path
    
    def download_disease_symptom(self):
        """Download disease-symptom dataset"""
        logger.info("📥 Downloading Disease-Symptom Dataset...")
        config = DATASETS_CONFIG["general"]
        dataset_path = self.base_path / config["path"]
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        if not self.kaggle_api:
            if not self.setup_kaggle():
                logger.error("❌ Cannot download without Kaggle API")
                return None
        
        try:
            self.kaggle_api.dataset_download_files(
                config["dataset_id"],
                path=str(dataset_path),
                unzip=True
            )
            logger.info(f"✅ Disease-Symptom dataset ready at {dataset_path}")
            return dataset_path
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return None
    
    def download_all(self):
        """Download all datasets"""
        logger.info("🚀 Starting download of all medical datasets...")
        
        results = {
            "cardiology": self.download_ptbxl(),
            "dermatology": self.download_ham10000(),
            "respiratory": self.download_chest_xray(),
            "orthopedics": self.download_mura(),
            "gastroenterology": self.generate_gi_dataset(),
            "general": self.download_disease_symptom()
        }
        
        logger.info("\n" + "="*60)
        logger.info("📊 Dataset Download Summary:")
        for name, path in results.items():
            status = "✅" if path else "❌"
            logger.info(f"{status} {name.capitalize()}: {path}")
        logger.info("="*60)
        
        return results


if __name__ == "__main__":
    downloader = DatasetDownloader()
    downloader.download_all()

