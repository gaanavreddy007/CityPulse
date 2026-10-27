# Missingness Audit & Data Layer Specification: CITYPULSE

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `./`  
**Gate Status:** **GATE 2 PASSED** (Data layer implemented, validated, and offline tested).

---

## 1. Missingness Profile: Before vs. After Reindexing

### 1.1 The Nature of Missing Data in the Raw Files
In the raw SCOOT flow CSV files (`flows/*.csv`), missing observations are represented as **omitted rows** (implicit missingness) rather than explicit `NaN` or `-999` sentinel values:
* **Before Reindexing:**
  - 108 sensors contain exactly 33,644 rows.
  - 362 sensors contain exactly 33,643 rows (missing `2023-08-13 03:00:00 BST`).
  - There are zero `NaN` values in the raw CSV files.
  - Legitimate zero flows ($q = 0\text{ veh/hr}$) represent between $0.6\%$ and $6.4\%$ of observed records (occurring naturally during overnight hours $01:00 - 05:00$).
* **After Reindexing (`citypulse.data.loader.reindex_sensor_flow`):**
  - An explicit, continuous hourly timeline spanning 35,064 calendar hours (`2019-10-01 00:00:00` to `2023-09-30 23:00:00`) is constructed.
  - Every omitted timestamp is explicitly populated with `np.nan`.
  - Exactly 1,420 NaNs are created for the 108 sensors; exactly 1,421 NaNs are created for the 362 sensors.
  - **Zero traffic values are strictly preserved as `0.0`** and are never conflated with missing data.

### 1.2 Breakdown of Missingness Across Chronological Partitions

| Partition | Calendar Hours ($H_{\text{cal}}$) | Observed Records ($N_{\text{obs}}$) | Missing Hours ($M_{\text{miss}}$) | Missingness (%) | Primary Historical Outage Cause |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train** | **17,544** | 16,639 | **905** | **5.16%** | Concentrated during initial API ingestion rollout (Oct/Nov 2019) |
| **Validation** | **8,760** | 8,663 | **97** | **1.11%** | Minimal routine telecommunication dropouts |
| **Test** | **8,760** | 8,342 (or 8,341) | **418 (or 419)** | **4.77%** | Late summer 2023 municipal server maintenance |
| **Total** | **35,064** | **33,644 (or 33,643)** | **1,420 (or 1,421)** | **4.05%** | Network-wide temporal join artifacts |

---

## 2. Implemented Synthetic Corruption Engine

Implemented in [`citypulse/data/corruption.py`](../citypulse/data/corruption.py), the `CorruptionEngine` applies controlled, mathematically defined perturbations exclusively to explicit copies of the **Test split**:

```
                       TEST SPLIT SERIES (8,760 Hours)
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
   MCAR DROPOUTS               BURST OUTAGES               CALIBRATION DRIFT
   p in {0.05, 0.15, 0.30}     tau in {4h, 12h, 24h}       delta in {+-15%, +-30%, +-50%}
   Stochastic packet loss      Hardware/power cut          Loop resonance drift
```

### 2.1 Corruption Mechanisms and Binary Labeling Rules

| Mechanism | Enum Identifier | Parameterization | Perturbation Transformation | Ground Truth Label Definition |
| :--- | :--- | :--- | :--- | :--- |
| **Missing Completely at Random** | `CorruptionType.MCAR` | $p \in [0.05, 0.30]$ | $x'_t = \text{NaN}$ with probability $p$ on valid observations | $\text{Label}_t = 1$ if forced to NaN; $0$ otherwise |
| **Burst Outage (MNAR)** | `CorruptionType.BURST` | Duration $\tau \in [4, 24]\text{ hrs}$ | $x'_t = \text{NaN} \quad \forall t \in [t_0, t_0 + \tau]$ | $\text{Label}_t = 1$ during window $[t_0, t_0+\tau]$ |
| **Calibration Drift** | `CorruptionType.DRIFT` | Scaling $\delta \in [\pm 0.15, \pm 0.50]$ | $x'_t = \text{round}(x_t \cdot (1 + \delta))$ | $\text{Label}_t = 1$ on scaled valid records |
| **Stuck-at-Zero** | `CorruptionType.STUCK_ZERO` | Duration $\tau \in [12, 48]\text{ hrs}$ | $x'_t = 0.0$ | $\text{Label}_t = 1$ during frozen window |
| **Stuck-at-Mean** | `CorruptionType.STUCK_MEAN` | Duration $\tau \in [12, 48]\text{ hrs}$ | $x'_t = \mu_{\text{train}}$ | $\text{Label}_t = 1$ during frozen window |

### 2.2 Guarantees Enforced in Code:
1. **Zero Raw Overwriting:** Raw files in `data/` are opened read-only.
2. **Explicit Deep Copies:** `inject_*` methods call `.copy()` immediately on series inputs.
3. **Reproducibility:** Seeded with `np.random.default_rng(seed=seed)`. Identical seeds produce bitwise-identical corrupted values and labels (verified in unit tests).
4. **Data Isolation:** `CorruptedDataset` dataclass packages `original_series`, `corrupted_series`, and `labels` together for downstream benchmarking without leakage.
