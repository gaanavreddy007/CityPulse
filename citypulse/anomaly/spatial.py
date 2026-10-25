"""
CITYPULSE Spatial Cross-Consistency Anomaly Detector.
Compares normalized seasonal deviations between eligible adjacent sensors
along the same directed corridor.
Disambiguates isolated sensor-level degradations (hardware drift) from
shared macro-corridor traffic events (incidents, diversions, weather).
"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd

from .base import BaseAnomalyDetector
from .seasonal_mad import SeasonalMADDetector

class SpatialCrossConsistencyDetector(BaseAnomalyDetector):
    """
    Spatial Cross-Consistency Anomaly Detector.
    
    Evaluates discrepancy between a target sensor and an eligible spatial neighbor:
        delta_t = z_{target, t} - z_{neighbor, t}
    Where z_{s, t} is the normalized seasonal residual from sensor s's own historical MAD profile.
    
    Key Scientific Guardrail:
    A small delta_t (spatial agreement) does NOT imply traffic is normal.
    If both z_{target} and z_{neighbor} are large and negative, the system flags
    SHARED_CORRIDOR_CHANGE (e.g. upstream road closure or diversion), distinguishing
    it from ISOLATED_SENSOR_DEGRADATION.
    """
    def __init__(
        self,
        target_sensor_id: str,
        neighbor_sensor_id: str,
        direction_mode: str = "two_sided",  # 'two_sided' or 'downward_drift'
        min_samples_per_bin: int = 10,
        eps: float = 1.0
    ):
        super().__init__(model_name=f"Spatial_{target_sensor_id}_{neighbor_sensor_id}")
        self.target_id = target_sensor_id
        self.neighbor_id = neighbor_sensor_id
        self.direction_mode = direction_mode
        self.eps = eps
        
        self.target_seasonal = SeasonalMADDetector(min_samples_per_bin=min_samples_per_bin, eps=eps)
        self.neighbor_seasonal = SeasonalMADDetector(min_samples_per_bin=min_samples_per_bin, eps=eps)
        
        self.univariate_threshold_target: float = 3.0
        self.univariate_threshold_neighbor: float = 3.0

    def fit(self, train_target: pd.Series, train_neighbor: Optional[pd.Series] = None) -> "SpatialCrossConsistencyDetector":
        """
        Fits independent 168-hour seasonal MAD baselines for both target and neighbor sensors
        on historical training data (t <= 2021-09-30).
        """
        if train_neighbor is None:
            raise ValueError("train_neighbor series is required to fit SpatialCrossConsistencyDetector")
            
        self.target_seasonal.fit(train_target)
        self.neighbor_seasonal.fit(train_neighbor)
        self.is_fitted = True
        return self

    def calibrate_threshold(
        self,
        val_target: pd.Series,
        val_neighbor: Optional[pd.Series] = None,
        contamination_rate: float = 0.01
    ) -> float:
        """
        Calibrates spatial discrepancy threshold on uncorrupted validation data (2021-10-01 to 2022-09-30).
        Zero test leakage.
        """
        if val_neighbor is None:
            raise ValueError("val_neighbor series is required for threshold calibration")
            
        # Calibrate univariate thresholds
        self.univariate_threshold_target = self.target_seasonal.calibrate_threshold(val_target, contamination_rate)
        self.univariate_threshold_neighbor = self.neighbor_seasonal.calibrate_threshold(val_neighbor, contamination_rate)
        
        val_scores = self.score(val_target, val_neighbor)
        valid_scores = val_scores.dropna()
        
        percentile = (1.0 - contamination_rate) * 100.0
        self.threshold = float(np.percentile(valid_scores.values, percentile))
        self.threshold_percentile = percentile
        return self.threshold

    def score(self, series_target: pd.Series, series_neighbor: Optional[pd.Series] = None) -> pd.Series:
        """
        Computes spatial discrepancy anomaly score:
            s_t = |z_{target, t} - z_{neighbor, t}| (two-sided)
            or max(0, z_{neighbor, t} - z_{target, t}) (downward drift mode)
        """
        if not self.is_fitted:
            raise RuntimeError("SpatialCrossConsistencyDetector must be fitted before scoring.")
        if series_neighbor is None:
            raise ValueError("series_neighbor must be provided for spatial scoring")

        # Compute signed normalized residuals z_t
        z_target = self._compute_signed_z(self.target_seasonal, series_target)
        z_neighbor = self._compute_signed_z(self.neighbor_seasonal, series_neighbor)
        
        scores = pd.Series(np.nan, index=series_target.index, dtype='float32')
        valid_mask = z_target.notnull() & z_neighbor.notnull()
        
        zt_vals = z_target.loc[valid_mask].values
        zn_vals = z_neighbor.loc[valid_mask].values
        
        if self.direction_mode == "downward_drift":
            # High score when neighbor is normal/high and target is depressed: zn - zt
            disc = np.maximum(0.0, zn_vals - zt_vals)
        else:
            disc = np.abs(zt_vals - zn_vals)
            
        scores.loc[valid_mask] = disc.astype('float32')
        return scores

    def predict(
        self,
        series: pd.Series,
        series_neighbor: Optional[pd.Series] = None,
        threshold: Optional[float] = None
    ) -> pd.Series:
        """
        Generates binary spatial anomaly predictions (1 = anomaly, 0 = normal).
        """
        scores = self.score(series, series_neighbor)
        th = threshold if threshold is not None else self.threshold
        if th is None:
            raise RuntimeError(f"Threshold has not been calibrated for {self.model_name}")

        preds = pd.Series(np.nan, index=series.index, dtype='float32')
        valid_mask = scores.notnull()
        preds.loc[valid_mask] = (scores.loc[valid_mask] >= th).astype('float32')
        return preds

    def classify_state(
        self,
        series_target: pd.Series,
        series_neighbor: pd.Series
    ) -> pd.DataFrame:
        """
        Classifies each observation into:
        1. 'NORMAL': Neither sensor deviates significantly from baseline.
        2. 'ISOLATED_SENSOR_DEGRADATION': Target deviates, neighbor does not (high spatial discrepancy).
        3. 'SHARED_CORRIDOR_CHANGE': Both sensors deviate synchronously (low spatial discrepancy, macro event).
        4. 'NEIGHBOR_ONLY_DEVIATION': Neighbor deviates while target is normal.
        """
        scores = self.score(series_target, series_neighbor)
        z_target = self._compute_signed_z(self.target_seasonal, series_target)
        z_neighbor = self._compute_signed_z(self.neighbor_seasonal, series_neighbor)
        
        th_spatial = self.threshold if self.threshold is not None else 3.0
        
        df = pd.DataFrame(index=series_target.index)
        df['flow_target'] = series_target
        df['flow_neighbor'] = series_neighbor
        df['z_target'] = z_target
        df['z_neighbor'] = z_neighbor
        df['spatial_score'] = scores
        df['spatial_threshold'] = th_spatial
        
        # State classification
        t_flag = (z_target.abs() >= self.univariate_threshold_target)
        n_flag = (z_neighbor.abs() >= self.univariate_threshold_neighbor)
        s_flag = (scores >= th_spatial)
        
        states = pd.Series("NORMAL", index=series_target.index)
        
        # Shared event: both deviate, low spatial discrepancy
        shared_mask = t_flag & n_flag & (~s_flag)
        states.loc[shared_mask] = "SHARED_CORRIDOR_CHANGE"
        
        # Isolated target degradation: target deviates with high spatial discrepancy
        isolated_mask = t_flag & s_flag
        states.loc[isolated_mask] = "ISOLATED_SENSOR_DEGRADATION"
        
        # Neighbor only
        neighbor_mask = (~t_flag) & n_flag & s_flag
        states.loc[neighbor_mask] = "NEIGHBOR_ONLY_DEVIATION"
        
        df['state'] = states
        return df

    def _compute_signed_z(self, seasonal_model: SeasonalMADDetector, series: pd.Series) -> pd.Series:
        """Computes signed normalized deviation z = (y - median) / MAD."""
        how_series = series.index.dayofweek * 24 + series.index.hour
        z = pd.Series(np.nan, index=series.index, dtype='float32')
        valid_mask = series.notnull()
        
        valid_y = series.loc[valid_mask].values
        valid_how = how_series[valid_mask].values
        
        medians = np.array([seasonal_model.hourly_profile[h]["median"] for h in valid_how], dtype='float32')
        mads = np.array([seasonal_model.hourly_profile[h]["mad"] for h in valid_how], dtype='float32')
        
        z_vals = (valid_y - medians) / mads
        z.loc[valid_mask] = z_vals
        return z
