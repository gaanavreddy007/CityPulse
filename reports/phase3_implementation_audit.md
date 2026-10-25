# Phase 3 Implementation Audit & Pre-Execution Verification

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `C:\Gaanav\Projects\CityPulse`  
**Phase Status:** **PHASE 3 AUDIT COMPLETED & VERIFIED**  

---

## 1. Executive Summary

Prior to implementing the Phase 3 anomaly detection benchmark and experimental evaluation, a rigorous audit of the code, data layer, road network graph, and mathematical assumptions was conducted. This audit resolved four outstanding questions regarding temporal conventions, network spatial coverage, sensor-to-edge matching rates, and resilience parameter provenance.

All findings are backed by automated offline regression tests and empirical code verification.

---

## 2. Temporal Convention and the 2023-08-13 Divergence

### 2.1 Fixed 24-Hour Calendar vs. Daylight Saving Time (DST)
A key operational ambiguity in urban traffic datasets is whether timestamps represent wall-clock local time (e.g., GMT/BST with seasonal clock shifts) or a continuous timeline.

1. **DST Transition Day Analysis:**
   In the UK, daylight saving time shifts occur on the last Sunday in March (clock jumps from 01:00 to 02:00, creating a 23-hour day in local clock time) and the last Sunday in October (clock jumps from 02:00 back to 01:00, creating a 25-hour day with a duplicate 01:00 hour in naive local time).
   
   An inspection of the raw Glasgow SCOOT dataset across all eight transition dates during the 4-year study period (`2019-10-27`, `2020-03-29`, `2020-10-25`, `2021-03-28`, `2021-10-31`, `2022-03-27`, `2022-10-30`, `2023-03-26`) revealed:
   - On **every** transition date, the raw detector CSV logs exactly **24 rows**, with integer hours indexed from `0` to `23` (`time` $\in [0, 23]$).
   - Zero duplicate timestamps occur on October transition dates.
   - Zero omitted hours occur on March transition dates.
   
   **Conclusion:** The raw data timeline operates on a continuous, fixed 24-hour daily progression (equivalent to UTC / timezone-naive continuous standard time). It does not track wall-clock local daylight saving shifts.

### 2.2 Root Cause of the 2023-08-13 at 03:00 Divergence
The Gate 1 census established that 108 sensors contain 33,644 rows while 362 sensors contain 33,643 rows. Comparing exact timestamps between representative sensors (`GA0151_A` vs. `GA0601_T`) confirmed:
- On Sunday, August 13, 2023, a telemetry server outage began at `00:00:00`.
- Hours `00:00`, `01:00`, and `02:00` are omitted across **all 470 sensors**.
- At `03:00:00`, a subset of 108 detectors (23.0% of the network) recovered and logged an observation (predominantly 0 or 1 vehicle).
- The remaining 362 detectors (77.0% of the network) did not recover until `04:00:00`.
- This single hour of staggered telemetry restoration in August 2023 (within the Test partition) is the exact mathematical reason for the per-sensor count variation.

---

## 3. Sensor-to-Road Matching Coverage Audit

### 3.1 Why 437 of 470 Detectors Are Unmatched
The Gate 3 candidate matcher reported that 437 sensors were classified as `UNMATCHED_DISTANCE_EXCEEDED`. An audit of the spatial data established the structural reason:

