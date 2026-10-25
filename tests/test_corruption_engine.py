"""
CITYPULSE - Gate 2 Synthetic Corruption Engine Unit Tests
Validates reproducible perturbation generation, separation of copies, and ground-truth labels.
Runs 100% offline.
"""

import os
import unittest
import numpy as np
import pandas as pd

from citypulse.data.schemas import SplitName, CorruptionType
from citypulse.data.loader import load_sensor_flow, reindex_sensor_flow, split_chronological
from citypulse.data.corruption import CorruptionEngine, CorruptedDataset

class TestCorruptionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.sample_dir = os.path.join(cls.base_dir, "data", "sample")
        cls.sample_id = "GA0151_A"
        
        # Load and split to obtain pristine test partition
        raw_df = load_sensor_flow(cls.sample_dir, cls.sample_id)
        reindexed = reindex_sensor_flow(raw_df)
        splits = split_chronological(reindexed)
        cls.test_series = splits[SplitName.TEST]

    def test_mcar_injection(self):
        """Verify MCAR injects stochastic NaNs, produces matching labels, and preserves original series."""
        p = 0.15
        dataset = CorruptionEngine.inject_mcar(self.test_series, dropout_prob=p, seed=42)
        
        self.assertIsInstance(dataset, CorruptedDataset)
        self.assertEqual(dataset.corruption_type, CorruptionType.MCAR)
        self.assertEqual(len(dataset.corrupted_series), len(self.test_series))
        
        # Original series must not be modified in place
        self.assertEqual(self.test_series.isnull().sum(), dataset.original_series.isnull().sum())
        
        # Corrupted entries must equal label 1
        new_nans = dataset.corrupted_series.isnull() & self.test_series.notnull()
        self.assertEqual((dataset.labels == 1).sum(), new_nans.sum())
        self.assertAlmostEqual(new_nans.mean(), p, delta=0.03)

    def test_burst_injection(self):
        """Verify burst outage creates contiguous block of NaNs with exact duration."""
        duration = 24
        dataset = CorruptionEngine.inject_burst(self.test_series, duration_hours=duration, num_outages=2, seed=101)
        
        self.assertEqual(dataset.corruption_type, CorruptionType.BURST)
        self.assertEqual((dataset.labels == 1).sum(), duration * 2)
        
        # Check contiguous blocks
        label_diff = dataset.labels.diff().abs()
        # Each block has an entry (1) and exit (1)
        self.assertLessEqual(label_diff.sum(), 4)

    def test_drift_injection(self):
        """Verify calibration drift applies multiplicative scaling without negative values."""
        scale = 0.40
        duration = 72
        dataset = CorruptionEngine.inject_drift(self.test_series, scale_delta=scale, duration_hours=duration, seed=777)
        
        self.assertEqual(dataset.corruption_type, CorruptionType.DRIFT)
        corrupted_vals = dataset.corrupted_series.loc[dataset.labels == 1]
        orig_vals = dataset.original_series.loc[dataset.labels == 1]
        
        # For non-null values, corrupted must be >= original
        valid = orig_vals.notnull()
        self.assertTrue((corrupted_vals[valid] >= orig_vals[valid]).all())

    def test_stuck_value_injection(self):
        """Verify stuck-at-value forces constant output (zero or mean) over window."""
        duration = 48
        # Stuck at zero
        ds_zero = CorruptionEngine.inject_stuck_value(self.test_series, mode="zero", duration_hours=duration, seed=999)
        self.assertEqual(ds_zero.corruption_type, CorruptionType.STUCK_ZERO)
        self.assertTrue((ds_zero.corrupted_series.loc[ds_zero.labels == 1] == 0.0).all())
        
        # Stuck at mean
        ds_mean = CorruptionEngine.inject_stuck_value(self.test_series, mode="mean", duration_hours=duration, seed=999)
        self.assertEqual(ds_mean.corruption_type, CorruptionType.STUCK_MEAN)
        expected_mean = float(self.test_series.mean(skipna=True))
        self.assertTrue((ds_mean.corrupted_series.loc[ds_mean.labels == 1] == expected_mean).all())

    def test_reproducibility_with_seed(self):
        """Verify identical seed produces identical corrupted data and labels."""
        ds1 = CorruptionEngine.inject_mcar(self.test_series, dropout_prob=0.20, seed=12345)
        ds2 = CorruptionEngine.inject_mcar(self.test_series, dropout_prob=0.20, seed=12345)
        
        pd.testing.assert_series_equal(ds1.corrupted_series, ds2.corrupted_series)
        pd.testing.assert_series_equal(ds1.labels, ds2.labels)

if __name__ == "__main__":
    unittest.main()
