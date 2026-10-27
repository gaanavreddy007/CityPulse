# Anomaly Detection Experiment Protocol: CITYPULSE Phase 3

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `./`  
**Protocol Version:** 1.0 (Phase 3 Baseline Benchmark)  

---

## 1. Overview and Core Objectives

This protocol defines the formal, reproducible experimental benchmark for traffic flow anomaly detection in CITYPULSE Phase 3. The objectives are:
1. Benchmark four primary baseline algorithms alongside two reference lower-bound baselines on Glasgow SCOOT hourly traffic data.
2. Formally decouple evaluation into two independent tracks:
   - **Track A:** Synthetic Corruption Detection with known ground-truth labels.
   - **Track B:** Unsupervised Statistical Flow Anomaly Discovery on raw, uncorrupted observations.
3. Enforce strict mathematical guards against test leakage, metric fabrication, and false equivalence between missing data and numeric outliers.

---

## 2. Models and Parameter Configurations

### 2.1 Model Specifications

| Model Name | Class / Package | Input Features & Units | Primary Hyperparameters | Fallback Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **`Missingness_Detector`** | Reference Baseline (`citypulse.anomaly.baselines`) | Flow missingness indicator (`pd.isna(flow)`) | None (deterministic rule) | None (always computable) |
| **`Static_Quantile`** | Simple Baseline (`citypulse.anomaly.baselines`) | Hourly flow volume ($y_t$, veh/hr) | IQR scaling floor $\epsilon = 1.0$ | None (uses global train IQR) |
| **`Seasonal_MAD`** | Baseline 1 (`citypulse.anomaly.seasonal_mad`) | Hourly flow volume ($y_t$, veh/hr) | $T = 168\text{h}$ (weekly), $N_{\min} = 10$, scale $= 1.4826$, $\epsilon = 1.0$ | Tier 1: Hour-of-day ($24\text{h}$); Tier 2: Global train median & MAD |
| **`Rolling_ZScore`** | Baseline 2 (`citypulse.anomaly.rolling_zscore`) | Hourly flow volume ($y_t$, veh/hr) | Window $W = 168\text{h}$, $N_{\min} = 12$, $\epsilon = 1.0$, retrospective shift | Fallback to global train mean & std when valid window samples $< 12$ |
| **`Isolation_Forest`** | Baseline 3 (`citypulse.anomaly.isolation_forest`, PyOD) | 7 features: flow, $\sin/\cos(24\text{h})$, $\sin/\cos(7\text{d})$, $\Delta y_{1\text{h}}$, $\Delta y_{24\text{h}}$ | $n_{\text{estimators}} = 100$, contamination $= 0.01$, random seed $\in \mathcal{S}$ | None (PyOD default tree partitioning) |
| **`ECOD`** | Baseline 4 (`citypulse.anomaly.ecod`, PyOD) | 7 features: flow, $\sin/\cos(24\text{h})$, $\sin/\cos(7\text{d})$, $\Delta y_{1\text{h}}$, $\Delta y_{24\text{h}}$ | Non-parametric empirical CDF tail estimation, contamination $= 0.01$ | None (parameter-free $O(nd)$ tail estimator) |

### 2.2 Feature Engineering and Unit Standards
- **Flow Volume ($y_t$):** Non-negative integer vehicle counts converted to hourly float rates (`veh/hr`).
- **Cyclical Temporal Encodings:**
  $$\text{hour\_sin} = \sin\left(\frac{2\pi \cdot \text{hour}}{24}\right), \quad \text{hour\_cos} = \cos\left(\frac{2\pi \cdot \text{hour}}{24}\right)$$
  $$\text{day\_sin} = \sin\left(\frac{2\pi \cdot \text{dayofweek}}{7}\right), \quad \text{day\_cos} = \cos\left(\frac{2\pi \cdot \text{dayofweek}}{7}\right)$$
- **Retrospective Differences:**
  $$\Delta y_{1\text{h}}(t) = y_t - y_{t-1}, \quad \Delta y_{24\text{h}}(t) = y_t - y_{t-24}$$
  Both differences strictly utilize causal backward lags to prevent lookahead leakage.

### 2.3 Treatment of Missing Data (Anti-Fabrication Policy)
1. **No Silent Zero Imputation:** Missing observations (`NaN`) must never be replaced with `0.0`. In SCOOT detector records, zero is a valid empirical observation indicating empty roads during nocturnal hours.
2. **Missing Flow in Numeric Models:** If an observation at timestamp $t$ is `NaN`, numeric models output `NaN` anomaly scores.
3. **Scoring for Benchmark Evaluation:** When computing benchmark ranking metrics (PR-AUC, F1), numeric models are evaluated on whether they detect numeric corruptions; missing timestamps are populated with `0.0` detection confidence so that numeric models receive zero unearned credit for missingness.

---

## 3. Data Partitions and Zero-Leakage Protocol

All experiments strictly adhere to the chronological split boundaries validated in Gate 1:

