# Novelty and Prior-Art Audit: CITYPULSE

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience Under Disruptions  
**Audit Date:** October 2026  
**Auditor:** Automated Pair-Programming Research Agent (Antigravity)  
**Budget Constraint:** £0.00 (Strictly utilizing open-access academic literature, open government data, and permissive open-source software)  
**Investigated Research Question:**  
> *"How does traffic-sensor data quality and uncertainty affect urban mobility anomaly detection and estimates of road-network resilience under hypothetical disruptions?"*

---

## 1. Executive Summary

This audit evaluates the novelty, prior art, academic originality, and practical feasibility of the proposed CITYPULSE project before embarking on code implementation.

A comprehensive multi-source investigation was performed across:
1. **Scholarly Literature Databases:** Google Scholar, Semantic Scholar, Crossref, arXiv, Nature Portfolio (*Scientific Data*), Elsevier (*Transportation Research Part A/C*), IEEE Xplore, and PubMed/PMC.
2. **Open-Source Code Repositories:** GitHub, Zenodo, and public software archives (including alternate names, forks, and related projects).
3. **Domain & Regional Platforms:** The Urban Big Data Centre (UBDC, University of Glasgow), Glasgow Open Data Hub, Transport Scotland, and Ordnance Survey OpenData.
4. **Existing Named Frameworks:** The EU FP7 "CityPulse" project (2013–2016), the "SynthCity" mobility and synthetic data platforms, and network resilience packages (`gravel`, `FTOT-Resilience-Link_Removal`, `open-gira`, `OSMnx`).

### Key Verdict
* **No Direct Prior Work:** No published paper or open-source repository was identified that solves the *exact end-to-end question* of how traffic sensor uncertainty, calibration drift, and anomaly misclassification propagate downstream into road network resilience estimates and link criticality rankings under hypothetical disruptions.
* **Significant Partial Overlaps in Disjoint Silos:** The literature is heavily segmented:
  - *Silo A (Sensor Quality & Anomaly Detection):* Rich literature on detecting loop sensor faults and isolating physical congestion from hardware failure (e.g., PeMS studies, PyOD, spatio-temporal autoencoders).
  - *Silo B (Network Resilience & Criticality):* Mature literature on graph-theoretic road network vulnerability under link removals (e.g., Jenelius & Mattsson, Scott et al. Network Robustness Index, OSMnx disruption simulations).
  - *Silo C (Glasgow Data):* Open-access publication of the Glasgow SCOOT 4-year traffic flow dataset by UBDC researchers (Li, Zhao, & Wang, 2025, *Scientific Data*).
* **Novelty Assessment:** The genuine research contribution lies in **bridging the interface between sensor data uncertainty and network resilience estimation**—specifically testing how data quality degradations (missingness, sensor bias, false anomaly alerts) distort the identification of critical infrastructure links and network-level resilience curves during major arterial/bridge closures.
* **Audit Recommendation:** **PROCEED** with a clearly scoped methodology centered on three defined, realistically implementable contributions, adhering strictly to the verified open datasets and £0 budget.

---

## 2. Audit Scope and Search Methodology

### 2.1 Search Strategy
Searches were conducted systematically using targeted keyword combinations, exact-match phrase operators, and domain filters:
* **Academic Databases:** Querying combinations of `("traffic sensor" OR "SCOOT") AND ("data quality" OR "uncertainty propagation") AND ("anomaly detection") AND ("road network resilience" OR "vulnerability analysis" OR "link closure")`.
* **Glasgow Specific Queries:** Querying `("Glasgow" OR "Urban Big Data Centre" OR "UBDC") AND ("traffic flow" OR "SCOOT" OR "sensor" OR "resilience" OR "M8")`.
* **Repository Audits:** Auditing GitHub organizations and repos (`CityPulse`, `urbanbigdatacentre`, `rhoekstr/gravel`, `VolpeUSDOT`, `gboeing/osmnx`).
* **Framework Cross-Checks:** Investigating potential nomenclature collisions with EU FP7 `CityPulse` and `SynthCity`.

### 2.2 Classification Standard
Prior works and tools are categorized into four standardized tiers:
1. **Direct Overlap:** Identical research question, workflow, datasets, and analytical outputs.
2. **Partial Overlap:** Shares substantial methodological components, analytical pipelines, or data sources, but addresses a different research question or stops short of the full end-to-end integration.
3. **Related Background:** Foundational theory, standalone tools, or general algorithms (e.g., classic graph algorithms, generic anomaly detection libraries) that serve as building blocks.
4. **No Substantial Overlap Found:** Specific investigated niches where no prior implementation was discovered in public sources.

