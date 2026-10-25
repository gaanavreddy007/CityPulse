"""
CITYPULSE Reference and Simple Baseline Detectors.
Provides explicit baselines to establish comparative lower bounds:
1. MissingnessDetector: Specifically identifies missing observations (NaN).
2. StaticQuantileDetector: Static historical threshold baseline without temporal dynamics.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from .base import BaseAnomalyDetector

class MissingnessDetector(BaseAnomalyDetector):
    """
    Trivial reference detector for missing-data detection.
    Assigns anomaly score 1.0 if observation is missing (NaN), 0.0 otherwise.
    Demonstrates that missingness detection is distinct from numeric flow anomaly detection.
    """
    def __init__(self):
        super().__init__(model_name="Missingness_Detector")

    def fit(self, train_series: pd.Series) -> "MissingnessDetector":
        self.is_fitted = True
        self.threshold = 0.5
        self.threshold_percentile = 50.0
        return self

    def score(self, series: pd.Series) -> pd.Series:
        # Score is 1.0 for NaN, 0.0 for observed numbers
        scores = series.isnull().astype('float32')
        scores.name = "missingness_score"
        return scores

    def calibrate_threshold(self, val_series: pd.Series, contamination_rate: float = 0.01) -> float:
        self.threshold = 0.5
        self.threshold_percentile = 50.0
        return self.threshold

class StaticQuantileDetector(BaseAnomalyDetector):
    """
    Static empirical quantile detector.
    Does not model time-of-day, day-of-week, or rolling context.
    Scores anomalies as distance from training median normalized by IQR.
    """
    def __init__(self, eps: float = 1.0):
        super().__init__(model_name="Static_Quantile")
        self.eps = eps
        self.median = 0.0
        self.iqr = 1.0

    def fit(self, train_series: pd.Series) -> "StaticQuantileDetector":
        valid = train_series.dropna()
        if len(valid) == 0:
            raise ValueError("train_series contains no valid observations")
        self.median = float(valid.median())
        q75, q25 = np.percentile(valid.values, [75, 25])
        self.iqr = max(float(q75 - q25), self.eps)
        self.is_fitted = True
        return self

    def score(self, series: pd.Series) -> pd.Series:
        if not self.is_fitted:
            raise RuntimeError("StaticQuantileDetector must be fitted before scoring.")
        scores = pd.Series(np.nan, index=series.index, dtype='float32')
        valid_mask = series.notnull()
        diffs = np.abs(series.loc[valid_mask].values - self.median)
        scores.loc[valid_mask] = (diffs / self.iqr).astype('float32')
        return scores
