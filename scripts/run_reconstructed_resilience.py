"""
CITYPULSE Phase 4.2: Resilience Experiment Runner on Reconstructed OSM Graph.
Evaluates road-network resilience across:
- 3 OD Cohorts (Cross-River Commuters, Core Grid Sample, Gateway East-West)
- 4 Closure Scenarios (Kingston Bridge, George V & Glasgow Bridge, Clyde Arc, Compound)
- 2 Impedance Metrics (Free-Flow Travel Time in seconds, Geodetic Distance in meters)
- Disconnection Penalty Sensitivity (M in [600s, 1800s, 3600s, 7200s])
Outputs machine-readable results to reports/phase4_2_resilience_sensitivity.csv.
"""

import os
import sys
import time
import random
import numpy as np
import pandas as pd
import networkx as nx

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_edges.csv")
nodes_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_nodes.csv")

edges_df = pd.read_csv(edges_csv)
nodes_df = pd.read_csv(nodes_csv)
node_coords = dict(zip(nodes_df['node_id'], zip(nodes_df['latitude'], nodes_df['longitude'])))

# Build base graph
G_time = nx.DiGraph()
G_dist = nx.DiGraph()

for _, r in edges_df.iterrows():
    u, v = int(r['u']), int(r['v'])
    e_id = r['edge_id']
    name = str(r['name'])
    l_m = float(r['length_m'])
    t_sec = float(r['free_flow_time_sec'])
    
    G_time.add_edge(u, v, edge_id=e_id, name=name, weight=t_sec, length_m=l_m)
    G_dist.add_edge(u, v, edge_id=e_id, name=name, weight=l_m, time_sec=t_sec)

# Define Closure Edge Sets
m8_edges = set(edges_df[edges_df['name'].str.contains('Kingston Bridge', case=False, na=False)]['edge_id'])
gv_edges = set(edges_df[edges_df['name'].str.contains('George V Bridge|Glasgow Bridge', case=False, na=False)]['edge_id'])
arc_edges = set(edges_df[edges_df['name'].str.contains('Clyde Arc', case=False, na=False)]['edge_id'])
compound_edges = m8_edges.union(gv_edges)

scenarios = [
    ("M8_KINGSTON_CLOSURE", m8_edges, "M8 Kingston Bridge Motorway Viaduct (10 lanes)"),
    ("GEORGE_V_GLASGOW_BRIDGE_CLOSURE", gv_edges, "George V & Glasgow Bridge Arterial Axis (7 lanes)"),
    ("CLYDE_ARC_CLOSURE", arc_edges, "Clyde Arc / Squinty Bridge Western Crossing (2 lanes)"),
    ("COMPOUND_KINGSTON_GEORGE_V_CLOSURE", compound_edges, "Compound Motorway + Central Arterial Bridges")
]

# Define OD Cohorts
# Cohort A: Cross-River (South -> North)
south_nodes = [n for n, (lat, lon) in node_coords.items() if lat < 55.854 and n in G_time]
north_nodes = set(n for n, (lat, lon) in node_coords.items() if lat > 55.858 and n in G_time)

# Cohort B: Core City Centre Grid Sample
# Use largest SCC
sccs = list(nx.strongly_connected_components(G_time))
largest_scc = list(max(sccs, key=len))
random.seed(42)
cohort_b_nodes = random.sample(largest_scc, 100)
cohort_b_pairs = [(u, v) for u in cohort_b_nodes for v in cohort_b_nodes if u != v][:1000]

# Cohort C: East-West Gateway Transit
west_gateways = [n for n, (lat, lon) in node_coords.items() if lon < -4.280 and n in largest_scc][:30]
east_gateways = [n for n, (lat, lon) in node_coords.items() if lon > -4.248 and n in largest_scc][:30]

cohort_definitions = [
    ("COHORT_A_CROSS_RIVER", south_nodes, north_nodes, "Cross-River Commuters (South -> North)"),
    ("COHORT_B_CORE_GRID_SAMPLE", None, None, "Core City-Centre Circulation (N=1,000 pairs)"),
    ("COHORT_C_EAST_WEST_GATEWAYS", west_gateways, east_gateways, "East-West Gateway Transit (West -> East)")
]

penalties = [600.0, 1800.0, 3600.0, 7200.0]

results = []

print("=" * 80)
print("RUNNING RECONSTRUCTED RESILIENCE EXPERIMENTS")
print("=" * 80)