---

## 3. Systematic Prior-Art Findings & Overlap Matrix

The table below summarizes the key works evaluated. Detailed profiles for each work are documented in [`reports/related_work.md`](./related_work.md).

| Identifier / Project | Lead Authors / Maintainer | Year / Status | Domain / Focus | Overlap Classification | Core Distinction from CITYPULSE |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **High-Res Glasgow Traffic Flow Dataset** | Li, Zhao, & Wang (UBDC, Univ. of Glasgow) | 2025 (*Sci. Data*) | 470 SCOOT sensors in Glasgow (2019–2023) | **Partial Overlap** (Data Source) | Focuses on data curation, cleaning, and COVID travel shifts; does not perform network disruption simulation or resilience modeling. |
| **`glasgowtrafficdata`** | Urban Big Data Centre (`urbanbigdatacentre`) | 2020–2024 | GCC Open Data API ingestion scripts | **Partial Overlap** (Pipeline) | Data extraction and logging utility; no analytical models for anomaly detection or topological network resilience. |
| **EU FP7 "CityPulse" Project** | Univ. of Surrey, Siemens, Ericsson et al. | 2013–2016 | Smart City IoT stream reasoning (Aarhus) | **Partial Overlap** (Nomenclature / Stream Anomaly) | Focuses on RDF streams, CEP, and semantic sensor web; does not model road network graph resilience or link closure stress tests. |
| **`rhoekstr/gravel`** | R. Hoekstra | 2023–2024 | High-performance road network fragility (OSM) | **Partial Overlap** (Resilience Engine) | Evaluates edge-failure accessibility using static graph topologies; assumes deterministic travel times without real-time sensor streams or sensor uncertainty. |
| **`FTOT-Resilience-Link_Removal`** | US Department of Transportation (Volpe Center) | 2021–2023 | Freight network disruption & link removal | **Partial Overlap** (Simulation Logic) | Static volume-capacity freight assignment; does not ingest empirical sensor data or analyze sensor quality degradation. |
| **Importance and Exposure in Road Vulnerability** | Jenelius, Petersen, & Mattsson | 2006, 2015 | Foundational transport network vulnerability | **Related Background** (Theoretical Foundation) | Seminal theory of link criticality and travel-time delay, but assumes perfect knowledge of network topology and demand. |
| **OSMnx** | G. Boeing | 2017–2024 | Street network extraction and graph metrics | **Related Background** (Core Tool) | Geospatial network library; provides graph infrastructure, not domain-specific sensor uncertainty propagation. |
| **PyOD / ADTK** | Zhao et al. / Arundo Analytics | 2019–2024 | Python Outlier Detection toolkits | **Related Background** (Algorithm Baselines) | General-purpose anomaly detection algorithms; lacks urban transport graph modeling and resilience evaluation. |
| **SynthCity (Mobility / SUMO)** | Various ITS Researchers (e.g., Genoa case study) | 2022–2024 | Synthetic multimodal mobility simulation | **Partial Overlap** (Simulation Baseline) | Micro-simulation of synthetic traffic; does not couple sensor fault uncertainty with macroscopic road network vulnerability. |
| **`synthcity` (Healthcare/ML)** | van der Schaar Lab | 2023–2024 | Synthetic tabular/time-series data library | **Related Background** (Generic ML) | Unrelated general tabular synthesis tool sharing the name "SynthCity". |
| **Sensor Uncertainty in Dynamic Network Resilience** | *Current CITYPULSE Proposal* | 2026 | Sensor fault propagation to road resilience | **No Direct Overlap Found** | End-to-end integration: empirical SCOOT noise/uncertainty $\rightarrow$ anomaly classification $\rightarrow$ network resilience degradation. |

---

## 4. Analysis of Novelty: Genuinely New vs. Derivative

