"""
Audit Script: Network Resilience Connectivity & Penalty Sensitivity.
Investigates the 38-node network topology, baseline disconnection,
separates connected pair impedance from penalty impedance across multiple penalty values,
and outputs reports/resilience_connectivity_sensitivity.csv.
"""

import os
import sys
import numpy as np
import pandas as pd
import networkx as nx

PROJECT_ROOT = r"C:\Gaanav\Projects\CityPulse"
edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "glasgow_network_edges.csv")
edges_df = pd.read_csv(edges_csv)

m8_closure_edges = [
    "M8_KINGSTON_NB_1", "M8_KINGSTON_SB_1",
    "M8_RAMP_BROOMIELAW_OFF", "M8_RAMP_ANDERSTON_ON"
]
george_v_closure_edges = [
    "GEORGE_V_BRIDGE_SB", "GLASGOW_BRIDGE_NB"
]

scenarios = [
    ("M8_KINGSTON_CLOSURE", m8_closure_edges),
    ("GEORGE_V_GLASGOW_BRIDGE_CLOSURE", george_v_closure_edges)
]

penalties = [600.0, 1200.0, 1800.0, 3600.0, 7200.0, 14400.0]
alphas = [0.10, 0.20, 0.30]
betas = [1.5, 2.0, 4.0]

def build_graph(alpha, beta):
    G = nx.DiGraph()
    for _, r in edges_df.iterrows():
        edge_id = str(r['edge_id'])
        u, v = int(r['u']), int(r['v'])
        lanes = int(r.get('lanes', 2))
        length_m = 500.0 # defaulted in prototype
        h_type = str(r.get('highway', 'secondary'))
        
        if 'motorway' in h_type:
            cap_per_lane = 1800.0
            speed_mps = 22.2
        elif 'trunk' in h_type:
            cap_per_lane = 1400.0
            speed_mps = 17.8
        elif 'primary' in h_type:
            cap_per_lane = 900.0
            speed_mps = 13.4
        else:
            cap_per_lane = 600.0
            speed_mps = 8.9
            
        capacity = lanes * cap_per_lane
        free_flow_sec = length_m / max(1.0, speed_mps)
        flow = float(r.get('flow', capacity * 0.45))
        vc = flow / max(1.0, capacity)
        tau = free_flow_sec * (1.0 + alpha * (vc ** beta))
        
        G.add_edge(u, v, id=edge_id, weight=tau, free_flow=free_flow_sec)
        if not bool(r.get('oneway', False)):
            G.add_edge(v, u, id=f"{edge_id}_rev", weight=tau, free_flow=free_flow_sec)
    return G

results = []

for scen_name, closed_edges in scenarios:
    for penalty in penalties:
        for a in alphas:
            for b in betas:
                G_base = build_graph(a, b)
                nodes = list(G_base.nodes)
                od_pairs = [(u, v) for u in nodes for v in nodes if u != v]
                total_od = len(od_pairs)
                
                # Baseline calculation
                base_lengths = dict(nx.all_pairs_dijkstra_path_length(G_base, weight='weight'))
                base_connected_cost = 0.0
                base_conn_count = 0
                base_disc_count = 0
                for u, v in od_pairs:
                    if u in base_lengths and v in base_lengths[u]:
                        base_connected_cost += base_lengths[u][v]
                        base_conn_count += 1
                    else:
                        base_disc_count += 1
                base_total_cost = base_connected_cost + (base_disc_count * penalty)
                base_penalty_pct = (base_disc_count * penalty) / max(1.0, base_total_cost) * 100.0
                
                # Closure calculation
                G_close = G_base.copy()
                for u, v, data in list(G_close.edges(data=True)):
                    if data.get('id') in closed_edges:
                        G_close.remove_edge(u, v)
                        
                close_lengths = dict(nx.all_pairs_dijkstra_path_length(G_close, weight='weight'))
                close_connected_cost = 0.0
                close_conn_count = 0
                close_disc_count = 0
                
                # Also check intersection of pairs still connected in both
                still_connected_cost_base = 0.0
                still_connected_cost_close = 0.0
                still_conn_count = 0
                
                for u, v in od_pairs:
                    is_base_conn = (u in base_lengths and v in base_lengths[u])
                    is_close_conn = (u in close_lengths and v in close_lengths[u])
                    
                    if is_close_conn:
                        close_connected_cost += close_lengths[u][v]
                        close_conn_count += 1
                    else:
                        close_disc_count += 1
                        
                    if is_base_conn and is_close_conn:
                        still_connected_cost_base += base_lengths[u][v]
                        still_connected_cost_close += close_lengths[u][v]
                        still_conn_count += 1
                        
                close_total_cost = close_connected_cost + (close_disc_count * penalty)
                delta_total = close_total_cost - base_total_cost
                newly_disc = close_disc_count - base_disc_count
                
                delta_still_connected = still_connected_cost_close - still_connected_cost_base
                penalty_contribution_to_delta = (newly_disc * penalty)
                
                results.append({
                    "scenario": scen_name,
                    "disconnection_penalty_sec": penalty,
                    "alpha": a,
                    "beta": b,
                    "total_od_pairs": total_od,
                    "baseline_connected_pairs": base_conn_count,
                    "baseline_disconnected_pairs": base_disc_count,
                    "baseline_disconnected_pct": round(base_disc_count / total_od * 100.0, 2),
                    "baseline_total_cost": round(base_total_cost, 2),
                    "baseline_penalty_share_pct": round(base_penalty_pct, 4),
                    "closure_connected_pairs": close_conn_count,
                    "closure_disconnected_pairs": close_disc_count,
                    "closure_disconnected_pct": round(close_disc_count / total_od * 100.0, 2),
                    "newly_disconnected_pairs": newly_disc,
                    "closure_total_cost": round(close_total_cost, 2),
                    "delta_total_cost": round(delta_total, 2),
                    "still_connected_pairs": still_conn_count,
                    "delta_still_connected_impedance": round(delta_still_connected, 4),
                    "penalty_contribution_to_delta": round(penalty_contribution_to_delta, 2),
                    "penalty_share_of_delta_pct": round(penalty_contribution_to_delta / max(1e-6, delta_total) * 100.0, 2)
                })

df_resilience = pd.DataFrame(results)
out_csv = os.path.join(PROJECT_ROOT, "reports", "resilience_connectivity_sensitivity.csv")
df_resilience.to_csv(out_csv, index=False)
print(f"Resilience connectivity sensitivity saved to {out_csv} ({len(df_resilience)} rows)")

# Display representative subset
sample = df_resilience[(df_resilience["alpha"] == 0.20) & (df_resilience["beta"] == 2.0)]
print("\n--- Sensitivity to Disconnection Penalty (alpha=0.20, beta=2.0) ---")
print(sample[[
    "scenario", "disconnection_penalty_sec", "baseline_total_cost", "closure_total_cost",
    "delta_total_cost", "newly_disconnected_pairs", "delta_still_connected_impedance", "penalty_share_of_delta_pct"
]].to_string(index=False))
