# CITYPULSE Phase 4.1: Independent Scientific Review & Validation Audit

**Project:** `./`  
**Role:** Independent Scientific Reviewer and Statistical Auditor  
**Date:** October 2026  
**Operating Constraints:** 100% Offline, £0 Budget, Standard Scientific Python Stack  
**Audit Artifacts Generated:**
- [`reports/spatial_detector_threshold_analysis.csv`](./spatial_detector_threshold_analysis.csv) (720 evaluations across 8 thresholds, 3 corridors, 6 scenarios, 5 seeds)
- [`reports/resilience_connectivity_sensitivity.csv`](./resilience_connectivity_sensitivity.csv) (108 evaluations across 6 penalties, 9 BPR configurations, 2 closure scenarios)
- [`reports/observability_sensitivity.csv`](./observability_sensitivity.csv) (400 evaluations across 5 distance scales, 4 penalties, 20 network edges)
- [`reports/phase4_1_test_log.md`](./phase4_1_test_log.md) (Full test log of 50 passing unit tests)

---

## Executive Summary & Formal Decision

### Formal Decision: **`PROCEED WITH REDESIGN`**

This independent scientific audit evaluated the Phase 4 implementation and completion report against the raw source code, experimental data, and mathematical formulations. 

### Key Audit Findings:
1. **Spatial Detector Reality Check:** The reported metric improvements for `SpatialCrossConsistencyDetector` are statistically reproducible from raw data, and threshold calibration was confirmed to be free of test-label leakage. However, the claim that spatial cross-consistency **"solves"** univariate blindness is scientifically indefensible. At the operational 99th percentile threshold, the detector achieves only **4.96% recall** (missing 95.04% of degraded hours) and **10.24% precision** (yielding ~74 false alarms per sensor-year). Achieving $>50\%$ recall requires lowering the threshold to a 10% contamination rate, which unleashes over 860 false alarms per year. Spatial cross-consistency provides a statistically detectable relative gain over univariate baselines, but is **not an operationally ready stand-alone solution**.
2. **Network Resilience Topological Flaw:** Independent reconstruction of the 38-node graph revealed a critical structural defect: **the 38 nodes are not an interconnected road network, but 19 completely disconnected two-node link segments.** In the baseline graph, **1,384 out of 1,406 OD pairs (98.44%) are already completely disconnected before any closure.** Consequently, the reported total impedance ($\approx 4.98\text{M seconds}$) and closure cost increases ($\approx 14,306\text{s}$ for Kingston Bridge and $\approx 7,122\text{s}$ for George V Bridge) are **pure mathematical artifacts of the arbitrary $3,600\text{s}$ disconnection penalty**. When closures occur, **still-connected pairs experience exactly 0.0 seconds of rerouting or congestion change**. The simulation does not model network rerouting or spillback.
3. **Monte Carlo Interval Confounding:** In the Monte Carlo uncertainty report, the 95% interval $[14,298.66\text{s}, 14,313.70\text{s}]$ was mislabeled as the "Monte Carlo uncertainty interval" of the estimated mean. It actually describes the **empirical spread of scenario outcomes** ($\pm 1.96 \sigma \approx 15.0\text{s}$ wide), which remains constant as $N$ increases. The true 95% confidence interval of the estimated mean at $N=5,000$ draws is $[14,306.08\text{s}, 14,306.30\text{s}]$ (width $= 0.21\text{s}$, with $\text{SEM} = 0.0539\text{s}$).
4. **Observability Index Normalization Artifact:** The ranking of the Observability Risk Index ($\Omega_e$) is dominated by a normalization artifact. Because the graph consists of isolated links, raw Network Robustness Index ($NRI$) equals $M - t_0$ for one-way edges ($\approx 3,577\text{s}$) and $2M - 2t_0$ for two-way edges ($\approx 7,125\text{s}$). Min-max normalization artificially forces all 18 one-way edges into normalized criticality $< 0.01$, while locking the two two-way edges (Broomielaw and Argyle Street) at $\approx 1.0$. The index reflects the boolean `oneway` attribute rather than true network centrality or bottleneck severity.

---

## 1. Spatial Cross-Consistency Detector Audit

