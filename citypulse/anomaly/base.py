"""
CITYPULSE Anomaly Detection Base Interface and Data Structures.
Defines unified contracts for fitting, threshold calibration, scoring,
and explicit missing-value and fallback reporting.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import pandas as pd

@dataclass
class AnomalyEvaluationResult:
    """Encapsulates model outputs, anomaly scores, and binary predictions."""
    model_name: str
    scores: pd.Series
    predictions: pd.Series
    threshold: float
    threshold_percentile: float
    fallback_report: Dict[str, Any] = field(default_factory=dict)
    runtime_seconds: float = 0.0

class BaseAnomalyDetector(ABC):
    """
    Abstract Base Class for CITYPULSE Anomaly Detectors.
    
    Guarantees:
    1. Pure historical training: fit() operates solely on historical training data.
    2. Zero test leakage: calibrate_threshold() selects decision thresholds on validation data.
    3. Explicit missingness: missing values (NaN) yield NaN anomaly scores in numeric models;
       never silently imputed as zero traffic.
    4. Transparent fallbacks: records whenever sparse history triggers a fallback profile.
    """
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.is_fitted = False
        self.threshold: Optional[float] = None
        self.threshold_percentile: Optional[float] = None
        self.fallback_counts = {"invocations": 0, "total_evaluations": 0}

    @abstractmethod
    def fit(self, train_series: pd.Series) -> "BaseAnomalyDetector":
        """
        Fits baseline parameters on historical training data (t <= 2021-09-30).
        Missing values (NaN) must be handled explicitly without silent zero-imputation.
        """
        pass

    @abstractmethod
    def score(self, series: pd.Series) -> pd.Series:
        """
        Computes continuous anomaly scores where higher values indicate greater anomaly.
        Returns a pd.Series with identical index to input.
        Missing values (NaN) in input must yield NaN in output for numeric detectors.
        """
        pass

    def calibrate_threshold(
        self,
        val_series: pd.Series,
        contamination_rate: float = 0.01
    ) -> float:
        """
        Selects anomaly decision threshold on uncorrupted validation data.
        Never accesses test data or test labels.
        Threshold is set to the (1 - contamination_rate) quantile of valid scores.
        """
        if not self.is_fitted:
            raise RuntimeError(f"Model {self.model_name} must be fitted before threshold calibration.")
        
        if not (0.0 < contamination_rate < 1.0):
            raise ValueError(f"contamination_rate must be in (0, 1), got {contamination_rate}")

        val_scores = self.score(val_series)
        valid_scores = val_scores.dropna()
        
        if len(valid_scores) == 0:
            raise ValueError(f"No valid scores computed on validation series for {self.model_name}")

        percentile = (1.0 - contamination_rate) * 100.0
        self.threshold = float(np.percentile(valid_scores.values, percentile))
        self.threshold_percentile = percentile
        return self.threshold

    def predict(
        self,
        series: pd.Series,
        threshold: Optional[float] = None
    ) -> pd.Series:
        """
        Generates binary anomaly predictions (1 = anomaly, 0 = normal).
        If input timestamp is NaN, output is NaN (int or float pd.Series).
        """
        scores = self.score(series)
        th = threshold if threshold is not None else self.threshold
        if th is None:
            raise RuntimeError(f"Threshold has not been calibrated for {self.model_name}. Call calibrate_threshold first.")

        # Binary prediction: 1 if score >= threshold, 0 if score < threshold, NaN if score is NaN
        preds = pd.Series(np.nan, index=series.index, dtype='float32')
        valid_mask = scores.notnull()
        preds.loc[valid_mask] = (scores.loc[valid_mask] >= th).astype('float32')
        return preds

    def fallback_usage_report(self) -> Dict[str, Any]:
        """Returns statistics on fallback usage during fitting or scoring."""
        total = max(1, self.fallback_counts.get("total_evaluations", 0))
        invocations = self.fallback_counts.get("invocations", 0)
        return {
            "model_name": self.model_name,
            "fallback_invocations": invocations,
            "total_evaluations": total,
            "fallback_rate_pct": round((invocations / total) * 100.0, 2)
        }