1. **Graph Extent vs. Sensor Extent:**
   - The road network file [`data/network/glasgow_network_edges.csv`](file:///C:/Gaanav/Projects/CityPulse/data/network/glasgow_network_edges.csv) contains **21 directed edges** representing the central River Clyde crossing corridor (M8 Kingston Bridge, George V Bridge, Glasgow Bridge, Clyde Arc, Victoria Bridge, Albert Bridge, and adjacent approach roads).
   - The bounding box of these 21 edges spans latitude $[55.851, 55.866]$ and longitude $[-4.283, -4.243]$ (an area of ~1.7 km $\times$ 2.5 km).
   - In contrast, the 470 SCOOT sensors in `locations.csv` span the entire Greater Glasgow metropolitan region (latitude $[55.70, 56.05]$, longitude $[-4.55, -4.00]$), reaching suburbs up to 15–20 km away (e.g., Baillieston, Scotstoun, Pollokshields, Clydebank).
2. **Strict Distance Threshold:**
   - The candidate matcher uses a strict search radius $R = 60.0\text{ meters}$ and planar metric projection calibrated for Glasgow's latitude.
   - For all 437 suburban sensors, the distance to the nearest edge in the 21-edge central corridor exceeds 60 meters (often by several kilometers).
   - The matcher correctly assigns `UNMATCHED_DISTANCE_EXCEEDED` with confidence `0.0`.

### 3.2 Geographic Scope Declaration
- **Finding:** Describing the current 21-edge network as "city-wide" is scientifically inaccurate.
- **Defensible Scope:** The current graph represents the **River Clyde Central Crossing Corridor**. All network and resilience results must be explicitly bounded to this corridor. Scaling to city-wide road network modeling requires a full OpenStreetMap ingestion covering Greater Glasgow.

---

## 4. Resilience Prototype Input Provenance

An inspection of [`citypulse/resilience/prototype.py`](file:///C:/Gaanav/Projects/CityPulse/citypulse/resilience/prototype.py) was conducted to delineate empirical measurements from model parameters:

| Input Variable | Role in Model | Provenance / Source | Empirical vs. Modeled |
| :--- | :--- | :--- | :--- |
| **Detector Flow ($y_t$)** | Traffic volume on monitored link | Glasgow SCOOT inductive loop counts | **Empirically Measured** (veh/hr) |
| **Link Length ($L_e$)** | Physical link length | WGS84 geodesic node coordinates | **Empirically Measured / Spatial** |
| **Link Capacity ($C_e$)** | Denominator in volume-to-capacity ratio | UK Department for Transport WebTAG / DMRB standards ($1800$ veh/hr/lane motorway, $900$ primary, $600$ secondary) | **Engineering Norm / Assumed** |
| **Free-Flow Speed ($v_0$)** | Baseline travel time numerator ($t_0 = L / v_0$) | Speed limits / UK design standards ($22.2$ m/s motorway, $13.4$ m/s primary, $8.9$ m/s secondary) | **Engineering Norm / Assumed** (SCOOT loops do not measure vehicle speed) |
| **BPR Parameters ($\alpha, \beta$)** | Congestion delay curvature: $t = t_0 [1 + \alpha (v/C)^\beta]$ | Standard BPR literature defaults ($\alpha = 0.20, \beta = 2.0$) | **Assumed Parameter** |
| **Disconnection Penalty ($M$)** | Cost assigned to disconnected OD pairs | Bounded penalty parameter ($M = 3,600\text{ seconds} = 1\text{ hour}$) | **Assumed Scenario Parameter** |

**Conclusion:** The primary outcome of the resilience prototype is strictly a **Model-Based Accessibility Impedance Proxy ($\Delta \mathcal{C}$)**. It cannot and must not be described as observed real-world travel time.

---

## 5. Defects Identified and Resolutions

1. **Determinism Test Assertion Failure:**
   - *Defect:* `test_track_a_determinism_across_runs` in `tests/test_experiment_reproducibility.py` failed during initial test execution because `pd.testing.assert_frame_equal()` evaluated wall-clock elapsed time columns (`fit_runtime_sec` and `eval_runtime_sec`), which naturally fluctuate by milliseconds between runs.
   - *Resolution:* Excluded wall-clock runtime columns from bit-level equality assertions while preserving strict equality checks on all analytical outputs (scores, predictions, thresholds, confusion matrices, and metrics).
2. **Sensor Flow File Path in Benchmark Script:**
   - *Defect:* `run_anomaly_benchmark.py` passed `flow_dir` instead of `sample_dir` to `load_sensor_flow()`, producing an erroneous duplicate subdirectory path `flows/flows/...`.
   - *Resolution:* Corrected argument to pass `sample_dir` directly.

All 40 unit tests pass offline with zero errors.