### 1.1 Alignment, Data Integrity & Leakage Verification
- **Raw Data Alignment:** Injected anomaly timestamps, durations, and sensor IDs in `reports/spatial_consistency_results.csv` were verified against `CorruptionEngine.inject_drift()`. Start times are uniformly distributed across the test split (8,760 hours), and labels strictly align.
- **Leakage Verification:** Examination of `citypulse/anomaly/spatial.py` and `scripts/run_spatial_benchmark.py` confirmed that `fit()` was called strictly on `t_train` and `n_train` (2019-10-01 to 2021-09-30). Thresholds were calibrated strictly on `t_val` and `n_val` (2021-10-01 to 2022-09-30) without access to test labels.
- **Class Prevalence:**
  - 24-hour drift scenarios: 24 positive anomaly hours out of 8,760 test hours $\implies$ **prevalence = 0.00274 (0.274%)**.
  - 168-hour drift scenarios: 168 positive anomaly hours out of 8,760 test hours $\implies$ **prevalence = 0.01918 (1.918%)**.
  - This extreme class imbalance ($\approx 1:50$ to $1:365$) explains why PR-AUC and MCC are the only statistically valid evaluation metrics, and why naive accuracy is meaningless.

### 1.2 Multi-Threshold Performance Trade-off Analysis
To evaluate whether the 4.96% recall at the 99th percentile threshold ($c = 0.01$) can be tuned to operational viability, a multi-threshold sensitivity evaluation was executed across 8 contamination levels ($c \in [0.001, 0.200]$) in `scripts/audit_spatial_detector.py`.

The aggregate results across all 5 seeds and 3 corridors for the primary scenario **`Drift (-50%, 168h)`** are detailed below:

| Contamination Rate ($c$) | Decision Threshold ($\tau$) | Recall (Mean) | Precision (Mean) | F1-Score (Mean) | MCC (Mean) | FPR (Mean) | Annual False Positives (Hours/Yr) |
|---|---|---|---|---|---|---|---|
| $0.001$ (99.9th %) | 9.60 | 0.0080 (0.80%) | **0.4048** | 0.0224 | +0.0439 | **0.0005** | **4.0** |
| $0.005$ (99.5th %) | 5.08 | 0.0119 (1.19%) | 0.0580 | 0.0292 | +0.0181 | 0.0033 | 28.3 |
| **$0.010$ (99.0th %)** | **3.75** | **0.0496 (4.96%)** | **0.1024** | **0.0664** | **+0.0585** | **0.0086** | **73.7** |
| $0.020$ (98.0th %) | 2.72 | 0.1568 (15.68%) | 0.1424 | 0.1492 | +0.1318 | 0.0187 | 161.0 |
| $0.050$ (95.0th %) | 1.82 | 0.3551 (35.51%) | 0.1241 | 0.1838 | +0.1844 | 0.0486 | 417.3 |
| $0.100$ (90.0th %) | 1.24 | 0.5655 (56.55%) | 0.0996 | 0.1694 | +0.2049 | 0.1001 | 860.3 |
| $0.150$ (85.0th %) | 0.89 | 0.7043 (70.43%) | 0.0834 | 0.1492 | +0.2058 | 0.1516 | 1,303.0 |
| $0.200$ (80.0th %) | 0.63 | 0.7341 (73.41%) | 0.0664 | 0.1218 | +0.1785 | 0.2023 | 1,737.7 |

### 1.3 Breakdown by Sensor Pair & Drift Duration
Performance varies considerably across physical corridors:
- **Newton Street (`GA0151_A` vs `GC0151_B`):** At $c=0.01$, PR-AUC is $0.1189$, Precision is $0.1228$, Recall is $0.0536$. High baseline correlation along this one-way arterial yields the cleanest differential signal.
- **Kingston Bridge NB (`GL0451_B` vs `GL0401_V`):** PR-AUC is $0.1012$, Precision is $0.0971$, Recall is $0.0476$. Weaving between on-ramps introduces residual variance that dampens sensitivity.
- **Broomielaw (`GA1501_T` vs `GA1851_A`):** PR-AUC is $0.0905$, Precision is $0.0874$, Recall is $0.0476$.
- **Short-Duration Drifts (`24h`):** On 24-hour drifts, PR-AUC drops from $0.1035$ to $0.0359$ at -50%, and to $0.0081$ at -15%. Subtle -15% decalibrations over 24 hours remain largely indistinguishable from diurnal noise ($MCC \approx +0.002$).

