"""
CITYPULSE Anomaly Detection Benchmark Runner.
Executes Track A (Synthetic Corruption Detection across 5 master seeds)
and Track B (Unsupervised Statistical Flow Anomaly Discovery).
Guarantees strict zero-leakage threshold calibration, explicit metric handling,
and transparent separation between missingness and numeric corruption tasks.
"""

import time
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd

from ..data.schemas import SplitBounds, SplitName, CorruptionType
from ..data.corruption import CorruptionEngine, CorruptedDataset
from .base import BaseAnomalyDetector
from .seasonal_mad import SeasonalMADDetector
from .rolling_zscore import RollingZScoreDetector
from .isolation_forest import IsolationForestDetector
from .ecod import ECODDetector
from .baselines import MissingnessDetector, StaticQuantileDetector
from .metrics import compute_classification_metrics

MASTER_SEEDS = [42, 101, 2024, 777, 999]

def get_default_models(random_state: int = 42) -> List[BaseAnomalyDetector]:
    """Returns freshly initialized instances of all benchmark models."""
    return [
        MissingnessDetector(),
        StaticQuantileDetector(),
        SeasonalMADDetector(min_samples_per_bin=10, scale_factor=1.4826, eps=1.0),
        RollingZScoreDetector(window_size=168, min_periods=12, eps=1.0),
        IsolationForestDetector(n_estimators=100, random_state=random_state, contamination=0.01),
        ECODDetector(contamination=0.01)
    ]

