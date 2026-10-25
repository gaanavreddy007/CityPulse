# Research Gap Analysis & Realistic Contributions: CITYPULSE

**Project:** CITYPULSE  
**Audited Question:**  
> *"How does traffic-sensor data quality and uncertainty affect urban mobility anomaly detection and estimates of road-network resilience under hypothetical disruptions?"*  
**Date:** October 2026  
**Auditor:** Automated Pair-Programming Research Agent (Antigravity)  
**Budget Constraint:** £0.00 (Exclusively free, accessible data and open-source tools)  

---

## 1. Synthesis of Identified Research Gaps

The prior-art audit across five literature domains ([`reports/related_work.md`](file:///C:/Gaanav/Projects/CityPulse/reports/related_work.md)) reveals that while traffic anomaly detection and transport network resilience are individually mature fields, their **coupling remains almost entirely unaddressed**. 

```
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│       SILO A: SENSOR DATA QC         │       │     SILO B: NETWORK RESILIENCE       │
│  - Missing data imputation           │       │  - Graph-theoretic vulnerability     │
│  - Loop detector fault diagnostics   │       │  - Link removal simulation (NRI)     │
│  - Anomaly detection (PyOD, ST-GNN)  │       │  - Shortest path travel delay        │
│  * Evaluation: RMSE, MAE, F1-Score   │       │  * Evaluation: System-wide delay     │
└──────────────────┬───────────────────┘       └──────────────────┬───────────────────┘
                   │                                              │
                   └───────────────────┐      ┌───────────────────┘
                                       ▼      ▼
                        ┌────────────────────────────────────┐
                        │      THE UNADDRESSED GAP           │
                        │ How does sensor noise, missingness │
                        │ and false anomaly detection skew   │
                        │ downstream network resilience and  │
                        │ critical link ranking?             │
                        └────────────────────────────────────┘
```

### Gap 1: Decoupling of Sensor Uncertainty from Network Topological Resilience
* **Current State:** Transportation resilience literature (e.g., Jenelius, Petersen, & Mattsson, 2006; Mattsson & Jenelius, 2015; Scott et al., 2006) calculates the Network Robustness Index (NRI) or link criticality assuming deterministic, known edge parameters (speed limits, fixed capacities, or static Bureau of Public Roads [BPR] volume-delay curves).
* **Deficiency:** Real-world traffic management systems rely on noisy, drifting, and intermittently missing sensor feeds (such as SCOOT loop detectors). No benchmark investigates how empirical sensor measurement uncertainty propagates through graph-traversal algorithms (e.g., Dijkstra, Contraction Hierarchies) to distort network resilience estimates.

### Gap 2: Asymmetric Downstream Penalties of Sensor Faults vs. Physical Incidents
* **Current State:** Anomaly detection literature treats false positives and false negatives as symmetric statistical penalties evaluated via receiver operating characteristic (ROC) curves or F1-scores on isolated sensor feeds (e.g., Laszka et al., 2017; Zhao et al., 2019).
* **Deficiency:** In an urban road network, the operational consequences of these errors are fundamentally asymmetric:
  * A *false positive* (a faulty sensor reporting zero flow or zero speed due to hardware dropouts) misleads rerouting engines into declaring a phantom bottleneck, causing unwarranted traffic diversion onto unsuitable residential corridors.
  * A *false negative* (a sensor failing to detect actual gridlock caused by a bridge closure) delays incident response and blinds routing algorithms to cascading congestion.
  Existing literature does not evaluate the network-level travel time cost of these competing error modes.

### Gap 3: Observability Bias Induced by Spatial Sensor Sparsity
* **Current State:** SCOOT detector networks are non-uniformly distributed across urban road graphs. In Glasgow, over 400 SCOOT sensors are clustered around the city center, signalized junctions, and major arterials, while peripheral connectors and secondary alternative routes remain uninstrumented (Li et al., 2025).
* **Deficiency:** When a major crossing is severed (such as the M8 Kingston Bridge or George V Bridge over the River Clyde), diversion traffic spills into the secondary and unmonitored network. Current resilience models cannot quantify the "observability gap"—how much resilience degradation goes undetected because the sensors are in the wrong place.

---

## 2. Three Realistic, Implementable Contributions

To address these gaps without manufacturing novelty through terminology or relying on paid datasets, we formulate three concrete, tightly coupled contributions. All three are 100% implementable in Python using free, accessible open-source libraries and public Glasgow open data.

---

### Contribution 1: Multi-Regime Sensor Degradation Benchmark on Empirical Glasgow SCOOT Data

#### Research Question Addressed:
*How do realistic sensor degradation regimes (random dropouts, burst communication loss, calibration drift, and frozen readings) degrade anomaly detection performance, and at what error thresholds do detectors reliably separate hardware faults from genuine physical traffic anomalies?*

#### Methodological Formulation:
Using the 4-year, hourly Glasgow SCOOT traffic flow dataset (Li, Zhao, & Wang, 2025; Zenodo DOI: 10.5281/zenodo.12100278; CC BY 4.0), we establish an empirical baseline across 400+ detector locations. We inject controlled, parameterized synthetic degradation profiles:
1. **Missing Completely at Random (MCAR):** Uniform dropouts from $p \in [0.05, 0.50]$ simulating packet loss.
2. **Missing Not at Random (MNAR) / Burst Outages:** Contiguous outages spanning $\tau \in [4, 24]$ hours simulating power cuts or localized backhaul disruptions.
3. **Calibration Drift / Multiplicative Bias:** Systematic scaling $x'_t = (1 \pm \delta) x_t$ with $\delta \in [0.10, 0.40]$ simulating physical sensor misalignment.
4. **Stuck-at-Value (Freeze):** Sensors frozen at zero flow or historical mean flow.

We evaluate a standardized suite of open-source anomaly detectors from `PyOD` and time-series methods:
* Statistical baselines: Seasonal Median Absolute Deviation (MAD), Z-score.
* Unsupervised ML: Isolation Forest (`iForest`), Empirical Cumulative Distribution Outlier Detection (`ECOD`).
* Spatial Cross-Consistency Filter: An adjacent-detector correlation filter comparing target sensor flow against upstream/downstream neighbors on the OpenStreetMap graph.

#### Evaluation Metrics:
* Precision-Recall AUC (PR-AUC), F1-Score, False Positive Rate (FPR) across degradation regimes.
* Anomaly Disambiguation Index ($ADI$): The mathematical separation margin between hardware failure signatures (sharp, isolated step changes) and traffic incident signatures (spatio-temporal wave propagation across neighboring sensors).

---

### Contribution 2: Probabilistic Uncertainty-Propagation Pipeline for Road-Network Resilience

#### Research Question Addressed:
*When empirical sensor flows are used to calibrate dynamic link costs, how does sensor uncertainty propagate through graph traversal to alter total system travel delay ($\Delta T$) and the Network Robustness Index (NRI) under hypothetical closures of key Glasgow river crossings?*

#### Methodological Formulation:
1. **Graph Construction:** Download the routable drivable road network of Glasgow via `OSMnx` from OpenStreetMap (ODbL). Build a directed, topologically clean multigraph $G = (V, E)$.
2. **Empirical Edge Calibration:** Map SCOOT sensor coordinates to the nearest OSM road segments via spatial KD-Tree matching. Calibrate baseline link travel times using hourly flow-to-speed conversion via the standard BPR (Bureau of Public Roads) function:
   $$t_e(q_e) = t_e^0 \left[1 + \alpha \left(\frac{q_e}{C_e}\right)^\beta\right]$$
   where $t_e^0$ is free-flow travel time, $C_e$ is estimated lane capacity, and $q_e$ is the observed or imputed SCOOT volume.
3. **Uncertainty Propagation via Monte Carlo Ensembles:** Instead of deterministic values, each sensor flow $q_e$ is modeled as a probabilistic distribution $q_e \sim \mathcal{N}(\mu_e, \sigma_e^2 + \sigma_{\text{impute}}^2)$ reflecting sensor variance and imputation uncertainty from Contribution 1. We sample $M = 500$ realizations of network edge weights.
4. **Hypothetical Disruption Stress-Testing:** Simulate the targeted closure of critical Glasgow transport infrastructure:
   * **Scenario A (Motorway Severance):** Complete closure of the M8 Kingston Bridge across the River Clyde (the busiest road bridge in Scotland).
   * **Scenario B (Arterial River Crossings):** Simultaneous closure of city-center crossings (George V Bridge and Glasgow Bridge).
   * **Scenario C (Sequential Link Deletion):** Top-$K$ edge removal based on betweenness centrality.
5. **Systemic Resilience Metric:** For each Monte Carlo realization $m$, compute the Network Robustness Index:
   $$NRI(e) = \sum_{(o, d) \in \mathcal{W}} \left[ d_m(o, d \mid G \setminus \{e\}) - d_m(o, d \mid G) \right] \cdot w_{od}$$
   where $\mathcal{W}$ represents origin-destination pairs sampled across Glasgow's 56 Intermediate Data Zones, and $w_{od}$ represents population travel weights.

#### Evaluation Metrics:
* Resilience Distortion Ratio: Ratio of predicted delay under noisy/imputed sensor data versus ground-truth baseline: $\mathcal{R}_{\text{dist}} = \mathbb{E}[\Delta T_{\text{noisy}}] / \Delta T_{\text{clean}}$.
* 95% Confidence Bounds on network travel-time degradation under bridge closure scenarios.
* Kolmogorov-Smirnov test assessing the divergence between deterministic and uncertainty-aware resilience curves.

---

### Contribution 3: Observability Bias and Critical Link Ranking Robustness Analysis

#### Research Question Addressed:
*How does spatial sensor sparsity distort the identification of critical infrastructure links, and what are the unobserved vulnerability hotspots in Glasgow's diversion corridors?*

#### Methodological Formulation:
1. **Criticality Ranking Comparison:** Calculate the criticality of all major Glasgow links under full network knowledge vs. sensor-restricted knowledge. In the sensor-restricted state, flow and congestion information is only available on links containing SCOOT detectors; all other links default to uncalibrated free-flow speed limits.
2. **Rank Perturbation Metric:** Measure the distortion of critical link prioritization using:
   * **Spearman's Rank Correlation ($\rho_s$):** Measuring global rank reordering of the top 100 vulnerable links.
   * **Top-$K$ Jaccard Similarity ($J_K$):** Measuring whether transportation authorities identify the exact same top-10 or top-20 most critical links under data uncertainty:
     $$J_K = \frac{|\mathcal{T}_K^{\text{true}} \cap \mathcal{T}_K^{\text{sensor}}|}{|\mathcal{T}_K^{\text{true}} \cup \mathcal{T}_K^{\text{sensor}}|}$$
3. **Identification of Unobserved Vulnerability Hotspots:** Define the *Vulnerability Observability Deficit* ($VOD_e$) for link $e$:
   $$VOD_e = NRI(e) \cdot \text{dist}(e, \mathcal{S}_{\text{sensor}})$$
   where $\text{dist}(e, \mathcal{S}_{\text{sensor}})$ is the network shortest distance from link $e$ to the nearest active SCOOT detector. Links with high $VOD_e$ are high-consequence failure points that exist in complete sensor blind spots.

#### Evaluation Metrics:
* Decay curve of Spearman $\rho_s$ and Jaccard $J_K$ as sensor coverage is systematically thinned from 100% down to 20%.
* Spatial mapping and classification of Glasgow's top unobserved diversion corridors during River Clyde crossing closures.

---

## 3. Feasibility and £0 Budget Compliance

| Dimension | Requirement | CITYPULSE Implementation | Cost |
| :--- | :--- | :--- | :--- |
| **Data Acquisition** | Multi-year urban traffic flow data | UBDC Glasgow SCOOT dataset (Zenodo DOI: 10.5281/zenodo.12100278; CC BY 4.0; 470 sensors; 2019–2023) | **£0.00** |
| **Geospatial Graph** | Routable road network topology | OpenStreetMap via `osmnx` (ODbL) | **£0.00** |
| **Demographic Weights** | Origin-Destination travel weighting | Scottish Government Data Zones & Scottish Index of Multiple Deprivation (SIMD; OGL v3.0) | **£0.00** |
| **Software Stack** | Geospatial, ML, graph processing | Python 3.10+, `osmnx`, `networkx`, `geopandas`, `pyod`, `scipy`, `matplotlib` | **£0.00** |
| **Compute Hardware** | Graph routing & Monte Carlo sampling | Local workstation execution; sub-minute shortest-path computation for Glasgow urban boundary using vectorized Dijkstra | **£0.00** |

All components are strictly non-commercial, fully reproducible, and legally compliant with open-access terms.

---

## 4. Final Recommendation and Next Actions

### Final Recommendation: **PROCEED**

* **Novelty:** The research question addresses a verified void in the literature—the propagation of sensor data quality degradation and anomaly misclassification into road-network topological resilience and link criticality rankings.
* **Academic Integrity:** It does not manufacture novelty by renaming existing algorithms. It combines established foundational theories (Jenelius & Mattsson NRI, PyOD anomaly detection, OSMnx graph models) to solve an open engineering question on empirical Glasgow data.
* **Feasibility:** Verified datasets (UBDC Zenodo), open tooling, and £0 budget.

### Next Steps for Implementation:
1. **Data Ingestion:** Download `status.csv`, `locations.csv`, and sample representative sensor flow CSVs from Zenodo `10.5281/zenodo.12100278`.
2. **Network Model:** Build the Glasgow road graph via `OSMnx` and match sensor points to graph edges.
3. **Execution:** Implement Contributions 1, 2, and 3 sequentially with full unit tests and reproducible reporting.
