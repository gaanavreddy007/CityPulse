"""
Audit Script: Bridge Separate & Combined Closures.
Evaluates:
1. George V Bridge alone
2. Glasgow Bridge alone
3. George V + Glasgow Bridge together
4. Kingston Bridge alone
5. Clyde Arc alone
Provides exact before-and-after route examples with coordinates, lengths, and travel times.
"""

import os
import pandas as pd
import networkx as nx
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_edges.csv")
nodes_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_nodes.csv")

edges_df = pd.read_csv(edges_csv)
nodes_df = pd.read_csv(nodes_csv)
node_coords = dict(zip(nodes_df['node_id'], zip(nodes_df['latitude'], nodes_df['longitude'])))

G = nx.DiGraph()
for _, r in edges_df.iterrows():
    G.add_edge(int(r['u']), int(r['v']),
               edge_id=r['edge_id'],
               name=r['name'],
               length_m=float(r['length_m']),
               weight=float(r['free_flow_time_sec']))

south_nodes = [n for n, (lat, lon) in node_coords.items() if lat < 55.854 and n in G]
north_nodes = set(n for n, (lat, lon) in node_coords.items() if lat > 55.858 and n in G)

# Baseline cross-river South -> North
base_pairs_s_to_n = {}
for s in south_nodes:
    lengths = nx.single_source_dijkstra_path_length(G, s, weight='weight')
    for n in north_nodes:
        if n in lengths:
            base_pairs_s_to_n[(s, n)] = lengths[n]

# Baseline cross-river North -> South
base_pairs_n_to_s = {}
for n in north_nodes:
    lengths = nx.single_source_dijkstra_path_length(G, n, weight='weight')
    for s in south_nodes:
        if s in lengths:
            base_pairs_n_to_s[(n, s)] = lengths[s]

print(f"Baseline South -> North reachable pairs: {len(base_pairs_s_to_n):,}")
print(f"Baseline North -> South reachable pairs: {len(base_pairs_n_to_s):,}")

gv_edges = set(edges_df[edges_df['name'].str.contains('George V Bridge', case=False, na=False)]['edge_id'])
gb_edges = set(edges_df[edges_df['name'].str.contains('Glasgow Bridge', case=False, na=False)]['edge_id'])
kingston_edges = set(edges_df[edges_df['name'].str.contains('Kingston Bridge', case=False, na=False)]['edge_id'])
arc_edges = set(edges_df[edges_df['name'].str.contains('Clyde Arc', case=False, na=False)]['edge_id'])

bridge_scenarios = [
    ("GEORGE_V_ALONE", gv_edges, "George V Bridge Alone (Southbound)"),
    ("GLASGOW_BRIDGE_ALONE", gb_edges, "Glasgow Bridge Alone (Northbound)"),
    ("GEORGE_V_AND_GLASGOW_BRIDGE", gv_edges.union(gb_edges), "George V + Glasgow Bridge Combined Axis"),
    ("KINGSTON_BRIDGE_ALONE", kingston_edges, "M8 Kingston Bridge Viaduct Alone"),
    ("CLYDE_ARC_ALONE", arc_edges, "Clyde Arc Western Crossing Alone")
]

def evaluate_bridge_scenario(name, closed_set, desc):
    G_sub = G.copy()
    for u, v, d in list(G_sub.edges(data=True)):
        if d.get('edge_id') in closed_set:
            G_sub.remove_edge(u, v)
            
    # Evaluate South -> North
    res_s_to_n = {}
    for s in south_nodes:
        l = nx.single_source_dijkstra_path_length(G_sub, s, weight='weight')
        for n in north_nodes:
            if (s, n) in base_pairs_s_to_n and n in l:
                res_s_to_n[(s, n)] = l[n]
                
    # Evaluate North -> South
    res_n_to_s = {}
    for n in north_nodes:
        l = nx.single_source_dijkstra_path_length(G_sub, n, weight='weight')
        for s in south_nodes:
            if (n, s) in base_pairs_n_to_s and s in l:
                res_n_to_s[(n, s)] = l[s]
                
    delays_s_to_n = [res_s_to_n[p] - base_pairs_s_to_n[p] for p in res_s_to_n]
    delays_n_to_s = [res_n_to_s[p] - base_pairs_n_to_s[p] for p in res_n_to_s]
    
    print(f"\n{'='*75}\nSCENARIO: {name} ({desc})\n{'='*75}")
    print(f"South -> North Direction:")
    print(f"  Still Connected: {len(res_s_to_n):,} ({(len(res_s_to_n)/len(base_pairs_s_to_n))*100:.1f}%) | Newly Disconnected: {len(base_pairs_s_to_n) - len(res_s_to_n):,}")
    print(f"  Rerouted Pairs: {sum(1 for d in delays_s_to_n if d > 0.01):,} | Mean Delay: +{np.mean(delays_s_to_n):.2f}s | Max Delay: +{np.max(delays_s_to_n):.1f}s")
    
    print(f"North -> South Direction:")
    print(f"  Still Connected: {len(res_n_to_s):,} ({(len(res_n_to_s)/len(base_pairs_n_to_s))*100:.1f}%) | Newly Disconnected: {len(base_pairs_n_to_s) - len(res_n_to_s):,}")
    print(f"  Rerouted Pairs: {sum(1 for d in delays_n_to_s if d > 0.01):,} | Mean Delay: +{np.mean(delays_n_to_s):.2f}s | Max Delay: +{np.max(delays_n_to_s):.1f}s")

for sc_name, sc_set, sc_desc in bridge_scenarios:
    evaluate_bridge_scenario(sc_name, sc_set, sc_desc)
