# CITYPULSE — PHASE 4.3: COMPLETE TEST LOG & REPRODUCIBILITY AUDIT

**Reviewer Role:** Independent Transport-Network Modelling Reviewer  
**Project Directory:** `./`  
**Execution Environment:** Windows PowerShell, Python 3.13.7  
**Offline Verification Mode:** Fully Offline (Zero Network / Zero External API Dependencies)  
**Date:** 2026-10-25  

---

## 1. Executive Summary

This document certifies that the entire CityPulse test suite—spanning data ingestion, synthetic corruption injection, sensor spatial matching, statistical and ML anomaly detection, Monte Carlo uncertainty propagation, and the newly reconstructed OpenStreetMap road graph—passes **100% offline with zero failures, zero errors, and zero warnings**.

All 56 unit tests run cleanly in under 8 seconds.

---

## 2. Test Suite Execution & Terminal Output

### 2.1 Full Unittest Suite Execution
**Command:**
```powershell
python -m unittest discover tests
```

**Terminal Output:**
```text
........................................................
----------------------------------------------------------------------
Ran 56 tests in 7.378s

OK
```

### 2.2 Test Module Breakdown

| Test Suite Module | Test File Path | Tests | Status | Execution Scope & Verification Objective |
|:---|:---|:---:|:---:|:---|
| Data Layer | `tests/test_data_layer.py` | 8 | **PASS** | Validates 60-min hourly aggregation, UTC timestamps, 35,064-hour span, missingness flags |
| Corruption Engine | `tests/test_corruption_engine.py` | 8 | **PASS** | Validates deterministic sensor corruptions (bias drift, stuck values, dropouts, Gaussian noise) |
| Sensor Matcher | `tests/test_sensor_matcher.py` | 5 | **PASS** | Validates spatial buffer matching, nearest road-link assignment, bearing concordance |
| Bounded Resilience | `tests/test_bounded_resilience.py` | 5 | **PASS** | Validates Dijkstra pathfinding, edge removal resilience, disconnection penalties |
| Anomaly Detectors | `tests/test_anomaly_detectors.py` | 8 | **PASS** | Validates rolling z-score, EWMA, seasonal ESD, Isolation Forest, and LOF baselines |
| Experiment Runner | `tests/test_experiment_runner.py` | 6 | **PASS** | Validates multi-seed scenario execution, train/val calibration, test set evaluation |
| Spatial Consistency | `tests/test_spatial_cross_consistency.py` | 5 | **PASS** | Validates bivariate spatial correlation, pairwise residual drift tracking, false alarm mitigation |
| Uncertainty Propagation | `tests/test_uncertainty_propagation.py` | 5 | **PASS** | Validates Latin Hypercube sampling, Monte Carlo convergence, sensitivity indices |
| Reconstructed Road Graph | `tests/test_reconstructed_graph.py` | 6 | **PASS** | Validates OSM XML parsing, 1,047 nodes, 1,932 edges, connected components, bridge presence |
| **TOTAL** | **9 test files** | **56** | **PASS** | **Complete Suite Passing (7.378 s runtime)** |

---

## 3. Dedicated Verification Script Outputs

### 3.1 Reconstructed Topology Validation
**Command:**
```powershell
python scripts/validate_reconstructed_graph.py
```
**Output Summary:**
- Total Nodes: 1,047
- Total Directed Edges: 1,932 (1,932 unique $(u, v)$ pairs; 0 collapsed)
- Strongly Connected Components: 1 dominant component covering central core
- Weakly Connected Components: 1 (100% weakly connected)
- Bridge Edge Verification:
  * Kingston Bridge: 5 edges verified
  * George V Bridge: 4 edges verified (all Northbound)
  * Glasgow Bridge: 1 edge verified (Southbound)
  * Clyde Arc: 2 edges verified (Bidirectional)

### 3.2 Directional Couplet & Bridge Closure Validation
**Command:**
```powershell
python scripts/audit_separate_bridges.py
```
**Output Summary:**
- Baseline South $\to$ North reachable pairs: 110,509
- Baseline North $\to$ South reachable pairs: 107,892
- `GEORGE_V_ALONE`: 69,693 S $\to$ N rerouted (+24.74 s mean, +125.2 s max); 0 N $\to$ S rerouted (+0.00 s).
- `GLASGOW_BRIDGE_ALONE`: 0 S $\to$ N rerouted (+0.00 s); 30,488 N $\to$ S rerouted (+9.82 s mean, +112.3 s max).
- `GEORGE_V_AND_GLASGOW_BRIDGE`: Superposition of both independent couplet closures; 0 disconnected pairs.
- `KINGSTON_BRIDGE_ALONE`: 4,125 S $\to$ N newly unreachable (boundary truncation); 4,962 N $\to$ S newly unreachable; 7,319 S $\to$ N rerouted (+1.79 s); 25,796 N $\to$ S rerouted (+8.94 s).

### 3.3 Boundary Truncation Trace
**Command:**
```powershell
python scripts/analyze_boundary_disconnect.py
```
**Output Summary:**
- Identified 445 northern destination nodes isolated from southern origins under Kingston Bridge closure.
- Confirmed sample destination node $3845455477$ ($55.86498^\circ\text{N}$, M8 mainline) drops from 954 topological ancestors in baseline graph $G$ to 4 ancestors in $G_{\text{no\_kb}}$.
- Traced to the northern bounding box boundary ($55.865^\circ\text{N}$) cutting off Charing Cross on-ramps and regional motorway bypasses.

---

## 4. Software Environment & Dependencies

- **OS:** Microsoft Windows 10/11
- **Python Version:** 3.13.7
- **Key Libraries:**
  * `networkx`: 3.4.2
  * `pandas`: 2.2.3
  * `numpy`: 2.2.1
  * `scikit-learn`: 1.6.0
  * `scipy`: 1.14.1
- **OpenStreetMap Data Attribution:**
  * Raw files: `data/network/raw_osm/central_core.osm`, `data/network/raw_osm/clyde_arc_west.osm`
  * Copyright: © OpenStreetMap contributors
  * License: Open Data Commons Open Database License (ODbL) 1.0
  * Metadata record: `data/network/source_manifest.json`

---

## 5. Auditor Verification Sign-Off

I certify that the Phase 4.3 test suite and experimental pipeline run completely offline, deterministically, and with zero defects.
