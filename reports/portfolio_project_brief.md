# CITYPULSE: PORTFOLIO PROJECT BRIEF

**Project Title:** CityPulse: Traffic Sensor Data Quality, Spatial Consistency & Road Network Resilience  
**Author:** Gaanav Reddy (`gaanavreddy007`)  
**Target Audience:** Academic Reviewers (MSc Data Science) & UK Graduate Data Science Employers  
**Repository:** `./`  
**Current Frozen Commit:** `bf378f0`  
**Date:** 2026-10-25  

---

## 1. Executive Summary

CityPulse is an end-to-end data science and transport-network engineering investigation into **sensor fault vulnerability, spatial cross-consistency anomaly detection, and graph-theoretic road network resilience** across central Glasgow, Scotland.

Using four continuous calendar years of real-world municipal SCOOT inductive-loop traffic sensor data (35,064 hourly intervals) combined with a topologically verified OpenStreetMap road network (1,047 nodes, 1,932 directed links), this research demonstrates how subtle sensor degradation corrupts traffic observability and establishes the true directional resilience of urban river crossings under bridge severance scenarios.

---

## 2. Research Problem & Motivation

1. **The Sensor Degradation Dilemma:** Modern urban traffic control systems rely on inductive loops to manage signals and detect congestion. While catastrophic failures (power cutoffs, stuck values) are readily detected, subtle calibration drifts ($\pm 15\%$ to $\pm 30\%$) degrade traffic control without triggering conventional univariate threshold alarms.
2. **The Spatial Confounding Problem:** When traffic drops across an entire corridor during extreme weather or bank holidays, univariate models generate widespread false alarms. Conversely, localized single-sensor dropouts may blend into diurnal troughs.
3. **The Network Topology Failure Mode:** In transport analytics, oversimplified road graphs (e.g., planar snapping of elevated flyovers, collapsing dual carriageways, or ignoring one-way couplets) produce completely fictitious resilience estimates. Defensible resilience analysis requires a topologically validated directed road graph.

---

## 3. Data Provenance & Methodology

```
+----------------------------------------------------------------------------------------------------+
|                                    CITYPULSE RESEARCH WORKFLOW                                     |
+------------------------------------+---------------------------------------------------------------+
| 1. High-Frequency Sensor Feeds     | 470 SCOOT sensors in Glasgow (2019-2023), 35,064 calendar     |
|    (Glasgow City Council / OGL)    | hours. Missingness audited to DST clock shifts & maintenance.  |
+------------------------------------+---------------------------------------------------------------+
| 2. Controlled Corruption Engine    | Deterministic injection of step offsets, scale drift, stuck   |
|    (Synthetic Benchmarking)        | values, and burst dropouts across 5 master seeds.             |
+------------------------------------+---------------------------------------------------------------+
| 3. Multi-Model Detection Benchmark | Evaluation of Rolling Z-Score, Seasonal ESD, Isolation Forest,|
|    (Univariate Baseline)           | ECOD, and Local Outlier Factor (LOF).                         |
+------------------------------------+---------------------------------------------------------------+
| 4. Bivariate Spatial Detector      | Neighbor correlation and residual drift tracking to filter   |
|    (Corridor Cross-Consistency)    | shared macro flow drops from localized sensor failures.       |
+------------------------------------+---------------------------------------------------------------+
| 5. Geospatial OSM Graph Ingestion  | Raw OpenStreetMap XML (ODbL 1.0) parsed to 1,047 nodes and    |
|    (Topological Reconstruction)    | 1,932 edges. 0 multi-edge collapse; 0 flyover snapping.      |
+------------------------------------+---------------------------------------------------------------+
| 6. Directional Couplet Resilience  | Dijkstra pathfinding across 218,401 cross-river OD pairs;     |
|    (Bridge Severance Simulation)   | forensic trace of boundary truncation cul-de-sacs.           |
+------------------------------------+---------------------------------------------------------------+
```

---

## 4. Key Empirical Findings