### 1.4 Reviewer Verdict on "Solving" Univariate Blindness
The Phase 4 claim that the method "solves" univariate blindness must be formally retracted and restated with scientific precision:
- **Relative Improvement (Confirmed):** Spatial cross-consistency achieves an order-of-magnitude increase in PR-AUC ($0.012 \to 0.1035$) and raises MCC from negative values ($-0.013$) to positive ($+0.0585$), whereas all univariate models have $0.00\%$ recall.
- **Absolute Operational Utility (Flawed):** At a standard 1% false alarm budget, the detector misses **95 out of 100 degraded hours**. To catch more than half of the degraded hours ($>50\%$ recall), the system must accept a 10% FPR, resulting in **860 false alarms per year** per sensor pair (2.4 false alarms per day). In municipal traffic operations, such a false alarm rate induces alert fatigue and system abandonment.
- **Operational Recommendation:** Spatial cross-consistency cannot be used as an automated actuator. It should operate as an **evidence accumulator** that triggers maintenance inspections only after persisting across $\ge 12-24$ contiguous hours.

---

## 2. Network Resilience Model & Graph Topology Audit

### 2.1 Independent Graph Reconstruction & Connectivity Breakdown
The road graph was reconstructed directly from `data/network/glasgow_network_edges.csv`. The file defines 20 directed link records spanning 38 node identifiers (1001 to 1039):

```
Graph Structural Audit:
  Total Nodes: 38
  Total Directed Edges: 22 (19 one-way + 3 two-way edges)
  Total Directed OD Pairs (u != v): 1,406
  Weakly Connected Components: 19 components of size 2 (plus 1 overlap)
  Strongly Connected Components: 35 components
  Baseline Connected OD Pairs: EXACTLY 22 (1.56%)
  Baseline Disconnected OD Pairs: EXACTLY 1,384 (98.44%)
```

### 2.2 The Topological Disconnection Discovery
In an authentic urban network graph, nodes are intersections where multiple links meet, allowing traffic to traverse multi-edge paths and switch routes when links are severed.

In `glasgow_network_edges.csv`:
- `M8_KINGSTON_NB_1` connects node $1001 \to 1002$. No other edge enters 1001 or leaves 1002!
- `M8_KINGSTON_SB_1` connects node $1003 \to 1004$. No other edge connects to 1003 or 1004!
- `GEORGE_V_BRIDGE_SB` connects node $1010 \to 1011$. No other edge connects to 1010 or 1011!
- `GLASGOW_BRIDGE_NB` connects node $1012 \to 1013$. No other edge connects to 1012 or 1013!

**Every single edge in the file was created with completely disjoint node IDs.** The graph is a collection of 20 isolated link "islands" floating in coordinate space. There are **zero network junctions** connecting any bridge to any arterial.

### 2.3 Deconstruction of the 99% Disconnection Figure
The Phase 4 report stated: *"severing Kingston Bridge disconnects 1,388 pairs (98.7%), and George V Bridge disconnects 1,386 pairs (98.6%)."*

The audit proves that the closures did **not** disconnect 1,388 or 1,386 pairs:
- **1,384 pairs were ALREADY disconnected in the baseline graph before any closure was applied!**
- Closing the 4 edges of the M8 Kingston Bridge corridor severed exactly **4 newly disconnected pairs** ($1001 \to 1002, 1003 \to 1004, 1005 \to 1006, 1007 \to 1008$). Total disconnected pairs: $1,384 + 4 = 1,388$.
- Closing the 2 edges of the George V / Glasgow Bridge corridor severed exactly **2 newly disconnected pairs** ($1010 \to 1011, 1012 \to 1013$). Total disconnected pairs: $1,384 + 2 = 1,386$.

