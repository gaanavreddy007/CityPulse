"""
CITYPULSE Isolation Forest Anomaly Detector.
Wraps PyOD IForest with temporal and cyclical traffic feature engineering.
Enforces zero test leakage and explicit missing-value handling.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from pyod.models.iforest import IForest

from .base import BaseAnomalyDetector

def extract_traffic_features(series: pd.Series) -> pd.DataFrame:
    """
    Extracts cyclical temporal and differential features from hourly flow series.
    Features:
        - flow: current vehicle flow count (veh/hr)
        - hour_sin, hour_cos: cyclical 24-hour time-of-day encoding
        - day_sin, day_cos: cyclical 7-day day-of-week encoding
        - diff_1h: short-term lag difference (y_t - y_{t-1})
        - diff_24h: daily seasonal lag difference (y_t - y_{t-24})
    """
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Input series must have a DatetimeIndex")
        
    df = pd.DataFrame(index=series.index)
    df['flow'] = series.astype('float32')
    
    hours = series.index.hour.values
    days = series.index.dayofweek.values
    
    df['hour_sin'] = np.sin(2.0 * np.pi * hours / 24.0).astype('float32')
    df['hour_cos'] = np.cos(2.0 * np.pi * hours / 24.0).astype('float32')
    df['day_sin'] = np.sin(2.0 * np.pi * days / 7.0).astype('float32')
    df['day_cos'] = np.cos(2.0 * np.pi * days / 7.0).astype('float32')
    
    # Strictly causal retrospective differences
    df['diff_1h'] = (series - series.shift(1)).fillna(0.0).astype('float32')
    df['diff_24h'] = (series - series.shift(24)).fillna(0.0).astype('float32')
    
    return df

class IsolationForestDetector(BaseAnomalyDetector):
    """
    Isolation Forest Detector for multidimensional traffic anomaly scoring.
    
    Attributes:
        n_estimators: Number of isolation trees (default 100).
        random_state: Configurable RNG seed for reproducibility.
        contamination: Nominal contamination rate passed to PyOD (default 0.01).
    """
    def __init__(
        self,
        n_estimators: int = 100,
        random_state: int = 42,
        contamination: float = 0.01
    ):
        super().__init__(model_name="Isolation_Forest")
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.contamination = contamination
        self.model = IForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            behaviour="new"
        )
        self.feature_names = ['flow', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'diff_1h', 'diff_24h']

    def fit(self, train_series: pd.Series) -> "IsolationForestDetector":
        """
        Fits Isolation Forest on valid historical training observations.
        Drops missing rows; never imputes missing flow as zero.
        """
        feats = extract_traffic_features(train_series)
        # Only fit on complete observed rows
        valid_mask = feats['flow'].notnull()
        X_train = feats.loc[valid_mask, self.feature_names].values
        
        if len(X_train) == 0:
            raise ValueError("No valid rows available to fit IsolationForestDetector")

        self.model.fit(X_train)
        self.is_fitted = True
        return self

    def score(self, series: pd.Series) -> pd.Series:
        """
        Computes anomaly scores via PyOD decision_function().
        Higher score = more anomalous.
        Timestamps with missing flow (NaN) yield NaN score.
        """
        if not self.is_fitted:
            raise RuntimeError("IsolationForestDetector must be fitted before scoring.")

        feats = extract_traffic_features(series)
        valid_mask = feats['flow'].notnull()
        
        scores = pd.Series(np.nan, index=series.index, dtype='float32')
        if valid_mask.sum() == 0:
            return scores

        X_eval = feats.loc[valid_mask, self.feature_names].values
        # PyOD decision_function: higher score = more anomalous
        raw_scores = self.model.decision_function(X_eval)
        scores.loc[valid_mask] = raw_scores.astype('float32')
        
        self.fallback_counts["total_evaluations"] += len(X_eval)
        return scores
