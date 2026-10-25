"""
CITYPULSE Spatial Cross-Consistency Benchmark Runner.
Evaluates SpatialCrossConsistencyDetector against univariate baselines
under controlled isolated and shared downward-drift injections.
Outputs machine-readable results to reports/spatial_consistency_results.csv.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from citypulse.data.loader import load_sensor_flow, reindex_sensor_flow
from citypulse.data.schemas import SplitBounds
from citypulse.data.corruption import CorruptionEngine
from citypulse.anomaly.seasonal_mad import SeasonalMADDetector
from citypulse.anomaly.rolling_zscore import RollingZScoreDetector
from citypulse.anomaly.isolation_forest import IsolationForestDetector
from citypulse.anomaly.ecod import ECODDetector
from citypulse.anomaly.spatial import SpatialCrossConsistencyDetector
from citypulse.anomaly.metrics import compute_classification_metrics
from citypulse.anomaly.benchmark import MASTER_SEEDS, partition_series

def run_spatial_benchmark():
    print("=" * 80)
    print("CITYPULSE PHASE 4: SPATIAL CROSS-CONSISTENCY BENCHMARK")
    print(f"Master Seeds: {MASTER_SEEDS}")
    print("=" * 80)

    zip_path = os.path.join(PROJECT_ROOT, "data", "raw", "traffic_flow_data.zip")
    
    # 3 High-Confidence Eligible Pairs along distinct directed corridors:
    # Pair 1: Newton Street NB approach: GA0151_A (target) vs GC0151_B (neighbor)
    # Pair 2: M8 Kingston Bridge NB crossing: GL0451_B (target) vs GL0401_V (neighbor)
    # Pair 3: Broomielaw A814 riverside: GA1501_T (target) vs GA1851_A (neighbor)
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
    
    results = []

    for target_id, neighbor_id, edge_id, corridor_name in pairs:
        print(f"\n--- Corridor: {corridor_name} ({target_id} vs {neighbor_id}) ---")
        
        # Load and reindex both series
        target_raw = load_sensor_flow(zip_path, target_id)
        target_series = reindex_sensor_flow(target_raw)
        
        neighbor_raw = load_sensor_flow(zip_path, neighbor_id)
        neighbor_series = reindex_sensor_flow(neighbor_raw)
        
        t_train, t_val, t_test = partition_series(target_series)
        n_train, n_val, n_test = partition_series(neighbor_series)
        
        for seed in MASTER_SEEDS:
            # Fit models on Train
            spatial_detector = SpatialCrossConsistencyDetector(
                target_sensor_id=target_id,
                neighbor_sensor_id=neighbor_id,
                direction_mode="downward_drift",
                eps=1.0
            )
            spatial_detector.fit(t_train, n_train)
            spatial_detector.calibrate_threshold(t_val, n_val, contamination_rate=0.01)
            
            # Univariate baselines for target
            smad = SeasonalMADDetector(eps=1.0)
            smad.fit(t_train)
            smad.calibrate_threshold(t_val, contamination_rate=0.01)
            
            rz = RollingZScoreDetector(window_size=168, min_periods=12, eps=1.0)
            rz.fit(t_train)
            rz.calibrate_threshold(t_val, contamination_rate=0.01)
            
            iforest = IsolationForestDetector(n_estimators=100, random_state=seed, contamination=0.01)
            iforest.fit(t_train)
            iforest.calibrate_threshold(t_val, contamination_rate=0.01)
            
            ecod = ECODDetector(contamination=0.01)
            ecod.fit(t_train)
            ecod.calibrate_threshold(t_val, contamination_rate=0.01)
            
            models = {
                "Spatial_Cross_Consistency": spatial_detector,
                "Seasonal_MAD": smad,
                "Rolling_ZScore": rz,
                "Isolation_Forest": iforest,
                "ECOD": ecod
            }
            
            for cfg in drift_configs:
                scale_delta = cfg["scale_delta"]
                dur = cfg["duration_hours"]
                pattern = cfg["pattern"]
                desc = cfg["desc"]
                
                # Corrupt target
                target_corrupt_ds = CorruptionEngine.inject_drift(
                    t_test, scale_delta=scale_delta, duration_hours=dur, seed=seed
                )
                
                if pattern == "shared":
                    # Corrupt neighbor with identical temporal window to simulate real macro traffic drop
                    neighbor_corrupt_ds = CorruptionEngine.inject_drift(
                        n_test, scale_delta=scale_delta, duration_hours=dur, seed=seed
                    )
                    eval_neighbor = neighbor_corrupt_ds.corrupted_series
                    true_labels = target_corrupt_ds.labels.values
                else:
                    eval_neighbor = n_test.copy()
                    true_labels = target_corrupt_ds.labels.values
                    
                eval_target = target_corrupt_ds.corrupted_series
                
                for m_name, model in models.items():
                    t0 = time.perf_counter()
                    if m_name == "Spatial_Cross_Consistency":
                        scores = model.score(eval_target, eval_neighbor)
                        preds = model.predict(eval_target, eval_neighbor)
                        
                        # Also compute classification state
                        classified = model.classify_state(eval_target, eval_neighbor)
                        isolated_count = int((classified['state'] == 'ISOLATED_SENSOR_DEGRADATION').sum())
                        shared_count = int((classified['state'] == 'SHARED_CORRIDOR_CHANGE').sum())
                    else:
                        scores = model.score(eval_target)
                        preds = model.predict(eval_target)
                        isolated_count = np.nan
                        shared_count = np.nan
                        
                    eval_time = time.perf_counter() - t0
                    
                    clean_scores = np.nan_to_num(scores.values, nan=0.0)
                    clean_preds = np.nan_to_num(preds.values, nan=0.0)
                    
                    metrics = compute_classification_metrics(
                        y_true=true_labels,
                        y_pred=clean_preds,
                        y_score=clean_scores
                    )
                    
                    results.append({
                        "corridor": corridor_name,
                        "edge_id": edge_id,
                        "target_sensor": target_id,
                        "neighbor_sensor": neighbor_id,
                        "seed": seed,
                        "model": m_name,
                        "drift_scenario": desc,
                        "pattern": pattern,
                        "scale_delta": scale_delta,
                        "duration_hours": dur,
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
                        "isolated_sensor_alerts": isolated_count,
                        "shared_corridor_alerts": shared_count,
                        "eval_time_sec": round(eval_time, 4)
                    })

    results_df = pd.DataFrame(results)
    out_csv = os.path.join(PROJECT_ROOT, "reports", "spatial_consistency_results.csv")
    results_df.to_csv(out_csv, index=False)
    print(f"\nSpatial consistency results saved to: {out_csv} ({len(results_df)} evaluations)")
    
    # Summary
    print("\n" + "=" * 80)
    print("SPATIAL CONSISTENCY BENCHMARK SUMMARY (MEAN ACROSS 5 SEEDS)")
    print("=" * 80)
    
    agg = results_df.groupby(["model", "drift_scenario", "pattern"]).agg(
        pr_auc_mean=("pr_auc", "mean"),
        pr_auc_std=("pr_auc", "std"),
        recall_mean=("recall", "mean"),
        precision_mean=("precision", "mean"),
        f1_mean=("f1", "mean"),
        mcc_mean=("mcc", "mean"),
        fpr_mean=("fpr", "mean")
    ).reset_index()
    
    print(agg.to_string(index=False))
    
    agg_json = os.path.join(PROJECT_ROOT, "reports", "spatial_consistency_summary.json")
    agg.to_json(agg_json, orient="records", indent=2)
    print(f"Summary saved to: {agg_json}")

if __name__ == "__main__":
    run_spatial_benchmark()
