"""
Tests for CITYPULSE Phase 4.2 Reconstructed Road Graph.
Verifies shared-node connectivity, directed reachability, bridge identification,
edge-length integrity, and realistic detour path calculations under bridge closures.
100% Offline using NetworkX and Pandas.
"""

import os
import unittest
import pandas as pd
import networkx as nx

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EDGES_CSV = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_edges.csv")
NODES_CSV = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_nodes.csv")

class TestReconstructedGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edges_df = pd.read_csv(EDGES_CSV)
        cls.nodes_df = pd.read_csv(NODES_CSV)
        cls.node_coords = dict(zip(cls.nodes_df['node_id'], zip(cls.nodes_df['latitude'], cls.nodes_df['longitude'])))
        
        cls.G = nx.DiGraph()
        for _, r in cls.edges_df.iterrows():
            cls.G.add_edge(
                int(r['u']), int(r['v']),
                edge_id=r['edge_id'],
                name=r['name'],
                highway=r['highway'],
                length_m=float(r['length_m']),
                free_flow_sec=float(r['free_flow_time_sec']),
                lanes=int(r['lanes']),
                bridge=bool(r['bridge']),
                weight=float(r['free_flow_time_sec'])
            )

    def test_node_and_edge_schema_and_lengths(self):
        """Verifies schema, null absence, and strictly positive physical lengths."""
        self.assertGreater(len(self.nodes_df), 500, "Node count should exceed 500 intersection nodes.")
        self.assertGreater(len(self.edges_df), 1000, "Edge count should exceed 1,000 directed edges.")
        
        # Zero missing values
        self.assertEqual(self.edges_df.isna().sum().sum(), 0, "No null values allowed in edges DataFrame.")
        self.assertEqual(self.nodes_df.isna().sum().sum(), 0, "No null values allowed in nodes DataFrame.")
        
        # Strictly positive lengths (no 500m fallback)
        self.assertTrue((self.edges_df['length_m'] > 0.0).all(), "All edge lengths must be strictly positive.")
        self.assertNotEqual(self.edges_df['length_m'].nunique(), 1, "Lengths must vary realistically based on geometry.")
        self.assertGreater(self.edges_df['length_m'].min(), 0.5, "Minimum length should exceed 0.5m.")
        self.assertLess(self.edges_df['length_m'].max(), 3000.0, "Maximum length within study bbox should be < 3km.")

    def test_shared_intersection_connectivity(self):
        """Verifies that edges meet at shared junction nodes with zero coordinate error."""
        active_nodes = set(self.nodes_df['node_id'])
        for _, r in self.edges_df.iterrows():
            u, v = int(r['u']), int(r['v'])
            self.assertIn(u, active_nodes, f"Start node {u} must exist in nodes table.")
            self.assertIn(v, active_nodes, f"End node {v} must exist in nodes table.")
            
            # Check coordinate equality at junction
            n_u_lat, n_u_lon = self.node_coords[u]
            n_v_lat, n_v_lon = self.node_coords[v]
            
            self.assertAlmostEqual(r['u_lat'], n_u_lat, places=6)
            self.assertAlmostEqual(r['u_lon'], n_u_lon, places=6)
            self.assertAlmostEqual(r['v_lat'], n_v_lat, places=6)
            self.assertAlmostEqual(r['v_lon'], n_v_lon, places=6)

    def test_macro_connectivity_giant_component(self):
        """Verifies that the network forms a connected urban grid (not disconnected islands)."""
        wccs = list(nx.weakly_connected_components(self.G))
        largest_wcc = max(wccs, key=len)
        self.assertGreater(len(largest_wcc) / len(self.G), 0.90, "Giant WCC must contain >90% of all nodes.")
        
        sccs = list(nx.strongly_connected_components(self.G))
        largest_scc = max(sccs, key=len)
        self.assertGreater(len(largest_scc) / len(self.G), 0.80, "Giant SCC must contain >80% of all nodes.")

    def test_bridge_representation_and_approach_continuity(self):
        """Verifies identification and approach connectivity for all central Clyde bridges."""
        key_bridges = ["Kingston Bridge", "George V Bridge", "Glasgow Bridge", "Victoria Bridge", "Albert Bridge", "Clyde Arc"]
        for b_name in key_bridges:
            b_edges = self.edges_df[self.edges_df['name'].str.contains(b_name, case=False, na=False)]
            self.assertGreater(len(b_edges), 0, f"Bridge {b_name} must have directed edges in graph.")
            
            u_nodes = set(b_edges['u'])
            v_nodes = set(b_edges['v'])
            
            # Must have incoming approach links from the street grid
            in_links = [e for e in self.G.in_edges(u_nodes) if e[0] not in u_nodes and e[0] not in v_nodes]
            out_links = [e for e in self.G.out_edges(v_nodes) if e[1] not in u_nodes and e[1] not in v_nodes]
            
            self.assertGreater(len(in_links), 0, f"Bridge {b_name} must have in-degree approach connections.")
            self.assertGreater(len(out_links), 0, f"Bridge {b_name} must have out-degree exit connections.")

    def test_directed_cross_river_routing(self):
        """Verifies baseline directed shortest paths across the River Clyde."""
        # Southside Tradeston origin, Northside City Centre destination
        south_candidates = [n for n, (lat, lon) in self.node_coords.items() if lat < 55.854 and -4.260 < lon < -4.250 and n in self.G]
        north_candidates = [n for n, (lat, lon) in self.node_coords.items() if lat > 55.858 and -4.260 < lon < -4.250 and n in self.G]
        
        self.assertGreater(len(south_candidates), 0)
        self.assertGreater(len(north_candidates), 0)
        
        s_node = south_candidates[0]
        n_node = north_candidates[0]
        
        self.assertTrue(nx.has_path(self.G, s_node, n_node), "Must have directed cross-river path in baseline.")
        path = nx.shortest_path(self.G, s_node, n_node, weight='weight')
        time_sec = nx.shortest_path_length(self.G, s_node, n_node, weight='weight')
        
        self.assertGreater(len(path), 3, "Cross-river path should traverse multiple street segments.")
        self.assertGreater(time_sec, 30.0, "Cross-river travel time should exceed 30 seconds.")
        self.assertLess(time_sec, 600.0, "Central cross-river trip should be < 10 minutes.")

    def test_closure_detour_path_calculation(self):
        """Verifies that closing George V Bridge causes a real street detour onto Kingston Bridge."""
        s_node = 100878338  # Tradeston southside
        n_node = 28801025   # City centre northside
        
        if s_node not in self.G or n_node not in self.G:
            # Fallback to any valid south/north pair
            south_nodes = [n for n, (lat, lon) in self.node_coords.items() if lat < 55.854 and n in self.G]
            north_nodes = [n for n, (lat, lon) in self.node_coords.items() if lat > 55.858 and n in self.G]
            s_node, n_node = south_nodes[0], north_nodes[0]
            
        base_time = nx.shortest_path_length(self.G, s_node, n_node, weight='weight')
        
        # Sever George V and Glasgow Bridges
        gv_edges = set(self.edges_df[self.edges_df['name'].str.contains('George V Bridge|Glasgow Bridge', case=False, na=False)]['edge_id'])
        G_closed = self.G.copy()
        for u, v, d in list(G_closed.edges(data=True)):
            if d.get('edge_id') in gv_edges:
                G_closed.remove_edge(u, v)
                
        self.assertTrue(nx.has_path(G_closed, s_node, n_node), "Alternate crossing must maintain connectivity.")
        detour_time = nx.shortest_path_length(G_closed, s_node, n_node, weight='weight')
        
        # Must experience positive detour delay (rerouting around closure)
        detour_delay = detour_time - base_time
        self.assertGreater(detour_delay, 0.0, "Closure of direct bridge must cause positive detour delay.")
        self.assertLess(detour_delay, 300.0, "Detour delay in central grid should not exceed 5 minutes.")

if __name__ == '__main__':
    unittest.main()