### 4.1 What Would NOT Be Genuinely Novel (Pitfalls to Avoid)
To ensure the project makes a legitimate scientific contribution and does not manufacture novelty through superficial changes, we explicitly discard the following derivative approaches:
* ❌ *Applying standard Isolation Forests to Glasgow SCOOT data without network context:* Simply downloading the UBDC dataset and applying off-the-shelf outlier detectors has already been explored in generic time-series benchmarks.
* ❌ *Running standard OSMnx shortest paths with static link removals on Glasgow:* Simulating bridge closures on OpenStreetMap using Dijkstra's algorithm is standard classroom practice and does not advance the state of the art.
* ❌ *Renaming existing concepts:* Calling missing data imputation "resilience-aware imputation" or renaming the Network Robustness Index (NRI) without mathematical modification is unacceptable.

### 4.2 What IS Genuinely Novel and Justified
The genuine research contribution of CITYPULSE resides at the **intersection of physical infrastructure resilience and cyber-physical sensor uncertainty**:
1. **Uncertainty Propagation from Edge Sensors to Graph Metrics:** In almost all transportation vulnerability literature, link travel times are treated as deterministic parameters derived from speed limits or static BPR functions. CITYPULSE models travel time as an empirical distribution derived from SCOOT loop counts with quantified uncertainty (missingness, measurement variance, spatial imputation error).
2. **Differentiating Hardware Sensor Faults from Physical Network Disruptions:** A drop in vehicle counts can signify either a failed loop detector (zero flow, free speed) or gridlock from a downstream incident (zero flow, zero speed). CITYPULSE systematically evaluates the systemic penalty when an automated traffic management system misclassifies a sensor failure as a physical road anomaly.
3. **Link Criticality Rank Distortion under Imperfect Observability:** Identifying which Glasgow bridges (e.g., Kingston Bridge, George V Bridge, Clyde Arc) or arterial bottlenecks are "most critical" depends on the fidelity of the underlying flow data. CITYPULSE quantifies how degradation in sensor coverage (sensor outage rates from 5% to 50%) causes transport planners to misidentify critical links.

---

## 5. Data Access, Licensing, and Feasibility Verification

A fundamental constraint of this investigation is maintaining a **£0 budget** and confirming that all required data and software licenses permit research and reproducibility.

| Asset | Source / Host | License | Access Method | Cost | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Glasgow High-Res SCOOT Traffic Flow (2019–2023)** | Zenodo (DOI: [10.5281/zenodo.12100278](https://doi.org/10.5281/zenodo.12100278)) / UBDC | Creative Commons Attribution 4.0 International (CC BY 4.0) | Direct HTTP/REST download via Zenodo API | £0 | **Verified & Accessible** |
| **Glasgow City Council Live/Historical Traffic Feeds** | Glasgow Open Data Hub / GCC | Open Government Licence v3.0 (OGL v3.0) | Open Data CKAN API endpoints | £0 | **Verified & Accessible** |
| **Glasgow Road Network Topology** | OpenStreetMap (OSM) via `osmnx` | Open Database License (ODbL) | Overpass API download via `osmnx.graph_from_place` | £0 | **Verified & Accessible** |
| **Scottish Index of Multiple Deprivation (SIMD) / Zones** | Scottish Government SpatialData.gov.scot | Open Government Licence v3.0 (OGL v3.0) | Direct GeoPackage / Shapefile download | £0 | **Verified & Accessible** |
| **Python Computational Toolchain** | PyPI / Conda-Forge (`osmnx`, `networkx`, `geopandas`, `pyod`, `scipy`) | Permissive Open Source (MIT, BSD, Apache 2.0) | `pip install` / `uv pip install` | £0 | **Verified & Accessible** |

All datasets are verified to be fully open-access, requiring no paid subscriptions, proprietary credentials, or NDA agreements.

---

## 6. Audit Recommendation and Next Steps

### Recommendation: PROCEED WITH REFINED SPECIFICATION

The audit confirms that the revised research question is scientifically sound, occupies a verified research gap, has no direct competing implementation, and is 100% feasible under a £0 budget using the verified UBDC Glasgow SCOOT dataset and OpenStreetMap.

### Immediate Action Plan
1. Establish the project workspace at `C:\Users\Admin\.gemini\antigravity-ide\scratch\citypulse`.
2. Finalize the companion audit documents:
   - Complete inventory and analysis of prior art in [`reports/related_work.md`](./related_work.md).
   - Detailed mathematical formulation of the three contributions in [`reports/research_gap.md`](./research_gap.md).
3. Present the audit findings to the user for formal approval before initiating data pipeline construction and experimental code implementation.
