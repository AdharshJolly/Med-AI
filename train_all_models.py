#!/usr/bin/env python3
"""
MedAI-Pro Model Training Script
Trains all 7 AI models on downloaded datasets
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Color codes
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

def train_model(model_name, train_function, data_path):
    """Train a single model and return results"""
    print_header(f"Training {model_name}")
    print_info(f"Data path: {data_path}")
    
    start_time = time.time()
    
    try:
        # Check if data exists
        if not os.path.exists(data_path):
            print_error(f"Data not found at {data_path}")
            print_info("Please run download_and_prepare_datasets.py first")
            return None
        
        print_info("Starting training...")
        results = train_function(data_path)
        
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        print_success(f"Training completed in {minutes}m {seconds}s")
        
        if results and 'accuracy' in results:
            accuracy = results['accuracy'] * 100
            print_success(f"Final Accuracy: {accuracy:.2f}%")
            
            if accuracy >= 85:
                print_success(f"✓ Meets accuracy threshold (≥85%)")
            else:
                print_error(f"✗ Below accuracy threshold (≥85%)")
        
        return results
        
    except Exception as e:
        print_error(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print_header("MedAI-Pro Model Training")
    
    # Setup paths
    project_root = Path(__file__).parent
    data_dir = project_root / 'data'
    models_dir = project_root / 'models' / 'weights'
    logs_dir = project_root / 'logs'
    
    # Create directories
    models_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    print_info(f"Project root: {project_root}")
    print_info(f"Data directory: {data_dir}")
    print_info(f"Models directory: {models_dir}")
    print_info(f"Logs directory: {logs_dir}")
    print_info("\nThis process may take 2-4 hours depending on your hardware")
    print_info("GPU is highly recommended for faster training\n")
    
    # Ask for confirmation
    response = input(f"{YELLOW}Do you want to proceed? (yes/no): {RESET}").strip().lower()
    if response not in ['yes', 'y']:
        print_error("Training cancelled by user")
        return 1
    
    # Training results
    training_results = {}
    
    # 1. Train Cardiology Model
    print_header("1/7: Cardiology Model (ECG Classification)")
    print_info("Architecture: EfficientNet 1D-CNN")
    print_info("Dataset: PTB-XL")
    print_info("Target Accuracy: >85%")
    
    try:
        from models.cardiology_model import train_model as train_cardio
        results = train_model(
            "Cardiology Model",
            train_cardio,
            str(data_dir / 'ptb-xl')
        )
        training_results['cardiology'] = results
    except Exception as e:
        print_error(f"Failed to train cardiology model: {e}")
        training_results['cardiology'] = None
    
    # 2. Train Dermatology Model
    print_header("2/7: Dermatology Model (Skin Lesion Classification)")
    print_info("Architecture: EfficientNetB7")
    print_info("Dataset: HAM10000")
    print_info("Target Accuracy: >90%")
    
    try:
        from models.dermatology_model import train_model as train_derm
        results = train_model(
            "Dermatology Model",
            train_derm,
            str(data_dir / 'ham10000')
        )
        training_results['dermatology'] = results
    except Exception as e:
        print_error(f"Failed to train dermatology model: {e}")
        training_results['dermatology'] = None
    
    # 3. Train Respiratory Model
    print_header("3/7: Respiratory Model (Chest X-Ray Classification)")
    print_info("Architecture: DenseNet121")
    print_info("Dataset: NIH Chest X-Ray")
    print_info("Target Accuracy: >88%")
    
    try:
        from models.respiratory_model import train_model as train_resp
        results = train_model(
            "Respiratory Model",
            train_resp,
            str(data_dir / 'chest_xray')
        )
        training_results['respiratory'] = results
    except Exception as e:
        print_error(f"Failed to train respiratory model: {e}")
        training_results['respiratory'] = None
    
    # 4. Train Orthopedics Model
    print_header("4/7: Orthopedics Model (Bone X-Ray Classification)")
    print_info("Architecture: ResNet50")
    print_info("Dataset: MURA")
    print_info("Target Accuracy: >85%")
    
    try:
        from models.orthopedics_model import train_model as train_ortho
        results = train_model(
            "Orthopedics Model",
            train_ortho,
            str(data_dir / 'mura')
        )
        training_results['orthopedics'] = results
    except Exception as e:
        print_error(f"Failed to train orthopedics model: {e}")
        training_results['orthopedics'] = None
    
    # 5. Train Gastroenterology Model
    print_header("5/7: Gastroenterology Model (GI Condition Classification)")
    print_info("Architecture: XGBoost + TabNet Ensemble")
    print_info("Dataset: Synthetic GI Dataset")
    print_info("Target Accuracy: >85%")
    
    try:
        from models.gastro_model import train_model as train_gastro
        results = train_model(
            "Gastroenterology Model",
            train_gastro,
            str(data_dir / 'gi_symptoms.csv')
        )
        training_results['gastroenterology'] = results
    except Exception as e:
        print_error(f"Failed to train gastroenterology model: {e}")
        training_results['gastroenterology'] = None
    
    # 6. Train General Medicine Model
    print_header("6/7: General Medicine Model (Multi-Disease Classification)")
    print_info("Architecture: RandomForest + XGBoost Ensemble")
    print_info("Dataset: Synthetic General Medicine Dataset")
    print_info("Target Accuracy: >87%")
    
    try:
        from models.general_model import train_model as train_general
        results = train_model(
            "General Medicine Model",
            train_general,
            str(data_dir / 'disease_symptoms.csv')
        )
        training_results['general_medicine'] = results
    except Exception as e:
        print_error(f"Failed to train general medicine model: {e}")
        training_results['general_medicine'] = None
    
    # 7. Train Router Model
    print_header("7/7: Router Model (Intelligent Routing)")
    print_info("Architecture: BERT-based Classifier")
    print_info("Dataset: Synthetic Multi-Organ Symptoms")
    print_info("Target Accuracy: >90%")
    
    try:
        from models.router_model import train_model as train_router
        # Generate router training data
        print_info("Generating router training data...")
        from models.router_model import generate_training_data
        router_data_path = str(data_dir / 'router_training_data.csv')
        generate_training_data(router_data_path)
        
        results = train_model(
            "Router Model",
            train_router,
            router_data_path
        )
        training_results['router'] = results
    except Exception as e:
        print_error(f"Failed to train router model: {e}")
        training_results['router'] = None
    
    # Generate Summary Report
    print_header("Training Summary")
    
    successful = 0
    failed = 0
    total_accuracy = 0
    
    for model_name, results in training_results.items():
        if results and 'accuracy' in results:
            accuracy = results['accuracy'] * 100
            print_success(f"{model_name.capitalize()}: {accuracy:.2f}%")
            successful += 1
            total_accuracy += accuracy
        else:
            print_error(f"{model_name.capitalize()}: Failed")
            failed += 1
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{GREEN}Successful: {successful}/7{RESET}")
    print(f"{RED}Failed: {failed}/7{RESET}")
    
    if successful > 0:
        avg_accuracy = total_accuracy / successful
        print(f"{BLUE}Average Accuracy: {avg_accuracy:.2f}%{RESET}")
    
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Save results to JSON
    results_file = logs_dir / f'training_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(results_file, 'w') as f:
        json.dump(training_results, f, indent=2, default=str)
    
    print_success(f"Training results saved to: {results_file}")
    
    if successful == 7:
        print_success("\n🎉 All models trained successfully!")
        print_info("You can now start the application with: docker-compose up -d")
        return 0
    elif successful > 0:
        print_info(f"\n{successful} models trained successfully")
        print_error(f"{failed} models failed - check errors above")
        return 1
    else:
        print_error("\nAll training failed - please check your configuration")
        return 2

if __name__ == "__main__":
    sys.exit(main())

