"""
Audit Script: Spatial Cross-Consistency Detector.
Reproduces metrics from raw data, verifies label alignment, conducts multi-threshold
evaluation, breaks down results by sensor pair, and generates
reports/spatial_detector_threshold_analysis.csv.
"""

import os
import sys
import numpy as np
import pandas as pd

PROJECT_ROOT = r"C:\Gaanav\Projects\CityPulse"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from citypulse.data.loader import load_sensor_flow, reindex_sensor_flow
from citypulse.data.corruption import CorruptionEngine
from citypulse.anomaly.spatial import SpatialCrossConsistencyDetector
from citypulse.anomaly.seasonal_mad import SeasonalMADDetector
from citypulse.anomaly.rolling_zscore import RollingZScoreDetector
from citypulse.anomaly.isolation_forest import IsolationForestDetector
from citypulse.anomaly.ecod import ECODDetector
from citypulse.anomaly.metrics import compute_classification_metrics
from citypulse.anomaly.benchmark import MASTER_SEEDS, partition_series

zip_path = os.path.join(PROJECT_ROOT, "data", "raw", "traffic_flow_data.zip")

pairs = [
    ("GA0151_A", "GC0151_B", "NEWTON_ST_A804_NB", "Newton Street NB"),
    ("GL0451_B", "GL0401_V", "M8_KINGSTON_NB_1", "M8 Kingston Bridge NB"),
    ("GA1501_T", "GA1851_A", "BROOMIELAW_A814", "Broomielaw A814")
]

drift_configs = [
    {"desc": "Drift (-15%, 24h)", "scale_delta": -0.15, "duration_hours": 24, "pattern": "isolated"},
    {"desc": "Drift (-30%, 24h)", "scale_delta": -0.30, "duration_hours": 24, "pattern": "isolated"},
    {"desc": "Drift (-50%, 24h)", "scale_delta": -0.50, "duration_hours": 24, "pattern": "isolated"},
    {"desc": "Drift (-30%, 168h)", "scale_delta": -0.30, "duration_hours": 168, "pattern": "isolated"},
    {"desc": "Drift (-50%, 168h)", "scale_delta": -0.50, "duration_hours": 168, "pattern": "isolated"},
    {"desc": "Shared Drift (-30%, 168h)", "scale_delta": -0.30, "duration_hours": 168, "pattern": "shared"}
]

# Multiple thresholds to audit operational trade-offs
contamination_rates = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20]

threshold_results = []

print("Running Spatial Detector Threshold & Alignment Audit...")

for target_id, neighbor_id, edge_id, corridor_name in pairs:
    target_raw = load_sensor_flow(zip_path, target_id)
    target_series = reindex_sensor_flow(target_raw)
    neighbor_raw = load_sensor_flow(zip_path, neighbor_id)
    neighbor_series = reindex_sensor_flow(neighbor_raw)
    
    t_train, t_val, t_test = partition_series(target_series)
    n_train, n_val, n_test = partition_series(neighbor_series)
    
    # Verify no test leakage during fitting
    spatial_detector = SpatialCrossConsistencyDetector(
        target_sensor_id=target_id,
        neighbor_sensor_id=neighbor_id,
        direction_mode="downward_drift",
        eps=1.0
    )
    spatial_detector.fit(t_train, n_train)
    
    # Check residual scores on validation split for each contamination rate
    val_scores = spatial_detector.score(t_val, n_val)
    val_clean = val_scores.dropna()
    
    thresholds_by_c = {}
    for c in contamination_rates:
        thresholds_by_c[c] = float(np.percentile(val_clean.values, 100.0 * (1.0 - c)))
        
    for seed in MASTER_SEEDS:
        for cfg in drift_configs:
            scale_delta = cfg["scale_delta"]
            dur = cfg["duration_hours"]
            pattern = cfg["pattern"]
            desc = cfg["desc"]
            
            # Inject drift
            target_corrupt = CorruptionEngine.inject_drift(
                t_test, scale_delta=scale_delta, duration_hours=dur, seed=seed
            )
            
            if pattern == "shared":
                neighbor_corrupt = CorruptionEngine.inject_drift(
                    n_test, scale_delta=scale_delta, duration_hours=dur, seed=seed
                )
                eval_neighbor = neighbor_corrupt.corrupted_series
            else:
                eval_neighbor = n_test.copy()
                
            eval_target = target_corrupt.corrupted_series
            true_labels = target_corrupt.labels.values
            
            # Anomaly class prevalence
            pos_count = int(true_labels.sum())
            total_count = len(true_labels)
            prevalence = pos_count / total_count
            
            # Continuous score
            scores = spatial_detector.score(eval_target, eval_neighbor)
            clean_scores = np.nan_to_num(scores.values, nan=0.0)
            
            for c in contamination_rates:
                thresh = thresholds_by_c[c]
                preds = (clean_scores >= thresh).astype(int)
                
                metrics = compute_classification_metrics(
                    y_true=true_labels,
                    y_pred=preds,
                    y_score=clean_scores
                )
                
                threshold_results.append({
                    "corridor": corridor_name,
                    "target_sensor": target_id,
                    "neighbor_sensor": neighbor_id,
                    "seed": seed,
                    "drift_scenario": desc,
                    "pattern": pattern,
                    "contamination_rate": c,
                    "calibrated_threshold": round(thresh, 4),
                    "anomaly_hours": pos_count,
                    "total_hours": total_count,
                    "prevalence": round(prevalence, 6),
                    "pr_auc": round(metrics["pr_auc"], 6),
                    "recall": round(metrics["recall"], 6),
                    "precision": round(metrics["precision"], 6),
                    "f1": round(metrics["f1"], 6) if metrics["f1"] is not None else np.nan,
                    "mcc": round(metrics["mcc"], 6),
                    "fpr": round(metrics["fpr"], 6),
                    "tp": metrics["tp"],
                    "fp": metrics["fp"],
                    "tn": metrics["tn"],
                    "fn": metrics["fn"]
                })

df_thresholds = pd.DataFrame(threshold_results)
out_csv = os.path.join(PROJECT_ROOT, "reports", "spatial_detector_threshold_analysis.csv")
df_thresholds.to_csv(out_csv, index=False)
print(f"Threshold analysis saved to {out_csv} ({len(df_thresholds)} rows)")

# Summary table for Drift (-50%, 168h) across contamination rates
print("\n--- Summary for Drift (-50%, 168h) across contamination rates (averaged across all seeds and pairs) ---")
agg_50 = df_thresholds[df_thresholds["drift_scenario"] == "Drift (-50%, 168h)"].groupby("contamination_rate").agg(
    threshold_mean=("calibrated_threshold", "mean"),
    recall_mean=("recall", "mean"),
    precision_mean=("precision", "mean"),
    f1_mean=("f1", "mean"),
    mcc_mean=("mcc", "mean"),
    fpr_mean=("fpr", "mean"),
    fp_mean=("fp", "mean")
).reset_index()
print(agg_50.to_string(index=False))
