# CITYPULSE: TECHNICAL INTERVIEW NOTES & DEFENSE GUIDE

**Target Audience:** Technical Interviewers, Lead Data Scientists, MSc Academic Examiners  
**Author:** Gaanav Reddy (`gaanavreddy007`)  
**Project:** CityPulse (`./`)  
**Repository State:** Frozen at `commit bf378f0`  
**Date:** 2026-10-25  

---

## 1. Data Engineering & Timestamp Provenance

### Q1: How did you handle temporal alignment and missingness in the Glasgow SCOOT sensor data?
**Evidence-Based Answer:**
- **Calendar Reindexing:** The raw dataset spans 4 calendar years (2019-10-01 00:00 through 2023-09-30 23:00), totaling **35,064 calendar hours**. In the raw CSVs, missing hours were completely omitted rows rather than explicit `NaN` values.
- **Separation of Concepts:** The data layer explicitly separates three distinct quantities:
  1. *Calendar Hours ($H_{\text{cal}} = 35,064$):* The continuous chronological timeline.
  2. *Observed Observations ($N_{\text{obs}} = 33,644$ or $33,643$):* The rows recorded by the physical loop.
  3. *Missing Hours ($M = 1,420$ or $1,421$):* Populated with `np.nan` during reindexing without corrupting legitimate zero-flow counts.
- **Forensic Accounting of Missing Data:** We proved that missing hours were not random dropouts:
  * 2 missing hours correspond to UK Daylight Saving Time (DST) forward clock shifts on 2020-03-29 and 2021-03-28.
  * 1,418 missing hours correspond to a localized Glasgow City Council system maintenance outage during August 2023.
  * Exactly 1 observation diverged across the network on Sunday, August 13, 2023, at 03:00 (108 sensors recorded flow; 362 sensors had an omitted record).

### Q2: Are the timestamps in UTC or local UK time?
**Evidence-Based Answer:**
- The raw Glasgow Open Data files contain columns `date` (e.g. `2019-10-01`) and `time` (integers `0` to `23`) with **no timezone designator or UTC offset**.
- Because the raw data omits 01:00 on UK spring-forward dates, the physical logging system operates on **UK Local Time (GMT during winter, BST during summer)**.
- In our pipeline, `reindex_sensor_flow` parses these as **timezone-naive continuous hourly timestamps**. Earlier documentation loosely referred to them as "UTC", but our reproducibility audit established that treating them as continuous nominal hours without DST shifts is a modeling assumption.

---

## 2. Anomaly Detection & Statistical Evaluation

### Q3: Why is standard classification accuracy inappropriate for evaluating your anomaly detectors?
**Evidence-Based Answer:**
- **Extreme Class Imbalance:** In our controlled benchmark scenarios, anomaly durations are either 24 hours ($24 / 8,760 \implies 0.274\%$ prevalence) or 168 hours ($168 / 8,760 \implies 1.918\%$ prevalence).
- **Metric Breakdown:**
  * Naive accuracy would exceed **99.7%** by predicting all points as normal.
  * ROC-AUC is artificially inflated by the overwhelming majority class of true negatives ($TN \approx 8,500+$ hours).
  * Consequently, we evaluate strictly using **Precision-Recall Area Under the Curve (PR-AUC)**, **Matthews Correlation Coefficient (MCC)**, and **Recall at fixed False Positive Rates**.

### Q4: Why do univariate models fail to detect calibration drift, and did spatial cross-consistency solve this?
**Evidence-Based Answer:**
- **Univariate Fragility:** Models like Rolling Z-Score and Seasonal ESD rely on moving baseline statistics or seasonal profiles. When a sensor experiences a multiplicative decalibration (e.g., measuring $-30\%$ or $-50\%$ of true volume over 168 hours), the corrupted readings remain within the diurnal range of night-time and off-peak flows, resulting in near-zero recall.
- **Spatial Cross-Consistency Mechanics:** By tracking the normalized residual ratio between paired adjacent sensors along the same corridor (e.g., Newton Street or Broomielaw), the spatial detector decouples sensor-specific drops from shared corridor demand fluctuations.
- **Honest Performance Defense:** Spatial cross-consistency increases PR-AUC by an order of magnitude (from $0.012$ to $0.1035$ on -50% drift). However, **it does not solve univariate blindness for automated alarming**:
  * At a 1% False Positive Rate ($c=0.01$), recall is only **4.96%** (precision $10.24\%$).
  * Tuning for 5% FPR raises recall to **35.51%**, but incurs a **92.94% False Discovery Rate**.
  * Therefore, in an operational setting, spatial cross-consistency must be deployed as an **evidence accumulator** requiring $\ge 6-12$ contiguous anomalous hours before triggering a dispatch.

---

## 3. Road Network Reconstruction & Graph Resilience

