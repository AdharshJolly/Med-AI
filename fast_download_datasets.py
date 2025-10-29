#!/usr/bin/env python3
"""
Fast Parallel Dataset Download for MedAI-Pro
Downloads multiple datasets simultaneously for faster completion
"""

import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configuration
DATA_DIR = Path("data/production")
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("FAST PARALLEL DATASET DOWNLOAD")
print("Target: 30,000+ cases per organ")
print("=" * 80)

# Dataset configurations
DATASETS = [
    # Cardiology (already downloaded)
    # {
    #     "name": "Cardiology - PTB-XL",
    #     "kaggle_id": "khyeh0719/ptb-xl-dataset",
    #     "output_dir": DATA_DIR / "cardiology" / "ptb-xl",
    #     "priority": 1
    # },
    {
        "name": "Cardiology - MIT-BIH",
        "kaggle_id": "shayanfazeli/heartbeat",
        "output_dir": DATA_DIR / "cardiology" / "mit-bih",
        "priority": 1
    },
    
    # Dermatology
    {
        "name": "Dermatology - HAM10000",
        "kaggle_id": "kmader/skin-cancer-mnist-ham10000",
        "output_dir": DATA_DIR / "dermatology" / "ham10000",
        "priority": 2
    },
    {
        "name": "Dermatology - ISIC 2019",
        "kaggle_id": "nodoubttome/skin-cancer9-classesisic",
        "output_dir": DATA_DIR / "dermatology" / "isic2019",
        "priority": 2
    },
    {
        "name": "Dermatology - Melanoma",
        "kaggle_id": "hasnainjaved/melanoma-skin-cancer-dataset-of-10000-images",
        "output_dir": DATA_DIR / "dermatology" / "melanoma",
        "priority": 2
    },
    
    # Respiratory
    {
        "name": "Respiratory - Pneumonia",
        "kaggle_id": "paultimothymooney/chest-xray-pneumonia",
        "output_dir": DATA_DIR / "respiratory" / "pneumonia",
        "priority": 3
    },
    {
        "name": "Respiratory - COVID-19",
        "kaggle_id": "tawsifurrahman/covid19-radiography-database",
        "output_dir": DATA_DIR / "respiratory" / "covid19",
        "priority": 3
    },
    
    # Orthopedics
    {
        "name": "Orthopedics - Fracture",
        "kaggle_id": "vuppalaadithyasairam/bone-fracture-detection-using-xrays",
        "output_dir": DATA_DIR / "orthopedics" / "fracture",
        "priority": 4
    },
    {
        "name": "Orthopedics - MURA",
        "kaggle_id": "kmader/mura-bone-xrays",
        "output_dir": DATA_DIR / "orthopedics" / "mura",
        "priority": 4
    },
    
    # Gastroenterology
    {
        "name": "Gastroenterology - Diabetes",
        "kaggle_id": "alexteboul/diabetes-health-indicators-dataset",
        "output_dir": DATA_DIR / "gastroenterology" / "diabetes",
        "priority": 5
    },
    {
        "name": "Gastroenterology - Liver",
        "kaggle_id": "uciml/indian-liver-patient-records",
        "output_dir": DATA_DIR / "gastroenterology" / "liver",
        "priority": 5
    },
    
    # General Medicine
    {
        "name": "General Medicine - Heart Disease",
        "kaggle_id": "johnsmith88/heart-disease-dataset",
        "output_dir": DATA_DIR / "general_medicine" / "heart",
        "priority": 6
    },
    {
        "name": "General Medicine - Stroke",
        "kaggle_id": "fedesoriano/stroke-prediction-dataset",
        "output_dir": DATA_DIR / "general_medicine" / "stroke",
        "priority": 6
    },
]

def download_dataset(dataset_info):
    """Download a single dataset"""
    name = dataset_info["name"]
    kaggle_id = dataset_info["kaggle_id"]
    output_dir = dataset_info["output_dir"]
    
    print(f"\n[DOWNLOADING] {name}")
    print(f"  Dataset: {kaggle_id}")
    print(f"  Output: {output_dir}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Check if already downloaded
        files = list(output_dir.glob("**/*"))
        if len(files) > 10:  # Already has files
            print(f"  ✓ {name} already downloaded ({len(files)} files)")
            return {"name": name, "status": "ALREADY_DOWNLOADED", "files": len(files)}
        
        # Download using Kaggle CLI
        cmd = f'kaggle datasets download -d {kaggle_id} -p "{output_dir}" --unzip'
        
        start_time = time.time()
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            files = list(output_dir.glob("**/*"))
            file_count = len([f for f in files if f.is_file()])
            size = sum(f.stat().st_size for f in files if f.is_file()) / 1e9
            
            print(f"  ✓ {name} downloaded successfully")
            print(f"    Files: {file_count:,}")
            print(f"    Size: {size:.2f} GB")
            print(f"    Time: {elapsed:.1f}s")
            
            return {
                "name": name,
                "status": "SUCCESS",
                "files": file_count,
                "size_gb": size,
                "time_seconds": elapsed
            }
        else:
            print(f"  ✗ {name} failed")
            print(f"    Error: {result.stderr}")
            return {"name": name, "status": "FAILED", "error": result.stderr}
            
    except Exception as e:
        print(f"  ✗ {name} error: {e}")
        return {"name": name, "status": "ERROR", "error": str(e)}

# Download datasets in parallel (3 at a time to avoid overwhelming the system)
print("\nStarting parallel downloads (3 concurrent)...")
print("-" * 80)

results = []
with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit all download tasks
    future_to_dataset = {
        executor.submit(download_dataset, dataset): dataset 
        for dataset in DATASETS
    }
    
    # Process completed downloads
    for future in as_completed(future_to_dataset):
        dataset = future_to_dataset[future]
        try:
            result = future.result()
            results.append(result)
        except Exception as e:
            print(f"  ✗ {dataset['name']} exception: {e}")
            results.append({"name": dataset['name'], "status": "EXCEPTION", "error": str(e)})

# Summary
print("\n" + "=" * 80)
print("DOWNLOAD SUMMARY")
print("=" * 80)

successful = [r for r in results if r["status"] in ["SUCCESS", "ALREADY_DOWNLOADED"]]
failed = [r for r in results if r["status"] not in ["SUCCESS", "ALREADY_DOWNLOADED"]]

print(f"\n✓ Successful: {len(successful)}/{len(results)}")
print(f"✗ Failed: {len(failed)}/{len(results)}")

if successful:
    print("\nSuccessful Downloads:")
    total_files = 0
    total_size = 0
    for r in successful:
        files = r.get("files", 0)
        size = r.get("size_gb", 0)
        total_files += files
        total_size += size
        print(f"  ✓ {r['name']}: {files:,} files, {size:.2f} GB")
    
    print(f"\nTotal: {total_files:,} files, {total_size:.2f} GB")

if failed:
    print("\nFailed Downloads:")
    for r in failed:
        print(f"  ✗ {r['name']}: {r.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
print("✓ Download process complete!")
print("Next: Run train_production_models.py to train all models")
print("=" * 80)

