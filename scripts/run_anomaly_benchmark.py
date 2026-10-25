"""
CITYPULSE Benchmark Execution Script.
Runs Track A (Synthetic Corruptions across 5 master seeds)
and Track B (Unsupervised Statistical Flow Anomalies)
on representative Glasgow SCOOT detectors.
Outputs machine-readable results to reports/anomaly_benchmark_results.csv.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from citypulse.data.loader import load_sensor_flow, reindex_sensor_flow
from citypulse.anomaly.benchmark import BenchmarkRunner, MASTER_SEEDS

def run_benchmark():
    print("=" * 80)
    print("CITYPULSE PHASE 3: BENCHMARK EXECUTION")
    print(f"Master Seeds: {MASTER_SEEDS}")
    print("=" * 80)

    sample_dir = os.path.join(PROJECT_ROOT, "data", "sample")
    
    # Representative sample sensors across different corridor roles:
    # GA0151_A: Motorway off/on ramp arterial (Newton St A804 NB)
    # GA0151_C: Key urban arterial westbound (St Vincent St WB)
    # GA0401_R: River Clyde crossing approach (George V Bridge corridor)
    target_sensors = ["GA0151_A", "GA0151_C", "GA0401_R"]
    
    runner = BenchmarkRunner(seeds=MASTER_SEEDS, val_contamination=0.01)
    
    all_track_a_dfs = []
    all_track_b_dfs = []
    
    for sensor_id in target_sensors:
        print(f"\n--- Loading and Reindexing Sensor: {sensor_id} ---")
        csv_path = os.path.join(sample_dir, "flows", f"{sensor_id}.csv")
        if not os.path.exists(csv_path):
            print(f"File not found: {csv_path}, skipping.")
            continue
            
        raw_df = load_sensor_flow(sample_dir, sensor_id)
        series = reindex_sensor_flow(raw_df)
        print(f"Series reindexed to {len(series)} calendar hours.")
        print(f"Non-null observations: {series.notnull().sum()}, Null hours: {series.isnull().sum()}")
        
        # Track A: Synthetic Corruption Detection
        print(f"Running Track A across 5 seeds and 10 corruption scenarios...")
        t0 = time.time()
        track_a_df = runner.run_track_a(sensor_id=sensor_id, full_series=series)
        elapsed_a = time.time() - t0
        print(f"Track A completed in {elapsed_a:.2f}s ({len(track_a_df)} scenario evaluations).")
        all_track_a_dfs.append(track_a_df)
        
        # Track B: Unsupervised Statistical Flow Anomalies
        print(f"Running Track B (Unsupervised Discovery on uncorrupted Test split)...")
        track_b_df = runner.run_track_b(sensor_id=sensor_id, full_series=series, top_k=10)
        print(f"Track B completed: {len(track_b_df)} top statistical anomaly records extracted.")
        all_track_b_dfs.append(track_b_df)

    if not all_track_a_dfs:
        print("No evaluations executed.")
        return

    combined_track_a = pd.concat(all_track_a_dfs, ignore_index=True)
    combined_track_b = pd.concat(all_track_b_dfs, ignore_index=True)

    # Save raw granular outputs
    out_csv = os.path.join(PROJECT_ROOT, "reports", "anomaly_benchmark_results.csv")
    combined_track_a.to_csv(out_csv, index=False)
    print(f"\nGranular Track A results saved to: {out_csv}")
    
    track_b_csv = os.path.join(PROJECT_ROOT, "reports", "statistical_anomalies_track_b.csv")
    combined_track_b.to_csv(track_b_csv, index=False)
    print(f"Track B top statistical anomalies saved to: {track_b_csv}")

    # Generate Aggregate Summary (Mean ± Std across seeds)
    print("\n" + "=" * 80)
    print("TRACK A AGGREGATE SUMMARY (MEAN ACROSS 5 SEEDS)")
    print("=" * 80)
    
    agg = combined_track_a.groupby(["model", "task_category", "corruption_desc"]).agg(
        pr_auc_mean=("pr_auc", "mean"),
        pr_auc_std=("pr_auc", "std"),
        f1_mean=("f1", "mean"),
        f1_std=("f1", "std"),
        mcc_mean=("mcc", "mean"),
        mcc_std=("mcc", "std"),
        fpr_mean=("fpr", "mean"),
        recall_mean=("recall", "mean"),
        precision_mean=("precision", "mean"),
        eval_time_ms=("eval_runtime_sec", lambda x: np.mean(x) * 1000.0)
    ).reset_index()

    print(agg.to_string(index=False))
    
    # Save aggregate summary JSON for reporting
    agg_json_path = os.path.join(PROJECT_ROOT, "reports", "anomaly_benchmark_summary.json")
    agg.to_json(agg_json_path, orient="records", indent=2)
    print(f"\nAggregate summary saved to: {agg_json_path}")

if __name__ == "__main__":
    run_benchmark()
