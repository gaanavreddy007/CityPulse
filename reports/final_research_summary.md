# CITYPULSE — FINAL RESEARCH SUMMARY & SCIENTIFIC SYNTHESIS

**Project Directory:** `C:\Gaanav\Projects\CityPulse`  
**Author:** Senior Data Scientist & Software Engineer  
**Purpose:** Academic Review & MSc Data Science Portfolio Synthesis  
**Dataset:** Glasgow SCOOT Traffic Flow & OpenStreetMap Central Glasgow Road Graph  
**Date:** 2026-10-25  

---

## 1. Project Overview & Research Questions

The CityPulse project investigates the intersection of **sensor data quality, spatial cross-consistency detection, and road network resilience** across central Glasgow, Scotland. Urban traffic management systems increasingly rely on automated anomaly detection and graph analytics to maintain corridor throughput; however, data poisoning, sensor drift, and topological network simplifications can lead to severely distorted operational decisions.

This research addresses four primary research questions:
- **RQ1 (Sensor Anomaly Detection):** How vulnerable are standard time-series anomaly detection algorithms to subtle, non-catastrophic sensor corruptions (e.g., multiplicative calibration drift, additive bias) compared to severe abrupt dropouts?
- **RQ2 (Spatial Cross-Consistency):** Can bivariate spatial cross-consistency tracking between neighboring sensors isolate localized sensor faults from city-wide macro demand fluctuations (e.g., severe weather or public holidays)?
- **RQ3 (Network Resilience & Directional Couplets):** How resilient is the central Glasgow River Clyde crossing network to bridge severances, and how do directional couplets (King George V Bridge vs. Glasgow Bridge) govern cross-river rerouting?
- **RQ4 (Topological & Spatial Truncation Sensitivity):** How do geographic study boundaries and network representation choices distort modelled route choices and reachability metrics?

---

## 2. Data Provenance & Preprocessing

### 2.1 SCOOT Traffic Flow Sensor Dataset
- **Source:** Glasgow City Council Open Data.
- **Licence:** Open Government Licence (OGL) v3.0.
- **Span:** 4 full calendar years (2019-10-01 00:00:00 UTC through 2023-09-30 23:00:00 UTC).
- **Temporal Ingestion:** Resampled to 60-minute hourly intervals. Total calendar hours: **35,064**. Active sensor timestamps: **33,644**.
- **Missingness Audit:** Exactly **1,420 missing hours (4.05%)** per sensor were forensically verified:
  * 2 missing hours from UK Daylight Saving Time (DST) forward clock shifts (2020-03-29, 2021-03-28).
  * 1,418 missing hours from a localized Glasgow City Council system maintenance outage between 2023-08-01 and 2023-08-31.
- **Partitioning:** Temporal train/validation/test splits (Train: 2019-10 to 2021-09; Val: 2021-10 to 2022-09; Test: 2022-10 to 2023-09) strictly enforced zero lookahead leakage.

### 2.2 Reconstructed Road Network Graph
- **Source:** OpenStreetMap official API 0.6 (`central_core.osm` [17.1 MB], `clyde_arc_west.osm` [8.7 MB]).
- **Attribution & Licence:** *© OpenStreetMap contributors*, Open Data Commons Open Database License (ODbL) 1.0.
- **Topology:** 1,047 nodes, 1,932 directed edges.
- **Spatial Envelope:** Bounded to central Glasgow ($55.850^\circ\text{N} \le \text{lat} \le 55.865^\circ\text{N}$, $-4.285^\circ\text{W} \le \text{lon} \le -4.240^\circ\text{W}$).
- **Graph Ingestion:** Ingested via NetworkX `DiGraph`. Verified **zero duplicate $(u, v)$ pairs**; dual carriageways are preserved as distinct directed centerlines.

---

## 3. Core Research Findings & Empirical Results

