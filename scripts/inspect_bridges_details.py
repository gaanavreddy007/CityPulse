import os
import pandas as pd
import networkx as nx

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_edges.csv")
nodes_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_nodes.csv")

edges = pd.read_csv(edges_csv)
nodes = pd.read_csv(nodes_csv)
n_dict = dict(zip(nodes['node_id'], zip(nodes['latitude'], nodes['longitude'])))

for name in ['George V Bridge', 'Glasgow Bridge', 'Kingston Bridge', 'Clyde Arc']:
    sub = edges[edges['name'].str.contains(name, case=False, na=False)]
    print(f"=== {name} ({len(sub)} edges) ===")
    for _, r in sub.iterrows():
        u, v = int(r['u']), int(r['v'])
        u_lat, u_lon = n_dict[u]
        v_lat, v_lon = n_dict[v]
        direction = "Northbound" if v_lat > u_lat else "Southbound"
        print(f"  Edge {r['edge_id']} (Way {r['osm_way_id']}): {u} ({u_lat:.5f},{u_lon:.5f}) -> {v} ({v_lat:.5f},{v_lon:.5f}) | {direction} | {r['length_m']:.1f}m, {r['free_flow_time_sec']:.1f}s")

# Let's inspect route examples
G = nx.DiGraph()
for _, r in edges.iterrows():
    G.add_edge(int(r['u']), int(r['v']),
               edge_id=r['edge_id'],
               name=r['name'],
               length_m=float(r['length_m']),
               weight=float(r['free_flow_time_sec']))

gv_edges = set(edges[edges['name'].str.contains('George V Bridge', case=False, na=False)]['edge_id'])
gb_edges = set(edges[edges['name'].str.contains('Glasgow Bridge', case=False, na=False)]['edge_id'])

# Find a route using George V Bridge
print("\n--- Route Example: Impact of George V Bridge Closure ---")
for s in [n for n, (lat, lon) in n_dict.items() if lat < 55.854 and n in G][:20]:
    for t in [n for n, (lat, lon) in n_dict.items() if lat > 55.858 and n in G][:20]:
        try:
            path = nx.shortest_path(G, s, t, weight='weight')
            path_edges = [G[path[i]][path[i+1]]['edge_id'] for i in range(len(path)-1)]
            if any(e in gv_edges for e in path_edges):
                base_time = nx.shortest_path_length(G, s, t, weight='weight')
                base_dist = sum(G[path[i]][path[i+1]]['length_m'] for i in range(len(path)-1))
                # Now close George V Bridge
                G_sub = G.copy()
                for u, v, d in list(G_sub.edges(data=True)):
                    if d.get('edge_id') in gv_edges:
                        G_sub.remove_edge(u, v)
                new_path = nx.shortest_path(G_sub, s, t, weight='weight')
                new_time = nx.shortest_path_length(G_sub, s, t, weight='weight')
                new_dist = sum(G_sub[new_path[i]][new_path[i+1]]['length_m'] for i in range(len(new_path)-1))
                new_edges_names = [G_sub[new_path[i]][new_path[i+1]]['name'] for i in range(len(new_path)-1)]
                
                print(f"Origin Node: {s} ({n_dict[s][0]:.5f}, {n_dict[s][1]:.5f})")
                print(f"Destination Node: {t} ({n_dict[t][0]:.5f}, {n_dict[t][1]:.5f})")
                print(f"Baseline Path: {len(path)} nodes, {base_dist:.1f}m, {base_time:.1f}s")
                print(f"Rerouted Path: {len(new_path)} nodes, {new_dist:.1f}m, {new_time:.1f}s")
                print(f"Change: +{new_dist - base_dist:.1f}m (+{(new_dist - base_dist)/base_dist*100:.1f}%), +{new_time - base_time:.1f}s")
                print(f"Rerouted Crossing Road: {[n for n in new_edges_names if 'Bridge' in str(n) or 'Arc' in str(n)]}")
                break
        except nx.NetworkXNoPath:
            continue
    if 'base_time' in locals():
        break

# Find a route using Glasgow Bridge
print("\n--- Route Example: Impact of Glasgow Bridge Closure ---")
for s in [n for n, (lat, lon) in n_dict.items() if lat > 55.858 and n in G][:20]:
    for t in [n for n, (lat, lon) in n_dict.items() if lat < 55.854 and n in G][:20]:
        try:
            path = nx.shortest_path(G, s, t, weight='weight')
            path_edges = [G[path[i]][path[i+1]]['edge_id'] for i in range(len(path)-1)]
            if any(e in gb_edges for e in path_edges):
                base_time = nx.shortest_path_length(G, s, t, weight='weight')
                base_dist = sum(G[path[i]][path[i+1]]['length_m'] for i in range(len(path)-1))
                # Now close Glasgow Bridge
                G_sub = G.copy()
                for u, v, d in list(G_sub.edges(data=True)):
                    if d.get('edge_id') in gb_edges:
                        G_sub.remove_edge(u, v)
                new_path = nx.shortest_path(G_sub, s, t, weight='weight')
                new_time = nx.shortest_path_length(G_sub, s, t, weight='weight')
                new_dist = sum(G_sub[new_path[i]][new_path[i+1]]['length_m'] for i in range(len(new_path)-1))
                new_edges_names = [G_sub[new_path[i]][new_path[i+1]]['name'] for i in range(len(new_path)-1)]
                
                print(f"Origin Node: {s} ({n_dict[s][0]:.5f}, {n_dict[s][1]:.5f})")
                print(f"Destination Node: {t} ({n_dict[t][0]:.5f}, {n_dict[t][1]:.5f})")
                print(f"Baseline Path: {len(path)} nodes, {base_dist:.1f}m, {base_time:.1f}s")
                print(f"Rerouted Path: {len(new_path)} nodes, {new_dist:.1f}m, {new_time:.1f}s")
                print(f"Change: +{new_dist - base_dist:.1f}m (+{(new_dist - base_dist)/base_dist*100:.1f}%), +{new_time - base_time:.1f}s")
                print(f"Rerouted Crossing Road: {[n for n in new_edges_names if 'Bridge' in str(n) or 'Arc' in str(n)]}")
                break
        except nx.NetworkXNoPath:
            continue
    if 'base_dist' in locals():
        break
