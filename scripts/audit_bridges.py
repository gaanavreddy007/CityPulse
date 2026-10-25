"""
Audit Script: Bridge Edge Verification.
Extracts exact Edge IDs, OSM Way IDs, node coordinates, lengths, lanes, and highways
for M8 Kingston Bridge, George V Bridge, Glasgow Bridge, and Clyde Arc.
"""

import os
import pandas as pd

PROJECT_ROOT = r"C:\Gaanav\Projects\CityPulse"
edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_edges.csv")
df = pd.read_csv(edges_csv)

bridges = {
    'M8 Kingston Bridge': df[df['name'].str.contains('Kingston Bridge', case=False, na=False)],
    'George V Bridge': df[df['name'].str.contains('George V Bridge', case=False, na=False)],
    'Glasgow Bridge': df[df['name'].str.contains('Glasgow Bridge', case=False, na=False)],
    'Clyde Arc': df[df['name'].str.contains('Clyde Arc', case=False, na=False)]
}

for name, b_df in bridges.items():
    print(f"\n{'='*70}\n{name}: {len(b_df)} directed edges\n{'='*70}")
    for _, r in b_df.iterrows():
        print(f"Edge ID: {r['edge_id']}")
        print(f"  OSM Way ID: {r['osm_way_id']} | Road Name: {r['name']} | Highway: {r['highway']}")
        print(f"  Nodes: {r['u']} -> {r['v']}")
        print(f"  Coords: ({r['u_lat']:.6f}, {r['u_lon']:.6f}) -> ({r['v_lat']:.6f}, {r['v_lon']:.6f})")
        print(f"  Lanes: {r['lanes']} | Length: {r['length_m']:.2f} m | Free-Flow Time: {r['free_flow_time_sec']:.2f} s | Oneway: {r['oneway']}")