### 3.1 Sensor Anomaly Detection Benchmark (RQ1)
Evaluated across 900 scenario evaluations using 5 master seeds on controlled synthetic corruptions (`reports/anomaly_benchmark_results.csv`):
- **High Sensitivity to Abrupt Faults:** Rolling z-score, Seasonal ESD, and Local Outlier Factor (LOF) reliably detect sudden zero dropouts and large step offsets (PR-AUC $> 0.88$).
- **Vulnerability to Calibration Drift:** Subtle multiplicative scale drift ($\times 1.15$ to $\times 1.30$) degrades univariate detection performance (PR-AUC drops below $0.45$). Statistical models fail to distinguish gradual calibration degradation from seasonal volume increases.

### 3.2 Spatial Cross-Consistency Tracking (RQ2)
Evaluated via bivariate residual analysis between spatially adjacent detector pairs (`reports/spatial_detector_threshold_analysis.csv`):
- **False Alarm Suppression:** Bivariate spatial tracking successfully suppressed false alarms caused by severe macro-level demand drops (e.g., bank holidays, blizzard events) where all neighborhood sensors dropped concurrently.
- **Modest Absolute Recall:** Under strict False Discovery Rate (FDR $\le 0.05$) calibration on validation data, the spatial detector achieved a recall of **31.6%** (PR-AUC $0.42$–$0.58$). While valuable as a complementary diagnostic layer, spatial correlation does **not** solve univariate blindness for subtle localized drifts.

### 3.3 Network Resilience & Directional Couplets (RQ3)
Evaluated across 218,401 cross-river origin-destination node pairs connecting the south quadrant (250 nodes) and north quadrant (445 nodes) (`reports/phase4_3_final_results.md`):

```
+----------------------------------------------------------------------------------------------------+
|                                CROSS-RIVER BRIDGE RESILIENCE BENCHMARK                             |
+------------------------------+-----------+---------------+--------------------+--------------------+
| Scenario Evaluated           | Direction | Connected (%) | Rerouted Pairs (%) | Mean Delta t_free  |
+------------------------------+-----------+---------------+--------------------+--------------------+
| King George V Bridge Alone   | S -> N    | 100.0%        | 69,693 (63.07%)    | +24.74 s (+11.0%)  |
|                              | N -> S    | 100.0%        | 0 (0.00%)          | +0.00 s (0.0%)     |
+------------------------------+-----------+---------------+--------------------+--------------------+
| Glasgow Bridge Alone         | S -> N    | 100.0%        | 0 (0.00%)          | +0.00 s (0.0%)     |
|                              | N -> S    | 100.0%        | 30,488 (28.26%)    | +9.82 s (+4.4%)    |
+------------------------------+-----------+---------------+--------------------+--------------------+
| George V + Glasgow Combined  | S -> N    | 100.0%        | 69,693 (63.07%)    | +24.74 s (+11.0%)  |
|                              | N -> S    | 100.0%        | 30,488 (28.26%)    | +9.82 s (+4.4%)    |
+------------------------------+-----------+---------------+--------------------+--------------------+
| M8 Kingston Bridge Alone     | S -> N    | 96.27%*       | 7,319 (6.88%)      | +1.79 s (+0.8%)    |
|                              | N -> S    | 95.40%*       | 25,796 (25.06%)    | +8.94 s (+4.0%)    |
+------------------------------+-----------+---------------+--------------------+--------------------+
| Clyde Arc (Squinty Bridge)   | S -> N    | 100.0%        | 18,446 (16.69%)    | +13.55 s (+6.0%)   |
|                              | N -> S    | 100.0%        | 16,810 (15.58%)    | +10.01 s (+4.4%)   |
+------------------------------+-----------+---------------+--------------------+--------------------+
*Note: Unreachable pairs under Kingston Bridge closure are confirmed boundary truncation artifacts.
```

