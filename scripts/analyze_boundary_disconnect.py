import os
import pandas as pd
import networkx as nx

PROJECT_ROOT = r"C:\Gaanav\Projects\CityPulse"
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

kingston_edges = set(edges[edges['name'].str.contains('Kingston Bridge', case=False, na=False)]['edge_id'])
G_no_kb = G.copy()
for u, v, d in list(G_no_kb.edges(data=True)):
    if d.get('edge_id') in kingston_edges:
        G_no_kb.remove_edge(u, v)

south_nodes = [n for n, (lat, lon) in n_dict.items() if lat < 55.854 and n in G]
north_nodes = [n for n, (lat, lon) in n_dict.items() if lat > 55.858 and n in G]

disconnected_destinations = set()
disconnected_origins = set()
disconnected_pairs_sample = []

for s in south_nodes:
    l_base = nx.single_source_dijkstra_path_length(G, s, weight='weight')
    l_closed = nx.single_source_dijkstra_path_length(G_no_kb, s, weight='weight')
    for n in north_nodes:
        if n in l_base and n not in l_closed:
            disconnected_origins.add(s)
            disconnected_destinations.add(n)
            if len(disconnected_pairs_sample) < 5:
                disconnected_pairs_sample.append((s, n))

print(f"Total distinct disconnected destination nodes (North): {len(disconnected_destinations)}")
print(f"Total distinct disconnected origin nodes (South): {len(disconnected_origins)}")

print("\nSample disconnected destination nodes:")
for d in list(disconnected_destinations)[:10]:
    lat, lon = n_dict[d]
    # Check incoming edges to d in G
    in_edges = list(G.in_edges(d, data=True))
    edge_names = [e[2].get('name') for e in in_edges]
    print(f"  Node {d} ({lat:.5f}, {lon:.5f}) | In-degree: {len(in_edges)} | Incoming road names: {edge_names}")

# Let's check why these destination nodes are only reachable via Kingston Bridge:
# Trace path in baseline G from an origin to sample destination:
s_samp, d_samp = disconnected_pairs_sample[0]
path = nx.shortest_path(G, s_samp, d_samp, weight='weight')
print(f"\nBaseline path for ({s_samp} -> {d_samp}):")
for i in range(len(path)-1):
    u, v = path[i], path[i+1]
    e_data = G[u][v]
    print(f"  {u} -> {v} : {e_data['name']} ({e_data['edge_id']})")
