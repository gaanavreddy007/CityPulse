"""
CITYPULSE Phase 4.2: Graph Topology Validator.
Performs comprehensive structural, geometric, and topological validation on the
reconstructed OpenStreetMap graph for central Glasgow.
Evaluates:
- Node and edge counts, duplicate edges, null/missing values
- Endpoint intersection tolerances
- Weakly and strongly connected components
- Reachable OD pairs in baseline
- Cross-river reachability and alternate route availability under bridge closures
"""

import os
import sys
import pandas as pd
import networkx as nx
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_edges.csv")
nodes_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_nodes.csv")

edges_df = pd.read_csv(edges_csv)
nodes_df = pd.read_csv(nodes_csv)

print("=" * 80)
print("CITYPULSE PHASE 4.2: GRAPH TOPOLOGY VALIDATION")
print("=" * 80)

# 1. Structural & Attribute Checks
print("\n--- 1. Structural and Attribute Integrity ---")
print(f"Total Nodes: {len(nodes_df):,}")
print(f"Total Directed Edges: {len(edges_df):,}")
print(f"Missing Values in Edges: {edges_df.isna().sum().to_dict()}")
print(f"Missing Values in Nodes: {nodes_df.isna().sum().to_dict()}")

# Check for duplicate directed edges between same (u, v)
dup_edges = edges_df.duplicated(subset=['u', 'v']).sum()
print(f"Duplicate (u, v) pairs: {dup_edges}")

# Self-loops
self_loops = (edges_df['u'] == edges_df['v']).sum()
print(f"Self-loop edges (u == v): {self_loops}")

# Degenerate lengths
zero_length = (edges_df['length_m'] <= 0).sum()
print(f"Non-positive lengths (length <= 0): {zero_length}")

# Endpoint coordinate tolerance check
node_coords = dict(zip(nodes_df['node_id'], zip(nodes_df['latitude'], nodes_df['longitude'])))
max_endpoint_diff = 0.0
for _, r in edges_df.iterrows():
    u, v = int(r['u']), int(r['v'])
    u_lat, u_lon = r['u_lat'], r['u_lon']
    v_lat, v_lon = r['v_lat'], r['v_lon']
    
    n_u_lat, n_u_lon = node_coords[u]
    n_v_lat, n_v_lon = node_coords[v]
    
    diff_u = abs(u_lat - n_u_lat) + abs(u_lon - n_u_lon)
    diff_v = abs(v_lat - n_v_lat) + abs(v_lon - n_v_lon)
    max_endpoint_diff = max(max_endpoint_diff, diff_u, diff_v)

print(f"Max Endpoint-to-Node Coordinate Difference: {max_endpoint_diff:.10f} deg (Tolerance = 0.0m)")

# 2. Build NetworkX DiGraph
G = nx.DiGraph()
for _, r in edges_df.iterrows():
    G.add_edge(
        int(r['u']), int(r['v']),
        edge_id=r['edge_id'],
        osm_way_id=r['osm_way_id'],
        name=r['name'],
        highway=r['highway'],
        length_m=float(r['length_m']),
        free_flow_sec=float(r['free_flow_time_sec']),
        capacity=float(r['capacity']),
        lanes=int(r['lanes']),
        bridge=bool(r['bridge']),
        weight=float(r['free_flow_time_sec'])
    )

# 3. Connectivity Analysis
print("\n--- 2. Network Connectivity & Components ---")
wccs = list(nx.weakly_connected_components(G))
sccs = list(nx.strongly_connected_components(G))
print(f"Number of Weakly Connected Components: {len(wccs)}")
print(f"Largest Weakly Connected Component Size: {len(max(wccs, key=len))} nodes ({len(max(wccs, key=len)) / len(G) * 100:.1f}%)")
print(f"Number of Strongly Connected Components: {len(sccs)}")
largest_scc = max(sccs, key=len)
print(f"Largest Strongly Connected Component Size: {len(largest_scc)} nodes ({len(largest_scc) / len(G) * 100:.1f}%)")

# Extract Giant Connected Subgraph (the main urban street network)
# Filter components with at least 5 nodes
substantial_wccs = [c for c in wccs if len(c) >= 10]
print(f"Substantial WCCs (>= 10 nodes): {len(substantial_wccs)} (Sizes: {[len(c) for c in substantial_wccs]})")