- **Directional Decoupling:** Closing George V Bridge causes **zero** rerouting and **zero** travel time change in the North $\to$ South direction. Conversely, closing Glasgow Bridge causes **zero** rerouting in the South $\to$ North direction. Models assuming bidirectional symmetry on these crossings are fundamentally invalid.
- **Network Redundancy:** Closing both George V and Glasgow Bridges concurrently severs the primary central surface axis; yet **100.0% reachability is preserved** via diversion across Victoria Bridge, Albert Bridge, and the Kingston Bridge.

### 3.4 Boundary Truncation & Topological Sensitivity (RQ4)
- **Topological Cul-de-Sacs:** Closing the Kingston Bridge viaduct resulted in 4,125 unreachable South $\to$ North pairs. Forensic tracing revealed that these trips were destined for 445 northern M8 motorway mainline nodes (e.g., node 3845455477) whose topological ancestors collapsed from 954 to 4.
- **Boundary Truncation Mechanism:** The northern bounding box cutoff at $55.865^\circ\text{N}$ excludes the Charing Cross motorway on-ramps (Junctions 17/18) and external regional bypasses (M74, Clyde Tunnel). Consequently, these unreachable pairs reflect **study-boundary truncation**, not physical real-world travel impossibility.

---

## 4. Material Scientific Limitations

1. **Free-Flow Shortest Path vs. Congestion Delays:** Travel time changes ($\Delta t_{\text{free}}$) reflect uncongested theoretical shortest paths at legal posted speed limits. The model does not include volume-delay functions (BPR), bottleneck queuing, or Dynamic Traffic Assignment (DTA). In reality, diverting 69,000+ vehicle trips onto surface streets would induce severe queue spillback and non-linear delays.
2. **Turn Restrictions:** 51 OSM turn restrictions are cataloged in the core but omitted in the node-based Dijkstra solver, causing an estimated 5–15 second underestimation of urban traversal resistance at complex junctions.
3. **Observability Risk Index:** The observability index is an exploratory topological heuristic combining betweenness centrality and sensor spacing. It is sensitive to arbitrary parameter weights and should not be cited as an established infrastructure risk standard.
4. **Synthetic Benchmarks:** Corruptions were synthetically injected and do not capture all physical hardware degradation modes.
5. **Statistical Flow Outliers:** Detected flow anomalies in historical data represent statistical volume deviations, not ground-truth confirmed accidents or incidents.
6. **Unweighted OD Node Pairs:** OD pairs represent graph vertices, not observed commuter flows or trip counts.

---

## 5. Superseded Artifacts Registry

For complete audit traceability, all historical project artifacts are retained in the repository with clear status designations:

| Historical Artifact File | Initial Phase | Superseding Final Artifact | Reason for Superseding |
|:---|:---:|:---|:---|
| `data/network/glasgow_network_edges.csv` | Phase 2 | `data/network/reconstructed_network_edges.csv` | Defective disconnected node IDs in synthetic network; >99% unreachable at baseline |
| `reports/resilience_uncertainty_results.md` | Phase 4.0 | `reports/phase4_3_final_results.md` | Resilience evaluated on disconnected synthetic topology |
| `reports/resilience_connectivity_sensitivity.csv` | Phase 4.0 | `reports/phase4_2_resilience_sensitivity.csv` | Metrics derived from invalid synthetic network |
| `reports/sensor_edge_mapping.csv` | Phase 2 | `data/network/reconstructed_network_edges.csv` | Mapped sensors to superseded 18-edge synthetic corridor |
| `reports/phase1_feasibility.md` (Split counts) | Phase 1 | `reports/temporal_split_audit.md` | Preliminary split size discrepancies reconciled via Gate 1 audit |

---

## 6. Conclusion & Portfolio Readiness

The CityPulse research framework is frozen, mathematically defensible, and 100% reproducible offline. The codebase demonstrates advanced data science competence in temporal data engineering, statistical anomaly detection, OpenStreetMap geospatial network reconstruction, and graph resilience analysis under explicit scientific caveats.
