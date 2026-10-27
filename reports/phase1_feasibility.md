# Phase 1 Feasibility Report: Data Feasibility and Methodology Validation

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026 (Updated with Gate 1 Verified Counts)  
**Primary Project Directory:** `./`  
**Phase Status:** Phase 1 Completed & Verified  
**Final Decision:** **PROCEED WITH REDESIGN** (Narrowed scope, decoupled claims, mathematically normalized observability metrics, and explicit proxy declarations).

---

## 1. Executive Summary

This Phase 1 Feasibility Report presents an empirical and methodological evaluation of the CITYPULSE project before any full application or pipeline implementation begins.

Unlike the initial exploratory novelty audit, this report:
1. **Directly verified the Glasgow traffic dataset** by querying the Zenodo REST API, downloading the full 53.05 MB archive (`traffic_flow_data.zip`), extracting metadata, and inspecting sample files.
2. **Corrected previous metadata errors:** Discovered that the canonical dataset license is actually **Open Government Licence v3.0 (`ogl-uk-3.0`)**, not CC BY 4.0 as previously stated.
3. **Resolved the Temporal-Count Inconsistency (Gate 1):** Verified that the continuous calendar spans exactly **35,064 calendar hours** (Train: 17,544 hrs including leap year 2020; Val: 8,760 hrs; Test: 8,760 hrs). Discovered that 108 sensors contain 33,644 observed records (1,420 missing hours) and 362 sensors contain 33,643 observed records (1,421 missing hours, differing at `2023-08-13 03:00:00 BST`).
4. **Subjected all scientific assumptions to stress-testing:** Identified critical methodology risks regarding BPR travel-time calibration from volume-only feeds, multi-sensor junction snapping, absence of ground-truth incident logs, and dimensionally unsound ad-hoc observability metrics.
5. **Enforced a strict £0 budget:** Proved that all raw data, geospatial networks, and computational tools are 100% open, permissive, and executable on a standard local personal computer without paid APIs or cloud dependencies.

---

## 2. Dataset Verification & Empirical Grounding

