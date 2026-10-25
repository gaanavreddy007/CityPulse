"""
CITYPULSE - Gate 1 Temporal Split and Count Validation Tests
Regression tests verifying calendar hours, leap year 2020, split boundaries,
and per-sensor record variation.
Runs 100% offline.
"""

import os
import unittest
import pandas as pd

class TestTemporalSplits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.sample_dir = os.path.join(cls.base_dir, "data", "sample")
        cls.flow_44_path = os.path.join(cls.sample_dir, "flows", "GA0151_A.csv")
        
        # Partition boundary timestamps
        cls.t_start = pd.Timestamp("2019-10-01 00:00:00")
        cls.t_train_end = pd.Timestamp("2021-09-30 23:00:00")
        cls.t_val_start = pd.Timestamp("2021-10-01 00:00:00")
        cls.t_val_end = pd.Timestamp("2022-09-30 23:00:00")
        cls.t_test_start = pd.Timestamp("2022-10-01 00:00:00")
        cls.t_test_end = pd.Timestamp("2023-09-30 23:00:00")

    def test_calendar_hour_counts_and_leap_year(self):
        """Verify calendar-hour math: 2020 is leap year (366 days), total calendar hours = 35064."""
        idx_train = pd.date_range(self.t_start, self.t_train_end, freq="h")
        idx_val = pd.date_range(self.t_val_start, self.t_val_end, freq="h")
        idx_test = pd.date_range(self.t_test_start, self.t_test_end, freq="h")
        idx_full = pd.date_range(self.t_start, self.t_test_end, freq="h")

        # Leap year check: Feb 29, 2020 must exist in train
        self.assertIn(pd.Timestamp("2020-02-29 12:00:00"), idx_train)
        
        # Exact calendar counts
        self.assertEqual(len(idx_train), 17544, "Train calendar hours must equal 17544 (731 days * 24)")
        self.assertEqual(len(idx_val), 8760, "Val calendar hours must equal 8760 (365 days * 24)")
        self.assertEqual(len(idx_test), 8760, "Test calendar hours must equal 8760 (365 days * 24)")
        self.assertEqual(len(idx_full), 35064, "Total calendar hours must equal 35064")
        self.assertEqual(len(idx_train) + len(idx_val) + len(idx_test), len(idx_full))

    def test_split_boundary_non_overlap(self):
        """Verify that split boundaries are strictly non-overlapping and contiguous."""
        # 1-hour step from train end to val start
        step_train_val = self.t_val_start - self.t_train_end
        self.assertEqual(step_train_val, pd.Timedelta(hours=1))
        
        # 1-hour step from val end to test start
        step_val_test = self.t_test_start - self.t_val_end
        self.assertEqual(step_val_test, pd.Timedelta(hours=1))
        
        # Zero intersection between partition indices
        idx_train = set(pd.date_range(self.t_start, self.t_train_end, freq="h"))
        idx_val = set(pd.date_range(self.t_val_start, self.t_val_end, freq="h"))
        idx_test = set(pd.date_range(self.t_test_start, self.t_test_end, freq="h"))
        
        self.assertEqual(len(idx_train.intersection(idx_val)), 0, "Train and Val must not overlap")
        self.assertEqual(len(idx_val.intersection(idx_test)), 0, "Val and Test must not overlap")
        self.assertEqual(len(idx_train.intersection(idx_test)), 0, "Train and Test must not overlap")

    def test_observed_records_vs_calendar_missingness(self):
        """Verify observed record counts and missingness calculation on sample detector."""
        self.assertTrue(os.path.exists(self.flow_44_path))
        df = pd.read_csv(self.flow_44_path)
        df['dt'] = pd.to_datetime(df['date'] + ' ' + df['time'].astype(str) + ':00:00')
        
        obs_train = df[(df['dt'] >= self.t_start) & (df['dt'] <= self.t_train_end)]
        obs_val = df[(df['dt'] >= self.t_val_start) & (df['dt'] <= self.t_val_end)]
        obs_test = df[(df['dt'] >= self.t_test_start) & (df['dt'] <= self.t_test_end)]
        
        # Verified census values for 33644-row detector
        self.assertEqual(len(obs_train), 16639, "Expected exactly 16639 observed train records")
        self.assertEqual(len(obs_val), 8663, "Expected exactly 8663 observed val records")
        self.assertEqual(len(obs_test), 8342, "Expected exactly 8342 observed test records")
        self.assertEqual(len(df), 33644, "Total observed records must equal 33644")
        
        # Missingness per split
        self.assertEqual(17544 - len(obs_train), 905, "Expected 905 missing train hours")
        self.assertEqual(8760 - len(obs_val), 97, "Expected 97 missing val hours")
        self.assertEqual(8760 - len(obs_test), 418, "Expected 418 missing test hours")
        self.assertEqual(35064 - len(df), 1420, "Total missing hours must equal 1420")

    def test_reindex_preserves_zero_flow_as_distinct_from_missing(self):
        """Verify that reindexing sets omitted timestamps to NaN without converting legitimate zero flows to NaN."""
        df = pd.read_csv(self.flow_44_path)
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'].astype(str) + ':00:00')
        
        # Count legitimate zeros in raw data
        raw_zero_count = (df['flow'] == 0).sum()
        self.assertGreater(raw_zero_count, 0, "Raw data must contain legitimate zero flows")
        
        # Reindex to full calendar timeline
        full_idx = pd.date_range(self.t_start, self.t_test_end, freq="h")
        reindexed = df.set_index('datetime').reindex(full_idx)
        
        # Missing timestamps must be NaN
        self.assertEqual(reindexed['flow'].isnull().sum(), 1420, "Reindexed series must contain exactly 1420 NaNs")
        
        # Legitimate zero flows must be preserved as 0.0, NOT converted to NaN
        post_zero_count = (reindexed['flow'] == 0).sum()
        self.assertEqual(raw_zero_count, post_zero_count, "Legitimate zero flows must remain intact")

if __name__ == '__main__':
    unittest.main()
