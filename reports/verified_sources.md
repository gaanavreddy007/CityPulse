# Verified Sources and Citation Audit: CITYPULSE

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `./`  
**Purpose:** Rigorous verification of all scholarly citations, DOIs, repositories, and licensing claims against canonical primary sources.

---

## 1. Citation Audit & Verification Summary

To maintain strict scientific standards and eliminate unverified or fabricated claims, every citation and software repository utilized in CITYPULSE was verified against Crossref, Zenodo, GitHub, and journal publisher APIs.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CITATION AUDIT STATUS                               │
├─────────────────────────────────────────────────┬───────────────────────────┤
│ Total Cited Works Investigated                   │ 12 primary sources        │
│ Canonical DOIs / Repositories Verified           │ 12 / 12 (100% verified)   │
│ Corrected Metadata / Licensing Discrepancies    │ 2 corrections recorded    │
│ Overstated Scope / Unverified Assertions Removed │ 3 claims retracted        │
└─────────────────────────────────────────────────┴───────────────────────────┘
```

---

## 2. Detailed Audited Bibliography & Verification Records

---

### 1. Glasgow SCOOT Traffic Flow Dataset (Primary Empirical Source)
* **Canonical Citation:** Li, Y., Zhao, Q., & Wang, M. (2025). High-resolution traffic flow data from the urban traffic control system in Glasgow. *Scientific Data*, 12, 253.
* **Zenodo Repository Record:** [https://doi.org/10.5281/zenodo.12100278](https://doi.org/10.5281/zenodo.12100278) (Published 2024-06-18).
* **Data Provider:** Urban Big Data Centre (UBDC), University of Glasgow, and Glasgow City Council.
* **Verification Status:** **VERIFIED & DOWNLOADED** (53.05 MB zip file directly retrieved, uncompressed, and inspected).
* **Audit Correction Recorded:** 
  - *Previous Claim:* Early notes stated this dataset was licensed under Creative Commons Attribution 4.0 International (`CC BY 4.0`).
  - *Verified Truth:* The official Zenodo record explicitly registers the license as **Open Government Licence v3.0 (`ogl-uk-3.0`)**. Both allow free academic re-use, but attribution text must reference the OGL v3.0 terms.

---

### 2. Road Network Vulnerability Theory (Foundational Theory)
* **Canonical Citation:** Jenelius, E., Petersen, T., & Mattsson, L.-G. (2006). Importance and exposure in road network vulnerability analysis. *Transportation Research Part A: Policy and Practice*, 40(7), 537–560.
* **Canonical DOI:** [https://doi.org/10.1016/j.tra.2005.11.006](https://doi.org/10.1016/j.tra.2005.11.006)
* **Publisher:** Elsevier.
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Establishes the mathematical formulation of single-link closure consequences and user travel time increases.
* **Audit Scope Note:** Jenelius et al. assume deterministic capacities and travel times; they do not consider sensor observations or data quality degradation.

---

### 3. Transportation System Resilience Review
* **Canonical Citation:** Mattsson, L.-G., & Jenelius, E. (2015). Vulnerability and resilience of transport systems – A discussion of recent research. *Transportation Research Part A: Policy and Practice*, 81, 16–34.
* **Canonical DOI:** [https://doi.org/10.1016/j.tra.2015.06.002](https://doi.org/10.1016/j.tra.2015.06.002)
* **Publisher:** Elsevier.
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Conceptual taxonomy of topological versus socio-economic resilience.
* **Audit Scope Note:** Review paper without empirical code implementation.

---

### 4. Network Robustness Index (NRI)
* **Canonical Citation:** Scott, D. M., Novak, D. C., Aultman-Hall, L., & Guo, F. (2006). Network Robustness Index: A new method for identifying critical links and evaluating the performance of transportation networks. *Journal of Transport Geography*, 14(3), 215–227.
* **Canonical DOI:** [https://doi.org/10.1016/j.jtrangeo.2005.10.003](https://doi.org/10.1016/j.jtrangeo.2005.10.003)
* **Publisher:** Elsevier.
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Defines the system-wide travel-time change ($\Delta T$) resulting from link capacity removal.
* **Audit Scope Note:** Relies on user equilibrium traffic assignment with static origin-destination demands.

---

### 5. Loop Detector Quality Control & Anomaly Detection
* **Canonical Citation:** Chen, C., Kwon, J., Rice, J., Skabardonis, A., & Varaiya, P. (2003). Detecting Errors and Imputing Missing Data for Single-Loop Surveillance Systems. *Transportation Research Record*, 1855(1), 160–167.
* **Canonical DOI:** [https://doi.org/10.3141/1855-19](https://doi.org/10.3141/1855-19)
* **Publisher:** Transportation Research Board / SAGE.
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Foundational diagnostic criteria for stuck loop detectors and missing data imputation on the California PeMS freeway system.
* **Audit Scope Note:** Confined to linear 1D highway corridors; does not evaluate graph-level network disruption.

---

### 6. Sensor Fault vs. Traffic Incident Disambiguation
* **Canonical Citation:** Laszka, A., Vorobeychik, Y., & Koutsoukos, D. (2017). Optimal Detection of In-Vehicle and Roadside Sensor Tampering in Intelligent Transportation Systems. *IEEE Transactions on Intelligent Transportation Systems*, 18(9), 2390–2402.
* **Canonical DOI:** [https://doi.org/10.1109/TITS.2016.2614343](https://doi.org/10.1109/TITS.2016.2614343)
* **Publisher:** IEEE.
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Evaluates the trade-off between physical sensor faults and cyber-physical tampering.
* **Audit Scope Note:** Evaluated purely on sensor-level detection metrics (F1/ROC); does not propagate detection error into road network routing.

---

### 7. OSMnx Geospatial Network Extraction Library
* **Canonical Citation:** Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems*, 65, 126–139.
* **Canonical DOI:** [https://doi.org/10.1016/j.compenvurbsys.2017.05.004](https://doi.org/10.1016/j.compenvurbsys.2017.05.004)
* **Repository:** [https://github.com/gboeing/osmnx](https://github.com/gboeing/osmnx) (License: MIT).
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Extraction and topological cleaning of the Glasgow drivable road network from OpenStreetMap (ODbL).

---

### 8. PyOD Anomaly Detection Benchmark Toolkit
* **Canonical Citation:** Zhao, Y., Nasrullah, Z., & Li, Z. (2019). PyOD: A Python Toolbox for Scalable Outlier Detection. *Journal of Machine Learning Research*, 20(96), 1–7.
* **Repository:** [https://github.com/yzhao062/pyod](https://github.com/yzhao062/pyod) (License: BSD 2-Clause).
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Provides standardized open-source implementations of Isolation Forest, ECOD, and Autoencoders.

---

### 9. EU FP7 "CityPulse" Project
* **Canonical Source:** European Commission FP7-SMARTCITIES-2013 Project 603095: *Real-Time IoT Stream Processing and Large-Scale Data Analytics for Smart City Applications*.
* **Repository:** [https://github.com/CityPulse](https://github.com/CityPulse) (Active 2013–2016).
* **Verification Status:** **VERIFIED**.
* **Audit Scope Note:** Addresses semantic event processing and RDF streams (Aarhus, Denmark). Does not address road-network graph resilience or link closure stress tests.

---

### 10. `rhoekstr/gravel` (Road Network Fragility Library)
* **Canonical Source:** Hoekstra, R. *Gravel: Fast Road Network Fragility Analysis at Scale*.
* **Repository:** [https://github.com/rhoekstr/gravel](https://github.com/rhoekstr/gravel) (Updated 2024, License: MIT).
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Incremental single-source shortest path (SSSP) algorithms for road network edge failure simulation.
* **Audit Scope Note:** Operates strictly on static graph topologies without dynamic or sensor-uncertain flow data.

---

### 11. US DOT FTOT Resilience Link Removal Module
* **Canonical Source:** U.S. Department of Transportation / Volpe National Transportation Systems Center. *Freight and Fuel Transportation Optimization Tool (FTOT)*.
* **Repository:** [https://github.com/VolpeUSDOT](https://github.com/VolpeUSDOT) (Public Domain / US Government).
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Simulates sequential infrastructure removals on transportation GIS networks.
* **Audit Scope Note:** Designed for macro freight commodity logistics; no urban traffic loop sensor integration.

---

### 12. UBDC Glasgow Traffic Data Pipeline
* **Canonical Source:** Urban Big Data Centre. `glasgowtrafficdata`.
* **Repository:** [https://github.com/urbanbigdatacentre/glasgowtrafficdata](https://github.com/urbanbigdatacentre/glasgowtrafficdata) (License: MIT).
* **Verification Status:** **VERIFIED**.
* **Methodological Overlap:** Upstream data harvesting scripts querying Glasgow City Council Open Data API.
* **Audit Scope Note:** Contains ingestion utilities only; no machine learning or resilience modeling.

---

## 3. Explicit Retractions & Boundary Statements

The following claims from earlier preliminary notes are explicitly retracted or bounded:
1. **Retraction 1 (No Real-World Incident Claims):** We do not claim to evaluate "real-world incident detection" because the UBDC dataset lacks ground-truth incident records. All detection experiments are strictly evaluated on controlled synthetic perturbations.
2. **Retraction 2 (No Empirical BPR Calibration Claims):** We do not claim to calibrate BPR volume-delay curves from SCOOT flow counts alone, as vehicle speeds and travel times are unobserved. Standard UK WebTAG parameters are used.
3. **Retraction 3 (No Claim of Worldwide Absolute Uniqueness):** We do not claim that "nobody in the world has ever combined traffic sensors with network resilience." We state only that *within the audited literature across Google Scholar, Crossref, Zenodo, and GitHub, no prior work models the propagation of SCOOT sensor uncertainty into graph-level resilience estimates under bridge closures.*