### 2.1 Canonical Dataset Provenance
* **Official Title:** *High-resolution traffic flow data in Glasgow*
* **Creators:** Yue Li, Qunshan Zhao, Mingshu Wang (Urban Big Data Centre, University of Glasgow)
* **Zenodo Record ID:** `12100278`
* **Canonical DOI:** [10.5281/zenodo.12100278](https://doi.org/10.5281/zenodo.12100278)
* **Associated Data Paper:** Li, Y., Zhao, Q., & Wang, M. (2025). *High-resolution traffic flow data from the urban traffic control system in Glasgow*. *Scientific Data*, 12, 253.
* **Publication Date on Zenodo:** 2024-06-18
* **Verified License:** **Open Government Licence v3.0 (`ogl-uk-3.0`)** (Permits free commercial and non-commercial re-use with attribution).

### 2.2 Download & Archive Anatomy
The archive was downloaded directly from `https://zenodo.org/api/records/12100278/files/traffic_flow_data.zip/content` into `data/raw/traffic_flow_data.zip`:
* **Archive Size:** 53.05 MB (55,627,707 bytes).
* **Archive Contents:** Exactly 471 files:
  - 1 spatial metadata file: `locations.csv` (16,076 bytes).
  - 470 detector time-series files: `flows/[sensor_id].csv`.
* **Hardware Footprint:** Uncompressed size is ~380 MB. The entire dataset easily fits in memory on any modern PC (16 GB RAM) and processes in pandas within seconds. No high-performance cluster or cloud storage is needed.

### 2.3 Empirical Audit of Spatial Metadata (`locations.csv`)
* **Total Sensor Detectors:** 470.
* **Columns:** `id`, `latitude`, `longitude`.
* **Missing Coordinates:** 0 nulls (100% valid WGS84 coordinates).
* **Spatial Bounding Box:**
  - Latitude: $[55.805004, 55.897428]$
  - Longitude: $[-4.364622, -4.128821]$
* **Junction Clustering:** 
  The 470 sensors are derived from 195 unique SCOOT junction controller prefixes (e.g., `GA0151_A`, `GA0151_C`, `GA0151_D`). 
  - 33 junctions have 1 detector.
  - 79 junctions have 2 detectors.
  - 55 junctions have 3 detectors.
  - 26 junctions have 4 detectors.
  - 2 junctions have 5 detectors.
  *Implication:* Detectors measure distinct approach legs at the same intersection. A candidate-based spatial matching workflow considering approach bearing and road attributes is mandatory.

### 2.4 Empirical Audit of Sensor Flow Data (`flows/*.csv`)
Across all 470 detectors in the dataset:
* **Temporal Horizon:** October 1, 2019, 00:00:00 to September 30, 2023, 23:00:00 (1,461 calendar days = 35,064 theoretical hours).
* **Observed Records per Sensor:**
  - 108 sensors contain exactly 33,644 rows (1,420 missing hours).
  - 362 sensors contain exactly 33,643 rows (1,421 missing hours).
* **Missing Data Mechanism:** Missing hours are **omitted rows** rather than explicit `NaN` entries. 
  - Train Split (17,544 cal hrs): 16,639 observed rows (905 missing hrs).
  - Validation Split (8,760 cal hrs): 8,663 observed rows (97 missing hrs).
  - Test Split (8,760 cal hrs): 8,342 observed rows (108 sensors) or 8,341 observed rows (362 sensors).
  *Implication:* An explicit datetime reindexing step (`pd.date_range`) is mandatory during data ingestion to represent true missingness as `NaN` without conflating it with legitimate zero-traffic hours.
* **Flow Statistics:**
  - Values are non-negative integers representing hourly vehicle volume counts.
  - Zero flows occur naturally during night hours ($01:00 - 05:00$).
  - Mean hourly flows range from 17.7 vehicles/hr to 119.1 vehicles/hr.
  - No negative values or corrupt strings exist.

---

## 3. Methodological Risk Assessment & Decoupling

The scientific assumptions of CITYPULSE were audited in detail (see [`reports/methodology_risks.md`](./methodology_risks.md)). The key findings dictate mandatory methodology adjustments:

1. **Volume Counts Do Not Equal Travel Time:**
   SCOOT detectors measure *flow* ($q$, veh/hr), not speed or travel time. A BPR function requires free-flow travel time $t_0$, link capacity $C$, and shape parameters $\alpha, \beta$. Because speed is unobserved, BPR parameters cannot be calibrated empirically from volume alone; they must use standard UK WebTAG / highway engineering defaults.
2. **Absence of Real-World Incident Labels:**
   The dataset does not provide external labels for traffic accidents or bridge closures. Synthetic fault injection evaluates detector performance on *mathematically specified degradation signatures*, but **cannot claim validated real-world incident detection**.
3. **Lack of Dynamic OD Demand:**
   Scottish census data zones provide residential population counts, not dynamic hourly vehicle trip matrices. The project must explicitly label its origin-destination weights as an **accessibility connectivity proxy**, not observed vehicular journeys.
4. **Bridge Representations in Graph Networks:**
   Major river crossings (e.g., Kingston Bridge, Clyde Arc) are not single graph edges; they consist of multi-edge directional carriageways and slip-road ramps. Disruption scenarios must be implemented via subgraph edge-set removals rather than single-edge deletion.
5. **Dimensional Inconsistency in Observability Metrics:**
   The previously suggested product $VOD = NRI \cdot \text{dist}$ yields nonsensical units ($hours \times meters$). We replace it with a **dimensionless Observability Risk Index** based on spatial decay functions.

---

## 4. Minimum Viable Experiment (MVE)

The minimum viable experiment is formulated to guarantee strict reproducibility:

```
[4-Year SCOOT Time Series (35,064 Calendar Hours)]
                   │
                   ▼ Chronological Split (No Leakage)
┌──────────────────────────────────────┬────────────────────────┬────────────────────────┐
│ Train: Oct 2019 – Sep 2021 (50.0%)  │ Val: Oct 2021 – Sep 22 │ Test: Oct 22 – Sep 23  │
│ 17,544 cal hrs (16,639 obs rows)     │ 8,760 cal hrs (8,663)  │ 8,760 cal hrs (8,342)  │
│ Baseline Pattern Estimation          │ Threshold Calibration  │ Synthetic Evaluation   │
└──────────────────────────────────────┴────────────────────────┴────────────────────────┘
                   │
                   ▼ Controlled Degradations (MCAR, Burst, Drift, Freeze)
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Anomaly Detection Evaluation: Seasonal MAD, Rolling Z-Score, Isolation Forest, ECOD   │
│ Metrics: PR-AUC, F1-Score, False Positive Rate (evaluated under 5 random seeds)        │
└──────────────────────────────────┬─────────────────────────────────────────────────────┘
                                   │
                                   ▼ Uncertainty Bounds
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Monte Carlo Edge-Cost Propagation on Glasgow OSMnx Graph (M = 100 ensembles)           │
│ Simulated Closures: M8 Kingston Bridge Corridor, George V / Glasgow Bridge Pair        │
│ Resilience Metrics: System Delay (Delta T), NRI, Observability Risk Index (Omega)      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Budget, Infrastructure & Licensing Verification

| Requirement | Audit Finding | Compliance |
| :--- | :--- | :--- |
| **Financial Budget** | Zero monetary expenditure required (£0.00). | **Compliant** |
| **Data Licensing** | Zenodo Glasgow SCOOT data is licensed under Open Government Licence v3.0 (`ogl-uk-3.0`). OpenStreetMap data is licensed under ODbL. | **Compliant** |
| **API Costs** | OpenStreetMap data fetched via free Overpass API / OSMnx; no commercial Google/Mapbox APIs. | **Compliant** |
| **Compute Constraints** | Data size: 53 MB compressed / 380 MB raw. Memory requirement: < 2 GB RAM. Graph size: ~15,000 nodes, ~35,000 edges. Shortest paths compute in sub-second vectorized batches via NetworkX/SciPy. | **Compliant** |

---

## 6. Deliverable Inventory & Next Milestones

All Phase 1 & Gate 1 deliverables are prepared in `reports/`:
* [`reports/phase1_feasibility.md`](./phase1_feasibility.md) — Overall feasibility and empirical verification.
* [`reports/temporal_split_audit.md`](./temporal_split_audit.md) — Gate 1 temporal count discrepancy resolution.
* [`reports/methodology_risks.md`](./methodology_risks.md) — Investigation of 7 scientific assumptions and required corrections.
* [`reports/data_dictionary.md`](./data_dictionary.md) — Precise dataset schemas, spatial coordinates, missingness profiles, and data types.
* [`reports/experiment_protocol.md`](./experiment_protocol.md) — Chronological train/val/test splits, perturbation specifications, and baseline models.
* [`reports/verified_sources.md`](./verified_sources.md) — Audited bibliography verifying canonical DOIs and corrected licenses.
