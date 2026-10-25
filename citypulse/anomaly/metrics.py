"""
CITYPULSE Anomaly Detection Evaluation Metrics Module.
Calculates PR-AUC, Precision, Recall, F1, MCC, and FPR.
Explicitly identifies and documents undefined metric cases without silent zero-fabrication.
"""

from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_score: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Computes standard binary classification metrics with rigorous handling of edge cases.
    
    Returns:
        Dict containing tp, fp, tn, fn, precision, recall, f1, mcc, fpr, pr_auc,
        and undefined_reasons detailing why any metric could not be computed.
    """
    # Filter out NaNs in true or pred
    valid_mask = ~np.isnan(y_true) & ~np.isnan(y_pred)
    if y_score is not None:
        valid_mask = valid_mask & ~np.isnan(y_score)
        
    yt = y_true[valid_mask].astype(int)
    yp = y_pred[valid_mask].astype(int)
    ys = y_score[valid_mask] if y_score is not None else None

    n_samples = len(yt)
    undefined_reasons: Dict[str, str] = {}

    if n_samples == 0:
        return {
            "n_samples": 0,
            "tp": 0, "fp": 0, "tn": 0, "fn": 0,
            "precision": np.nan, "recall": np.nan, "f1": np.nan,
            "mcc": np.nan, "fpr": np.nan, "pr_auc": np.nan,
            "undefined_reasons": {"all": "Zero valid paired samples"}
        }

    tp = int(np.sum((yt == 1) & (yp == 1)))
    fp = int(np.sum((yt == 0) & (yp == 1)))
    tn = int(np.sum((yt == 0) & (yp == 0)))
    fn = int(np.sum((yt == 1) & (yp == 0)))

    n_pos = tp + fn
    n_neg = tn + fp
    n_pred_pos = tp + fp
    n_pred_neg = tn + fn

    # Precision
    if n_pred_pos == 0:
        precision = np.nan
        undefined_reasons["precision"] = "No positive predictions made (TP + FP == 0)"
    else:
        precision = float(tp / n_pred_pos)

    # Recall
    if n_pos == 0:
        recall = np.nan
        undefined_reasons["recall"] = "No ground-truth positive labels exist (TP + FN == 0)"
    else:
        recall = float(tp / n_pos)

    # F1 Score
    if np.isnan(precision) or np.isnan(recall) or (precision + recall == 0.0):
        f1 = np.nan
        undefined_reasons["f1"] = "Precision or recall is NaN or precision + recall == 0"
    else:
        f1 = float(2.0 * precision * recall / (precision + recall))

    # Matthews Correlation Coefficient (MCC)
    # MCC = (TP*TN - FP*FN) / sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN))
    denom = float(np.sqrt(float(tp + fp) * float(tp + fn) * float(tn + fp) * float(tn + fn)))
    if denom == 0.0:
        mcc = np.nan
        undefined_reasons["mcc"] = "Denominator in MCC calculation is zero (trivial prediction or single-class ground truth)"
    else:
        mcc = float((tp * tn - fp * fn) / denom)

    # False Positive Rate (FPR) = FP / (FP + TN)
    if n_neg == 0:
        fpr = np.nan
        undefined_reasons["fpr"] = "No ground-truth negative labels exist (TN + FP == 0)"
    else:
        fpr = float(fp / n_neg)

    # Precision-Recall AUC (PR-AUC)
    if ys is not None:
        if n_pos == 0 or n_neg == 0:
            pr_auc = np.nan
            undefined_reasons["pr_auc"] = "Ground truth labels are single-class; PR-AUC is undefined"
        else:
            try:
                pr_auc = float(average_precision_score(yt, ys))
            except Exception as e:
                pr_auc = np.nan
                undefined_reasons["pr_auc"] = f"Calculation error: {str(e)}"
    else:
        pr_auc = np.nan
        undefined_reasons["pr_auc"] = "Continuous scores not provided"

    return {
        "n_samples": n_samples,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 4) if not np.isnan(precision) else np.nan,
        "recall": round(recall, 4) if not np.isnan(recall) else np.nan,
        "f1": round(f1, 4) if not np.isnan(f1) else np.nan,
        "mcc": round(mcc, 4) if not np.isnan(mcc) else np.nan,
        "fpr": round(fpr, 4) if not np.isnan(fpr) else np.nan,
        "pr_auc": round(pr_auc, 4) if not np.isnan(pr_auc) else np.nan,
        "undefined_reasons": undefined_reasons
    }
