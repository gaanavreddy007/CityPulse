# CITYPULSE — REPRODUCIBILITY AUDIT AND METHODOLOGICAL LIMITATIONS

**Reviewer Role:** Senior Data Scientist & Transport-Network Software Engineer  
**Project Directory:** `./`  
**Evaluation Scope:** MSc Data Science Research Portfolio Freeze  
**Execution Environment:** Windows PowerShell, Python 3.13.7  
**Date:** 2026-10-25  

---

## 1. Executive Summary

Scientific integrity in transport data science requires explicit demarcation between verified empirical code execution, historical inspected results, and unvalidated modeling simplifications. A software repository cannot be described as "reproducible" merely because automated unit tests exit with status code 0.

This document establishes the definitive reproducibility audit for the CityPulse research project:
1. It partitions all project claims into **Passing Unit Tests**, **Independently Reproduced Experiments**, **Inspected Historical Results**, and **Unvalidated Assumptions**.
2. It details the material scientific limitations of each research track.
3. It provides an offline execution protocol for regenerating primary outputs.

---

## 2. Four-Tier Verification Categorization

```
+----------------------------------------------------------------------------------------------------+
|                                    CITYPULSE VERIFICATION TIERS                                    |
+------------------------------------+---------------------------------------------------------------+
| Tier 1: Passing Unit Tests (56/56) | Automated test suite validating code logic, interfaces,      |
|                                    | mathematical functions, and data transformations.             |
+------------------------------------+---------------------------------------------------------------+
| Tier 2: Independently Reproduced   | Full benchmark executions run locally in this audit session   |
|         Experiments (EXP 09-14)    | from raw OSM XML and local sensor caches.                     |
+------------------------------------+---------------------------------------------------------------+
| Tier 3: Inspected Historical       | Artifacts preserved from Phase 1-3 whose outputs were audited |
|         Results (EXP 03-04)        | against saved CSVs but not recomputed from scratch.           |
+------------------------------------+---------------------------------------------------------------+
| Tier 4: Unvalidated Modeling       | Physical simplifications, heuristics, and boundary assumptions|
|         Assumptions (7 items)      | that require explicit caveat in academic review.              |
+------------------------------------+---------------------------------------------------------------+
```

### 2.1 Tier 1: Passing Unit Tests (56 Tests, 100% Passing)
The complete unit test suite executes offline in **8.660 seconds** via `python -m unittest discover tests`:
- `tests/test_data_layer.py` (8 tests): Hourly resampling, UTC timestamp parsing, continuity verification across 35,064 calendar hours, missingness flag handling.
- `tests/test_corruption_engine.py` (8 tests): Deterministic generation of synthetic corruptions (step offsets, multiplicative scale drift, zero dropouts, Gaussian noise, stuck values).
- `tests/test_sensor_matcher.py` (5 tests): Spatial buffer spatial matching, bearing concordance, nearest road-link assignment.
- `tests/test_bounded_resilience.py` (5 tests): Dijkstra shortest-path calculations, edge removal mechanics, disconnected pair penalty calculations.
- `tests/test_anomaly_detectors.py` (8 tests): Rolling z-score, EWMA, Seasonal ESD, Isolation Forest, Local Outlier Factor.
- `tests/test_experiment_runner.py` (6 tests): Train/val/test calibration, multi-seed orchestration, deterministic reproducibility.
- `tests/test_spatial_cross_consistency.py` (5 tests): Bivariate correlation, spatial neighbor tracking, residual drift calculation.
- `tests/test_uncertainty_propagation.py` (5 tests): Latin Hypercube Sampling, parameter uncertainty bounds, variance decomposition.
- `tests/test_reconstructed_graph.py` (6 tests): OSM XML parsing, 1,047 node and 1,932 edge ingestion, connected components, bridge presence.

