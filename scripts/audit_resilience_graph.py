"""
Audit script for Section 2 & 3: Network Resilience & Graph Topology.
Investigates 38-node graph connectivity, disconnection causes, penalty sensitivity,
and Monte Carlo mechanics.
"""

import os
import sys
import pandas as pd
import networkx as nx
import numpy as np

PROJECT_ROOT = r"C:\Gaanav\Projects\CityPulse"
edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "glasgow_network_edges.csv")
df = pd.read_csv(edges_csv)

print(f"Total rows in edges_df: {len(df)}")
G = nx.DiGraph()
for _, r in df.iterrows():
    u, v = int(r['u']), int(r['v'])
    G.add_edge(u, v, id=r['edge_id'], oneway=r['oneway'])
    if not bool(r['oneway']):
        G.add_edge(v, u, id=f"{r['edge_id']}_rev")

nodes = list(G.nodes)
od_pairs = [(u, v) for u in nodes for v in nodes if u != v]
print(f"Total nodes: {len(nodes)}, Total OD pairs: {len(od_pairs)}")
print(f"Number of directed edges in G: {G.number_of_edges()}")
print(f"Weakly connected components: {[len(c) for c in nx.weakly_connected_components(G)]}")
print(f"Strongly connected components: {[len(c) for c in nx.strongly_connected_components(G)]}")

lengths = dict(nx.all_pairs_shortest_path_length(G))
base_conn = sum(1 for u, v in od_pairs if u in lengths and v in lengths[u])
base_disc = len(od_pairs) - base_conn
print(f"Baseline connected OD pairs: {base_conn} ({base_conn / len(od_pairs) * 100:.2f}%)")
print(f"Baseline disconnected OD pairs: {base_disc} ({base_disc / len(od_pairs) * 100:.2f}%)")

# Test closures
m8_edges = ["M8_KINGSTON_NB_1", "M8_KINGSTON_SB_1", "M8_RAMP_BROOMIELAW_OFF", "M8_RAMP_ANDERSTON_ON"]
gv_edges = ["GEORGE_V_BRIDGE_SB", "GLASGOW_BRIDGE_NB"]

def test_closure(name, removed):
    G_sub = G.copy()
    for u, v, data in list(G_sub.edges(data=True)):
        if data.get('id') in removed:
            G_sub.remove_edge(u, v)
    l_sub = dict(nx.all_pairs_shortest_path_length(G_sub))
    conn = sum(1 for u, v in od_pairs if u in l_sub and v in l_sub[u])
    disc = len(od_pairs) - conn
    print(f"\nClosure: {name}")
    print(f"  Connected OD pairs: {conn} ({conn / len(od_pairs) * 100:.2f}%)")
    print(f"  Disconnected OD pairs: {disc} ({disc / len(od_pairs) * 100:.2f}%)")
    print(f"  Net newly disconnected: {disc - base_disc}")

test_closure("M8 Kingston Bridge", m8_edges)
test_closure("George V & Glasgow Bridge", gv_edges)

# Let's inspect the actual nodes and edges
print("\nEdge connections (u -> v):")
for u, v, data in G.edges(data=True):
    print(f"  {u} -> {v} : {data.get('id')}")