### Q5: What were the major defects in the preliminary road graph, and how did you reconstruct a defensible topology?
**Evidence-Based Answer:**
- **Defects in Phase 4.0 Graph:** The initial 18-edge synthetic graph had disconnected node IDs. Links did not share common junction vertices, making $>99\%$ of origin-destination pairs unreachable at baseline. Edge lengths were also missing and defaulted to 500 meters for every link.
- **Reconstruction Methodology:** In Phase 4.2, we extracted canonical OpenStreetMap XML extracts (`central_core.osm` [17.1 MB], `clyde_arc_west.osm` [8.7 MB]).
- **Topological Integrity Verification:**
  1. *Zero Parallel-Edge Collapse:* The 1,932 directed links map to 1,932 unique directed $(u, v)$ pairs, confirming NetworkX `DiGraph` introduces zero edge collapse. Dual carriageways are drawn with distinct OSM centerlines.
  2. *Grade Separation:* The elevated M8 Kingston Bridge viaduct shares **0 nodes** with underlying surface streets (Broomielaw, Argyle St). Flyovers are accessed strictly via dedicated on/off ramps.
  3. *Directional Flow:* Preserved one-way arterial couplets (0 vehicular roads use `oneway=-1`).

### Q6: What did you discover regarding the resilience of central Glasgow river crossings?
**Evidence-Based Answer:**
- **Asymmetric Directional Couplets:** In reality, **King George V Bridge** and **Glasgow Bridge (Jamaica Bridge)** do not function as generic bidirectional conduits:
  * King George V Bridge carries traffic exclusively **northbound**. Closing it impacts **only** South $\to$ North journeys (69,693 node pairs rerouted; mean travel time increase of **+24.74 s**, +11.0%; mean distance increase of **+253.74 m**). North $\to$ South routing is completely unaffected (0.00 s change).
  * Glasgow Bridge carries traffic exclusively **southbound**. Closing it impacts **only** North $\to$ South journeys (30,488 node pairs rerouted; mean travel time increase of **+9.82 s**, +4.4%; mean distance increase of **+136.08 m**). South $\to$ North routing is completely unaffected (0.00 s change).
- **Network Redundancy:** Even under the compound closure of both central surface bridges, **100.0% of cross-river node pairs remain reachable** via Victoria Bridge, Albert Bridge, and the Kingston Bridge.

### Q7: Why did 4,125 OD pairs disconnect when the Kingston Bridge was closed? Did people get trapped?
**Evidence-Based Answer:**
- **Forensic Root Cause:** Node pairs in our model are unweighted graph vertices, not people. Forensic tracing revealed that the 4,125 unreachable pairs all terminate at 445 northern M8 motorway mainline nodes (e.g., node 3845455477). When Kingston Bridge is removed, the topological ancestors of these nodes drop from 954 to 4.
- **Bounding Box Artifact:** Our study area truncates at latitude $55.865^\circ\text{N}$. The surface on-ramps to M8 northbound at Charing Cross (Junctions 17/18) and the external regional bypasses (M74 Northern Extension, Clyde Tunnel) lie outside this boundary.
- **Scientific Takeaway:** The disconnections are an artifact of evaluating trips destined for truncated motorway stubs inside a bounded box, **not** physical real-world travel impossibility.

---

## 4. Methodological Limitations & Professional Integrity

### Q8: What are the primary limitations of your transport modeling, and how would you extend it?
**Evidence-Based Answer:**
- **Static Free-Flow Assumption:** Traversal times are calculated using free-flow speed limits ($t_{\text{free}} = L / v_{\text{posted}}$). We do not model volume-delay functions (BPR), signal queue spillbacks, or Dynamic Traffic Assignment (DTA). In a real closure, diverting 69,000+ vehicle trips onto surface streets would saturate capacity and create non-linear delays far exceeding +24.74 seconds.
- **Turn Restrictions:** We cataloged 51 OSM turn restrictions (`type=restriction`), but our node-based Dijkstra routing does not enforce them. Incorporating turn restrictions requires expanding $G=(V, E)$ into a dual directed line graph $L(G)$.
- **Unweighted OD Node Pairs:** We evaluate connectivity between all vertices in the south and north quadrants. We do not have surveyed origin-destination trip demand matrices.

### Q9: How is the project structured for software engineering rigor and reproducibility?
**Evidence-Based Answer:**
- **100% Offline Reproducibility:** The entire pipeline executes locally with zero paid APIs or internet access (£0 budget).
- **Comprehensive Test Suite:** 56 passing unit tests across 9 test modules (`python -m unittest discover tests` executes in ~8.6 seconds).
- **Deterministic Seeding:** Multi-seed orchestration across 5 fixed seeds ensures corruptions and train/val/test splits replicate identically.
- **Version Control & Freeze:** Frozen under Git (`commit bf378f0`) with an explicit four-tier verification framework distinguishing passing tests, reproduced experiments, inspected historical data, and unvalidated modeling assumptions.
