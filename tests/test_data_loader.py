"""
CITYPULSE - Gate 2 Data Loader Unit Tests
Validates loading, parsing, reindexing, reporting, and chronological splitting.
Runs 100% offline.
"""

import os
import unittest
import numpy as np
import pandas as pd

from citypulse.data.schemas import SplitName, SplitBounds, MissingnessReport
from citypulse.data.loader import (
    load_sensor_locations,
    load_sensor_flow,
    reindex_sensor_flow,
    compute_missingness_report,
    split_chronological
)

class TestDataLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.sample_dir = os.path.join(cls.base_dir, "data", "sample")
        cls.loc_path = os.path.join(cls.sample_dir, "locations.csv")
        cls.sample_id = "GA0151_A"

    def test_load_sensor_locations(self):
        """Verify locations loader outputs validated dataframe with 470 sensors."""
        df = load_sensor_locations(self.loc_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 470)
        self.assertIn("id", df.columns)
        self.assertIn("latitude", df.columns)
        self.assertIn("longitude", df.columns)
        self.assertEqual(df["latitude"].isnull().sum(), 0)

    def test_load_sensor_flow(self):
        """Verify flow loader reads sensor flow, checks non-negativity and required columns."""
        df = load_sensor_flow(self.sample_dir, self.sample_id)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 33644)
        self.assertTrue((df["flow"] >= 0).all())
        self.assertTrue((df["time"] >= 0).all() and (df["time"] <= 23).all())

    def test_reindex_sensor_flow(self):
        """Verify reindexing builds exact 35064 continuous hourly timeline with NaNs for gaps."""
        df = load_sensor_flow(self.sample_dir, self.sample_id)
        reindexed = reindex_sensor_flow(df)
        
        self.assertEqual(len(reindexed), 35064)
        self.assertEqual(reindexed.index.freqstr, "h")
        self.assertEqual(reindexed.isnull().sum(), 1420)
        
        # Verify legitimate zero flow is preserved and not converted to NaN
        raw_zeros = (df["flow"] == 0).sum()
        reindexed_zeros = (reindexed == 0).sum()
        self.assertEqual(raw_zeros, reindexed_zeros)

    def test_compute_missingness_report(self):
        """Verify missingness report calculates accurate statistics."""
        df = load_sensor_flow(self.sample_dir, self.sample_id)
        reindexed = reindex_sensor_flow(df)
        report = compute_missingness_report(self.sample_id, df, reindexed)
        
        self.assertIsInstance(report, MissingnessReport)
        self.assertEqual(report.sensor_id, self.sample_id)
        self.assertEqual(report.calendar_hours, 35064)
        self.assertEqual(report.observed_records, 33644)
        self.assertEqual(report.missing_hours, 1420)
        self.assertAlmostEqual(report.missing_percentage, 4.05, delta=0.01)

    def test_split_chronological(self):
        """Verify chronological split partitions data into non-overlapping splits with exact calendar counts."""
        df = load_sensor_flow(self.sample_dir, self.sample_id)
        reindexed = reindex_sensor_flow(df)
        splits = split_chronological(reindexed)
        
        self.assertEqual(len(splits[SplitName.TRAIN]), 17544)
        self.assertEqual(len(splits[SplitName.VAL]), 8760)
        self.assertEqual(len(splits[SplitName.TEST]), 8760)
        
        # Verify split continuity
        self.assertEqual(splits[SplitName.TRAIN].index.max() + pd.Timedelta(hours=1), splits[SplitName.VAL].index.min())
        self.assertEqual(splits[SplitName.VAL].index.max() + pd.Timedelta(hours=1), splits[SplitName.TEST].index.min())

if __name__ == "__main__":
    unittest.main()