### 4.1 Sensor Fault Detection & Spatial Trade-offs
- **Catastrophic Dropouts:** Readily detected by Seasonal ESD and LOF (PR-AUC $>0.88$).
- **Insidious Scale Drift:** Multiplicative decalibration ($\pm 30\%$) severely degrades univariate detectors (PR-AUC drops to $0.01$–$0.02$; recall near $0\%$).
- **Bivariate Spatial Detection:**
  * Successfully suppresses false alarms during corridor-wide volume drops (e.g., bank holidays, storms).
  * On a controlled -50% 168-hour drift, spatial cross-consistency achieves **PR-AUC = 0.1035** (compared to $0.012$ univariate).
  * At a 1% False Positive Rate (FPR) threshold ($c=0.01$), recall is **4.96%** (precision 10.24%). Tuning to 5% FPR ($c=0.05$) raises recall to **35.51%** (precision 7.06%, False Discovery Rate 92.94%).
  * *Verdict:* Spatial correlation is an essential complementary filter, not a standalone automated actuator.

### 4.2 Road Network Topology & River Crossing Resilience
Evaluated across 218,401 cross-river origin-destination node pairs connecting the southern and northern quadrants:
- **Asymmetric Directional Couplet:**
  * **King George V Bridge** operates exclusively northbound into the city centre. Severing it affects **only** South $\to$ North journeys (69,693 node pairs rerouted; mean free-flow travel time increase of **+24.74 s**, +11.0%; mean distance increase of **+253.74 m**). North $\to$ South journeys experience **0.00 s change**.
  * **Glasgow Bridge (Jamaica Bridge)** operates exclusively southbound. Severing it affects **only** North $\to$ South journeys (30,488 node pairs rerouted; mean free-flow travel time increase of **+9.82 s**, +4.4%; mean distance increase of **+136.08 m**). South $\to$ North journeys experience **0.00 s change**.
- **Resilience Redundancy:** Even with both central bridges closed simultaneously, **100.0% of cross-river node pairs remain reachable** via Victoria Bridge, Albert Bridge, and Kingston Bridge.
- **Boundary Truncation Mechanism:** Under Kingston Bridge closure, 4,125 South $\to$ North pairs become unreachable. Forensic tracing confirmed these trips are destined for 445 northern M8 motorway mainline nodes whose ancestors collapse from 954 to 4 because the $55.865^\circ\text{N}$ study perimeter cuts off Charing Cross on-ramps and regional bypasses (M74, Clyde Tunnel). This is an artifact of geographic bounding, not physical travel impossibility.

---

## 5. Material Scientific Limitations

1. **Free-Flow vs. Congestion Delays:** Route costs use static free-flow travel times ($t_{\text{free}} = \text{length} / v_{\text{posted}}$). In a real-world closure, diverting 69,000+ vehicle trips onto surface streets would trigger severe capacity bottlenecks, signal delays, and non-linear congestion far exceeding the static free-flow delta of +24.74 seconds.
2. **Turn Restrictions:** 51 OSM turn restrictions are cataloged in the core but omitted in the node-based Dijkstra solver, underestimating urban traversal resistance by an estimated 5–15 seconds at complex junctions.
3. **Spatial Bounding Cutoff:** Bounding box $[55.850^\circ\text{N}, 55.865^\circ\text{N}]$ isolates northern motorway stubs and excludes regional orbital bypasses (M74, M73, Clyde Tunnel).
4. **Unweighted OD Node Pairs:** Pairs $(u, v)$ represent theoretical graph vertices, not observed commuter trips or surveyed travel demand matrices.
5. **Synthetic Benchmarks:** Injected drifts and dropouts are controlled mathematical cases, not physical hardware telemetry.

---

## 6. Next Steps & Extension Roadmap

1. **Dynamic Traffic Assignment (DTA):** Implement Bureau of Public Roads (BPR) volume-delay functions to simulate flow-dependent congestion and queue spillback.
2. **Dual Line-Graph Routing:** Expand the node-based network $G=(V, E)$ to a directed line graph $L(G)$ to strictly enforce the 51 OSM turn restrictions.
3. **Regional Perimeter Expansion:** Expand the spatial bounding box to include Charing Cross on-ramps (Junctions 17/18) and the M74 regional bypass.
4. **Multi-Hour Evidence Persistence:** Transition the spatial detector from a single-hour threshold to an evidence accumulator requiring $\ge 6$ contiguous anomalous hours before raising a maintenance ticket.
