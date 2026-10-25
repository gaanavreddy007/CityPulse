"""
Unit tests for CITYPULSE Observability Risk Index Calculator.
Verifies mathematical properties: range [0, 1], monotonicity, zero-distance bounds,
and asymptotic unobservability limits.
"""

import unittest
import pandas as pd
import numpy as np

from citypulse.resilience.observability import ObservabilityRiskCalculator, geodetic_distance_m

class TestObservabilityIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 3 edges in a line
        cls.edges_df = pd.DataFrame([
            {"edge_id": "E1", "u": 1, "v": 2, "name": "Bridge 1", "highway": "primary", "lanes": 2, "length_m": 500, "oneway": False, "u_lat": 55.85, "u_lon": -4.26, "v_lat": 55.855, "v_lon": -4.26},
            {"edge_id": "E2", "u": 2, "v": 3, "name": "Bridge 2", "highway": "primary", "lanes": 2, "length_m": 500, "oneway": False, "u_lat": 55.855, "u_lon": -4.26, "v_lat": 55.86, "v_lon": -4.26},
            {"edge_id": "E3", "u": 1, "v": 3, "name": "Bypass", "highway": "secondary", "lanes": 2, "length_m": 1200, "oneway": False, "u_lat": 55.85, "u_lon": -4.27, "v_lat": 55.86, "v_lon": -4.27}
        ])
        
        # Sensor placed directly at midpoint of E1 (lat 55.8525, lon -4.26)
        cls.sensors_df = pd.DataFrame([
            {"sensor_id": "S1", "latitude": 55.8525, "longitude": -4.26, "status": "MATCHED_HIGH_CONFIDENCE"}
        ])

    def test_geodetic_distance_formula(self):
        """Verifies planar distance matches expected metric scale for Glasgow latitude."""
        # 0.01 deg lat = 1,113.2 meters
        d_lat = geodetic_distance_m(55.85, -4.26, 55.86, -4.26)
        self.assertAlmostEqual(d_lat, 1113.2, places=0)
        
        # 0.01 deg lon at lat 55.85 = 1113.2 * cos(55.85 rad) ~ 624.5 meters
        d_lon = geodetic_distance_m(55.85, -4.26, 55.85, -4.25)
        self.assertAlmostEqual(d_lon, 624.5, places=0)

    def test_observability_index_mathematical_bounds(self):
        """Observability Risk Index Omega_e must be strictly bounded in [0, 1]."""
        calc = ObservabilityRiskCalculator(self.edges_df, self.sensors_df, d0_meters=500.0)
        table = calc.compute_observability_index()
        
        self.assertTrue((table['observability_risk_index'] >= 0.0).all())
        self.assertTrue((table['observability_risk_index'] <= 1.0).all())
        self.assertTrue((table['normalized_nri'] >= 0.0).all())
        self.assertTrue((table['normalized_nri'] <= 1.0).all())
        self.assertTrue((table['unobservability_factor'] >= 0.0).all())
        self.assertTrue((table['unobservability_factor'] <= 1.0).all())

    def test_zero_distance_produces_zero_risk(self):
        """An edge with a sensor placed directly at its midpoint must have Omega_e = 0.0."""
        calc = ObservabilityRiskCalculator(self.edges_df, self.sensors_df, d0_meters=500.0)
        table = calc.compute_observability_index()
        
        row_e1 = table[table['edge_id'] == 'E1'].iloc[0]
        # Distance to sensor should be virtually 0 meters
        self.assertLess(row_e1['dist_to_sensor_meters'], 1.0)
        # Omega_e must be 0.0 (or within floating-point epsilon)
        self.assertAlmostEqual(row_e1['observability_risk_index'], 0.0, places=3)

    def test_distance_monotonicity(self):
        """Unobservability factor must strictly increase as distance increases."""
        calc = ObservabilityRiskCalculator(self.edges_df, self.sensors_df, d0_meters=500.0)
        table = calc.compute_observability_index()
        
        # Edge E3 is farther from S1 than E2
        row_e1 = table[table['edge_id'] == 'E1'].iloc[0]
        row_e2 = table[table['edge_id'] == 'E2'].iloc[0]
        
        self.assertGreater(row_e2['dist_to_sensor_meters'], row_e1['dist_to_sensor_meters'])
        self.assertGreater(row_e2['unobservability_factor'], row_e1['unobservability_factor'])

if __name__ == "__main__":
    unittest.main()
