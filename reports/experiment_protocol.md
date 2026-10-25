# Defensible Experimental Protocol: CITYPULSE Minimum Viable Experiment

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026 (Updated with Gate 1 Counts and Gate 5 Bounded Claims)  
**Primary Project Directory:** `C:\Gaanav\Projects\CityPulse`  
**Protocol Status:** Pre-Registration / Protocol Design (No results fabricated)  

---

## 1. Experimental Boundaries & Scientific Claim Decoupling

To prevent overstating findings or conflating synthetic models with operational reality, all experiments are partitioned into strictly decoupled evaluation tracks:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DECOUPLED EVALUATION TRACKS                           │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ Track 1: Synthetic Sensor     │ Evaluated STRICTLY against labels generated │
│ Corruption Benchmark          │ by the mathematical injection process.      │
│                               │ *Claims:* Algorithm sensitivity to defined  │
│                               │ noise and dropouts.                         │
│                               │ *Disclaimed:* Validation against physical   │
│                               │ hardware degradation.                       │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Track 2: Statistical Flow     │ Unsupervised detection of distribution tail │
│ Outlier Characterization      │ events in raw data.                         │
│                               │ *Claims:* Characterization of extreme volume│
│                               │ deviations from seasonal medians.           │
│                               │ *Disclaimed:* Real-world incident detection │
│                               │ (no accident/police logs exist).            │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Track 3: Model-Based Network  │ Evaluates structural graph impedance        │
│ Resilience Sensitivity        │ under multi-edge bridge closures.           │
│                               │ *Claims:* Accessibility proxy degradation.  │
│                               │ *Disclaimed:* Observed travel times.        │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 2. Chronological Data Splitting (Verified Gate 1 Counts)

Partitions are strictly chronological and non-overlapping:

| Split | Date Range (Inclusive) | Calendar Days | Calendar Hours ($H_{\text{cal}}$) | Observed Records ($N_{\text{obs}}$) | Missing Hours ($M_{\text{miss}}$) | Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Train** | `2019-10-01 00:00` to `2021-09-30 23:00` | 731 (leap yr 2020) | **17,544** | 16,639 | 905 (5.16%) | Baseline diurnal profiles and covariance matrices. Zero synthetic perturbations. |
| **Validation** | `2021-10-01 00:00` to `2022-09-30 23:00` | 365 | **8,760** | 8,663 | 97 (1.11%) | Hyperparameter tuning and decision threshold calibration. Zero synthetic perturbations. |
| **Test** | `2022-10-01 00:00` to `2023-09-30 23:00` | 365 | **8,760** | 8,342 (or 8,341) | 418 (or 419) (4.77%) | Held-out evaluation under controlled synthetic corruption injection. |
| **Total** | `2019-10-01 00:00` to `2023-09-30 23:00` | 1,461 | **35,064** | **33,644 (or 33,643)** | **1,420 (or 1,421)** | **4.05%** | Continuous timeline. |

---

## 3. Controlled Synthetic Degradation Mechanisms (Track 1)

Implemented in [`citypulse/data/corruption.py`](file:///C:/Gaanav/Projects/CityPulse/citypulse/data/corruption.py), applied exclusively to explicit copies of the Test split:

1. **MCAR Dropouts:** $p \in \{0.05, 0.15, 0.30\}$, stochastically setting values to `NaN`.
2. **Burst Outages (MNAR):** $\tau \in \{4, 12, 24\}\text{ hours}$, contiguous `NaN` blocks simulating communication drops.
3. **Calibration Drift:** Multiplicative offset $\delta \in \{\pm 15\%, \pm 30\%, \pm 50\%\}$ sustained over $72\text{ hours}$.
4. **Stuck-at-Value:** Forced constant flow ($0.0$ or training mean $\mu_{\text{train}}$) over $24\text{ hours}$.

---

## 4. Anomaly Detection Baselines & Standardized Metrics

### Baseline Models:
1. **Seasonal Median Absolute Deviation (MAD):**
   $$S_{\text{MAD}}(x_t) = \frac{|x_t - \tilde{\mu}_{h(t)}|}{\text{MAD}_{h(t)} + 1.0}$$
   computed per hour of the week $h \in [0, 167]$.
2. **Rolling Window Z-Score:**
   $$S_Z(x_t) = \frac{|x_t - \mu_{t-168:t-1}|}{\sigma_{t-168:t-1} + 1.0}$$
3. **Isolation Forest (`PyOD.models.iforest`):**
   Ensemble of isolation trees partitioning multivariate time features (current flow, lag-1, lag-24, hour, day of week).
4. **ECOD (`PyOD.models.ecod`):**
   Empirical Cumulative Distribution Functions capturing multidimensional tail probabilities.

### Evaluated Metrics (Imbalanced Target Labels):
* **Precision-Recall Area Under Curve (PR-AUC):** Primary threshold-independent metric.
* **F1-Score ($F_1$):** At threshold calibrated on Validation split.
* **Matthews Correlation Coefficient (MCC):** Standard for imbalanced binary evaluation.
* **Synthetic Spatial Consistency Separation Rate:** Measures how frequently an isolated stuck-at-zero sensor fault is distinguished from a spatially correlated corridor flow reduction using adjacent detector correlation.
  *(Note: Replaced previous unsupportable "Incident Disambiguation Rate" because real incident labels do not exist).*

---

## 5. Model-Based Resilience Evaluation Protocol (Track 3)

Implemented in [`citypulse/resilience/prototype.py`](file:///C:/Gaanav/Projects/CityPulse/citypulse/resilience/prototype.py):
1. **Network Representation:** Glasgow road multigraph with capacities from WebTAG standards and free-flow times from OSM lengths/speeds.
2. **Simulated Closures:**
   - *M8 Kingston Bridge Corridor:* Simultaneous removal of `M8_KINGSTON_NB_1`, `M8_KINGSTON_SB_1`, and access ramps.
   - *George V & Glasgow Bridge Pair:* Removal of `GEORGE_V_BRIDGE_SB` and `GLASGOW_BRIDGE_NB`.
3. **Metrics Reported:**
   - $\Delta \mathcal{C}$: System accessibility impedance delta.
   - $N_{\text{disc}}$: Number of severed OD pairs penalized at $3,600\text{ seconds}$.
   - Sensitivity sweep across BPR parameters ($\alpha \in [0.10, 0.30]$, $\beta \in [1.5, 4.0]$).

---

## 6. Reproducibility & Seed Protocol

All stochastic runs (splits, synthetic corruptions, Isolation Forest trees, Monte Carlo draws) are executed across five fixed seeds:
$$\mathcal{S} = \{42, 101, 2024, 777, 999\}$$
All final result tables report mean and standard deviation across seeds ($\mu \pm \sigma$).
