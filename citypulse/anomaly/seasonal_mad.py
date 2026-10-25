"""
CITYPULSE Seasonal Median Absolute Deviation (MAD) Anomaly Detector.
Constructs a 168-hour seasonal profile from historical training data.
Features transparent hierarchical fallback for sparse bins and zero test leakage.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from .base import BaseAnomalyDetector

class SeasonalMADDetector(BaseAnomalyDetector):
    """
    Seasonal Median Absolute Deviation (MAD) Anomaly Detector.
    
    Attributes:
        season_length: 168 hours (weekly cycle: 7 days x 24 hours).
        min_samples_per_bin: Minimum valid samples needed to avoid fallback.
        scale_factor: 1.4826 (normal distribution consistency factor for MAD).
        eps: Minimum denominator to prevent division by zero (default 1.0 veh/hr).
    """
    def __init__(
        self,
        min_samples_per_bin: int = 10,
        scale_factor: float = 1.4826,
        eps: float = 1.0
    ):
        super().__init__(model_name="Seasonal_MAD")
        self.season_length = 168
        self.min_samples_per_bin = min_samples_per_bin
        self.scale_factor = scale_factor
        self.eps = eps
        
        # Profile stores: bin_idx -> (median, mad)
        self.hourly_profile: Dict[int, Dict[str, float]] = {}
        self.daily_profile: Dict[int, Dict[str, float]] = {}
        self.global_median: float = 0.0
        self.global_mad: float = 1.0

    def fit(self, train_series: pd.Series) -> "SeasonalMADDetector":
        """
        Fits 168-hour seasonal medians and MADs on historical training data.
        Does not impute missing values as zero; computes statistics on non-null values only.
        """
        if not isinstance(train_series.index, pd.DatetimeIndex):
            raise ValueError("train_series must have a DatetimeIndex")
            
        valid_series = train_series.dropna()
        if len(valid_series) == 0:
            raise ValueError("train_series contains no valid observations")

        # Global statistics
        self.global_median = float(valid_series.median())
        devs = (valid_series - self.global_median).abs()
        self.global_mad = max(float(devs.median() * self.scale_factor), self.eps)

        # 1. Hour of day profile (0-23) for tier-1 fallback
        hod_series = valid_series.index.hour
        for h in range(24):
            subset = valid_series[hod_series == h]
            if len(subset) >= self.min_samples_per_bin:
                med = float(subset.median())
                mad = float((subset - med).abs().median() * self.scale_factor)
                mad = max(mad, self.eps)
            else:
                med = self.global_median
                mad = self.global_mad
            self.daily_profile[h] = {"median": med, "mad": mad, "count": len(subset)}

        # 2. Hour of week profile (0-167)
        how_series = valid_series.index.dayofweek * 24 + valid_series.index.hour
        for h in range(self.season_length):
            subset = valid_series[how_series == h]
            count = len(subset)
            if count >= self.min_samples_per_bin:
                med = float(subset.median())
                mad = float((subset - med).abs().median() * self.scale_factor)
                mad = max(mad, self.eps)
                is_fallback = False
            else:
                # Hierarchical fallback: use hour-of-day profile
                hod = h % 24
                med = self.daily_profile[hod]["median"]
                mad = self.daily_profile[hod]["mad"]
                is_fallback = True

            self.hourly_profile[h] = {
                "median": med,
                "mad": mad,
                "count": count,
                "is_fallback": is_fallback
            }

        self.is_fitted = True
        return self

    def score(self, series: pd.Series) -> pd.Series:
        """
        Computes robust seasonal Z-score:
            s_t = |y_t - median_h| / mad_h
        Missing observations (NaN) remain NaN in output scores.
        """
        if not self.is_fitted:
            raise RuntimeError("SeasonalMADDetector must be fitted before scoring.")
        if not isinstance(series.index, pd.DatetimeIndex):
            raise ValueError("Input series must have a DatetimeIndex")

        how_series = series.index.dayofweek * 24 + series.index.hour
        scores = pd.Series(np.nan, index=series.index, dtype='float32')
        
        valid_mask = series.notnull()
        valid_values = series.loc[valid_mask].values
        valid_how = how_series[valid_mask].values

        n_evals = len(valid_values)
        fallback_invocations = 0

        # Vectorized lookup using precomputed profile arrays
        medians = np.zeros(self.season_length, dtype='float32')
        mads = np.zeros(self.season_length, dtype='float32')
        fallbacks = np.zeros(self.season_length, dtype=bool)

        for h in range(self.season_length):
            medians[h] = self.hourly_profile[h]["median"]
            mads[h] = self.hourly_profile[h]["mad"]
            fallbacks[h] = self.hourly_profile[h]["is_fallback"]

        mapped_medians = medians[valid_how]
        mapped_mads = mads[valid_how]
        mapped_fallbacks = fallbacks[valid_how]

        fallback_invocations = int(np.sum(mapped_fallbacks))
        diffs = np.abs(valid_values - mapped_medians)
        computed_scores = (diffs / mapped_mads).astype('float32')

        scores.loc[valid_mask] = computed_scores
        
        self.fallback_counts["invocations"] += fallback_invocations
        self.fallback_counts["total_evaluations"] += n_evals
        
        return scores