```
┌──────────────────────────────────────┬──────────────────┬──────────────────┐
│                TRAIN                 │    VALIDATION    │       TEST       │
│        (Model Parameter Fit)         │  (Threshold Cal) │ (Evaluation Only)│
├──────────────────────────────────────┼──────────────────┼──────────────────┤
│ 2019-10-01 00:00 to 2021-09-30 23:00 │ 2021-10-01 00:00 │ 2022-10-01 00:00 │
│               (17,544 h)             │ to 2022-09-30    │ to 2023-09-30    │
│                                      │    (8,760 h)     │    (8,760 h)     │
└──────────────────────────────────────┴──────────────────┴──────────────────┘
```

### Threshold Calibration Procedure
1. Model parameters (medians, MADs, rolling parameters, isolation trees, CDFs) are fitted exclusively on the uncorrupted **Train** partition ($t \le \text{2021-09-30 23:00}$).
2. Raw anomaly scores are evaluated across the uncorrupted **Validation** partition ($t \in [\text{2021-10-01 00:00}, \text{2022-09-30 23:00}]$).
3. The binary decision threshold $\theta$ is set to the $(1 - \alpha)$ percentile of valid validation scores, with $\alpha = 0.01$ (nominal 1% false-positive rate / 99th percentile):
   $$\theta = \text{Percentile}(s_{\text{val}}, 99.0)$$
4. Under no circumstances is test data or test ground truth consulted during threshold selection.

---

## 4. Track A: Synthetic Corruption Experiment Design

Synthetic corruption injection is applied exclusively to test data copies using the 5 master random seeds:
$$\mathcal{S} = \{42, 101, 2024, 777, 999\}$$

### 4.1 Supported Corruption Types and Severities

1. **Missing Completely at Random (MCAR):**
   - *Mechanism:* Stochastic dropout of observed timestamps to `NaN`.
   - *Severities:* $p \in \{0.05, 0.10, 0.20\}$ (5%, 10%, 20% dropout rates).
   - *Category:* `missingness`.
2. **Burst Communication Outage:**
   - *Mechanism:* Contiguous block dropout to `NaN` simulating localized telemetry hardware or backhaul network failures.
   - *Severities:* Durations $\in \{4\text{h}, 12\text{h}, 24\text{h}\}$.
   - *Category:* `missingness`.
3. **Calibration Drift / Multiplicative Bias:**
   - *Mechanism:* Scaling of observed non-null flows by $(1 + \Delta_{\text{scale}})$ over a sustained 1-week ($168\text{h}$) window:
     $$y_{\text{corrupt}}(t) = \max\left(0, \text{round}\left(y_{\text{orig}}(t) \times (1 + \Delta_{\text{scale}})\right)\right)$$
   - *Severities:* $\Delta_{\text{scale}} \in \{+0.30, -0.30\}$ (+30% positive drift, -30% negative drift).
   - *Category:* `numeric`.
4. **Stuck-at-Zero (Sensor Dropout):**
   - *Mechanism:* Forcing flow to $0.0$ continuously for $24\text{h}$ during daytime/operational hours.
   - *Category:* `numeric`.
5. **Stuck-at-Mean (Sensor Freezing):**
   - *Mechanism:* Forcing sensor flow to the historical sensor mean continuously for $24\text{h}$.
   - *Category:* `numeric`.

---

## 5. Track B: Unsupervised Statistical Flow Anomaly Protocol

1. **Data Source:** Raw, uncorrupted Test split ($t \in [\text{2022-10-01}, \text{2023-09-30}]$).
2. **Detection Task:** Identify the top $K=10$ highest anomaly scores per model and sensor.
3. **Calendar Cross-Referencing:** Document day of week, time of day, whether the event falls on a weekend, bank holiday, or major cultural event (e.g., Hogmanay).
4. **Scientific Boundaries:**
   - Observations identified in Track B are strictly reported as *unsupervised statistical deviations*.
   - Because no external, independent incident log, accident register, or hardware maintenance log exists for Glasgow SCOOT loops during 2022–2023, these events must **never** be claimed as confirmed traffic accidents or validated physical equipment failures.

---

## 6. Evaluation Metrics & Undefined Case Policy

For every model, corruption type, and seed, the following metrics are reported:
- **Precision-Recall AUC (PR-AUC):** Average Precision across the continuous score spectrum.
- **Precision, Recall, F1:** Computed at the validation-calibrated threshold $\theta$.
- **Matthews Correlation Coefficient (MCC):** Balanced correlation metric for imbalanced classes.
- **False Positive Rate (FPR):** $FP / (FP + TN)$.
- **Runtime:** `fit_runtime_sec` and `eval_runtime_sec`.

### Handling Undefined Metrics:
- If a model makes zero positive predictions ($TP + FP = 0$), Precision is recorded as `NaN` (with `"precision": "No positive predictions made"` in `undefined_reasons`), rather than falsely fabricated as `0.0`.
- If no positive labels exist in the ground truth ($TP + FN = 0$), Recall and PR-AUC are recorded as `NaN`.
- In all aggregated summary tables, `NaN` values are excluded from means with the sample count documented.
