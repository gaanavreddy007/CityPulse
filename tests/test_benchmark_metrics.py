"""
Unit tests for CITYPULSE Metric Calculations.
Tests precision, recall, F1, MCC, FPR, PR-AUC, and verified handling of undefined cases.
"""

import unittest
import numpy as np
from citypulse.anomaly.metrics import compute_classification_metrics

class TestBenchmarkMetrics(unittest.TestCase):
    def test_perfect_classification(self):
        """Perfect predictions must yield 1.0 for Precision, Recall, F1, MCC, and PR-AUC."""
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_pred = np.array([0, 0, 0, 1, 1, 1])
        y_score = np.array([0.1, 0.2, 0.15, 0.9, 0.85, 0.95])
        
        metrics = compute_classification_metrics(y_true, y_pred, y_score)
        
        self.assertEqual(metrics["tp"], 3)
        self.assertEqual(metrics["fp"], 0)
        self.assertEqual(metrics["tn"], 3)
        self.assertEqual(metrics["fn"], 0)
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(metrics["f1"], 1.0)
        self.assertEqual(metrics["mcc"], 1.0)
        self.assertEqual(metrics["fpr"], 0.0)
        self.assertEqual(metrics["pr_auc"], 1.0)
        self.assertEqual(len(metrics["undefined_reasons"]), 0)

    def test_imperfect_classification(self):
        """Verifies exact manual calculation on a known confusion matrix."""
        # y_true: 4 positives, 4 negatives
        y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0])
        # y_pred: 3 TPs, 1 FN, 1 FP, 3 TNs
        y_pred = np.array([1, 1, 1, 0, 1, 0, 0, 0])
        y_score = np.array([0.8, 0.7, 0.6, 0.4, 0.65, 0.2, 0.1, 0.3])
        
        metrics = compute_classification_metrics(y_true, y_pred, y_score)
        
        self.assertEqual(metrics["tp"], 3)
        self.assertEqual(metrics["fp"], 1)
        self.assertEqual(metrics["fn"], 1)
        self.assertEqual(metrics["tn"], 3)
        
        expected_prec = 3.0 / (3.0 + 1.0)  # 0.75
        expected_rec = 3.0 / (3.0 + 1.0)   # 0.75
        expected_f1 = 0.75
        # MCC = (3*3 - 1*1) / sqrt(4 * 4 * 4 * 4) = 8 / 16 = 0.5
        expected_mcc = 0.5
        # FPR = FP / (FP + TN) = 1 / (1 + 3) = 0.25
        expected_fpr = 0.25
        
        self.assertAlmostEqual(metrics["precision"], expected_prec, places=4)
        self.assertAlmostEqual(metrics["recall"], expected_rec, places=4)
        self.assertAlmostEqual(metrics["f1"], expected_f1, places=4)
        self.assertAlmostEqual(metrics["mcc"], expected_mcc, places=4)
        self.assertAlmostEqual(metrics["fpr"], expected_fpr, places=4)

    def test_undefined_precision_when_no_positive_predictions(self):
        """When model predicts zero anomalies, precision must be NaN with documented reason."""
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 0, 0, 0])  # zero positive predictions
        
        metrics = compute_classification_metrics(y_true, y_pred)
        
        self.assertTrue(np.isnan(metrics["precision"]))
        self.assertEqual(metrics["recall"], 0.0)
        self.assertTrue(np.isnan(metrics["f1"]))
        self.assertIn("precision", metrics["undefined_reasons"])

    def test_undefined_recall_when_no_ground_truth_positives(self):
        """When dataset has zero positive labels, recall and PR-AUC must be NaN with documented reason."""
        y_true = np.array([0, 0, 0, 0])
        y_pred = np.array([0, 1, 0, 0])
        y_score = np.array([0.1, 0.8, 0.2, 0.3])
        
        metrics = compute_classification_metrics(y_true, y_pred, y_score)
        
        self.assertTrue(np.isnan(metrics["recall"]))
        self.assertTrue(np.isnan(metrics["pr_auc"]))
        self.assertIn("recall", metrics["undefined_reasons"])
        self.assertIn("pr_auc", metrics["undefined_reasons"])

    def test_nan_filtering_in_metric_computation(self):
        """NaN values in y_true, y_pred, or y_score must be cleanly filtered before metric computation."""
        y_true = np.array([0, 1, 0, 1, np.nan, 0])
        y_pred = np.array([0, 1, 0, 0, 1, np.nan])
        y_score = np.array([0.1, 0.9, 0.2, 0.4, 0.8, 0.3])
        
        # Valid pairs at indices 0, 1, 2, 3 (4 samples)
        metrics = compute_classification_metrics(y_true, y_pred, y_score)
        self.assertEqual(metrics["n_samples"], 4)

if __name__ == "__main__":
    unittest.main()
