"""
Model Accuracy Validation and Metrics Checker for MedAI-Pro
Ensures all models meet 85-90% accuracy requirement
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error
)
from typing import Dict, List, Tuple, Optional
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from loguru import logger
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


class ModelAccuracyChecker:
    """Comprehensive model validation and metrics calculation"""
    
    def __init__(self, model_name: str, min_accuracy: float = 0.85):
        self.model_name = model_name
        self.min_accuracy = min_accuracy
        self.metrics = {}
        self.validation_passed = False
    
    def calculate_classification_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None,
        class_names: Optional[List[str]] = None
    ) -> Dict:
        """Calculate comprehensive classification metrics"""
        
        metrics = {
            'model_name': self.model_name,
            'timestamp': datetime.utcnow().isoformat(),
            'n_samples': len(y_true),
            'n_classes': len(np.unique(y_true))
        }
        
        # Basic metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision_macro'] = precision_score(y_true, y_pred, average='macro', zero_division=0)
        metrics['precision_weighted'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics['recall_macro'] = recall_score(y_true, y_pred, average='macro', zero_division=0)
        metrics['recall_weighted'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics['f1_macro'] = f1_score(y_true, y_pred, average='macro', zero_division=0)
        metrics['f1_weighted'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # ROC-AUC (if probabilities provided)
        if y_prob is not None:
            try:
                if len(np.unique(y_true)) == 2:
                    # Binary classification
                    metrics['roc_auc'] = roc_auc_score(y_true, y_prob[:, 1])
                else:
                    # Multi-class classification
                    metrics['roc_auc'] = roc_auc_score(
                        y_true, y_prob, multi_class='ovr', average='macro'
                    )
            except Exception as e:
                logger.warning(f"Could not calculate ROC-AUC: {e}")
                metrics['roc_auc'] = None
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # Per-class metrics
        if class_names is None:
            class_names = [f"Class_{i}" for i in range(len(np.unique(y_true)))]
        
        class_report = classification_report(
            y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
        )
        metrics['per_class_metrics'] = class_report
        
        # Sensitivity and Specificity for each class
        metrics['class_details'] = {}
        for i, class_name in enumerate(class_names):
            if i < len(cm):
                tp = cm[i, i]
                fp = cm[:, i].sum() - tp
                fn = cm[i, :].sum() - tp
                tn = cm.sum() - tp - fp - fn
                
                sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
                specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
                
                metrics['class_details'][class_name] = {
                    'sensitivity': sensitivity,
                    'specificity': specificity,
                    'true_positives': int(tp),
                    'false_positives': int(fp),
                    'true_negatives': int(tn),
                    'false_negatives': int(fn)
                }
        
        self.metrics = metrics
        return metrics
    
    def validate_accuracy_threshold(self) -> bool:
        """Check if model meets minimum accuracy requirement"""
        if 'accuracy' not in self.metrics:
            logger.error("Metrics not calculated yet")
            return False
        
        accuracy = self.metrics['accuracy']
        self.validation_passed = accuracy >= self.min_accuracy
        
        if self.validation_passed:
            logger.info(
                f"✅ {self.model_name} PASSED validation: "
                f"Accuracy = {accuracy:.2%} (Required: {self.min_accuracy:.2%})"
            )
        else:
            logger.error(
                f"❌ {self.model_name} FAILED validation: "
                f"Accuracy = {accuracy:.2%} (Required: {self.min_accuracy:.2%})"
            )
        
        return self.validation_passed
    
    def print_metrics_summary(self):
        """Print formatted metrics summary"""
        if not self.metrics:
            logger.warning("No metrics to display")
            return
        
        print("\n" + "="*70)
        print(f"MODEL PERFORMANCE REPORT: {self.model_name}")
        print("="*70)
        print(f"Samples: {self.metrics['n_samples']}")
        print(f"Classes: {self.metrics['n_classes']}")
        print("-"*70)
        print(f"Accuracy:           {self.metrics['accuracy']:.4f} ({self.metrics['accuracy']*100:.2f}%)")
        print(f"Precision (Macro):  {self.metrics['precision_macro']:.4f}")
        print(f"Recall (Macro):     {self.metrics['recall_macro']:.4f}")
        print(f"F1-Score (Macro):   {self.metrics['f1_macro']:.4f}")
        
        if self.metrics.get('roc_auc'):
            print(f"ROC-AUC:            {self.metrics['roc_auc']:.4f}")
        
        print("-"*70)
        print("Per-Class Performance:")
        for class_name, details in self.metrics.get('class_details', {}).items():
            print(f"  {class_name}:")
            print(f"    Sensitivity: {details['sensitivity']:.4f}")
            print(f"    Specificity: {details['specificity']:.4f}")
        
        print("="*70)
        
        # Validation status
        status = "✅ PASSED" if self.validation_passed else "❌ FAILED"
        print(f"Validation Status: {status}")
        print("="*70 + "\n")
    
    def save_metrics(self, filepath: str):
        """Save metrics to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        logger.info(f"Metrics saved to {filepath}")
    
    def plot_confusion_matrix(self, class_names: List[str], save_path: Optional[str] = None):
        """Plot confusion matrix heatmap"""
        if 'confusion_matrix' not in self.metrics:
            logger.warning("No confusion matrix to plot")
            return
        
        cm = np.array(self.metrics['confusion_matrix'])
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names
        )
        plt.title(f'Confusion Matrix - {self.model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confusion matrix saved to {save_path}")
        else:
            plt.show()
        
        plt.close()


class ModelValidator:
    """Validate all MedAI-Pro models"""
    
    def __init__(self):
        self.model_checkers = {}
        self.validation_results = {}
    
    def validate_model(
        self,
        model_name: str,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None,
        class_names: Optional[List[str]] = None,
        min_accuracy: float = 0.85
    ) -> Dict:
        """Validate a single model"""
        
        checker = ModelAccuracyChecker(model_name, min_accuracy)
        metrics = checker.calculate_classification_metrics(y_true, y_pred, y_prob, class_names)
        passed = checker.validate_accuracy_threshold()
        checker.print_metrics_summary()
        
        self.model_checkers[model_name] = checker
        self.validation_results[model_name] = {
            'passed': passed,
            'accuracy': metrics['accuracy'],
            'metrics': metrics
        }
        
        return metrics
    
    def validate_pytorch_model(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
        model_name: str = "PyTorch Model",
        class_names: Optional[List[str]] = None
    ) -> Dict:
        """Validate PyTorch model on a dataloader"""
        
        model.eval()
        model.to(device)
        
        all_preds = []
        all_labels = []
        all_probs = []
        
        with torch.no_grad():
            for inputs, labels in dataloader:
                inputs = inputs.to(device)
                labels = labels.to(device)
                
                outputs = model(inputs)
                
                if isinstance(outputs, tuple):
                    outputs = outputs[0]
                
                probs = torch.softmax(outputs, dim=1)
                preds = torch.argmax(probs, dim=1)
                
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())
        
        y_true = np.array(all_labels)
        y_pred = np.array(all_preds)
        y_prob = np.array(all_probs)
        
        return self.validate_model(model_name, y_true, y_pred, y_prob, class_names)
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report for all models"""
        
        report = "\n" + "="*80 + "\n"
        report += "MEDAI-PRO MODEL VALIDATION REPORT\n"
        report += "="*80 + "\n\n"
        
        total_models = len(self.validation_results)
        passed_models = sum(1 for r in self.validation_results.values() if r['passed'])
        
        report += f"Total Models Validated: {total_models}\n"
        report += f"Models Passed: {passed_models}\n"
        report += f"Models Failed: {total_models - passed_models}\n\n"
        
        report += "-"*80 + "\n"
        report += f"{'Model Name':<30} {'Accuracy':<15} {'Status':<15}\n"
        report += "-"*80 + "\n"
        
        for model_name, result in self.validation_results.items():
            accuracy = f"{result['accuracy']:.2%}"
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            report += f"{model_name:<30} {accuracy:<15} {status:<15}\n"
        
        report += "="*80 + "\n"
        
        if passed_models == total_models:
            report += "🎉 ALL MODELS PASSED VALIDATION! 🎉\n"
        else:
            report += "⚠️ SOME MODELS NEED IMPROVEMENT ⚠️\n"
        
        report += "="*80 + "\n"
        
        return report
    
    def save_validation_report(self, filepath: str):
        """Save validation report to file"""
        report = self.generate_validation_report()
        with open(filepath, 'w') as f:
            f.write(report)
        logger.info(f"Validation report saved to {filepath}")


if __name__ == "__main__":
    # Example usage
    validator = ModelValidator()
    
    # Simulate validation for demonstration
    np.random.seed(42)
    y_true = np.random.randint(0, 3, 1000)
    y_pred = y_true.copy()
    # Add some errors to simulate 88% accuracy
    error_indices = np.random.choice(1000, 120, replace=False)
    y_pred[error_indices] = np.random.randint(0, 3, 120)
    
    validator.validate_model(
        "Cardiology Model",
        y_true, y_pred,
        class_names=['Normal', 'Arrhythmia', 'MI']
    )
    
    print(validator.generate_validation_report())

