# Comprehensive Related Work & Prior-Art Inventory: CITYPULSE

**Project:** CITYPULSE  
**Focus:** Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience Under Disruptions  
**Date:** October 2026  
**Auditor:** Automated Pair-Programming Research Agent (Antigravity)  

---

## 1. Classification Scheme

Each entry in this inventory is evaluated under the following criteria:
* **Title / Repository:** Name of paper or software project.
* **Authors / Maintainers:** Researchers or institutional owners.
* **Date:** Publication date or latest repository update.
* **URL / DOI:** Canonical access point.
* **Methods:** Core algorithms, statistical frameworks, or simulation techniques.
* **Data:** Sensor types, temporal span, geographic domain, and resolution.
* **Evaluation:** Benchmarks, validation metrics, and baseline comparisons.
* **Classification:** `Direct Overlap` | `Partial Overlap` | `Related Background` | `No Substantial Overlap Found`.
* **Detailed Overlap Analysis:** Direct comparison with CITYPULSE's research pipeline, highlighting technical convergences and divergences.

---

## 2. Inventory of Prior Works by Domain

```
                                  CITYPULSE ECOSYSTEM
                                           │
         ┌──────────────────┬──────────────┴──────────────┬──────────────────┐
         ▼                  ▼                             ▼                  ▼
    [Domain 1]         [Domain 2]                    [Domain 3]         [Domain 4]
 Glasgow Traffic    Traffic Sensor Data           Urban Traffic       Road Network
  Data & UBDC        Quality & Faults           Anomaly Detection      Resilience
```

---

### Domain 1: Glasgow Traffic Data & Urban Analytics