### 2.2 Tier 2: Independently Reproduced Experiments
These core research findings were recomputed from raw sources in the current environment:
1. **OSM Network Reconstruction (`scripts/build_reconstructed_graph.py`):**
   - Ingested `data/network/raw_osm/central_core.osm` (17.1 MB) and `clyde_arc_west.osm` (8.7 MB).
   - Generated `reconstructed_network_nodes.csv` (1,047 nodes) and `reconstructed_network_edges.csv` (1,932 edges).
   - Validated that dual carriageways map to 1,932 unique $(u, v)$ pairs with **zero edge collapses** in `networkx.DiGraph`.
2. **Directional Couplet Resilience (`scripts/audit_separate_bridges.py`):**
   - Evaluated 218,401 cross-river node pairs.
   - Proved complete directional decoupling: King George V Bridge affects only South $\to$ North journeys (+24.74 s mean on 69,693 pairs; 0 s North $\to$ South); Glasgow Bridge affects only North $\to$ South journeys (+9.82 s mean on 30,488 pairs; 0 s South $\to$ North).
3. **Boundary Truncation Trace (`scripts/analyze_boundary_disconnect.py`):**
   - Traced the 4,125 unreachable pairs under Kingston Bridge closure to 445 northern M8 mainline nodes (ancestors collapse from 954 to 4), confirming a geographic boundary cutoff at $55.865^\circ\text{N}$.
4. **Spatial Detector Benchmark Audit (`scripts/audit_spatial_detector.py`):**
   - Re-evaluated the bivariate detector against `data/raw/traffic_flow_data.zip`, establishing modest recall (4.96% at 1% FPR, 35.51% at 5% FPR; PR-AUC = 0.1035) and disproving claims of univariate blindness elimination.
5. **Distance & Time Trade-off Recalibration (`scripts/calculate_distance_changes.py`):**
   - Computed exact mean and maximum distance changes across all still-reachable pairs under all bridge disruptions.

### 2.3 Tier 3: Inspected Historical Results
These results were verified through forensic inspection of saved artifacts and code, but not rerun end-to-end to conserve computing resources:
1. **Univariate Anomaly Benchmark (`reports/anomaly_benchmark_results.csv`):**
   - 900 scenario evaluations across 5 master seeds, 6 anomaly models, and 3 corruption types. Calibration protocols and seed logs verified.
2. **Track B Statistical Flow Outliers (`reports/statistical_anomalies_track_b.csv`):**
   - 412 high-magnitude statistical flow deviations mined from uncorrupted SCOOT flows.
3. **Preliminary Observability Risk Table (`reports/observability_risk_table.csv`):**
   - Early corridor ranking evaluated on the preliminary 18-edge synthetic graph. Inspected and classified as an exploratory exercise.
4. **Initial Graph Resilience Results (`reports/resilience_uncertainty_results.md`):**
   - Historical artifact from Phase 4.0 evaluated on disconnected synthetic topology. Formally marked as **SUPERSEDED** by Phase 4.3 findings.

---

## 3. Comprehensive Scientific Limitations & Material Caveats

To ensure academic rigor and avoid over-claiming on a graduate portfolio or CV, the following limitations must be explicitly declared:

### 3.1 Transport Modeling Limitations
1. **Free-Flow Speed vs. Congestion Delays:**
   - All route travel times ($t_{\text{free}} = \text{length} / v_{\text{posted}}$) assume unconstrained free-flow conditions at legal speed limits (30 mph urban surface, 50 mph motorway).
   - The model does **not** implement volume-delay functions (e.g., Bureau of Public Roads / BPR formulas), junction turn penalties, signal progression delays, or Dynamic Traffic Assignment (DTA).
   - *Negative Result / Reality Check:* In a physical bridge closure, diverting 69,000+ trips onto surface streets would trigger severe capacity saturation, queue spillbacks, and non-linear delays far exceeding the static free-flow delta of +24.74 seconds.
2. **Micro-Level Turn Restrictions:**
   - 51 OSM turn restrictions (`type=restriction`) are present in the study area.
   - Because routing is executed on a standard node-based graph $G=(V, E)$ rather than a dual edge-expanded line graph $L(G)$, turn prohibitions at signalized junctions are not enforced. Traversal resistance through complex intersections is underestimated by an estimated 5–15 seconds.
