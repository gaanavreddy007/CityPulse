"""
CITYPULSE Synthetic Corruption Engine
Injects controlled, parameterized perturbations into test series copies.
Maintains absolute separation between raw observations and corrupted copies.
Outputs binary ground-truth anomaly labels (1 = corrupted, 0 = uncorrupted).
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

from .schemas import CorruptionType

@dataclass
class CorruptedDataset:
    """Encapsulates an explicitly corrupted series alongside its uncorrupted original and ground-truth labels."""
    original_series: pd.Series
    corrupted_series: pd.Series
    labels: pd.Series  # Binary: 1 = synthetic corruption, 0 = normal observation
    corruption_type: CorruptionType
    parameters: Dict[str, Any]
    seed: int

class CorruptionEngine:
    """
    Reproducible synthetic corruption generator with configurable random seeds.
    Operates strictly on copies of data; never modifies inputs in place.
    """

    @staticmethod
    def inject_mcar(
        series: pd.Series,
        dropout_prob: float = 0.10,
        seed: int = 42
    ) -> CorruptedDataset:
        """
        Missing Completely at Random (MCAR):
        Stochastically sets values to NaN with probability p.
        """
        if not (0.0 < dropout_prob < 1.0):
            raise ValueError(f"dropout_prob must be between 0 and 1, got {dropout_prob}")
        
        rng = np.random.default_rng(seed=seed)
        corrupted = series.copy()
        
        # Only perturb timestamps that have valid observed values
        valid_mask = corrupted.notnull().values
        rand_draws = rng.random(size=len(series))
        
        perturb_mask = valid_mask & (rand_draws < dropout_prob)
        corrupted.iloc[perturb_mask] = np.nan
        
        labels = pd.Series(0, index=series.index, dtype='int8')
        labels.iloc[perturb_mask] = 1
        
        return CorruptedDataset(
            original_series=series.copy(),
            corrupted_series=corrupted,
            labels=labels,
            corruption_type=CorruptionType.MCAR,
            parameters={"dropout_prob": dropout_prob},
            seed=seed
        )

    @staticmethod
    def inject_burst(
        series: pd.Series,
        duration_hours: int = 12,
        num_outages: int = 1,
        seed: int = 42
    ) -> CorruptedDataset:
        """
        Missing Not at Random (MNAR) / Burst Communication Outage:
        Sets contiguous blocks of duration_hours to NaN.
        """
        if duration_hours <= 0 or duration_hours >= len(series):
            raise ValueError(f"Invalid duration_hours: {duration_hours}")
        
        rng = np.random.default_rng(seed=seed)
        corrupted = series.copy()
        labels = pd.Series(0, index=series.index, dtype='int8')
        
        max_start = len(series) - duration_hours
        starts = rng.choice(max_start, size=num_outages, replace=False)
        
        for start_idx in starts:
            corrupted.iloc[start_idx:start_idx + duration_hours] = np.nan
            labels.iloc[start_idx:start_idx + duration_hours] = 1
            
        return CorruptedDataset(
            original_series=series.copy(),
            corrupted_series=corrupted,
            labels=labels,
            corruption_type=CorruptionType.BURST,
            parameters={"duration_hours": duration_hours, "num_outages": num_outages},
            seed=seed
        )

    @staticmethod
    def inject_drift(
        series: pd.Series,
        scale_delta: float = 0.30,
        start_fraction: float = 0.25,
        duration_hours: int = 168,
        seed: int = 42
    ) -> CorruptedDataset:
        """
        Calibration Drift / Multiplicative Bias:
        Scales observed flows by (1 + scale_delta) over a sustained time window.
        """
        corrupted = series.copy()
        labels = pd.Series(0, index=series.index, dtype='int8')
        
        start_idx = int(len(series) * start_fraction)
        end_idx = min(len(series), start_idx + duration_hours)
        
        slice_vals = corrupted.iloc[start_idx:end_idx].values
        valid_mask = ~np.isnan(slice_vals)
        
        perturbed_vals = slice_vals.copy()
        perturbed_vals[valid_mask] = np.maximum(0, np.round(perturbed_vals[valid_mask] * (1.0 + scale_delta)))
        
        corrupted.iloc[start_idx:end_idx] = perturbed_vals
        labels.iloc[start_idx:end_idx] = np.where(valid_mask, 1, 0).astype('int8')
        
        return CorruptedDataset(
            original_series=series.copy(),
            corrupted_series=corrupted,
            labels=labels,
            corruption_type=CorruptionType.DRIFT,
            parameters={"scale_delta": scale_delta, "duration_hours": duration_hours},
            seed=seed
        )

    @staticmethod
    def inject_stuck_value(
        series: pd.Series,
        mode: str = "zero",
        duration_hours: int = 24,
        start_fraction: float = 0.50,
        seed: int = 42
    ) -> CorruptedDataset:
        """
        Stuck-at-Value (Sensor Freezing):
        Forces sensor to output constant value (0 or historical mean) over a time window.
        """
        corrupted = series.copy()
        labels = pd.Series(0, index=series.index, dtype='int8')
        
        start_idx = int(len(series) * start_fraction)
        end_idx = min(len(series), start_idx + duration_hours)
        
        if mode == "zero":
            freeze_val = 0.0
            c_type = CorruptionType.STUCK_ZERO
        elif mode == "mean":
            freeze_val = float(series.mean(skipna=True))
            c_type = CorruptionType.STUCK_MEAN
        else:
            raise ValueError(f"Unknown stuck value mode: {mode}")
            
        corrupted.iloc[start_idx:end_idx] = freeze_val
        labels.iloc[start_idx:end_idx] = 1
        
        return CorruptedDataset(
            original_series=series.copy(),
            corrupted_series=corrupted,
            labels=labels,
            corruption_type=c_type,
            parameters={"mode": mode, "duration_hours": duration_hours, "freeze_val": freeze_val},
            seed=seed
        )
