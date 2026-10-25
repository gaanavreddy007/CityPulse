"""
CITYPULSE Empirical Cumulative Distribution Outlier Detection (ECOD) Detector.
Wraps PyOD ECOD with cyclical and differential traffic features.
Non-parametric, fast, and parameter-free outlier detection with zero test leakage.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from pyod.models.ecod import ECOD

from .base import BaseAnomalyDetector
from .isolation_forest import extract_traffic_features

class ECODDetector(BaseAnomalyDetector):
    """
    Empirical Cumulative Distribution Outlier Detection (ECOD).
    
    Attributes:
        contamination: Expected proportion of outliers for default thresholding (default 0.01).
    """
    def __init__(self, contamination: float = 0.01):
        super().__init__(model_name="ECOD")
        self.contamination = contamination
        self.model = ECOD(contamination=self.contamination)
        self.feature_names = ['flow', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'diff_1h', 'diff_24h']

    def fit(self, train_series: pd.Series) -> "ECODDetector":
        """
        Fits empirical cumulative distribution estimators on historical training observations.
        Drops missing rows without zero-imputation.
        """
        feats = extract_traffic_features(train_series)
        valid_mask = feats['flow'].notnull()
        X_train = feats.loc[valid_mask, self.feature_names].values
        
        if len(X_train) == 0:
            raise ValueError("No valid rows available to fit ECODDetector")

        self.model.fit(X_train)
        self.is_fitted = True
        return self

    def score(self, series: pd.Series) -> pd.Series:
        """
        Computes ECOD anomaly scores via decision_function().
        Higher score = more anomalous tail probability.
        Missing observations (NaN) remain NaN in output scores.
        """
        if not self.is_fitted:
            raise RuntimeError("ECODDetector must be fitted before scoring.")

        feats = extract_traffic_features(series)
        valid_mask = feats['flow'].notnull()
        
        scores = pd.Series(np.nan, index=series.index, dtype='float32')
        if valid_mask.sum() == 0:
            return scores

        X_eval = feats.loc[valid_mask, self.feature_names].values
        raw_scores = self.model.decision_function(X_eval)
        scores.loc[valid_mask] = raw_scores.astype('float32')
        
        self.fallback_counts["total_evaluations"] += len(X_eval)
        return scores
