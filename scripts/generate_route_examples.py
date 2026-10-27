import os
import pandas as pd
import networkx as nx

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

gv_edges = set(edges[edges['name'].str.contains('George V Bridge', case=False, na=False)]['edge_id'])
gb_edges = set(edges[edges['name'].str.contains('Glasgow Bridge', case=False, na=False)]['edge_id'])
kingston_edges = set(edges[edges['name'].str.contains('Kingston Bridge', case=False, na=False)]['edge_id'])

def get_route_example(origin_nodes, dest_nodes, bridge_edges, bridge_name):
    G_closed = G.copy()
    for u, v, d in list(G_closed.edges(data=True)):
        if d.get('edge_id') in bridge_edges:
            G_closed.remove_edge(u, v)

    for s in origin_nodes:
        for t in dest_nodes:
            try:
                base_path = nx.shortest_path(G, s, t, weight='weight')
                base_edges = [G[base_path[i]][base_path[i+1]]['edge_id'] for i in range(len(base_path)-1)]
                if any(e in bridge_edges for e in base_edges):
                    try:
                        new_path = nx.shortest_path(G_closed, s, t, weight='weight')
                        base_time = nx.shortest_path_length(G, s, t, weight='weight')
                        base_dist = sum(G[base_path[i]][base_path[i+1]]['length_m'] for i in range(len(base_path)-1))
                        new_time = nx.shortest_path_length(G_closed, s, t, weight='weight')
                        new_dist = sum(G_closed[new_path[i]][new_path[i+1]]['length_m'] for i in range(len(new_path)-1))
                        
                        base_names = [G[base_path[i]][base_path[i+1]]['name'] for i in range(len(base_path)-1)]
                        new_names = [G_closed[new_path[i]][new_path[i+1]]['name'] for i in range(len(new_path)-1)]
                        
                        return {
                            'bridge': bridge_name,
                            'origin': (s, n_dict[s][0], n_dict[s][1]),
                            'dest': (t, n_dict[t][0], n_dict[t][1]),
                            'base_nodes_cnt': len(base_path),
                            'base_dist_m': base_dist,
                            'base_time_s': base_time,
                            'base_bridges': [name for name in base_names if 'Bridge' in str(name) or 'Arc' in str(name)],
                            'new_nodes_cnt': len(new_path),
                            'new_dist_m': new_dist,
                            'new_time_s': new_time,
                            'new_bridges': [name for name in new_names if 'Bridge' in str(name) or 'Arc' in str(name)],
                            'delta_dist_m': new_dist - base_dist,
                            'delta_time_s': new_time - base_time
                        }
                    except nx.NetworkXNoPath:
                        continue
            except nx.NetworkXNoPath:
                continue
    return None

south_nodes = [n for n, (lat, lon) in n_dict.items() if lat < 55.854 and n in G]
north_nodes = [n for n, (lat, lon) in n_dict.items() if lat > 55.858 and n in G]

# 1. George V Bridge (Northbound)
ex_gv = get_route_example(south_nodes, north_nodes, gv_edges, "George V Bridge")
print("=== GEORGE V BRIDGE ROUTE EXAMPLE ===")
for k, v in ex_gv.items():
    print(f"{k}: {v}")

# 2. Glasgow Bridge (Southbound)
ex_gb = get_route_example(north_nodes, south_nodes, gb_edges, "Glasgow Bridge")
print("\n=== GLASGOW BRIDGE ROUTE EXAMPLE ===")
for k, v in ex_gb.items():
    print(f"{k}: {v}")

# 3. Kingston Bridge (Northbound)
ex_kb_nb = get_route_example(south_nodes, north_nodes, kingston_edges, "Kingston Bridge (Northbound)")
print("\n=== KINGSTON BRIDGE NORTHBOUND ROUTE EXAMPLE ===")
for k, v in ex_kb_nb.items():
    print(f"{k}: {v}")

# 4. Kingston Bridge (Southbound)
ex_kb_sb = get_route_example(north_nodes, south_nodes, kingston_edges, "Kingston Bridge (Southbound)")
print("\n=== KINGSTON BRIDGE SOUTHBOUND ROUTE EXAMPLE ===")
for k, v in ex_kb_sb.items():
    print(f"{k}: {v}")
