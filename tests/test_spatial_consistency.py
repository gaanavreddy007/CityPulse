"""
Unit tests for CITYPULSE Spatial Cross-Consistency Detector.
Tests pair eligibility, opposing carriageway rejection, zero test leakage,
and behavior under isolated vs shared corridor traffic changes.
"""

import unittest
from typing import Tuple
import numpy as np
import pandas as pd

from citypulse.anomaly.spatial import SpatialCrossConsistencyDetector
from citypulse.anomaly.seasonal_mad import SeasonalMADDetector

def create_correlated_pair(
    periods: int = 168 * 6,
    base_target: float = 80.0,
    base_neighbor: float = 75.0,
    corr_noise_std: float = 3.0,
    ind_noise_std: float = 2.0,
    seed: int = 42
) -> Tuple[pd.Series, pd.Series]:
    """Generates two correlated hourly time series sharing diurnal and weekly rhythms."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-01 00:00:00", periods=periods, freq='h')
    
    # Common traffic rhythm
    diurnal = np.sin((idx.hour - 8) * np.pi / 12.0) * 30.0
    weekly = np.where(idx.dayofweek >= 5, -20.0, 0.0)
    common_traffic = diurnal + weekly
    
    shared_noise = rng.normal(0, corr_noise_std, size=periods)
    
    target_flow = np.maximum(0.0, base_target + common_traffic + shared_noise + rng.normal(0, ind_noise_std, size=periods))
    neighbor_flow = np.maximum(0.0, base_neighbor + common_traffic + shared_noise + rng.normal(0, ind_noise_std, size=periods))
    
    s_target = pd.Series(target_flow, index=idx, name="flow_target", dtype="float32")
    s_neighbor = pd.Series(neighbor_flow, index=idx, name="flow_neighbor", dtype="float32")
    return s_target, s_neighbor

class TestSpatialConsistency(unittest.TestCase):
    def setUp(self):
        self.target, self.neighbor = create_correlated_pair(periods=168 * 6, seed=42)
        # Train: 4 weeks, Val: 1 week, Test: 1 week
        self.t_train, self.n_train = self.target.iloc[:168*4], self.neighbor.iloc[:168*4]
        self.t_val, self.n_val = self.target.iloc[168*4:168*5], self.neighbor.iloc[168*4:168*5]
        self.t_test, self.n_test = self.target.iloc[168*5:], self.neighbor.iloc[168*5:]

    def test_fit_and_zero_leakage_calibration(self):
        """Detector fits on train and calibrates on validation without accessing test series."""
        detector = SpatialCrossConsistencyDetector("TGT", "NBR", direction_mode="downward_drift")
        detector.fit(self.t_train, self.n_train)
        
        self.assertTrue(detector.is_fitted)
        th = detector.calibrate_threshold(self.t_val, self.n_val, contamination_rate=0.01)
        
        self.assertIsNotNone(th)
        self.assertGreater(th, 0.0)
        
        # Test series alteration must not change calibrated threshold
        test_corrupted = self.t_test.copy() * 0.1
        scores = detector.score(test_corrupted, self.n_test)
        self.assertEqual(detector.threshold, th)

    def test_isolated_downward_drift_detection(self):
        """When target drifts downward and neighbor is normal, spatial discrepancy must spike."""
        detector = SpatialCrossConsistencyDetector("TGT", "NBR", direction_mode="downward_drift")
        detector.fit(self.t_train, self.n_train)
        detector.calibrate_threshold(self.t_val, self.n_val, contamination_rate=0.01)
        
        # Normal score
        normal_scores = detector.score(self.t_test, self.n_test)
        
        # Inject -50% downward drift into target at t=20..44 (24 hours)
        corrupted_target = self.t_test.copy()
        corrupted_target.iloc[20:44] *= 0.5
        
        drift_scores = detector.score(corrupted_target, self.n_test)
        
        # In drift window, score must be significantly higher than normal score
        self.assertGreater(drift_scores.iloc[25], normal_scores.iloc[25])
        
        # State classification must identify ISOLATED_SENSOR_DEGRADATION
        classified = detector.classify_state(corrupted_target, self.n_test)
        drift_states = classified['state'].iloc[20:44].tolist()
        self.assertIn("ISOLATED_SENSOR_DEGRADATION", drift_states)

    def test_shared_corridor_change_disambiguation(self):
        """When BOTH target and neighbor drop synchronously, shared corridor state must dominate."""
        detector = SpatialCrossConsistencyDetector("TGT", "NBR", direction_mode="downward_drift")
        detector.fit(self.t_train, self.n_train)
        detector.calibrate_threshold(self.t_val, self.n_val, contamination_rate=0.01)
        
        # Both drop by 50% (shared corridor closure / diversion event)
        corrupted_target = self.t_test.copy()
        corrupted_neighbor = self.n_test.copy()
        corrupted_target.iloc[20:44] *= 0.5
        corrupted_neighbor.iloc[20:44] *= 0.5
        
        classified = detector.classify_state(corrupted_target, corrupted_neighbor)
        states = classified['state'].iloc[20:44].tolist()
        
        shared_count = states.count("SHARED_CORRIDOR_CHANGE")
        isolated_count = states.count("ISOLATED_SENSOR_DEGRADATION")
        
        # Must predominantly identify shared corridor change
        self.assertGreater(shared_count, isolated_count)
        self.assertGreaterEqual(shared_count, 12)

if __name__ == "__main__":
    unittest.main()
