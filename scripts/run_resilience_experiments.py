"""
CITYPULSE Resilience and Observability Risk Experiment Runner.
Executes Monte Carlo sampling at 100, 1,000, and 5,000 draws for M8 Kingston Bridge
and George V / Glasgow Bridge closure scenarios.
Computes NRI and Observability Risk Index Omega_e across all road edges.
Outputs results to reports/resilience_uncertainty_results.json and reports/observability_risk_table.csv.
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

from citypulse.resilience.monte_carlo import ResilienceMonteCarloEngine
from citypulse.resilience.observability import ObservabilityRiskCalculator

def run_resilience_experiments():
    print("=" * 80)
    print("CITYPULSE PHASE 4: RESILIENCE UNCERTAINTY & OBSERVABILITY EXPERIMENTS")
    print("=" * 80)

    edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "glasgow_network_edges.csv")
    sensors_csv = os.path.join(PROJECT_ROOT, "reports", "sensor_edge_mapping.csv")
    
    edges_df = pd.read_csv(edges_csv)
    sensors_df = pd.read_csv(sensors_csv)
    
    # 1. Observability Risk Index Calculation
    print("\n--- 1. Computing Observability Risk Index (Omega_e) ---")
    obs_calc = ObservabilityRiskCalculator(edges_df, sensors_df, d0_meters=500.0)
    obs_table = obs_calc.compute_observability_index()
    
    obs_csv = os.path.join(PROJECT_ROOT, "reports", "observability_risk_table.csv")
    obs_table.to_csv(obs_csv, index=False)
    print(f"Observability Risk Table saved to: {obs_csv}")
    print(obs_table[["edge_id", "name", "raw_nri_seconds", "normalized_nri", "dist_to_sensor_meters", "observability_risk_index"]].head(10).to_string(index=False))

    # 2. Monte Carlo Uncertainty Propagation
    print("\n--- 2. Executing Monte Carlo Sampling (100, 1000, 5000 draws) ---")
    mc_engine = ResilienceMonteCarloEngine(edges_df=edges_df, alpha=0.20, beta=2.0, seed=42)
    
    # Scenario definitions
    m8_closure_edges = [
        "M8_KINGSTON_NB_1", "M8_KINGSTON_SB_1",
        "M8_RAMP_BROOMIELAW_OFF", "M8_RAMP_ANDERSTON_ON"
    ]
    
    george_v_closure_edges = [
        "GEORGE_V_BRIDGE_SB", "GLASGOW_BRIDGE_NB"
    ]
    
    draw_sizes = [100, 1000, 5000]
    all_results = []
    
    print("\nEvaluating M8 Kingston Bridge Corridor Closure...")
    t0 = time.time()
    m8_results = mc_engine.run_monte_carlo("M8_KINGSTON_CLOSURE", m8_closure_edges, draw_sizes)
    print(f"M8 closure Monte Carlo completed in {time.time() - t0:.2f}s")
    for r in m8_results:
        print(f"  Draws: {r.n_draws:4d} | Mean Delta C: {r.mean_delta_cost:.1f}s (SEM: {r.sem_delta_cost:.2f}s) | 95% Interval: [{r.ci_lower_2_5:.1f}s, {r.ci_upper_97_5:.1f}s] | Elapsed: {r.runtime_seconds:.3f}s")
        all_results.append(r.__dict__)

    print("\nEvaluating George V & Glasgow Bridge Crossing Closure...")
    t0 = time.time()
    gv_results = mc_engine.run_monte_carlo("GEORGE_V_GLASGOW_BRIDGE_CLOSURE", george_v_closure_edges, draw_sizes)
    print(f"George V closure Monte Carlo completed in {time.time() - t0:.2f}s")
    for r in gv_results:
        print(f"  Draws: {r.n_draws:4d} | Mean Delta C: {r.mean_delta_cost:.1f}s (SEM: {r.sem_delta_cost:.2f}s) | 95% Interval: [{r.ci_lower_2_5:.1f}s, {r.ci_upper_97_5:.1f}s] | Elapsed: {r.runtime_seconds:.3f}s")
        all_results.append(r.__dict__)

    # Save results JSON
    results_json = os.path.join(PROJECT_ROOT, "reports", "resilience_uncertainty_results.json")
    with open(results_json, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResilience uncertainty results saved to: {results_json}")

if __name__ == "__main__":
    run_resilience_experiments()
