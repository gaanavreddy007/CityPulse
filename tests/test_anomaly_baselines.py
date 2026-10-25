"""
Unit tests for CITYPULSE Anomaly Detection Baselines.
Verifies score direction, output shape, NaN handling, zero-leakage thresholding,
and transparent fallback mechanisms.
"""

import unittest
import numpy as np
import pandas as pd

from citypulse.anomaly.base import BaseAnomalyDetector
from citypulse.anomaly.seasonal_mad import SeasonalMADDetector
from citypulse.anomaly.rolling_zscore import RollingZScoreDetector
from citypulse.anomaly.isolation_forest import IsolationForestDetector, extract_traffic_features
from citypulse.anomaly.ecod import ECODDetector
from citypulse.anomaly.baselines import MissingnessDetector, StaticQuantileDetector

def create_synthetic_hourly_series(
    start_date: str = "2020-01-01 00:00:00",
    periods: int = 168 * 4,  # 4 weeks
    base_flow: float = 50.0,
    noise_std: float = 5.0,
    seed: int = 42
) -> pd.Series:
    """Creates synthetic hourly traffic series with realistic weekly and diurnal profiles."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start=start_date, periods=periods, freq='h')
    
    # Diurnal pattern (peak at 17:00, trough at 03:00)
    hour_effect = np.sin((idx.hour - 8) * np.pi / 12.0) * 25.0
    # Weekend reduction
    weekend_effect = np.where(idx.dayofweek >= 5, -15.0, 0.0)
    
    noise = rng.normal(0, noise_std, size=periods)
    flows = np.maximum(0.0, base_flow + hour_effect + weekend_effect + noise)
    return pd.Series(flows, index=idx, name="flow", dtype="float32")

class TestAnomalyBaselines(unittest.TestCase):
    def setUp(self):
        self.series = create_synthetic_hourly_series(periods=168 * 6, seed=42)
        # Train: first 4 weeks, Val: 5th week, Test: 6th week
        self.train = self.series.iloc[:168 * 4]
        self.val = self.series.iloc[168 * 4:168 * 5]
        self.test = self.series.iloc[168 * 5:]

    def test_seasonal_mad_score_direction_and_shape(self):
        """Higher anomalies must produce strictly higher anomaly scores."""
        detector = SeasonalMADDetector(min_samples_per_bin=2, eps=1.0)
        detector.fit(self.train)
        detector.calibrate_threshold(self.val, contamination_rate=0.05)
        
        test_copy = self.test.copy()
        # Normal score
        normal_scores = detector.score(test_copy)
        self.assertEqual(len(normal_scores), len(test_copy))
        self.assertFalse(normal_scores.isnull().any())
        
        # Inject massive outlier (+300 veh/hr) at index 10
        outlier_copy = test_copy.copy()
        outlier_copy.iloc[10] += 300.0
        outlier_scores = detector.score(outlier_copy)
        
        # Outlier score at index 10 must be strictly greater than normal score
        self.assertGreater(outlier_scores.iloc[10], normal_scores.iloc[10])
        # Prediction at index 10 must be 1 (flagged as anomaly)
        preds = detector.predict(outlier_copy)
        self.assertEqual(preds.iloc[10], 1.0)

    def test_seasonal_mad_nan_handling_and_fallback(self):
        """Missing values must yield NaN scores; sparse histories trigger fallback."""
        # Create sparse train series
        sparse_train = self.train.copy()
        # Drop entire Wednesday 14:00 observations from train
        wed_14_mask = (sparse_train.index.dayofweek == 2) & (sparse_train.index.hour == 14)
        sparse_train.loc[wed_14_mask] = np.nan
        
        detector = SeasonalMADDetector(min_samples_per_bin=5, eps=1.0)
        detector.fit(sparse_train)
        
        # Hour of week for Wed 14:00 is 2*24 + 14 = 62
        self.assertTrue(detector.hourly_profile[62]["is_fallback"])
        
        # Scoring series with NaNs
        eval_series = self.test.copy()
        eval_series.iloc[5] = np.nan
        scores = detector.score(eval_series)
        
        self.assertTrue(np.isnan(scores.iloc[5]))
        preds = detector.predict(eval_series, threshold=3.0)
        self.assertTrue(np.isnan(preds.iloc[5]))
        
        # Verify fallback tracking
        report = detector.fallback_usage_report()
        self.assertIn("fallback_invocations", report)
        self.assertIn("fallback_rate_pct", report)

    def test_rolling_zscore_strictly_causal_no_future_leakage(self):
        """Rolling Z-score must only use past window; modifying future values must not affect current score."""
        detector = RollingZScoreDetector(window_size=24, min_periods=6, eps=1.0)
        detector.fit(self.train)
        detector.calibrate_threshold(self.val, contamination_rate=0.05)
        
        test1 = self.test.copy()
        score1 = detector.score(test1)
        
        # Modify future value at t=20
        test2 = self.test.copy()
        test2.iloc[20] = 999.0
        score2 = detector.score(test2)
        
        # Scores before t=20 must be exactly identical
        np.testing.assert_allclose(score1.iloc[:20].values, score2.iloc[:20].values)
        # Score at t=20 should reflect current flow vs past window
        self.assertGreater(score2.iloc[20], score1.iloc[20])

    def test_isolation_forest_and_ecod_scoring(self):
        """IForest and ECOD wrappers execute properly, return non-null scores on valid flows, and NaN on missing flows."""
        test_data = self.test.copy()
        test_data.iloc[12] = np.nan
        
        for ModelClass in [IsolationForestDetector, ECODDetector]:
            m = ModelClass()
            m.fit(self.train)
            m.calibrate_threshold(self.val, contamination_rate=0.02)
            
            scores = m.score(test_data)
            self.assertEqual(len(scores), len(test_data))
            self.assertTrue(np.isnan(scores.iloc[12]))
            self.assertFalse(scores.drop(scores.index[12]).isnull().any())
            
            # Predict
            preds = m.predict(test_data)
            self.assertTrue(np.isnan(preds.iloc[12]))

    def test_zero_leakage_calibration(self):
        """Thresholds calibrated on validation data must not access test labels or data."""
        detector = SeasonalMADDetector()
        detector.fit(self.train)
        
        # Calibrating with 5% contamination on validation set
        th = detector.calibrate_threshold(self.val, contamination_rate=0.05)
        self.assertIsNotNone(th)
        self.assertGreater(th, 0.0)
        
        # Modifying test data must have zero effect on calibrated threshold
        altered_test = self.test.copy() * 10.0
        preds = detector.predict(altered_test)
        self.assertEqual(detector.threshold, th)

    def test_missingness_and_static_baselines(self):
        """MissingnessDetector flags NaNs as 1.0; StaticQuantileDetector provides static reference."""
        m_det = MissingnessDetector()
        m_det.fit(self.train)
        
        eval_series = self.test.copy()
        eval_series.iloc[3:6] = np.nan
        scores = m_det.score(eval_series)
        
        self.assertEqual(scores.iloc[3], 1.0)
        self.assertEqual(scores.iloc[4], 1.0)
        self.assertEqual(scores.iloc[5], 1.0)
        self.assertEqual(scores.iloc[0], 0.0)
        
        sq_det = StaticQuantileDetector()
        sq_det.fit(self.train)
        sq_det.calibrate_threshold(self.val, contamination_rate=0.05)
        sq_scores = sq_det.score(eval_series)
        self.assertTrue(np.isnan(sq_scores.iloc[3]))

if __name__ == "__main__":
    unittest.main()
