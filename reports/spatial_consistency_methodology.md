# Spatial Cross-Consistency Methodology & Candidate Pair Audit

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `C:\Gaanav\Projects\CityPulse`  
**Gate Status:** **GATE 1 METHODOLOGY COMPLETED & VERIFIED**  
**Associated Artifact:** [`reports/spatial_consistency_results.csv`](file:///C:/Gaanav/Projects/CityPulse/reports/spatial_consistency_results.csv)  

---

## 1. Executive Summary

A core vulnerability of univariate time-series anomaly detection identified in Phase 3 is **insensitivity to downward calibration drift** (recall $< 0.4\%$). When an inductive loop loses sensitivity, peak traffic counts drop into valid off-peak envelopes, making isolated time-series thresholding structurally blind to negative sensor bias.

To solve this, Phase 4 evaluated the feasibility of **Spatial Cross-Consistency Filtering**. This document establishes:
1. An empirical census of all candidate sensor pairs in the River Clyde corridor network.
2. The directional criteria that distinguish valid corridor neighbors from invalid opposing-carriageway or crossroad sensors.
3. The mathematical formulation of the `SpatialCrossConsistencyDetector`.
4. The essential scientific guardrail distinguishing isolated single-sensor hardware faults from shared macro-corridor traffic shifts.

---

## 2. Sensor Pair Eligibility Criteria & Physical Constraints

In dense urban street grids, Euclidean proximity is not sufficient to establish spatial comparability. Treating two proximate detectors as interchangeable measurements can introduce severe systematic errors if the physical movements differ:

### 2.1 The Opposing Carriageway Trap
In urban radials and motorway dual carriageways, opposing lanes are separated by only 5 to 25 meters:
- **Example 1: St Vincent Street:** `GA0151_C` (Westbound outbound arterial) and `GA0151_D` (Eastbound inbound arterial) are separated by only 24 meters. However, their flow patterns are governed by asymmetric tidal flows: morning rush hour is heavily inbound (Eastbound into CBD), while evening rush hour is outbound (Westbound to M8). Their mean absolute flow difference exceeds **50.9 veh/hr**.
- **Example 2: M8 Kingston Bridge:** `GL0451_B` (Northbound crossing) and `GL0401_R` (Southbound crossing) are separated by a central concrete median. Directional tidal splits and incident queues frequently affect one carriageway while the other flows freely. Mean absolute flow difference exceeds **37.8 veh/hr**.
- **Rule:** Detectors on opposing carriageways must **never** be treated as spatial cross-consistency checks. They are classified as `EXCLUDED_OPPOSING_DIRECTION`.

### 2.2 Conflicting Junction Approaches
Detectors on perpendicular intersection legs (e.g., Newton Street A804 NB vs. St Vincent Street WB at junction `GA0151`) operate on separate signal phase splits. Their instantaneous flows are in opposition (when Newton St has a green phase, St Vincent St has red). They have a mean absolute flow difference of **87.6 veh/hr** and must be classified as `EXCLUDED_DIFFERENT_CORRIDOR`.

---

## 3. Quantitative Census Across Candidate Sensor Pairs

Evaluating all pairwise relationships among the 33 proximate detectors within a 350-meter search radius yielded **134 candidate pairs**:

### Table 1: Pairwise Candidate Relationship Distribution

| Category | Decision Code | Count | Operational Definition & Handling |
| :--- | :--- | :--- | :--- |
| **Eligible Same Edge** | `ELIGIBLE_SAME_EDGE` | **9** | High/Medium confidence detectors matched to the **same directed edge** with compatible approach movements. |
| **Excluded Opposing** | `EXCLUDED_OPPOSING_DIRECTION` | 9 | Detectors on opposing carriageways (NB vs. SB, EB vs. WB); rejected due to inverted diurnal tides. |
| **Excluded Intersecting**| `EXCLUDED_DIFFERENT_CORRIDOR` | 13 | Detectors on perpendicular intersecting streets or parallel non-connected corridors. |
| **Retained Ambiguous** | `RETAINED_AMBIGUOUS` | 103 | Pairs involving at least one detector with ambiguous mapping (e.g. Waterloo Street sub-approach conflicts). |
| **Total Evaluated** | | **134** | Full pairwise audit across central network. |

### Table 2: The 9 Eligible High-Confidence Sensor Pairs

| Pair ID | Sensor 1 | Sensor 2 | Road Edge ID | Corridor Name | Distance | Train Corr ($r$) | Baseline Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P1** | `GA0151_A` | `GC0151_B` | `NEWTON_ST_A804_NB` | Newton Street NB approach | 32.6m | **0.845** | Fully Verified |
| **P2** | `GL0451_B` | `GL0401_V` | `M8_KINGSTON_NB_1` | M8 Kingston Bridge NB | 69.5m | **0.825** | Fully Verified |
| **P3** | `GA1501_T` | `GA1851_A` | `BROOMIELAW_A814` | Broomielaw A814 riverside | 95.1m | **0.856** | Fully Verified |
| **P4** | `GA1051_P` | `GA1361_C` | `BOTHWELL_ST` | Bothwell Street commercial | 99.4m | **0.681** | Fully Verified |
| **P5** | `GA1051_P` | `GA1601_A` | `BOTHWELL_ST` | Bothwell Street commercial | 110.9m | 0.642 | Fully Verified |
| **P6** | `GA1361_C` | `GA1601_A` | `BOTHWELL_ST` | Bothwell Street commercial | 26.4m | 0.704 | Fully Verified |
| **P7** | `GA0151_D` | `GA0401_T` | `ST_VINCENT_ST_EB` | St Vincent St Eastbound | 136.8m | **0.616** | Fully Verified |
| **P8** | `GA0151_C` | `GA0651_A` | `ST_VINCENT_ST_WB` | St Vincent St Westbound | 171.0m | 0.584 | Fully Verified |
| **P9** | `GC4051_D` | `GC4101_V` | `CLYDESIDE_EXPRESSWAY_WB` | Clydeside Expressway WB | 28.3m | **0.578** | Fully Verified |

### Coverage Limitation Finding:
These 9 eligible pairs form **7 distinct directed corridor groups**. However, the remaining **437 suburban sensors** have zero eligible neighbors within this 21-edge network. Spatial cross-consistency is **only feasible within these 7 central corridors** and cannot be applied network-wide without ingesting a full metropolitan road graph.

---

## 4. Mathematical Formulation of the Spatial Detector

The [`SpatialCrossConsistencyDetector`](file:///C:/Gaanav/Projects/CityPulse/citypulse/anomaly/spatial.py) operates by comparing normalized residuals rather than raw flow volumes, ensuring differing lane configurations or baseline capacities do not cause spurious alarms:

### 4.1 Normalized Seasonal Residual
For sensor $s \in \{\text{target}, \text{neighbor}\}$ at timestamp $t$ with hour-of-the-week $h(t) \in [0, 167]$:
$$z_{s, t} = \frac{y_{s, t} - \tilde{y}_{s, h(t)}}{\max(\text{MAD}_{s, h(t)}, \epsilon)}$$
Where:
- $\tilde{y}_{s, h}$ is the historical median for hour-of-week $h$, fitted strictly on Train data ($t \le \text{2021-09-30}$).
- $\text{MAD}_{s, h}$ is the seasonal Median Absolute Deviation ($1.4826 \times \text{median}(|y - \tilde{y}|)$).
- $\epsilon = 1.0\text{ veh/hr}$ prevents division by zero during nocturnal periods.

### 4.2 Spatial Discrepancy Scoring
1. **Two-Sided Discrepancy:**
   $$s_{\text{spatial}, t} = |z_{\text{target}, t} - z_{\text{neighbor}, t}|$$
2. **Downward Drift Mode (Target Sensitivity Loss):**
   When specifically screening for negative sensor bias:
   $$s_{\text{downward}, t} = \max\left(0, \; z_{\text{neighbor}, t} - z_{\text{target}, t}\right)$$
   This score spikes only when the neighbor operates normally or above baseline while the target is depressed.

### 4.3 Zero-Leakage Threshold Calibration
Threshold $\theta_{\text{spatial}}$ is calibrated on uncorrupted Validation data ($t \in [\text{2021-10-01}, \text{2022-09-30}]$) at the 99th percentile ($\alpha = 0.01$ contamination rate):
$$\theta_{\text{spatial}} = \text{Percentile}\left(s_{\text{val}}, 99.0\right)$$
Test data and corruption labels are never accessed during calibration.

---

## 5. Disambiguating Sensor Faults from Shared Corridor Changes

A primary scientific risk in multi-sensor systems is the **False Normal Trap**: assuming that if two adjacent sensors agree, the traffic state must be normal.

```
                            CORRIDOR MONITORING STATE
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
       [High Spatial Discrepancy]              [Low Spatial Discrepancy]
      |z_target - z_neighbor| >= theta       |z_target - z_neighbor| < theta
                    │                                       │
                    ▼                                       ▼
       ISOLATED SENSOR DEGRADATION                Are residuals normal?
         (Hardware Fault / Drift)             ┌─────────────┴─────────────┐
                                              ▼                           ▼
                                            Both ~ 0                  Both << 0
                                         [NORMAL STATE]       SHARED CORRIDOR CHANGE
                                                              (Macro Incident / Closure)
```

The detector implements a multi-state classification method (`classify_state`):
1. **`ISOLATED_SENSOR_DEGRADATION`:** $|z_{\text{target}}| \ge \theta_{\text{univ}}$ AND $s_{\text{spatial}} \ge \theta_{\text{spatial}}$. The target deviates while the neighbor remains normal. Attributed to localized hardware degradation.
2. **`SHARED_CORRIDOR_CHANGE`:** $|z_{\text{target}}| \ge \theta_{\text{univ}}$ AND $|z_{\text{neighbor}}| \ge \theta_{\text{univ}}$ AND $s_{\text{spatial}} < \theta_{\text{spatial}}$. Both sensors drop synchronously. Attributed to real physical congestion, upstream lane closure, or corridor diversion.
3. **`NORMAL`:** Both residuals remain within normal seasonal bounds.

This state machine prevents macro-traffic drops from being falsely attributed to single-sensor hardware failures.
