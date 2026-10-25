"""
Audit Script: Observability Risk Index Sensitivity & Stability.
Evaluates the mathematical mechanics of NRI, distance decay sensitivity (D0 in 100m - 2000m),
disconnection penalty sensitivity (M in 600s - 7200s), rank correlation,
and outputs reports/observability_sensitivity.csv.
"""

import os
import sys
import math
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kendalltau

PROJECT_ROOT = r"C:\Gaanav\Projects\CityPulse"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from citypulse.resilience.observability import ObservabilityRiskCalculator, geodetic_distance_m

edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "glasgow_network_edges.csv")
sensors_csv = os.path.join(PROJECT_ROOT, "reports", "sensor_edge_mapping.csv")

edges_df = pd.read_csv(edges_csv)
sensors_df = pd.read_csv(sensors_csv)

d0_scales = [100.0, 250.0, 500.0, 1000.0, 2000.0]
penalties = [600.0, 1800.0, 3600.0, 7200.0]

results = []

# Baseline calculation
base_calc = ObservabilityRiskCalculator(edges_df, sensors_df, d0_meters=500.0, disconnection_penalty=3600.0)
base_table = base_calc.compute_observability_index()
base_rank_map = {row['edge_id']: idx + 1 for idx, row in base_table.iterrows()}

for p in penalties:
    for d0 in d0_scales:
        calc = ObservabilityRiskCalculator(edges_df, sensors_df, d0_meters=d0, disconnection_penalty=p)
        table = calc.compute_observability_index()
        
        # Merge baseline rank for stability comparison
        table['current_rank'] = np.arange(1, len(table) + 1)
        table['baseline_rank'] = table['edge_id'].map(base_rank_map)
        
        sp_corr, _ = spearmanr(table['current_rank'], table['baseline_rank'])
        kd_corr, _ = kendalltau(table['current_rank'], table['baseline_rank'])
        
        for _, row in table.iterrows():
            results.append({
                "disconnection_penalty_sec": p,
                "d0_meters": d0,
                "edge_id": row['edge_id'],
                "name": row['name'],
                "highway": row['highway'],
                "oneway": bool(edges_df[edges_df['edge_id'] == row['edge_id']]['oneway'].values[0]),
                "lanes": row['lanes'],
                "raw_nri_seconds": row['raw_nri_seconds'],
                "normalized_nri": row['normalized_nri'],
                "dist_to_sensor_meters": row['dist_to_sensor_meters'],
                "unobservability_factor": row['unobservability_factor'],
                "observability_risk_index": row['observability_risk_index'],
                "current_rank": int(row['current_rank']),
                "baseline_rank": int(row['baseline_rank']),
                "spearman_rank_correlation": round(float(sp_corr), 4),
                "kendall_tau_correlation": round(float(kd_corr), 4)
            })

df_obs = pd.DataFrame(results)
out_csv = os.path.join(PROJECT_ROOT, "reports", "observability_sensitivity.csv")
df_obs.to_csv(out_csv, index=False)
print(f"Observability sensitivity saved to {out_csv} ({len(df_obs)} rows)")

# Print rank correlation summary
summary = df_obs[["disconnection_penalty_sec", "d0_meters", "spearman_rank_correlation", "kendall_tau_correlation"]].drop_duplicates()
print("\n--- Observability Ranking Stability Across D0 and Penalty ---")
print(summary.to_string(index=False))

# Print Top-5 edges comparison between D0=250m and D0=1000m at Penalty=3600s
print("\n--- Top-5 Edges at D0=250m vs D0=500m vs D0=1000m (Penalty=3600s) ---")
for d0_val in [250.0, 500.0, 1000.0]:
    sub = df_obs[(df_obs["disconnection_penalty_sec"] == 3600.0) & (df_obs["d0_meters"] == d0_val)].head(5)
    print(f"\nD0 = {d0_val}m:")
    print(sub[["current_rank", "edge_id", "name", "oneway", "raw_nri_seconds", "normalized_nri", "dist_to_sensor_meters", "observability_risk_index"]].to_string(index=False))