### 2.4 Penalty Dominance and Sensitivity Analysis
Because 98.44% of OD pairs are disconnected in baseline, total network impedance is dominated entirely by the arbitrary disconnection penalty parameter $M = 3,600\text{s}$:
$$\mathcal{C}(G)_{\text{base}} = \sum_{\text{22 connected}} \tau_e + (1,384 \times M) = 940.03\text{s} + 4,982,400\text{s} = 4,983,340.03\text{s}$$
The penalty accounts for **99.981%** of total baseline network impedance!

When a bridge is closed:
$$\Delta \mathcal{C} = \sum_{e \in \text{severed}} (M - \tau_e)$$
For Kingston Bridge (4 severed edges): $\Delta \mathcal{C} = (4 \times 3,600\text{s}) - 93.74\text{s} = \mathbf{14,306.26\text{s}}$.  
For George V Bridge (2 severed edges): $\Delta \mathcal{C} = (2 \times 3,600\text{s}) - 77.65\text{s} = \mathbf{7,122.35\text{s}}$.

The sensitivity audit across 6 penalty values in `reports/resilience_connectivity_sensitivity.csv` demonstrates this linear dependency:

| Scenario | Penalty ($M$, sec) | Baseline Cost (s) | Closure Cost (s) | $\Delta \mathcal{C}$ (s) | Newly Disconnected Pairs | $\Delta \mathcal{C}$ for Still-Connected Pairs (s) | Penalty Share of $\Delta \mathcal{C}$ |
|---|---|---|---|---|---|---|---|
| M8 Kingston Closure | 600.0 (10 min) | 831,340.03 | 833,646.29 | 2,306.26 | 4 | **0.0000** | 104.06% |
| M8 Kingston Closure | 1,200.0 (20 min) | 1,661,740.03 | 1,666,446.29 | 4,706.26 | 4 | **0.0000** | 101.99% |
| M8 Kingston Closure | 1,800.0 (30 min) | 2,492,140.03 | 2,499,246.29 | 7,106.26 | 4 | **0.0000** | 101.32% |
| **M8 Kingston Closure** | **3,600.0 (1 hr)** | **4,983,340.03** | **4,997,646.29** | **14,306.26** | **4** | **0.0000** | **100.66%** |
| M8 Kingston Closure | 7,200.0 (2 hr) | 9,965,740.03 | 9,994,446.29 | 28,706.26 | 4 | **0.0000** | 100.33% |
| M8 Kingston Closure | 14,400.0 (4 hr) | 19,930,540.03 | 19,988,046.29 | 57,506.26 | 4 | **0.0000** | 100.16% |
| George V Closure | 600.0 (10 min) | 831,340.03 | 832,462.38 | 1,122.35 | 2 | **0.0000** | 106.92% |
| George V Closure | 1,200.0 (20 min) | 1,661,740.03 | 1,664,062.38 | 2,322.35 | 2 | **0.0000** | 103.34% |
| George V Closure | 1,800.0 (30 min) | 2,492,140.03 | 2,495,662.38 | 3,522.35 | 2 | **0.0000** | 102.20% |
| **George V Closure** | **3,600.0 (1 hr)** | **4,983,340.03** | **4,990,462.38** | **7,122.35** | **2** | **0.0000** | **101.09%** |
| George V Closure | 7,200.0 (2 hr) | 9,965,740.03 | 9,980,062.38 | 14,322.35 | 2 | **0.0000** | 100.54% |
| George V Closure | 14,400.0 (4 hr) | 19,930,540.03 | 19,959,262.38 | 28,722.35 | 2 | **0.0000** | 100.27% |

**Key Review Finding:** In every evaluation, **$\Delta \mathcal{C}$ for still-connected pairs is EXACTLY 0.0000 seconds.** Because the links do not connect to each other, closing the Kingston Bridge causes zero rerouting delay onto the Clyde Arc, George V Bridge, or Victoria Bridge. The metric measures nothing other than $N_{\text{new}} \times M - \text{free\_flow\_time}$.

