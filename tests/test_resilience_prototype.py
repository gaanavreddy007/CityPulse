"""
CITYPULSE - Gate 4 Resilience Feasibility Prototype Unit Tests
Validates graph construction, multi-edge closure, disconnection penalty, and parameter sensitivity.
Runs 100% offline.
"""

import os
import unittest
import pandas as pd
import networkx as nx

from citypulse.resilience.prototype import ResiliencePrototype, ResilienceSimulationResult

class TestResiliencePrototype(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Controlled synthetic network with two river banks and bridge crossings
        cls.edges_df = pd.DataFrame([
            # South Bank
            {"edge_id": "S_ROAD_1", "u": 1, "v": 2, "highway": "primary", "lanes": 2, "length_m": 400.0, "oneway": False, "name": "South Shore", "flow": 500.0},
            # North Bank
            {"edge_id": "N_ROAD_1", "u": 3, "v": 4, "highway": "primary", "lanes": 2, "length_m": 400.0, "oneway": False, "name": "North Shore", "flow": 500.0},
            # Bridge A (Primary crossing - 2 directional edges)
            {"edge_id": "BRIDGE_A_NB", "u": 1, "v": 3, "highway": "motorway", "lanes": 3, "length_m": 600.0, "oneway": True, "name": "Bridge A Northbound", "flow": 1200.0},
            {"edge_id": "BRIDGE_A_SB", "u": 3, "v": 1, "highway": "motorway", "lanes": 3, "length_m": 600.0, "oneway": True, "name": "Bridge A Southbound", "flow": 1200.0},
            # Bridge B (Alternative detour crossing)
            {"edge_id": "BRIDGE_B_NB", "u": 2, "v": 4, "highway": "secondary", "lanes": 1, "length_m": 1200.0, "oneway": True, "name": "Bridge B Northbound", "flow": 200.0},
            {"edge_id": "BRIDGE_B_SB", "u": 4, "v": 2, "highway": "secondary", "lanes": 1, "length_m": 1200.0, "oneway": True, "name": "Bridge B Southbound", "flow": 200.0}
        ])
        cls.prototype = ResiliencePrototype(cls.edges_df, alpha=0.20, beta=2.0)

    def test_baseline_graph_construction(self):
        """Verify directed graph contains correct edges, nodes, and positive impedance weights."""
        G = self.prototype.graph
        self.assertIsInstance(G, nx.DiGraph)
        self.assertEqual(len(G.nodes), 4)
        # 4 one-way bridge edges + 2 two-way roads (4 directed edges) = 8 edges
        self.assertEqual(len(G.edges), 8)
        
        for u, v, data in G.edges(data=True):
            self.assertIn("impedance", data)
            self.assertGreater(data["impedance"], 0.0, "Impedance must be strictly positive")

    def test_multi_edge_bridge_closure(self):
        """Verify closing both directions of Bridge A increases total network impedance."""
        closed_edges = ["BRIDGE_A_NB", "BRIDGE_A_SB"]
        res = self.prototype.simulate_closure("Bridge A Total Closure", closed_edges)
        
        self.assertIsInstance(res, ResilienceSimulationResult)
        self.assertEqual(res.scenario_name, "Bridge A Total Closure")
        self.assertGreater(res.cost_increase_delta, 0.0, "Closure of primary bridge must increase network cost")
        self.assertGreater(res.relative_cost_increase_pct, 0.0)
        self.assertEqual(set(res.closed_edges), set(closed_edges))
        # Network remains connected via Bridge B detour
        self.assertEqual(res.disconnected_od_pairs, 0)

    def test_disconnection_handling(self):
        """Verify closing both Bridge A and Bridge B correctly logs disconnected pairs without crashing."""
        all_bridges = ["BRIDGE_A_NB", "BRIDGE_A_SB", "BRIDGE_B_NB", "BRIDGE_B_SB"]
        res = self.prototype.simulate_closure("Total River Severance", all_bridges)
        
        # Cross-river trips (1->3, 1->4, 2->3, 2->4, 3->1, 3->2, 4->1, 4->2) become disconnected
        self.assertGreater(res.disconnected_od_pairs, 0)
        self.assertGreater(res.closure_total_cost, res.baseline_total_cost)

    def test_parameter_sensitivity(self):
        """Verify sensitivity testing outputs varying cost deltas across BPR parameter values."""
        df_sens = self.prototype.run_sensitivity_test("Bridge A Closure", ["BRIDGE_A_NB", "BRIDGE_A_SB"])
        self.assertEqual(len(df_sens), 9)  # 3 alphas * 3 betas
        self.assertTrue((df_sens["delta_cost"] > 0).all())
        # Higher alpha must yield higher impedance delta for congested links
        delta_low = df_sens.loc[(df_sens["alpha"] == 0.10) & (df_sens["beta"] == 2.0), "delta_cost"].values[0]
        delta_high = df_sens.loc[(df_sens["alpha"] == 0.30) & (df_sens["beta"] == 2.0), "delta_cost"].values[0]
        self.assertGreaterEqual(delta_high, delta_low)

if __name__ == "__main__":
    unittest.main()
