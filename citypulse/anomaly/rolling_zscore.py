"""
CITYPULSE Rolling-Window Z-Score Anomaly Detector.
Evaluates flow anomalies relative to a strictly causal, retrospective rolling window.
Zero future leakage: uses past observations strictly (t-W to t-1).
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from .base import BaseAnomalyDetector

class RollingZScoreDetector(BaseAnomalyDetector):
    """
    Rolling-Window Z-Score Anomaly Detector.
    
    Attributes:
        window_size: Length of past rolling window in hours (default 168h = 1 week).
        min_periods: Minimum valid observations required in window (default 12).
        eps: Minimum standard deviation floor to avoid division by zero (default 1.0 veh/hr).
    """
    def __init__(
        self,
        window_size: int = 168,
        min_periods: int = 12,
        eps: float = 1.0
    ):
        super().__init__(model_name="Rolling_ZScore")
        self.window_size = window_size
        self.min_periods = min_periods
        self.eps = eps
        
        self.train_mean: float = 0.0
        self.train_std: float = 1.0

    def fit(self, train_series: pd.Series) -> "RollingZScoreDetector":
        """
        Fits global baseline parameters on historical training data.
        These parameters serve as the fallback when the rolling retrospective window is sparse.
        """
        valid_series = train_series.dropna()
        if len(valid_series) == 0:
            raise ValueError("train_series contains no valid observations")

        self.train_mean = float(valid_series.mean())
        self.train_std = max(float(valid_series.std()), self.eps)
        self.is_fitted = True
        return self

    def score(self, series: pd.Series) -> pd.Series:
        """
        Computes causal rolling Z-score:
            s_t = |y_t - mu_{t-1}| / max(sigma_{t-1}, eps)
        Where mu and sigma are computed on the preceding window [t - W, t - 1].
        Missing observations (NaN) remain NaN in output scores.
        """
        if not self.is_fitted:
            raise RuntimeError("RollingZScoreDetector must be fitted before scoring.")

        # Shift by 1 to guarantee strictly causal retrospective calculation (no lookahead!)
        shifted = series.shift(1)
        rolling_mean = shifted.rolling(window=self.window_size, min_periods=self.min_periods).mean()
        rolling_std = shifted.rolling(window=self.window_size, min_periods=self.min_periods).std()

        # Identify where fallback to training mean/std is necessary
        fallback_mask = rolling_mean.isnull() | rolling_std.isnull()
        
        effective_mean = rolling_mean.copy()
        effective_std = rolling_std.copy()
        
        effective_mean[fallback_mask] = self.train_mean
        effective_std[fallback_mask] = self.train_std
        
        # Enforce epsilon floor
        effective_std = np.maximum(effective_std.values, self.eps)

        scores = pd.Series(np.nan, index=series.index, dtype='float32')
        valid_mask = series.notnull()
        
        valid_y = series.loc[valid_mask].values
        valid_mu = effective_mean[valid_mask].values
        valid_sigma = effective_std[valid_mask]
        
        computed_scores = (np.abs(valid_y - valid_mu) / valid_sigma).astype('float32')
        scores.loc[valid_mask] = computed_scores

        # Track fallback statistics
        n_evals = len(valid_y)
        fallback_count = int((valid_mask & fallback_mask).sum())
        self.fallback_counts["invocations"] += fallback_count
        self.fallback_counts["total_evaluations"] += n_evals

        return scores