### 2.5 Inadequacy of Flow-to-Edge Mapping
The methodology assumes detector flow can represent edge flow via simple lane scaling:
$$V_e = q_{\text{detector}} \times \frac{\text{lanes}_e}{\text{lanes}_{\text{detector}}}$$
This assumption is scientifically invalid for three reasons:
1. **Pulse Flows vs Link Volumes:** SCOOT detectors are localized stop-line or advance loops designed for traffic signal optimization. They record stop-and-go platoons, not link-wide spatial traffic volumes.
2. **Lane Homogeneity Fallacy:** Multiplying by lane count assumes equal utilization across 5 highway lanes, ignoring exit-only lanes, weaving zones, and dedicated bus lanes.
3. **Absence of Network Equilibrium:** Traffic cannot simply be assigned to disjoint links without an Origin-Destination matrix and a traffic assignment mechanism (e.g., User Equilibrium or Frank-Wolfe algorithm).

---

## 3. Monte Carlo Uncertainty Audit

### 3.1 Reproducibility of Sample Draw Statistics
The Monte Carlo draws were reproduced across $N \in \{100, 1000, 5000\}$ using master seed 42 in `scripts/audit_monte_carlo.py`:

```
Reproduction Verification (Seed 42, Kingston Bridge Closure):
  N = 100:  Mean = 14,305.73 s, Std = 3.69 s, SEM = 0.3686 s
  N = 1000: Mean = 14,306.28 s, Std = 3.75 s, SEM = 0.1185 s
  N = 5000: Mean = 14,306.19 s, Std = 3.81 s, SEM = 0.0539 s
```
The numerical outputs match the reported values bit-for-bit.

### 3.2 Confounding of Scenario Outcome Spread with Monte Carlo SEM
The Phase 4 report committed a severe statistical error by presenting the 2.5th and 97.5th percentiles of the simulation draws as the "uncertainty interval" of the resilience estimate:
- **Empirical Outcome Spread ($q_{2.5}$ to $q_{97.5}$):** Reflects the physical variance of hypothetical network outcomes under 10% flow volatility. As $N$ increases from 100 to 5,000, this spread **does not shrink**; it stabilizes at approximately **$15.04\text{ seconds}$** ($[14,298.66\text{s}, 14,313.70\text{s}]$).
- **Monte Carlo Estimation Error of the Mean ($\text{SEM}$):** Reflects algorithmic sampling error in computing the expected value. The 95% confidence interval for the mean is:
  $$\bar{X} \pm 1.96 \cdot \text{SEM}$$
  At $N = 100$: $[14,305.01\text{s}, 14,306.45\text{s}]$ (width $= 1.44\text{s}$).  
  At $N = 1,000$: $[14,306.05\text{s}, 14,306.51\text{s}]$ (width $= 0.46\text{s}$).  
  At $N = 5,000$: $[14,306.08\text{s}, 14,306.30\text{s}]$ (width $= \mathbf{0.21\text{s}}$).

Conflating these two concepts obscured the fact that algorithmic Monte Carlo error was already negligible at 1,000 draws ($< 0.5\text{s}$), while physical scenario variability remains $\approx 15\text{s}$.

### 3.3 Sensitivity to Assumed Flow Variance
Testing flow standard deviation across $\sigma_{\text{flow}} \in [0.05, 0.30]$ at $N=1,000$ draws demonstrates:
- At 5% CV: Outcome spread width $= 9.23\text{s}$ ($\sigma = 2.41\text{s}$).
- At 10% CV: Outcome spread width $= 18.59\text{s}$ ($\sigma = 4.83\text{s}$).
- At 20% CV: Outcome spread width $= 37.92\text{s}$ ($\sigma = 9.77\text{s}$).
- At 30% CV: Outcome spread width $= 57.37\text{s}$ ($\sigma = 14.89\text{s}$).

The standard deviation of $\Delta \mathcal{C}$ scales linearly with input flow variance ($\sigma \approx 49.1 \times \text{CV}$). Because the severed edges have no alternate routes, the standard deviation is simply the standard deviation of BPR delay on the severed edges themselves:
$$\sigma(\Delta \mathcal{C}) = \sqrt{\sum_{e \in \text{severed}} \text{Var}\left(\tau_e(\tilde{V}_e)\right)}$$

---

## 4. Observability Risk Index ($\Omega_e$) Audit

### 4.1 Deconstruction of the NRI Normalization Artifact
The Observability Risk Index is defined as:
$$\Omega_e = \widehat{NRI}(e) \cdot \left[1 - \exp\left(-\frac{\text{dist}_e}{D_0}\right)\right]$$
where $\widehat{NRI}(e) = \frac{NRI(e) - \min NRI}{\max NRI - \min NRI}$.

