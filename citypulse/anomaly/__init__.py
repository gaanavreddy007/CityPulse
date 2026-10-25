"""
CITYPULSE Anomaly Detection Subpackage.
Contains baseline detectors, metrics, and reproducible benchmark engines.
"""

from .base import BaseAnomalyDetector, AnomalyEvaluationResult
from .seasonal_mad import SeasonalMADDetector
from .rolling_zscore import RollingZScoreDetector
from .isolation_forest import IsolationForestDetector, extract_traffic_features
from .ecod import ECODDetector
from .baselines import MissingnessDetector, StaticQuantileDetector
from .spatial import SpatialCrossConsistencyDetector
from .metrics import compute_classification_metrics
from .benchmark import BenchmarkRunner, MASTER_SEEDS, get_default_models, partition_series

__all__ = [
    "BaseAnomalyDetector",
    "AnomalyEvaluationResult",
    "SeasonalMADDetector",
    "RollingZScoreDetector",
    "IsolationForestDetector",
    "extract_traffic_features",
    "ECODDetector",
    "MissingnessDetector",
    "StaticQuantileDetector",
    "SpatialCrossConsistencyDetector",
    "compute_classification_metrics",
    "BenchmarkRunner",
    "MASTER_SEEDS",
    "get_default_models",
    "partition_series"
]