# 4. Bridge Representation & Approach Connectivity
print("\n--- 3. Bridge Connectivity to Approaches ---")
bridges = {
    "M8 Kingston Bridge": edges_df[edges_df['name'].str.contains("Kingston Bridge", case=False, na=False)],
    "George V Bridge": edges_df[edges_df['name'].str.contains("George V Bridge", case=False, na=False)],
    "Glasgow Bridge (Jamaica Bridge)": edges_df[edges_df['name'].str.contains("Glasgow Bridge", case=False, na=False)],
    "Victoria Bridge": edges_df[edges_df['name'].str.contains("Victoria Bridge", case=False, na=False)],
    "Albert Bridge": edges_df[edges_df['name'].str.contains("Albert Bridge", case=False, na=False)],
    "Clyde Arc": edges_df[edges_df['name'].str.contains("Clyde Arc", case=False, na=False)],
}

for b_name, b_df in bridges.items():
    u_nodes = set(b_df['u'])
    v_nodes = set(b_df['v'])
    # Incoming edges from other roads
    in_edges = [e for e in G.in_edges(u_nodes) if e[0] not in u_nodes and e[0] not in v_nodes]
    out_edges = [e for e in G.out_edges(v_nodes) if e[1] not in u_nodes and e[1] not in v_nodes]
    print(f"{b_name:32s}: {len(b_df):2d} edges | In-degree approaches: {len(in_edges):2d} | Out-degree exits: {len(out_edges):2d}")

# 5. Alternate Routes Across the River Clyde
print("\n--- 4. Alternate Routing & Detour Path Verification ---")
# Pick a southside node (Tradeston) and northside node (Broomielaw/City Centre)
# Southside: near Bridge Street / West Street
# Northside: near Broomielaw / Oswald Street
south_nodes = [n for n, (lat, lon) in node_coords.items() if lat < 55.854 and -4.265 < lon < -4.250 and n in largest_scc]
north_nodes = [n for n, (lat, lon) in node_coords.items() if lat > 55.858 and -4.265 < lon < -4.250 and n in largest_scc]

print(f"Candidate Southside Nodes: {len(south_nodes)}, Candidate Northside Nodes: {len(north_nodes)}")

if south_nodes and north_nodes:
    s_test = south_nodes[0]
    n_test = north_nodes[0]
    print(f"Testing baseline path between South Node {s_test} and North Node {n_test}...")
    
    # Baseline shortest path
    base_path = nx.shortest_path(G, source=s_test, target=n_test, weight='weight')
    base_time = nx.shortest_path_length(G, source=s_test, target=n_test, weight='weight')
    base_edges = [G[base_path[i]][base_path[i+1]]['name'] for i in range(len(base_path)-1)]
    print(f"  Baseline Path: {base_time:.1f}s, Nodes: {len(base_path)}")
    print(f"  Crossings in baseline path: {[name for name in base_edges if 'Bridge' in name or 'Arc' in name]}")
    
    # Test closure of George V / Glasgow Bridge
    gv_edge_ids = set(bridges["George V Bridge"]['edge_id']).union(set(bridges["Glasgow Bridge (Jamaica Bridge)"]['edge_id']))
    G_no_gv = G.copy()
    for u, v, data in list(G_no_gv.edges(data=True)):
        if data.get('edge_id') in gv_edge_ids:
            G_no_gv.remove_edge(u, v)
            
    if nx.has_path(G_no_gv, s_test, n_test):
        detour_path = nx.shortest_path(G_no_gv, source=s_test, target=n_test, weight='weight')
        detour_time = nx.shortest_path_length(G_no_gv, source=s_test, target=n_test, weight='weight')
        detour_edges = [G_no_gv[detour_path[i]][detour_path[i+1]]['name'] for i in range(len(detour_path)-1)]
        print(f"\n  Detour Path under George V / Glasgow Bridge Closure:")
        print(f"  Detour Travel Time: {detour_time:.1f}s (Detour Delay: +{detour_time - base_time:.1f}s, +{(detour_time - base_time)/base_time*100:.1f}%)")
        print(f"  Rerouted Crossings: {[name for name in detour_edges if 'Bridge' in name or 'Arc' in name]}")
    else:
        print("  NO ALTERNATE PATH FOUND between test pair under George V closure!")

print("\nTopology validation checks successfully completed.")