The Phase 4 report reported that `BROOMIELAW_A814` has $\widehat{NRI} = 1.0000$ and `ARGYLE_ST_WB` has $\widehat{NRI} = 0.9895$, while all other 18 edges had $\widehat{NRI} \le 0.0094$.

The audit reveals the exact mathematical reason for this extreme bimodality:
1. `BROOMIELAW_A814` and `ARGYLE_ST_WB` are the only two links in `glasgow_network_edges.csv` with `oneway = False`.
2. When a two-way link is removed in `ObservabilityRiskCalculator.compute_nri()`, the algorithm severs **both directed edges** ($u \to v$ and $v \to u$), disconnecting **2 OD pairs**:
   $$NRI_{\text{two-way}} \approx (2 \times 3,600\text{s}) - 2 t_0 \approx \mathbf{7,100\text{s} - 7,125\text{s}}$$
3. Every other link has `oneway = True`. Removing it severs **1 OD pair**:
   $$NRI_{\text{one-way}} \approx (1 \times 3,600\text{s}) - t_0 \approx \mathbf{3,543\text{s} - 3,577\text{s}}$$
4. Min-max normalization maps the minimum value ($3,543.82\text{s}$, Clyde Arc) to $0.0$, and the maximum ($7,125.37\text{s}$, Broomielaw) to $1.0$. The range is $3,581.55\text{s}$.
5. Consequently, all 18 one-way edges span an $NRI$ difference of only $33.66\text{s}$ ($3,577.48 - 3,543.82$). Divided by $3,581.55\text{s}$, their normalized scores are compressed into $[0.0000, 0.0094]$!

**Conclusion:** The normalized criticality index $\widehat{NRI}(e)$ **does not measure network centrality, flow volume, or congestion risk.** It simply segregates two-way streets ($\approx 1.0$) from one-way streets ($\approx 0.0$).

### 4.2 Distance Scale ($D_0$) Sensitivity & Rank Stability
The ranking was evaluated across $D_0 \in [100\text{m}, 2000\text{m}]$ and penalty $M \in [600\text{s}, 7200\text{s}]$ in `reports/observability_sensitivity.csv`:
- **Rank Stability:** Spearman rank correlation with the baseline ranking exceeds **$0.947$** across all parameter combinations.
- **Why Ranks Appear Stable:** The stability is artificial. Ranks 1 and 2 are permanently locked by Broomielaw and Argyle Street due to their $2 \times M$ penalty. Ranks 3 through 20 are all clustered with normalized $NRI < 0.01$, meaning their ranking is determined almost exclusively by geodetic distance $\text{dist}_e$, which is completely invariant to network parameters.

### 4.3 Classification of the Metric
Because there is zero ground-truth validation data (no records of traffic diversion failures or unobserved congestion incidents), the Observability Risk Index **must be strictly classified as an unvalidated exploratory prioritization heuristic**, not a validated risk measure.

---

## 5. Methodological Boundaries & Sensor Mapping Review

1. **Missing Edge Lengths in Raw Network CSV:** Inspection of `data/network/glasgow_network_edges.csv` revealed that the column `length_m` is completely absent from the file. All resilience calculations defaulted silently to `length_m = 500.0` for all 20 edges. High-speed 1.5 km motorway bridge decks and short 100 m city-centre ramps were assigned identical 500-meter lengths.
2. **Missing Road Graph Topologies:** The project lacks a topological junction table mapping road segment endpoints to shared intersection nodes. Without shared intersection nodes, network routing is impossible.
3. **Sensor-to-Edge Spatial Gaps:** In `reports/sensor_edge_mapping.csv`, out of 470 sensors, only 33 sensors matched edges within 350 meters, and only 12 sensors matched with high confidence ($< 15\text{m}$). Projecting single-detector volume onto multi-lane bridge links is an unverified spatial extrapolation.

---

## 6. Synthesis, Lessons Learned & Redesign Blueprint

### Summary of Audit Determinations