3. **Study Area Bounding Box Truncation:**
   - The road network is restricted to $[55.850^\circ\text{N}, 55.865^\circ\text{N}]$ and $[-4.285^\circ\text{W}, -4.240^\circ\text{W}]$.
   - This boundary truncates northern motorway ramps at Charing Cross (Junctions 17/18) and completely excludes major regional bypasses (M74 Northern Extension, M73, Clyde Tunnel A739).
   - *Interpretation Rule:* The 4,125 unreachable pairs under Kingston Bridge closure represent trips destined for truncated motorway stubs inside the bounding box, **not** real-world motorists unable to reach destinations.
4. **Unweighted Origin-Destination (OD) Node Pairs:**
   - Evaluated OD pairs represent unweighted topological pairings between all nodes in the south quadrant and north quadrant.
   - They do **not** represent surveyed travel demand, origin-destination trip matrices, or counted commuters.

### 3.2 Data Quality & Anomaly Detection Limitations
1. **Synthetic Corruptions vs. Real Hardware Failures:**
   - Evaluated anomalies were synthetically generated via mathematical functions (step offsets, linear scale drifts, zero dropouts).
   - While effective as a controlled benchmark, they do not replicate complex analog hardware failure modes (e.g., inductive loop impedance changes under heavy rain, multi-vehicle occlusion, or SCOOT detector pulse chatter).
2. **Statistical Flow Outliers vs. Traffic Incidents:**
   - Unsupervised outlier detections (Track B) identify statistical anomalies in hourly vehicle counts.
   - They cannot be claimed as "confirmed traffic accidents" or "incidents" without ground-truth external validation against Police Scotland incident logs or Glasgow City Council maintenance records.
3. **Spatial Cross-Consistency Detector Recall:**
   - Bivariate spatial detection achieves an absolute recall of 4.96% at a 1% false positive rate and 35.51% at 5% FPR (PR-AUC = 0.1035; False Discovery Rate = 92.94%).
   - Spatial correlation effectively filters out macro-level weather or holiday flow drops, but it is **not** a standalone solution for detecting subtle, localized sensor drift.
4. **Exploratory Observability Index:**
   - The observability risk index is a heuristic formulation combining betweenness centrality and sensor spacing.
   - It is sensitive to subjective weighting parameters (Kendall $\tau$ rank correlation drops to 0.38–0.61 across weight variations). It must be described as an exploratory prioritization heuristic, not a validated infrastructure safety standard.
5. **Monte Carlo Spread vs. Mean Standard Error:**
   - Monte Carlo dispersion across scenarios represents model parameter sensitivity (variance of the outcome distribution under varying penalties), **not** the standard error of an estimated mean parameter.

---

## 4. Offline Reproduction Runbook

A researcher or technical interviewer can reproduce all primary outputs on a standard Windows/Linux machine without internet access using the following protocol:

```powershell
# 1. Navigate to project root
cd .

# 2. Run automated test suite (56 tests)
python -m unittest discover tests

# 3. Validate raw OpenStreetMap topology integrity
python scripts/validate_reconstructed_graph.py

# 4. Reproduce bridge closure resilience metrics & directional couplets
python scripts/audit_separate_bridges.py

# 5. Extract concrete detour route examples
python scripts/generate_route_examples.py

# 6. Trace bounding-box truncation mechanisms
python scripts/analyze_boundary_disconnect.py

# 7. Audit spatial cross-consistency detector
python scripts/audit_spatial_detector.py
```

---

## 5. Data Licensing & Legal Attributions

- **SCOOT Traffic Flow Dataset:** Derived from Glasgow City Council Open Data under the Open Government Licence (OGL) v3.0.
- **Road Network Graph:** Derived from OpenStreetMap.
  - Attribution: *© OpenStreetMap contributors*
  - License: *Open Data Commons Open Database License (ODbL) 1.0* (http://opendatacommons.org/licenses/odbl/1-0/)
  - Derivative Database Notice: Any public distribution of `reconstructed_network_nodes.csv` or `reconstructed_network_edges.csv` must be accompanied by this ODbL notice and attribution.
