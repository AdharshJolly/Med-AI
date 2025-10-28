"""
Model Versioning System for MedAI-Pro
Tracks model versions, performance metrics, and enables rollback
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
import hashlib


class ModelVersion:
    """Represents a single model version"""
    
    def __init__(
        self,
        model_name: str,
        version: str,
        file_path: str,
        metrics: Dict,
        metadata: Dict = None
    ):
        self.model_name = model_name
        self.version = version
        self.file_path = file_path
        self.metrics = metrics
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of model file"""
        if not Path(self.file_path).exists():
            return ""
        
        sha256_hash = hashlib.sha256()
        with open(self.file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "model_name": self.model_name,
            "version": self.version,
            "file_path": self.file_path,
            "metrics": self.metrics,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "checksum": self.checksum
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModelVersion':
        """Create from dictionary"""
        version = cls(
            model_name=data["model_name"],
            version=data["version"],
            file_path=data["file_path"],
            metrics=data["metrics"],
            metadata=data.get("metadata", {})
        )
        version.created_at = datetime.fromisoformat(data["created_at"])
        return version


class ModelVersionManager:
    """Manages model versions"""
    
    def __init__(self, versions_dir: str = "models/versions"):
        self.versions_dir = Path(versions_dir)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.versions_dir / "registry.json"
        self.versions: Dict[str, List[ModelVersion]] = {}
        self.active_versions: Dict[str, str] = {}
        
        self._load_registry()
    
    def _load_registry(self):
        """Load version registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                
                # Load versions
                for model_name, versions_data in data.get("versions", {}).items():
                    self.versions[model_name] = [
                        ModelVersion.from_dict(v) for v in versions_data
                    ]
                
                # Load active versions
                self.active_versions = data.get("active_versions", {})
                
                logger.info(f"Loaded {len(self.versions)} model version histories")
            except Exception as e:
                logger.error(f"Error loading registry: {e}")
                self.versions = {}
                self.active_versions = {}
        else:
            logger.info("No existing registry found, starting fresh")
    
    def _save_registry(self):
        """Save version registry to file"""
        try:
            data = {
                "versions": {
                    model_name: [v.to_dict() for v in versions]
                    for model_name, versions in self.versions.items()
                },
                "active_versions": self.active_versions,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info("Registry saved successfully")
        except Exception as e:
            logger.error(f"Error saving registry: {e}")
    
    def register_version(
        self,
        model_name: str,
        model_file: str,
        metrics: Dict,
        metadata: Dict = None,
        set_active: bool = True
    ) -> ModelVersion:
        """
        Register a new model version
        
        Args:
            model_name: Name of the model
            model_file: Path to model file
            metrics: Performance metrics
            metadata: Additional metadata
            set_active: Whether to set as active version
            
        Returns:
            ModelVersion object
        """
        # Generate version number
        if model_name not in self.versions:
            self.versions[model_name] = []
        
        version_num = len(self.versions[model_name]) + 1
        version_str = f"v{version_num}.0"
        
        # Create version directory
        version_dir = self.versions_dir / model_name / version_str
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy model file to version directory
        model_path = Path(model_file)
        versioned_file = version_dir / model_path.name
        shutil.copy2(model_file, versioned_file)
        
        # Create version object
        version = ModelVersion(
            model_name=model_name,
            version=version_str,
            file_path=str(versioned_file),
            metrics=metrics,
            metadata=metadata or {}
        )
        
        # Add to registry
        self.versions[model_name].append(version)
        
        # Set as active if requested
        if set_active:
            self.active_versions[model_name] = version_str
        
        # Save registry
        self._save_registry()
        
        logger.info(f"Registered {model_name} {version_str} with accuracy {metrics.get('accuracy', 'N/A')}")
        
        return version
    
    def get_version(self, model_name: str, version: str = None) -> Optional[ModelVersion]:
        """
        Get a specific model version
        
        Args:
            model_name: Name of the model
            version: Version string (defaults to active version)
            
        Returns:
            ModelVersion object or None
        """
        if model_name not in self.versions:
            return None
        
        if version is None:
            version = self.active_versions.get(model_name)
            if version is None:
                return None
        
        for v in self.versions[model_name]:
            if v.version == version:
                return v
        
        return None
    
    def get_all_versions(self, model_name: str) -> List[ModelVersion]:
        """Get all versions of a model"""
        return self.versions.get(model_name, [])
    
    def get_active_version(self, model_name: str) -> Optional[ModelVersion]:
        """Get the active version of a model"""
        return self.get_version(model_name)
    
    def set_active_version(self, model_name: str, version: str) -> bool:
        """
        Set a version as active
        
        Args:
            model_name: Name of the model
            version: Version string
            
        Returns:
            True if successful, False otherwise
        """
        # Check if version exists
        version_obj = self.get_version(model_name, version)
        if version_obj is None:
            logger.error(f"Version {version} not found for {model_name}")
            return False
        
        # Set as active
        self.active_versions[model_name] = version
        self._save_registry()
        
        logger.info(f"Set {model_name} active version to {version}")
        return True
    
    def rollback(self, model_name: str, steps: int = 1) -> Optional[ModelVersion]:
        """
        Rollback to a previous version
        
        Args:
            model_name: Name of the model
            steps: Number of versions to rollback
            
        Returns:
            New active ModelVersion or None
        """
        if model_name not in self.versions:
            logger.error(f"No versions found for {model_name}")
            return None
        
        versions = self.versions[model_name]
        if len(versions) < steps + 1:
            logger.error(f"Cannot rollback {steps} steps, only {len(versions)} versions available")
            return None
        
        # Get current active version index
        current_version = self.active_versions.get(model_name)
        current_index = -1
        for i, v in enumerate(versions):
            if v.version == current_version:
                current_index = i
                break
        
        if current_index == -1:
            current_index = len(versions) - 1
        
        # Calculate rollback index
        rollback_index = max(0, current_index - steps)
        rollback_version = versions[rollback_index]
        
        # Set as active
        self.set_active_version(model_name, rollback_version.version)
        
        logger.info(f"Rolled back {model_name} from {current_version} to {rollback_version.version}")
        
        return rollback_version
    
    def compare_versions(self, model_name: str, version1: str, version2: str) -> Dict:
        """
        Compare two versions of a model
        
        Args:
            model_name: Name of the model
            version1: First version
            version2: Second version
            
        Returns:
            Comparison dictionary
        """
        v1 = self.get_version(model_name, version1)
        v2 = self.get_version(model_name, version2)
        
        if v1 is None or v2 is None:
            return {"error": "One or both versions not found"}
        
        comparison = {
            "model_name": model_name,
            "version1": {
                "version": v1.version,
                "metrics": v1.metrics,
                "created_at": v1.created_at.isoformat()
            },
            "version2": {
                "version": v2.version,
                "metrics": v2.metrics,
                "created_at": v2.created_at.isoformat()
            },
            "metric_differences": {}
        }
        
        # Calculate metric differences
        for metric in v1.metrics:
            if metric in v2.metrics:
                diff = v2.metrics[metric] - v1.metrics[metric]
                comparison["metric_differences"][metric] = {
                    "v1": v1.metrics[metric],
                    "v2": v2.metrics[metric],
                    "difference": diff,
                    "improvement": diff > 0
                }
        
        return comparison
    
    def get_best_version(self, model_name: str, metric: str = "accuracy") -> Optional[ModelVersion]:
        """
        Get the best version based on a metric
        
        Args:
            model_name: Name of the model
            metric: Metric to compare
            
        Returns:
            Best ModelVersion or None
        """
        if model_name not in self.versions:
            return None
        
        versions = self.versions[model_name]
        if not versions:
            return None
        
        best_version = None
        best_value = float('-inf')
        
        for version in versions:
            if metric in version.metrics:
                value = version.metrics[metric]
                if value > best_value:
                    best_value = value
                    best_version = version
        
        return best_version
    
    def delete_version(self, model_name: str, version: str) -> bool:
        """
        Delete a model version
        
        Args:
            model_name: Name of the model
            version: Version to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Cannot delete active version
        if self.active_versions.get(model_name) == version:
            logger.error(f"Cannot delete active version {version}")
            return False
        
        # Find and remove version
        if model_name in self.versions:
            for i, v in enumerate(self.versions[model_name]):
                if v.version == version:
                    # Delete files
                    version_dir = Path(v.file_path).parent
                    if version_dir.exists():
                        shutil.rmtree(version_dir)
                    
                    # Remove from registry
                    del self.versions[model_name][i]
                    self._save_registry()
                    
                    logger.info(f"Deleted {model_name} {version}")
                    return True
        
        logger.error(f"Version {version} not found for {model_name}")
        return False


# Global version manager instance
version_manager = ModelVersionManager()


__all__ = ['ModelVersion', 'ModelVersionManager', 'version_manager']