| Phase 4 Component | Phase 4 Claim | Audit Determination | Evidence & Justification |
|---|---|---|---|
| **Spatial Anomaly Detection** | "Breaks univariate blindness; solves downward drift." | **PARTIALLY VALID / OVERSTATED** | Statistically verified relative improvement (PR-AUC $0.012 \to 0.1035$, MCC $+0.0585$), but recall is only 4.96% at 1% FPR. Tuning for $>50\%$ recall causes 860 false alarms/yr. |
| **Shared Event Safeguard** | "Disambiguates network changes from sensor faults." | **VALID** | Verified: during shared corridor drops, spatial difference stays low and state classifier flags `SHARED_CORRIDOR_CHANGE` (16 of 24 hrs). |
| **Network Resilience Graph** | "38-node network model evaluating bridge closure resilience." | **INVALID / STRUCTURALLY FLAWED** | The 38 nodes are 19 isolated link segments with 0 junctions. 98.44% of OD pairs are disconnected in baseline. Still-connected pairs experience 0.0s rerouting delay. |
| **Resilience Cost Output** | "Kingston closure increases network cost by 14,306s." | **INVALID ARTIFACT** | Output is purely $(4 \times 3,600\text{s}) - 93.74\text{s}$. Linear artifact of arbitrary $3,600\text{s}$ penalty cap. |
| **Monte Carlo Uncertainty** | "Monte Carlo uncertainty interval: [14,298s, 14,313s]." | **CONFUSED CONSTRUCTS** | Conflated scenario outcome spread ($\pm 15\text{s}$) with estimation error of the mean ($\pm 0.21\text{s}$ at $N=5000$). |
| **Observability Risk Index** | "Broomielaw identified as critical blind spot ($\Omega_e = 0.5766$)." | **NORMALIZATION ARTIFACT** | Broomielaw and Argyle St rank top solely because `oneway = False` doubles the penalty ($7,125\text{s}$ vs $3,577\text{s}$). |

---

## 7. Redesign Blueprint for Next Milestone

To salvage the valuable contributions of the project while eliminating invalid artifacts, the project must implement the following redesign:

### 1. Reconstruct an Authentically Connected Road Topology
- Replace the disjoint 20-edge file with an interconnected directed graph where intersection nodes are shared between intersecting edges (e.g., Broomielaw connecting to George V Bridge and Jamaica Bridge).
- Compute real edge lengths from geodetic coordinates ($\text{u\_lat}, \text{u\_lon} \to \text{v\_lat}, \text{v\_lon}$) rather than relying on a hardcoded 500-meter fallback.

### 2. Formulate Resilience as a Subgraph Rerouting Metric
- Restrict OD pairs strictly to the set of nodes that are **strongly connected in baseline** ($\mathcal{C}_{\text{conn}}(G)$).
- Measure resilience as the actual detour delay increase on connected paths:
  $$\Delta \mathcal{C}_{\text{detour}} = \sum_{(u, v) \in OD_{\text{conn}}} \left[ d_{G \setminus \{e\}}(u, v) - d_G(u, v) \right]$$
- Separate topological disconnection count ($\Delta N_{\text{disc}}$) completely from travel impedance ($\Delta \mathcal{C}_{\text{detour}}$) instead of conflating them via an arbitrary $3,600\text{s}$ penalty.

### 3. Redesign Anomaly Detection into a Multi-Stage Pipeline
- Do not deploy spatial cross-consistency as a single-hour binary classifier.
- Implement an **evidence persistence filter**: raise a hardware fault warning only when the spatial discrepancy $d_{s, n, t} > 2.0$ persists for $\ge 6$ consecutive hours.
- Acknowledge that 93% of Glasgow sensors have no spatial peers and must rely on univariate seasonal models with manual operational inspection.

### 4. Recalibrate Observability Index
- Redefine link criticality using betweenness centrality or connected rerouting impact rather than raw disconnection penalties.
- Normalize one-way and two-way roads on a per-directed-edge basis to prevent the boolean `oneway` attribute from dominating the index.

---

### Audit Sign-off:
The Phase 4.1 independent scientific review is complete. All 50 tests pass offline, all audit CSVs are generated, and the project is positioned to **`PROCEED WITH REDESIGN`**.
