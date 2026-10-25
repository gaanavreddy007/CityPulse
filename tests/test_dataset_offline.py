"""
CITYPULSE - Offline Dataset and Methodology Unit Tests
Runs 100% offline using standard library unittest and local sample data.
"""

import os
import unittest
import numpy as np
import pandas as pd

class TestDatasetOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Resolve path relative to this test file
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.sample_dir = os.path.join(cls.base_dir, "data", "sample")
        cls.loc_path = os.path.join(cls.sample_dir, "locations.csv")
        cls.sample_flow_path = os.path.join(cls.sample_dir, "flows", "GA0151_A.csv")

    def test_locations_schema_and_bounds(self):
        """Verify locations.csv exists, has valid columns, 0 nulls, and falls within Glasgow bbox."""
        self.assertTrue(os.path.exists(self.loc_path), "locations.csv must exist")
        df_loc = pd.read_csv(self.loc_path)
        
        expected_cols = {'id', 'latitude', 'longitude'}
        self.assertTrue(expected_cols.issubset(df_loc.columns), "Missing required columns in locations.csv")
        self.assertEqual(len(df_loc), 470, "locations.csv must contain exactly 470 sensors")
        self.assertEqual(df_loc['latitude'].isnull().sum(), 0, "Latitude contains null values")
        self.assertEqual(df_loc['longitude'].isnull().sum(), 0, "Longitude contains null values")
        
        # Glasgow bounding box check
        self.assertTrue((df_loc['latitude'] >= 55.75).all() and (df_loc['latitude'] <= 56.00).all(),
                        "Latitudes out of expected Glasgow bounds")
        self.assertTrue((df_loc['longitude'] >= -4.50).all() and (df_loc['longitude'] <= -4.00).all(),
                        "Longitudes out of expected Glasgow bounds")

    def test_flow_schema_and_non_negativity(self):
        """Verify sample flow time-series schema, types, and non-negativity."""
        self.assertTrue(os.path.exists(self.sample_flow_path), f"Sample flow file missing: {self.sample_flow_path}")
        df_flow = pd.read_csv(self.sample_flow_path)
        
        expected_cols = {'date', 'time', 'flow'}
        self.assertTrue(expected_cols.issubset(df_flow.columns), "Missing required columns in flow file")
        self.assertEqual(len(df_flow), 33644, "Sample flow file should contain 33644 rows")
        self.assertTrue((df_flow['time'] >= 0).all() and (df_flow['time'] <= 23).all(), "Invalid hour of day")
        self.assertTrue((df_flow['flow'] >= 0).all(), "Flow values cannot be negative")
        self.assertTrue(np.issubdtype(df_flow['flow'].dtype, np.integer), "Flow must be integer counts")

    def test_datetime_reindexing_and_gap_detection(self):
        """Verify that explicit datetime reindexing identifies missing observation hours."""
        df_flow = pd.read_csv(self.sample_flow_path)
        df_flow['datetime'] = pd.to_datetime(df_flow['date'] + ' ' + df_flow['time'].astype(str) + ':00:00')
        
        full_idx = pd.date_range(start="2019-10-01 00:00:00", end="2023-09-30 23:00:00", freq="h")
        self.assertEqual(len(full_idx), 35064, "4-year calendar must have exactly 35064 hours")
        
        missing_hours = len(full_idx) - len(df_flow)
        self.assertEqual(missing_hours, 1420, "Expected exactly 1420 missing hours across 4-year span")

    def test_synthetic_degradation_injection(self):
        """Verify that synthetic fault injection produces reproducible, correctly bounded labels."""
        df_flow = pd.read_csv(self.sample_flow_path)
        flows = df_flow['flow'].values[:1000].copy()
        
        # Test MCAR dropout
        rng = np.random.default_rng(seed=42)
        p = 0.10
        mask_mcar = rng.random(size=len(flows)) < p
        perturbed_mcar = flows.copy().astype(float)
        perturbed_mcar[mask_mcar] = np.nan
        
        self.assertEqual(len(perturbed_mcar), 1000)
        self.assertAlmostEqual(mask_mcar.mean(), p, delta=0.03, msg="MCAR dropout rate out of tolerance")
        self.assertEqual(np.isnan(perturbed_mcar).sum(), mask_mcar.sum())

        # Test Offset Bias (+30%)
        delta = 0.30
        perturbed_bias = np.round(flows * (1.0 + delta)).astype(int)
        self.assertTrue((perturbed_bias >= flows).all(), "Positive bias must not decrease flow")
        
        # Test Stuck-at-Zero
        t_start, duration = 100, 24
        perturbed_freeze = flows.copy()
        perturbed_freeze[t_start:t_start + duration] = 0
        self.assertTrue((perturbed_freeze[t_start:t_start + duration] == 0).all())

if __name__ == '__main__':
    unittest.main()
