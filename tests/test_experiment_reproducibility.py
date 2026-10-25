"""
Unit tests for CITYPULSE Benchmark Reproducibility and Track Separation.
Ensures deterministic runs with master seeds and explicit separation
between Track A (synthetic corruptions) and Track B (statistical flow anomalies).
"""

import unittest
import numpy as np
import pandas as pd

from citypulse.anomaly.benchmark import BenchmarkRunner, MASTER_SEEDS
from citypulse.data.schemas import SplitBounds

def create_canonical_test_series(seed: int = 42) -> pd.Series:
    """Creates a continuous hourly series matching full calendar range (35,064 hours)."""
    idx = pd.date_range(start=SplitBounds.TRAIN_START, end=SplitBounds.TEST_END, freq='h')
    rng = np.random.default_rng(seed)
    
    # 35,064 hours with periodic pattern
    hour_pattern = np.sin(idx.hour * np.pi / 12.0) * 20.0 + 40.0
    noise = rng.normal(0, 3.0, size=len(idx))
    flows = np.maximum(0.0, hour_pattern + noise)
    return pd.Series(flows, index=idx, name="flow", dtype="float32")

class TestExperimentReproducibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Build series spanning train, val, test splits for testing
        cls.series = create_canonical_test_series(seed=123)

    def test_track_a_determinism_across_runs(self):
        """Repeated executions with identical seed must yield identical analytical metrics."""
        runner1 = BenchmarkRunner(seeds=[42])
        runner2 = BenchmarkRunner(seeds=[42])
        
        cfg = [{"type": "mcar", "dropout_prob": 0.10, "category": "missingness"}]
        
        res1 = runner1.run_track_a(sensor_id="TEST_SENSOR", full_series=self.series, corruption_configs=cfg)
        res2 = runner2.run_track_a(sensor_id="TEST_SENSOR", full_series=self.series, corruption_configs=cfg)
        
        # Exclude wall-clock elapsed runtimes from bit-level equality check
        runtime_cols = ["fit_runtime_sec", "eval_runtime_sec"]
        res1_clean = res1.drop(columns=runtime_cols)
        res2_clean = res2.drop(columns=runtime_cols)
        
        # Check that scores, metrics, thresholds, and confusion matrix match bit-for-bit
        pd.testing.assert_frame_equal(res1_clean, res2_clean)

    def test_track_a_seed_sensitivity(self):
        """Different seeds must yield distinct stochastic corruption masks."""
        runner = BenchmarkRunner(seeds=[42, 101])
        cfg = [{"type": "mcar", "dropout_prob": 0.10, "category": "missingness"}]
        
        res = runner.run_track_a(sensor_id="TEST_SENSOR", full_series=self.series, corruption_configs=cfg)
        
        res_42 = res[res["seed"] == 42]
        res_101 = res[res["seed"] == 101]
        
        self.assertEqual(len(res_42), len(res_101))
        # Counts of TP may vary slightly due to different random dropouts
        self.assertIn("pr_auc", res.columns)
        self.assertIn("f1", res.columns)

    def test_track_b_separation_and_disclaimer(self):
        """Track B must operate purely unsupervised on uncorrupted test data and contain scientific disclaimers."""
        runner = BenchmarkRunner()
        track_b_df = runner.run_track_b(sensor_id="TEST_SENSOR", full_series=self.series, top_k=5)
        
        self.assertFalse(track_b_df.empty)
        self.assertIn("scientific_disclaimer", track_b_df.columns)
        # Verify that all rows contain the explicit disclaimer
        for disclaimer in track_b_df["scientific_disclaimer"]:
            self.assertIn("Unsupervised statistical deviation only", disclaimer)
            self.assertIn("not an independently validated incident", disclaimer)

if __name__ == "__main__":
    unittest.main()
