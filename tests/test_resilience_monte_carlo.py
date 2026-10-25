"""
Unit tests for CITYPULSE Monte Carlo Resilience Simulation Engine.
Tests seed determinism, sample convergence, closure edge sets, and impedance units.
"""

import unittest
import pandas as pd
import numpy as np

from citypulse.resilience.monte_carlo import ResilienceMonteCarloEngine

class TestResilienceMonteCarlo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Sample mini-corridor dataframe
        cls.edges_df = pd.DataFrame([
            {"edge_id": "M8_NB", "u": 1, "v": 2, "name": "M8 Kingston NB", "highway": "motorway", "lanes": 5, "length_m": 800, "oneway": True, "flow": 2500, "flow_std": 200},
            {"edge_id": "M8_SB", "u": 2, "v": 1, "name": "M8 Kingston SB", "highway": "motorway", "lanes": 5, "length_m": 800, "oneway": True, "flow": 2500, "flow_std": 200},
            {"edge_id": "SURFACE_NB", "u": 1, "v": 2, "name": "George V Bridge", "highway": "primary", "lanes": 3, "length_m": 900, "oneway": True, "flow": 800, "flow_std": 100},
            {"edge_id": "CROSS_EB", "u": 1, "v": 3, "name": "St Vincent St", "highway": "secondary", "lanes": 2, "length_m": 500, "oneway": True, "flow": 400, "flow_std": 50},
            {"edge_id": "CROSS_WB", "u": 3, "v": 1, "name": "Bothwell St", "highway": "secondary", "lanes": 2, "length_m": 500, "oneway": True, "flow": 400, "flow_std": 50}
        ])

    def test_seed_reproducibility(self):
        """Identical seeds must yield identical Monte Carlo uncertainty interval endpoints."""
        engine1 = ResilienceMonteCarloEngine(self.edges_df, seed=42)
        engine2 = ResilienceMonteCarloEngine(self.edges_df, seed=42)
        
        res1 = engine1.run_monte_carlo("TEST_CLOSURE", ["M8_NB"], n_draws_list=[100])[0]
        res2 = engine2.run_monte_carlo("TEST_CLOSURE", ["M8_NB"], n_draws_list=[100])[0]
        
        self.assertEqual(res1.mean_delta_cost, res2.mean_delta_cost)
        self.assertEqual(res1.ci_lower_2_5, res2.ci_lower_2_5)
        self.assertEqual(res1.ci_upper_97_5, res2.ci_upper_97_5)

    def test_sample_convergence(self):
        """Standard error of the mean must strictly decrease as sample size increases."""
        engine = ResilienceMonteCarloEngine(self.edges_df, seed=123)
        results = engine.run_monte_carlo("TEST_CLOSURE", ["M8_NB"], n_draws_list=[50, 500])
        
        sem_50 = results[0].sem_delta_cost
        sem_500 = results[1].sem_delta_cost
        
        self.assertLess(sem_500, sem_50)
        # Expected reduction is approx sqrt(10) ~ 3.16x
        self.assertAlmostEqual(sem_50 / sem_500, np.sqrt(10), delta=1.5)

    def test_closure_disconnection_penalty(self):
        """When an OD pair is severed by closure, disconnection penalty (3,600s) must be applied."""
        engine = ResilienceMonteCarloEngine(self.edges_df, disconnection_penalty=3600.0, seed=42)
        # Sever node 3 entirely by removing CROSS_EB and CROSS_WB
        results = engine.run_monte_carlo("SEVER_NODE_3", ["CROSS_EB", "CROSS_WB"], n_draws_list=[10])[0]
        
        # Disconnected OD count must be positive
        self.assertGreater(results.disconnected_od_count, 0)
        self.assertGreater(results.mean_delta_cost, 3600.0)

if __name__ == "__main__":
    unittest.main()
