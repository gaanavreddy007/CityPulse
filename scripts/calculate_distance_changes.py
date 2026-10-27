import os
import pandas as pd
import networkx as nx
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_edges.csv")
nodes_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_nodes.csv")

edges = pd.read_csv(edges_csv)
nodes = pd.read_csv(nodes_csv)
n_dict = dict(zip(nodes['node_id'], zip(nodes['latitude'], nodes['longitude'])))

G = nx.DiGraph()
for _, r in edges.iterrows():
    G.add_edge(int(r['u']), int(r['v']),
               edge_id=r['edge_id'],
               name=r['name'],
               length_m=float(r['length_m']),
               weight=float(r['free_flow_time_sec']))

south_nodes = [n for n, (lat, lon) in n_dict.items() if lat < 55.854 and n in G]
north_nodes = set(n for n, (lat, lon) in n_dict.items() if lat > 55.858 and n in G)

# Precompute baseline paths and lengths
base_s_to_n = {}
for s in south_nodes:
    paths = nx.single_source_dijkstra_path(G, s, weight='weight')
    for n in north_nodes:
        if n in paths:
            p = paths[n]
            t = sum(G[p[i]][p[i+1]]['weight'] for i in range(len(p)-1))
            d = sum(G[p[i]][p[i+1]]['length_m'] for i in range(len(p)-1))
            base_s_to_n[(s, n)] = (t, d)

base_n_to_s = {}
for n in north_nodes:
    paths = nx.single_source_dijkstra_path(G, n, weight='weight')
    for s in south_nodes:
        if s in paths:
            p = paths[s]
            t = sum(G[p[i]][p[i+1]]['weight'] for i in range(len(p)-1))
            d = sum(G[p[i]][p[i+1]]['length_m'] for i in range(len(p)-1))
            base_n_to_s[(n, s)] = (t, d)

gv_edges = set(edges[edges['name'].str.contains('George V Bridge', case=False, na=False)]['edge_id'])
gb_edges = set(edges[edges['name'].str.contains('Glasgow Bridge', case=False, na=False)]['edge_id'])
kingston_edges = set(edges[edges['name'].str.contains('Kingston Bridge', case=False, na=False)]['edge_id'])
arc_edges = set(edges[edges['name'].str.contains('Clyde Arc', case=False, na=False)]['edge_id'])

scenarios = [
    ("GEORGE_V_ALONE", gv_edges),
    ("GLASGOW_BRIDGE_ALONE", gb_edges),
    ("GEORGE_V_AND_GLASGOW", gv_edges.union(gb_edges)),
    ("KINGSTON_BRIDGE_ALONE", kingston_edges),
    ("CLYDE_ARC_ALONE", arc_edges)
]

print("Scenario,Direction,Reachable,Unreachable,Rerouted,MeanDeltaTime_s,MaxDeltaTime_s,MeanDeltaDist_m,MaxDeltaDist_m")

for sc_name, sc_edges in scenarios:
    G_sub = G.copy()
    for u, v, d in list(G_sub.edges(data=True)):
        if d.get('edge_id') in sc_edges:
            G_sub.remove_edge(u, v)

    # South to North
    delta_t_sn = []
    delta_d_sn = []
    unreach_sn = 0
    rerouted_sn = 0
    for s in south_nodes:
        paths = nx.single_source_dijkstra_path(G_sub, s, weight='weight')
        for n in north_nodes:
            if (s, n) in base_s_to_n:
                if n in paths:
                    p = paths[n]
                    t = sum(G_sub[p[i]][p[i+1]]['weight'] for i in range(len(p)-1))
                    d = sum(G_sub[p[i]][p[i+1]]['length_m'] for i in range(len(p)-1))
                    base_t, base_d = base_s_to_n[(s, n)]
                    dt = t - base_t
                    dd = d - base_d
                    delta_t_sn.append(dt)
                    delta_d_sn.append(dd)
                    if dt > 0.01:
                        rerouted_sn += 1
                else:
                    unreach_sn += 1

    print(f"{sc_name},South->North,{len(delta_t_sn)},{unreach_sn},{rerouted_sn},{np.mean(delta_t_sn):.2f},{np.max(delta_t_sn):.2f},{np.mean(delta_d_sn):.2f},{np.max(delta_d_sn):.2f}")

    # North to South
    delta_t_ns = []
    delta_d_ns = []
    unreach_ns = 0
    rerouted_ns = 0
    for n in north_nodes:
        paths = nx.single_source_dijkstra_path(G_sub, n, weight='weight')
        for s in south_nodes:
            if (n, s) in base_n_to_s:
                if s in paths:
                    p = paths[s]
                    t = sum(G_sub[p[i]][p[i+1]]['weight'] for i in range(len(p)-1))
                    d = sum(G_sub[p[i]][p[i+1]]['length_m'] for i in range(len(p)-1))
                    base_t, base_d = base_n_to_s[(n, s)]
                    dt = t - base_t
                    dd = d - base_d
                    delta_t_ns.append(dt)
                    delta_d_ns.append(dd)
                    if dt > 0.01:
                        rerouted_ns += 1
                else:
                    unreach_ns += 1

    print(f"{sc_name},North->South,{len(delta_t_ns)},{unreach_ns},{rerouted_ns},{np.mean(delta_t_ns):.2f},{np.max(delta_t_ns):.2f},{np.mean(delta_d_ns):.2f},{np.max(delta_d_ns):.2f}")
