"""
Analytics System for MedAI-Pro
Tracks system metrics, model performance, and usage statistics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import json
from pathlib import Path
from loguru import logger


class AnalyticsTracker:
    """Tracks and analyzes system metrics"""
    
    def __init__(self, data_dir: str = "logs/analytics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory metrics
        self.diagnosis_counts = defaultdict(int)
        self.model_usage = defaultdict(int)
        self.user_activity = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.chat_metrics = defaultdict(int)
        
        # Load existing data
        self._load_metrics()
    
    def _load_metrics(self):
        """Load metrics from file"""
        metrics_file = self.data_dir / "metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                
                self.diagnosis_counts = defaultdict(int, data.get("diagnosis_counts", {}))
                self.model_usage = defaultdict(int, data.get("model_usage", {}))
                self.user_activity = defaultdict(int, data.get("user_activity", {}))
                self.error_counts = defaultdict(int, data.get("error_counts", {}))
                self.chat_metrics = defaultdict(int, data.get("chat_metrics", {}))
                
                logger.info("Analytics metrics loaded")
            except Exception as e:
                logger.error(f"Error loading metrics: {e}")
    
    def _save_metrics(self):
        """Save metrics to file"""
        metrics_file = self.data_dir / "metrics.json"
        try:
            data = {
                "diagnosis_counts": dict(self.diagnosis_counts),
                "model_usage": dict(self.model_usage),
                "user_activity": dict(self.user_activity),
                "error_counts": dict(self.error_counts),
                "chat_metrics": dict(self.chat_metrics),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def track_diagnosis(self, organ: str, diagnosis: str, confidence: float, user_id: int):
        """Track a diagnosis event"""
        self.diagnosis_counts[f"{organ}_{diagnosis}"] += 1
        self.model_usage[organ] += 1
        self.user_activity[str(user_id)] += 1
        
        # Save periodically
        if sum(self.diagnosis_counts.values()) % 10 == 0:
            self._save_metrics()
    
    def track_chat_message(self, user_id: int, intent: str, sentiment: str):
        """Track a chat message"""
        self.chat_metrics["total_messages"] += 1
        self.chat_metrics[f"intent_{intent}"] += 1
        self.chat_metrics[f"sentiment_{sentiment}"] += 1
        self.user_activity[str(user_id)] += 1
        
        if self.chat_metrics["total_messages"] % 10 == 0:
            self._save_metrics()
    
    def track_error(self, error_type: str, endpoint: str):
        """Track an error"""
        self.error_counts[f"{endpoint}_{error_type}"] += 1
        self._save_metrics()
    
    def track_response_time(self, endpoint: str, response_time: float):
        """Track API response time"""
        self.response_times[endpoint].append(response_time)
        
        # Keep only last 1000 entries per endpoint
        if len(self.response_times[endpoint]) > 1000:
            self.response_times[endpoint] = self.response_times[endpoint][-1000:]
    
    def get_dashboard_stats(self) -> Dict:
        """Get comprehensive dashboard statistics"""
        total_diagnoses = sum(self.diagnosis_counts.values())
        total_chats = self.chat_metrics.get("total_messages", 0)
        total_users = len(self.user_activity)
        total_errors = sum(self.error_counts.values())
        
        # Model usage breakdown
        model_usage_percent = {}
        if total_diagnoses > 0:
            for model, count in self.model_usage.items():
                model_usage_percent[model] = (count / total_diagnoses) * 100
        
        # Top diagnoses
        top_diagnoses = sorted(
            self.diagnosis_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Active users
        active_users = sorted(
            self.user_activity.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Average response times
        avg_response_times = {}
        for endpoint, times in self.response_times.items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
        
        return {
            "overview": {
                "total_diagnoses": total_diagnoses,
                "total_chat_messages": total_chats,
                "total_users": total_users,
                "total_errors": total_errors,
                "error_rate": (total_errors / max(total_diagnoses + total_chats, 1)) * 100
            },
            "model_usage": {
                "counts": dict(self.model_usage),
                "percentages": model_usage_percent
            },
            "top_diagnoses": [
                {"diagnosis": diag, "count": count}
                for diag, count in top_diagnoses
            ],
            "active_users": [
                {"user_id": user_id, "activity_count": count}
                for user_id, count in active_users
            ],
            "chat_metrics": dict(self.chat_metrics),
            "response_times": avg_response_times,
            "errors": dict(self.error_counts)
        }
    
    def get_model_performance(self, model_name: str) -> Dict:
        """Get performance metrics for a specific model"""
        usage_count = self.model_usage.get(model_name, 0)
        
        # Get diagnoses for this model
        model_diagnoses = {
            k: v for k, v in self.diagnosis_counts.items()
            if k.startswith(f"{model_name}_")
        }
        
        return {
            "model_name": model_name,
            "total_usage": usage_count,
            "diagnoses": model_diagnoses,
            "usage_percentage": (usage_count / max(sum(self.model_usage.values()), 1)) * 100
        }
    
    def get_time_series_data(self, days: int = 7) -> Dict:
        """Get time series data for the last N days"""
        # This would require storing timestamped data
        # For now, return placeholder structure
        return {
            "days": days,
            "data": {
                "diagnoses_per_day": [],
                "chats_per_day": [],
                "users_per_day": [],
                "errors_per_day": []
            }
        }
    
    def get_user_analytics(self, user_id: int) -> Dict:
        """Get analytics for a specific user"""
        activity_count = self.user_activity.get(str(user_id), 0)
        
        return {
            "user_id": user_id,
            "total_activity": activity_count,
            "diagnoses": 0,  # Would need to track separately
            "chat_messages": 0  # Would need to track separately
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.diagnosis_counts.clear()
        self.model_usage.clear()
        self.user_activity.clear()
        self.error_counts.clear()
        self.response_times.clear()
        self.chat_metrics.clear()
        self._save_metrics()
        logger.info("Analytics metrics reset")


# Global analytics tracker
analytics = AnalyticsTracker()


def get_analytics_dashboard() -> Dict:
    """Get complete analytics dashboard"""
    return analytics.get_dashboard_stats()


def get_model_analytics(model_name: str) -> Dict:
    """Get analytics for a specific model"""
    return analytics.get_model_performance(model_name)


def track_diagnosis_event(organ: str, diagnosis: str, confidence: float, user_id: int):
    """Track a diagnosis event"""
    analytics.track_diagnosis(organ, diagnosis, confidence, user_id)


def track_chat_event(user_id: int, intent: str, sentiment: str):
    """Track a chat event"""
    analytics.track_chat_message(user_id, intent, sentiment)


def track_error_event(error_type: str, endpoint: str):
    """Track an error event"""
    analytics.track_error(error_type, endpoint)


def track_response_time_event(endpoint: str, response_time: float):
    """Track response time"""
    analytics.track_response_time(endpoint, response_time)


__all__ = [
    'AnalyticsTracker',
    'analytics',
    'get_analytics_dashboard',
    'get_model_analytics',
    'track_diagnosis_event',
    'track_chat_event',
    'track_error_event',
    'track_response_time_event'
]