def partition_series(series: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Splits continuous series into canonical Train, Validation, and Test partitions."""
    train = series.loc[SplitBounds.TRAIN_START:SplitBounds.TRAIN_END]
    val = series.loc[SplitBounds.VAL_START:SplitBounds.VAL_END]
    test = series.loc[SplitBounds.TEST_START:SplitBounds.TEST_END]
    return train, val, test

class BenchmarkRunner:
    """
    Executes reproducible anomaly detection benchmarks.
    """
    def __init__(
        self,
        seeds: List[int] = MASTER_SEEDS,
        val_contamination: float = 0.01
    ):
        self.seeds = seeds
        self.val_contamination = val_contamination

    def run_track_a(
        self,
        sensor_id: str,
        full_series: pd.Series,
        corruption_configs: Optional[List[Dict[str, Any]]] = None
    ) -> pd.DataFrame:
        """
        Executes Track A: Synthetic Corruption Detection benchmark across all models and seeds.
        """
        train_s, val_s, test_s = partition_series(full_series)
        
        if corruption_configs is None:
            corruption_configs = [
                # Missingness corruptions
                {"type": "mcar", "dropout_prob": 0.05, "category": "missingness"},
                {"type": "mcar", "dropout_prob": 0.10, "category": "missingness"},
                {"type": "mcar", "dropout_prob": 0.20, "category": "missingness"},
                {"type": "burst", "duration_hours": 4, "category": "missingness"},
                {"type": "burst", "duration_hours": 12, "category": "missingness"},
                {"type": "burst", "duration_hours": 24, "category": "missingness"},
                # Numeric value corruptions
                {"type": "drift", "scale_delta": 0.30, "duration_hours": 168, "category": "numeric"},
                {"type": "drift", "scale_delta": -0.30, "duration_hours": 168, "category": "numeric"},
                {"type": "stuck_zero", "duration_hours": 24, "category": "numeric"},
                {"type": "stuck_mean", "duration_hours": 24, "category": "numeric"}
            ]

        results: List[Dict[str, Any]] = []

        for seed in self.seeds:
            # Instantiate and fit fresh models for this seed
            models = get_default_models(random_state=seed)
            fitted_models: Dict[str, BaseAnomalyDetector] = {}
            fit_runtimes: Dict[str, float] = {}

            for m in models:
                t0 = time.perf_counter()
                m.fit(train_s)
                m.calibrate_threshold(val_s, contamination_rate=self.val_contamination)
                fit_runtimes[m.model_name] = time.perf_counter() - t0
                fitted_models[m.model_name] = m

            for cfg in corruption_configs:
                ctype = cfg["type"]
                cat = cfg["category"]
                
                # Generate synthetic corruption on test series copy
                if ctype == "mcar":
                    corrupted_ds = CorruptionEngine.inject_mcar(test_s, dropout_prob=cfg["dropout_prob"], seed=seed)
                    desc = f"MCAR (p={cfg['dropout_prob']})"
                elif ctype == "burst":
                    corrupted_ds = CorruptionEngine.inject_burst(test_s, duration_hours=cfg["duration_hours"], seed=seed)
                    desc = f"Burst ({cfg['duration_hours']}h)"
                elif ctype == "drift":
                    corrupted_ds = CorruptionEngine.inject_drift(test_s, scale_delta=cfg["scale_delta"], duration_hours=cfg["duration_hours"], seed=seed)
                    sign = "+" if cfg["scale_delta"] > 0 else ""
                    desc = f"Drift ({sign}{int(cfg['scale_delta']*100)}%, {cfg['duration_hours']}h)"
                elif ctype == "stuck_zero":
                    corrupted_ds = CorruptionEngine.inject_stuck_value(test_s, mode="zero", duration_hours=cfg["duration_hours"], seed=seed)
                    desc = f"Stuck-Zero ({cfg['duration_hours']}h)"
                elif ctype == "stuck_mean":
                    corrupted_ds = CorruptionEngine.inject_stuck_value(test_s, mode="mean", duration_hours=cfg["duration_hours"], seed=seed)
                    desc = f"Stuck-Mean ({cfg['duration_hours']}h)"
                else:
                    continue

                y_true = corrupted_ds.labels.values

                for model_name, model in fitted_models.items():
                    t0 = time.perf_counter()
                    scores = model.score(corrupted_ds.corrupted_series)
                    eval_runtime = time.perf_counter() - t0
                    
                    preds = model.predict(corrupted_ds.corrupted_series)
                    
                    # For numeric models evaluating missingness tasks, missing values are NaN
                    # For missingness detectors evaluating numeric tasks, missingness scores do not detect drift
                    y_score_vals = scores.values
                    y_pred_vals = preds.values

                    # If model is numeric and corruption is missingness, numeric scores are NaN on missing rows
                    # If we fill NaN scores with 0.0 for scoring, model gets 0 on missing data (correct, numeric models don't detect missingness)
                    # If model is Missingness_Detector, scores are 1.0 for missing data and 0.0 for numeric values
                    if model_name == "Missingness_Detector":
                        clean_scores = np.nan_to_num(y_score_vals, nan=0.0)
                        clean_preds = np.nan_to_num(y_pred_vals, nan=0.0)
                    else:
                        # Numeric detectors: replace NaN scores with 0.0 for ranking/binary detection evaluation
                        # so that missing values are NOT rewarded as detected numeric anomalies!
                        clean_scores = np.nan_to_num(y_score_vals, nan=0.0)
                        clean_preds = np.nan_to_num(y_pred_vals, nan=0.0)

                    metrics = compute_classification_metrics(
                        y_true=y_true,
                        y_pred=clean_preds,
                        y_score=clean_scores
                    )

                    fb_report = model.fallback_usage_report()

                    row = {
                        "sensor_id": sensor_id,
                        "seed": seed,
                        "model": model_name,
                        "task_category": cat,
                        "corruption_type": ctype,
                        "corruption_desc": desc,
                        "calibrated_threshold": round(float(model.threshold), 4) if model.threshold is not None else np.nan,
                        "pr_auc": metrics["pr_auc"],
                        "precision": metrics["precision"],
                        "recall": metrics["recall"],
                        "f1": metrics["f1"],
                        "mcc": metrics["mcc"],
                        "fpr": metrics["fpr"],
                        "tp": metrics["tp"],
                        "fp": metrics["fp"],
                        "tn": metrics["tn"],
                        "fn": metrics["fn"],
                        "fit_runtime_sec": round(fit_runtimes[model_name], 4),
                        "eval_runtime_sec": round(eval_runtime, 4),
                        "fallback_rate_pct": fb_report["fallback_rate_pct"],
                        "undefined_metrics_count": len(metrics["undefined_reasons"])
                    }
                    results.append(row)

        return pd.DataFrame(results)

    def run_track_b(
        self,
        sensor_id: str,
        full_series: pd.Series,
        top_k: int = 10
    ) -> pd.DataFrame:
        """
        Executes Track B: Unsupervised Statistical Flow Anomaly Discovery on uncorrupted Test data.
        Does NOT label anomalies as hardware faults or traffic incidents.
        """
        train_s, val_s, test_s = partition_series(full_series)
        models = [
            SeasonalMADDetector(min_samples_per_bin=10, scale_factor=1.4826, eps=1.0),
            RollingZScoreDetector(window_size=168, min_periods=12, eps=1.0),
            IsolationForestDetector(n_estimators=100, random_state=42, contamination=0.01),
            ECODDetector(contamination=0.01)
        ]

        anomaly_records: List[Dict[str, Any]] = []

        for m in models:
            m.fit(train_s)
            m.calibrate_threshold(val_s, contamination_rate=self.val_contamination)
            scores = m.score(test_s)
            
            # Extract top K anomalies
            valid_scores = scores.dropna()
            top_indices = valid_scores.nlargest(top_k).index

            for ts in top_indices:
                score_val = float(valid_scores.loc[ts])
                flow_val = float(test_s.loc[ts])
                is_exceeding = bool(score_val >= m.threshold) if m.threshold is not None else False
                
                # Contextual calendar notes
                day_name = ts.strftime('%A')
                is_weekend = ts.dayofweek >= 5
                
                anomaly_records.append({
                    "sensor_id": sensor_id,
                    "model": m.model_name,
                    "timestamp": str(ts),
                    "day_of_week": day_name,
                    "hour": ts.hour,
                    "observed_flow": flow_val,
                    "anomaly_score": round(score_val, 4),
                    "calibrated_threshold": round(float(m.threshold), 4) if m.threshold is not None else np.nan,
                    "exceeds_threshold": is_exceeding,
                    "is_weekend": is_weekend,
                    "scientific_disclaimer": "Unsupervised statistical deviation only; not an independently validated incident or hardware fault."
                })

        return pd.DataFrame(anomaly_records)
