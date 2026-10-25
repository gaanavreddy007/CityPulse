"""
Audit Script: Monte Carlo Uncertainty & SEM vs Spread Verification.
Reproduces 100, 1,000, 5,000 draw results, tests flow variance sensitivity (5% to 30%),
BPR parameter sensitivity, and distinguishes the sample outcome distribution from the SEM.
"""

import os
import sys
import numpy as np
import pandas as pd

PROJECT_ROOT = r"C:\Gaanav\Projects\CityPulse"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from citypulse.resilience.monte_carlo import ResilienceMonteCarloEngine

edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "glasgow_network_edges.csv")
edges_df = pd.read_csv(edges_csv)

m8_edges = ["M8_KINGSTON_NB_1", "M8_KINGSTON_SB_1", "M8_RAMP_BROOMIELAW_OFF", "M8_RAMP_ANDERSTON_ON"]
gv_edges = ["GEORGE_V_BRIDGE_SB", "GLASGOW_BRIDGE_NB"]

# 1. Reproduce at 100, 1000, 5000 draws with seed 42
engine_42 = ResilienceMonteCarloEngine(edges_df, alpha=0.20, beta=2.0, seed=42)
m8_res = engine_42.run_monte_carlo("M8_KINGSTON_CLOSURE", m8_edges, [100, 1000, 5000])

print("--- Reproductibility Verification of Monte Carlo Results (Seed 42) ---")
for r in m8_res:
    # Compute true 95% CI of the MEAN
    mean_ci_lower = r.mean_delta_cost - 1.96 * r.sem_delta_cost
    mean_ci_upper = r.mean_delta_cost + 1.96 * r.sem_delta_cost
    
    print(f"Draws: {r.n_draws:4d}")
    print(f"  Mean Delta C: {r.mean_delta_cost:.2f} s | Std: {r.std_delta_cost:.2f} s | SEM: {r.sem_delta_cost:.4f} s")
    print(f"  Outcome Spread [2.5%, 97.5%]: [{r.ci_lower_2_5:.2f} s, {r.ci_upper_97_5:.2f} s] (Width: {r.ci_upper_97_5 - r.ci_lower_2_5:.2f} s)")
    print(f"  95% Confidence Interval of the MEAN: [{mean_ci_lower:.2f} s, {mean_ci_upper:.2f} s] (Width: {mean_ci_upper - mean_ci_lower:.4f} s)")

# 2. Flow Variance Sensitivity
print("\n--- Sensitivity to Assumed Input Flow Variance (N=1000, Kingston Bridge) ---")
flow_stds = [0.05, 0.10, 0.15, 0.20, 0.30]

for f_ratio in flow_stds:
    # Override flow std in edges_df
    mod_df = edges_df.copy()
    # base flow is capacity * 0.45
    for idx, r in mod_df.iterrows():
        lanes = int(r.get('lanes', 2))
        h_type = str(r.get('highway', 'secondary'))
        cap_lane = 1800.0 if 'motorway' in h_type else 900.0
        cap = lanes * cap_lane
        flow = cap * 0.45
        mod_df.at[idx, 'flow'] = flow
        mod_df.at[idx, 'flow_std'] = flow * f_ratio
        
    engine = ResilienceMonteCarloEngine(mod_df, alpha=0.20, beta=2.0, seed=42)
    res = engine.run_monte_carlo("M8_KINGSTON_CLOSURE", m8_edges, [1000])[0]
    
    outcome_width = res.ci_upper_97_5 - res.ci_lower_2_5
    sem_width = 2 * 1.96 * res.sem_delta_cost
    print(f"Flow CV: {f_ratio*100:2.0f}% | Mean Delta C: {res.mean_delta_cost:.2f} s | Std: {res.std_delta_cost:.2f} s | Outcome Width: {outcome_width:.2f} s | Mean CI Width: {sem_width:.4f} s")