for cohort_id, origins, destinations, cohort_desc in cohort_definitions:
    print(f"\n=======================================================")
    print(f"EVALUATING: {cohort_id} ({cohort_desc})")
    print(f"=======================================================")
    
    # 1. Compute Baseline Reachability & Impedance
    t0 = time.time()
    base_reachable_time = {}
    base_reachable_dist = {}
    
    if cohort_id == "COHORT_B_CORE_GRID_SAMPLE":
        for u, v in cohort_b_pairs:
            try:
                base_reachable_time[(u, v)] = nx.shortest_path_length(G_time, u, v, weight='weight')
                base_reachable_dist[(u, v)] = nx.shortest_path_length(G_dist, u, v, weight='weight')
            except nx.NetworkXNoPath:
                pass
    else:
        for s in origins:
            l_t = nx.single_source_dijkstra_path_length(G_time, s, weight='weight')
            l_d = nx.single_source_dijkstra_path_length(G_dist, s, weight='weight')
            for dest in destinations:
                if dest in l_t:
                    base_reachable_time[(s, dest)] = l_t[dest]
                    base_reachable_dist[(s, dest)] = l_d[dest]
                    
    n_base = len(base_reachable_time)
    mean_base_time = float(np.mean(list(base_reachable_time.values())))
    mean_base_dist = float(np.mean(list(base_reachable_dist.values())))
    print(f"Baseline Reachable Pairs: {n_base:,} | Mean Time: {mean_base_time:.1f}s | Mean Dist: {mean_base_dist:.1f}m (computed in {time.time()-t0:.2f}s)")
    
    # 2. Evaluate Closure Scenarios
    for scen_id, closed_set, scen_desc in scenarios:
        # Create severed graph copies
        G_scen_time = G_time.copy()
        G_scen_dist = G_dist.copy()
        
        for u, v, d in list(G_scen_time.edges(data=True)):
            if d.get('edge_id') in closed_set:
                G_scen_time.remove_edge(u, v)
                G_scen_dist.remove_edge(u, v)
                
        # Evaluate shortest paths under closure
        scen_time_pairs = {}
        scen_dist_pairs = {}
        
        if cohort_id == "COHORT_B_CORE_GRID_SAMPLE":
            for (u, v) in base_reachable_time:
                try:
                    scen_time_pairs[(u, v)] = nx.shortest_path_length(G_scen_time, u, v, weight='weight')
                    scen_dist_pairs[(u, v)] = nx.shortest_path_length(G_scen_dist, u, v, weight='weight')
                except nx.NetworkXNoPath:
                    pass
        else:
            for s in origins:
                l_t = nx.single_source_dijkstra_path_length(G_scen_time, s, weight='weight')
                l_d = nx.single_source_dijkstra_path_length(G_scen_dist, s, weight='weight')
                for dest in destinations:
                    if (s, dest) in base_reachable_time and dest in l_t:
                        scen_time_pairs[(s, dest)] = l_t[dest]
                        scen_dist_pairs[(s, dest)] = l_d[dest]
                        
        n_still_conn = len(scen_time_pairs)
        n_newly_disc = n_base - n_still_conn
        pct_disc = (n_newly_disc / max(1, n_base)) * 100.0
        
        # Real Detour Delays (among still-connected pairs)
        time_delays = [scen_time_pairs[p] - base_reachable_time[p] for p in scen_time_pairs]
        dist_delays = [scen_dist_pairs[p] - base_reachable_dist[p] for p in scen_dist_pairs]
        
        mean_time_delay = float(np.mean(time_delays))
        mean_dist_delay = float(np.mean(dist_delays))
        max_time_delay = float(np.max(time_delays))
        max_dist_delay = float(np.max(dist_delays))
        rerouted_pairs = sum(1 for d in time_delays if d > 0.1)
        rerouted_share = (rerouted_pairs / max(1, n_still_conn)) * 100.0
        
        mean_base_time_still_conn = float(np.mean([base_reachable_time[p] for p in scen_time_pairs]))
        rel_time_delay_pct = (mean_time_delay / max(1e-6, mean_base_time_still_conn)) * 100.0
        
        print(f"\n  Scenario: {scen_id}")
        print(f"    Still Connected: {n_still_conn:,} ({(n_still_conn/n_base)*100:.1f}%) | Newly Disconnected: {n_newly_disc:,} ({pct_disc:.2f}%)")
        print(f"    Rerouted Pairs: {rerouted_pairs:,} ({rerouted_share:.1f}%)")
        print(f"    Mean Detour Delay (Time): +{mean_time_delay:.2f}s (+{rel_time_delay_pct:.1f}%) | Max Delay: +{max_time_delay:.1f}s")
        print(f"    Mean Detour Distance: +{mean_dist_delay:.1f}m | Max Detour Distance: +{max_dist_delay:.1f}m")
        
        # Evaluate with explicit penalty assumptions for sensitivity
        for penalty in penalties:
            # Baseline total with penalty for currently disconnected
            # For this cohort, baseline reachable are all evaluated
            base_total_time_with_penalty = sum(base_reachable_time.values())
            closure_total_time_with_penalty = sum(scen_time_pairs.values()) + (n_newly_disc * penalty)
            delta_total_with_penalty = closure_total_time_with_penalty - base_total_time_with_penalty
            
            results.append({
                "od_cohort": cohort_id,
                "cohort_description": cohort_desc,
                "scenario": scen_id,
                "scenario_description": scen_desc,
                "disconnection_penalty_sec": penalty,
                "baseline_reachable_pairs": n_base,
                "baseline_mean_time_sec": round(mean_base_time, 2),
                "baseline_mean_dist_m": round(mean_base_dist, 2),
                "still_connected_pairs": n_still_conn,
                "still_connected_pct": round(n_still_conn / n_base * 100.0, 2),
                "newly_disconnected_pairs": n_newly_disc,
                "newly_disconnected_pct": round(pct_disc, 2),
                "rerouted_pairs_count": rerouted_pairs,
                "rerouted_pairs_share_pct": round(rerouted_share, 2),
                "mean_detour_delay_sec": round(mean_time_delay, 2),
                "relative_detour_delay_pct": round(rel_time_delay_pct, 2),
                "max_detour_delay_sec": round(max_time_delay, 2),
                "mean_detour_distance_m": round(mean_dist_delay, 2),
                "max_detour_distance_m": round(max_dist_delay, 2),
                "total_delta_with_penalty_sec": round(delta_total_with_penalty, 2),
                "penalty_share_of_total_pct": round((n_newly_disc * penalty) / max(1e-6, delta_total_with_penalty) * 100.0, 2)
            })

df_results = pd.DataFrame(results)
out_csv = os.path.join(PROJECT_ROOT, "reports", "phase4_2_resilience_sensitivity.csv")
df_results.to_csv(out_csv, index=False)
print(f"\nReconstructed resilience sensitivity results saved to: {out_csv} ({len(df_results)} rows)")