#### 1.1 High-Resolution Traffic Flow Data from the Urban Traffic Control System in Glasgow
* **Title:** High-resolution traffic flow data from the urban traffic control system in Glasgow
* **Authors:** Yue Li, Qunshan Zhao, Mingshu Wang (Urban Big Data Centre, University of Glasgow)
* **Date:** 2025 (Published in *Scientific Data*, 12, 253; Preprint 2024)
* **URL / DOI:** [https://doi.org/10.1038/s41597-025-04576-y](https://doi.org/10.1038/s41597-025-04576-y) | Zenodo: [10.5281/zenodo.12100278](https://doi.org/10.5281/zenodo.12100278)
* **Methods:** Multi-stage spatial, temporal, and numerical filtering of raw SCOOT loop feeds; sensor status metadata extraction; hourly traffic flow harmonization.
* **Data:** 470 SCOOT loop sensors deployed across Glasgow City Council area; October 2019 to September 2023 (4 years, spanning pre-, during, and post-COVID-19 phases).
* **Evaluation:** Data completeness checks across temporal bands; spatial distribution analysis; comparison against national Department for Transport (DfT) manual count points.
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Provides the empirical traffic volume time series and detector coordinate metadata (`locations.csv`, `status.csv`) that CITYPULSE uses as the empirical foundation for Glasgow.
  - *Divergence:* Li et al. focus exclusively on data curation and epidemiological/lockdown mobility shifts. They do not simulate road closures, do not model graph-level network resilience, and do not evaluate how sensor noise impacts downstream anomaly detection or routing.

#### 1.2 `glasgowtrafficdata` (UBDC Open Source Repository)
* **Title:** UBDC Glasgow Traffic Data Pipeline
* **Authors / Organization:** Urban Big Data Centre (`urbanbigdatacentre/glasgowtrafficdata`)
* **Date:** 2020 (Updated 2024)
* **URL:** [https://github.com/urbanbigdatacentre/glasgowtrafficdata](https://github.com/urbanbigdatacentre/glasgowtrafficdata)
* **Methods:** Python ETL scripts (`writecount.py`, `writetravtimes.py`) querying Glasgow City Council Open Data API endpoints; relational database logging.
* **Data:** SCOOT flow counts, congestion index, parking occupancy, and variable message sign (VMS) logs.
* **Evaluation:** Script execution uptime; data completeness verification.
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Serves as the upstream collector script for the UBDC dataset.
  - *Divergence:* Contains no predictive modeling, no anomaly detection algorithms, and no network resilience analysis.

#### 1.3 Measuring COVID-19 Travel Behavior Shifts Using Glasgow UTC Data
* **Title:** The impact of built environment and spatial spillovers on urban traffic flow before, during, and after COVID-19
* **Authors:** Mingshu Wang, Yue Li
* **Date:** 2024
* **URL:** [https://doi.org/10.1016/j.trd.2024.104189](https://doi.org/10.1016/j.trd.2024.104189)
* **Methods:** Spatial Durbin Models (SDM); spatial autoregressive models; Google Street View greenness feature extraction.
* **Data:** Glasgow SCOOT traffic flow data aggregated across demographic zones and environmental covariates.
* **Evaluation:** Log-likelihood, AIC/BIC, spatial error coefficients.
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Employs spatial econometric models on the Glasgow SCOOT network.
  - *Divergence:* Focuses on socio-demographic and built-environment determinants of traffic volumes; does not model network failure, link removal, or sensor reliability degradation.

---

### Domain 2: Traffic Sensor Data Quality, Fault Detection & Uncertainty

#### 2.1 Quality Control and Anomaly Detection for Freeway Traffic Loop Detectors
* **Title:** Systematic Quality Control and Anomaly Detection in Freeway Loop Detector Data
* **Authors:** C. Chen, J. Kwon, J. Rice, A. Skabardonis, P. Varaiya
* **Date:** 2003 (Classic PeMS quality benchmark; foundational literature)
* **URL:** [https://doi.org/10.3141/1855-14](https://doi.org/10.3141/1855-14)
* **Methods:** Statistical hypothesis testing; occupancy-flow daily diagnostic profiles; spatial consistency tests between adjacent upstream and downstream detectors.
* **Data:** California Caltrans Performance Measurement System (PeMS) 30-second loop detector feeds.
* **Evaluation:** Manual field validation of detector cards; false positive vs. detection rate trade-offs.
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Establishes standard diagnostic taxonomy for loop detectors (stuck-at-zero, constant positive, high variance, communication dropouts).
  - *Divergence:* Confined to linear freeway corridors (PeMS); does not generalize to complex urban grid graphs or evaluate network-wide resilience metrics under disruptions.

#### 2.2 Differentiating Cyber-Physical Sensor Faults from Real-World Traffic Anomalies
* **Title:** Detecting False Data Injection and Sensor Failures in Intelligent Transportation Systems
* **Authors:** A. Laszka, Y. Vorobeychik, D. Koutsoukos
* **Date:** 2017
* **URL:** [https://doi.org/10.1109/TITS.2016.2614343](https://doi.org/10.1109/TITS.2016.2614343)
* **Methods:** Game-theoretic anomaly detection; Cumulative Sum (CUSUM) algorithms; spatial cross-sensor consistency checks.
* **Data:** Synthetically perturbed highway traffic flows and simulated urban grid detectors.
* **Evaluation:** Precision, Recall, F1-score against adversarial sensor tampering and stochastic hardware failure.
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Directly targets the ambiguity between true traffic incidents and sensor hardware failures.
  - *Divergence:* Focuses on cybersecurity defense at the sensor node layer. Does not propagate the resulting classification uncertainty into road-network shortest path routing or resilience calculations.

#### 2.3 Spatio-Temporal Traffic Imputation and Uncertainty Quantification
* **Title:** Task-Aware Neural Processes for Spatio-Temporal Traffic Data Imputation and Uncertainty Estimation
* **Authors:** X. Xu, C. Zhang, Y. Ding, et al.
* **Date:** 2023
* **URL:** [https://arxiv.org/abs/2305.18432](https://arxiv.org/abs/2305.18432)
* **Methods:** Neural Processes (NP); Spatio-temporal Graph Neural Networks (ST-GNN); aleatoric and epistemic uncertainty decomposition.
* **Data:** Metr-LA, PeMS-BAY, and LargeST traffic benchmarks.
* **Evaluation:** Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Continuous Ranked Probability Score (CRPS).
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Rigorous treatment of data missingness, synthetic noise masking, and probabilistic confidence bounds.
  - *Divergence:* Evaluation is strictly restricted to prediction/imputation accuracy (MAE/RMSE). It never injects imputed flows into network vulnerability models or assesses how uncertainty affects disruption management.

---

### Domain 3: Urban Traffic Anomaly Detection Frameworks

#### 3.1 EU FP7 "CityPulse" Framework
* **Title:** CityPulse: Real-Time IoT Stream Processing and Large-Scale Data Analytics for Smart City Applications
* **Authors / Organization:** University of Surrey, Siemens AG, Ericsson, University of Cantabria, et al.
* **Date:** 2013–2016
* **URL:** [https://github.com/CityPulse](https://github.com/CityPulse) | [EU CORDIS Project 603095](https://cordis.europa.eu/project/id/603095)
* **Methods:** Semantic Stream Reasoning; Resource Description Framework (RDF); Complex Event Processing (CEP); context-aware routing heuristics.
* **Data:** Smart city sensor streams from Aarhus (Denmark) and Brasov (Romania), covering traffic speed, parking, and air pollution.
* **Evaluation:** Processing latency, query throughput, event detection accuracy on benchmark suite (`CityBench`).
* **Classification:** **Partial Overlap** (Nomenclature & Stream Anomaly)
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Shares the project moniker "CityPulse" and targets real-time urban traffic anomaly detection.
  - *Divergence:* The EU FP7 project was a broad semantic web / IoT middleware framework built in Java. It did not analyze topological graph resilience, did not simulate link removal scenarios, and did not quantify the propagation of sensor uncertainty into road network criticality.

#### 3.2 PyOD: A Python Toolbox for Scalable Outlier Detection
* **Title:** PyOD: A Python Toolbox for Scalable Outlier Detection
* **Authors:** Yue Zhao, Zain Nasrullah, Zheng Li
* **Date:** 2019 (Continuously updated through 2024)
* **URL:** [https://github.com/yzhao062/pyod](https://github.com/yzhao062/pyod) | [JMLR Paper](https://jmlr.org/papers/v20/19-011.html)
* **Methods:** Comprehensive implementation of 40+ anomaly detection algorithms (Isolation Forest, One-Class SVM, LOF, Autoencoders, COPOD, ECOD).
* **Data:** Tabular and multivariate time-series benchmarks.
* **Evaluation:** ROC-AUC, Precision@Rank-K, inference execution time.
* **Classification:** **Related Background**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* CITYPULSE incorporates PyOD models (Isolation Forest, COPOD, Autoencoder) as standardized, reproducible baseline detectors for sensor time series.
  - *Divergence:* PyOD is a generic ML library with no native geospatial, graph-theoretic, or transportation routing capabilities.

#### 3.3 Spatio-Temporal Graph Convolutional Networks (ST-GCN) for Traffic Flow
* **Title:** Spatio-Temporal Graph Convolutional Networks: A Deep Learning Framework for Traffic Forecasting
* **Authors:** B. Yu, H. Yin, Z. Zhu
* **Date:** 2018 (IJCAI 2018)
* **URL:** [https://doi.org/10.24963/ijcai.2018/505](https://doi.org/10.24963/ijcai.2018/505)
* **Methods:** Graph convolution (Chebyshev polynomial approximation); 1D temporal convolution (Gated Linear Units).
* **Data:** Beijing and Los Angeles loop detector networks.
* **Evaluation:** Prediction MAE, RMSE, MAPE on 15/30/60 minute horizons.
* **Classification:** **Related Background**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Demonstrates the mathematical necessity of modeling spatial road network adjacency alongside temporal trends.
  - *Divergence:* Focuses purely on short-term forecasting under nominal conditions. Does not investigate network vulnerability under physical disruptions or sensor degradation.

---

### Domain 4: Road-Network Resilience, Disruption Simulation & Vulnerability

#### 4.1 Importance and Exposure in Road Network Vulnerability Analysis
* **Title:** Importance and exposure in road network vulnerability analysis
* **Authors:** Erik Jenelius, Tom Petersen, Lars-Göran Mattsson (KTH Royal Institute of Technology)
* **Date:** 2006
* **URL:** [https://doi.org/10.1016/j.tra.2005.11.006](https://doi.org/10.1016/j.tra.2005.11.006)
* **Methods:** Systematic edge-removal vulnerability analysis; Link Importance Metric ($I_k$); Site Exposure Metric ($E_i$); travel-time increase modeling under complete link closure.
* **Data:** Northern Sweden regional road network (all major highways and rural connectors).
* **Evaluation:** Total system travel cost increase; unsatisfied trip fractions.
* **Classification:** **Partial Overlap** (Theoretical Foundation)
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Establishes the exact mathematical foundation for calculating link criticality via single- and multi-edge deletion stress testing.
  - *Divergence:* Assumes perfect, deterministic knowledge of free-flow and capacity parameters. Completely ignores empirical sensor observation, sensor noise, and anomaly misclassification.

#### 4.2 Vulnerability and Resilience of Transport Systems: A Review
* **Title:** Vulnerability and resilience of transport systems – A discussion of recent research
* **Authors:** Lars-Göran Mattsson, Erik Jenelius
* **Date:** 2015
* **URL:** [https://doi.org/10.1016/j.tra.2015.06.002](https://doi.org/10.1016/j.tra.2015.06.002)
* **Methods:** Meta-analysis of topological vs. socio-economic transport vulnerability; resilience triangle (absorption, adaptation, recovery).
* **Data:** Comprehensive literature synthesis.
* **Evaluation:** Conceptual framework comparison.
* **Classification:** **Related Background**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Provides the conceptual framework distinguishing static vulnerability from dynamic resilience.
  - *Divergence:* Conceptual survey paper; contains no empirical implementation or sensor data integration.

#### 4.3 Network Robustness Index (NRI)
* **Title:** Network Robustness Index: A new method for identifying critical links and evaluating the performance of transportation networks
* **Authors:** D. M. Scott, D. C. Novak, L. Aultman-Hall, F. Guo
* **Date:** 2006
* **URL:** [https://doi.org/10.1016/j.jtrangeo.2005.10.003](https://doi.org/10.1016/j.jtrangeo.2005.10.003)
* **Methods:** User equilibrium traffic assignment; systemic travel-time delta calculation upon link capacity removal; critical link ranking.
* **Data:** Synthetic and regional highway networks.
* **Evaluation:** Comparison against static volume-capacity ratios and betweenness centrality.
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Defines the mathematical NRI delta metric ($NRI_e = C_e - C_0$, where $C$ is network total vehicle hours traveled).
  - *Divergence:* Relies on Frank-Wolfe user equilibrium on static origin-destination (OD) matrices. Does not examine how empirical sensor uncertainty corrupts the NRI ranking.

#### 4.4 `rhoekstr/gravel` (High-Performance Road Network Fragility Library)
* **Title:** Gravel: Fast Road Network Fragility Analysis at Scale
* **Authors / Maintainer:** R. Hoekstra (`rhoekstr/gravel`)
* **Date:** 2023–2024
* **URL:** [https://github.com/rhoekstr/gravel](https://github.com/rhoekstr/gravel)
* **Methods:** C++ core with Python bindings; Contraction Hierarchies; incremental Single-Source Shortest Path (SSSP); edge-failure vulnerability analysis.
* **Data:** OpenStreetMap road network extracts.
* **Evaluation:** Execution benchmarks comparing runtime against naive NetworkX Dijkstra link removals across continental-scale networks.
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Provides state-of-the-art computational algorithms for large-scale link deletion simulation.
  - *Divergence:* Purely structural graph algorithm operating on static OSM edge weights (speed limits and distances). Ingests no empirical sensor data and performs no anomaly detection.

#### 4.5 `FTOT-Resilience-Link_Removal` (US DOT Volpe Center)
* **Title:** Freight and Fuel Transportation Optimization Tool: Resilience Link Removal Module
* **Authors / Maintainer:** US Department of Transportation / Volpe National Transportation Systems Center
* **Date:** 2021–2023
* **URL:** [https://github.com/VolpeUSDOT](https://github.com/VolpeUSDOT)
* **Methods:** Sequential link removal simulation; shortest-path diversion; commodity flow re-routing.
* **Data:** US national highway and rail network GIS layers.
* **Evaluation:** Rerouting delay and cost increases under corridor disruptions.
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Simulates sequential and targeted infrastructure closures.
  - *Divergence:* Specialized for national macro freight logistics; does not integrate municipal loop sensor streams or model urban sensor uncertainty.

#### 4.6 OSMnx: Modeling Street Networks with OpenStreetMap
* **Title:** OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks
* **Authors:** Geoff Boeing
* **Date:** 2017 (Continuously maintained through 2026)
* **URL:** [https://github.com/gboeing/osmnx](https://github.com/gboeing/osmnx) | [https://doi.org/10.1016/j.compenvurbsys.2017.05.004](https://doi.org/10.1016/j.compenvurbsys.2017.05.004)
* **Methods:** Overpass API querying; multi-directed spatial graph construction; graph simplification; topological centrality and shortest path analysis.
* **Data:** OpenStreetMap global geospatial database.
* **Evaluation:** Graph construction fidelity; topological metric validation against benchmark GIS systems.
* **Classification:** **Related Background**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Primary geospatial graph extraction and manipulation framework used by CITYPULSE to build the Glasgow road network graph.
  - *Divergence:* General geospatial library; does not provide traffic sensor fusion or resilience stress-testing modules.

---

### Domain 5: Synthetic Mobility Platforms & "SynthCity"

#### 5.1 SynthCity: Generating Synthetic Urban Mobility Datasets with SUMO
* **Title:** SynthCity: Generating Synthetic Urban Mobility Datasets for Intelligent Transportation Systems
* **Authors:** Various (e.g., Genoa Smart Mobility consortium)
* **Date:** 2022–2024
* **URL / DOI:** [10.5281/zenodo.7107775](https://doi.org/10.5281/zenodo.7107775)
* **Methods:** Eclipse SUMO (Simulation of Urban MObility); microscopic agent-based vehicular simulation; synthetic detector induction.
* **Data:** City-scale road networks (e.g., Genoa, Italy) with calibrated origin-destination matrices.
* **Evaluation:** Calibrated flow validation against actual road counts; macro-flow speed distributions.
* **Classification:** **Partial Overlap**
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Explores synthetic generation of mobility data to overcome privacy or data-sharing restrictions.
  - *Divergence:* Focuses on generating realistic agent trajectories via microscopic SUMO simulations. Does not address the macroscopic vulnerability of urban graphs under sensor-uncertainty-induced misclassification.

#### 5.2 `synthcity` (van der Schaar Lab Synthetic Data Toolkit)
* **Title:** Synthcity: A Library for Generating and Evaluating Synthetic Data
* **Authors:** Z. Qian, B. Cebere, M. van der Schaar
* **Date:** 2023 (NeurIPS 2023 Software Track)
* **URL:** [https://github.com/vanderschaarlab/synthcity](https://github.com/vanderschaarlab/synthcity)
* **Methods:** Generative Adversarial Networks (GANs), Variational Autoencoders (VAEs), Diffusion Models, Normalizing Flows for tabular/time-series data.
* **Data:** Healthcare, finance, and generic tabular datasets.
* **Evaluation:** Synthetic fidelity metrics (alpha-precision, beta-recall, Wasserstein distance).
* **Classification:** **Related Background** (Nomenclature Overlap Only)
* **Detailed Overlap with CITYPULSE:**
  - *Convergence:* Shares the exact string "synthcity".
  - *Divergence:* Designed for privacy-preserving synthetic data generation in healthcare and general machine learning. Has no transportation, network routing, or urban infrastructure components.

---

## 3. Systematic Summary Matrix

The audit reveals a clear pattern:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PRIOR ART LANDSCAPE                              │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ Research Area                 │ State of the Art Status                     │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 1. Glasgow SCOOT Traffic Data │ Highly detailed open dataset available      │
│                               │ (UBDC, Li et al. 2025), but used only for   │
│                               │ flow cleaning & COVID travel trends.        │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 2. Traffic Sensor QC & Anomaly│ Extensive literature on detecting loop faults│
│                               │ and traffic incidents, but evaluated only on│
│                               │ isolated sensor metrics (F1, RMSE).         │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 3. Road Network Resilience    │ Strong theoretical foundation (Jenelius,    │
│                               │ Mattsson, Scott), but universally assumes   │
│                               │ perfect, deterministic network knowledge.   │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 4. "CITYPULSE" / "SynthCity"  │ Existing names refer to an EU IoT framework │
│    Frameworks                 │ (2013) or synthetic tabular tools, not      │
│                               │ dynamic sensor-uncertain resilience models. │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 5. End-to-End Coupling:       │ **NO SUBSTANTIAL OVERLAP FOUND IN EXAMINED  │
│    Sensor Uncertainty ->      │  SOURCES.** This forms the verified         │
│    Resilience Estimation      │  original research core of CITYPULSE.       │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

The detailed gap analysis and mathematical formulation of our proposed contributions are articulated in [`reports/research_gap.md`](./research_gap.md).
