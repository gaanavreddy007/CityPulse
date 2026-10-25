# CityPulse: Traffic Sensor Data Quality, Spatial Consistency & Road Network Resilience

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/tests-56%2F56%20passing-brightgreen.svg)]()
[![License: ODbL 1.0](https://img.shields.io/badge/network%20data-ODbL%201.0-orange.svg)](http://opendatacommons.org/licenses/odbl/1-0/)
[![License: OGL v3.0](https://img.shields.io/badge/flow%20data-OGL%20v3.0-blue.svg)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
[![Reproducibility: 100% Offline](https://img.shields.io/badge/reproducibility-100%25%20offline-success.svg)]()

> **Academic MSc Data Science Research Portfolio Project**  
> An end-to-end empirical investigation into urban traffic sensor corruption, spatial cross-consistency anomaly detection, and graph-theoretic road network resilience in central Glasgow, Scotland.

---

## 1. Research Overview & Key Questions

Urban Intelligent Transportation Systems (ITS) depend on automated sensor feeds to monitor congestion, optimize signal timing, and manage incident responses. However, physical detectors suffer from calibration drift, power dropouts, and environmental interference, while simplified road network representations often mask critical operational vulnerabilities.

This project addresses four central research questions:
1. **RQ1 (Sensor Fault Sensitivity):** How resilient are univariate time-series anomaly detection algorithms (rolling statistical filters, Seasonal ESD, Isolation Forests, Local Outlier Factor) to subtle, insidious sensor degradation (multiplicative scale drift, additive bias) compared to catastrophic dropouts?
2. **RQ2 (Spatial Cross-Consistency):** Can bivariate spatial cross-consistency tracking between neighboring sensors reliably isolate localized sensor faults from city-wide macro demand fluctuations (e.g., severe storms or bank holidays)?
3. **RQ3 (Network Resilience & Directional Couplets):** How resilient is the central Glasgow River Clyde crossing network to critical bridge severances, and how do asymmetric directional couplets (King George V Bridge vs. Glasgow Bridge) govern rerouting?
4. **RQ4 (Spatial Bounding & Sensitivity):** How do geographic study boundaries and network representation assumptions introduce topological edge artifacts in modelled route choices?

---

## 2. Principal Empirical Findings

All metrics reported below are traceable to saved output artifacts in the repository:

| Disruption Scenario | Evaluated Direction | Baseline Reachable OD Pairs | Still-Reachable OD Pairs (%) | Newly Unreachable OD Pairs (%) | Modelled Pairs Rerouted | Mean Free-Flow $\Delta t$ on Reachable | Mean $\Delta \text{dist}$ on Reachable | Primary Diversion Corridor |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **King George V Bridge Alone** | South $\to$ North | 110,509 | 110,509 (100.0%) | 0 (0.00%) | 69,693 (63.07%) | **+24.74 s (+11.0%)** | **+253.74 m** | Kingston Bridge / Victoria Bridge |
| *(Northbound Couplet Severed)* | North $\to$ South | 107,892 | 107,892 (100.0%) | 0 (0.00%) | 0 (0.00%) | **+0.00 s (0.0%)** | **+0.00 m** | *Unaffected (One-Way Couplet)* |
| **Glasgow Bridge Alone** | South $\to$ North | 110,509 | 110,509 (100.0%) | 0 (0.00%) | 0 (0.00%) | **+0.00 s (0.0%)** | **+0.00 m** | *Unaffected (One-Way Couplet)* |
| *(Southbound Couplet Severed)* | North $\to$ South | 107,892 | 107,892 (100.0%) | 0 (0.00%) | 30,488 (28.26%) | **+9.82 s (+4.4%)** | **+136.08 m** | Victoria Bridge / Albert Bridge |
| **George V + Glasgow Combined** | South $\to$ North | 110,509 | 110,509 (100.0%) | 0 (0.00%) | 69,693 (63.07%) | **+24.74 s (+11.0%)** | **+253.74 m** | Victoria Bridge / Kingston Bridge |
| *(Central Arterial Axis Severed)*| North $\to$ South | 107,892 | 107,892 (100.0%) | 0 (0.00%) | 30,488 (28.26%) | **+9.82 s (+4.4%)** | **+136.08 m** | Victoria Bridge / Albert Bridge |
| **M8 Kingston Bridge Alone** | South $\to$ North | 110,509 | 106,384 (96.27%) | 4,125 (3.73%)* | 7,319 (6.88%) | **+1.79 s (+0.8%)** | **+17.86 m** | Surface couplets (George V) |
| *(Motorway Flyover Severed)* | North $\to$ South | 107,892 | 102,930 (95.40%) | 4,962 (4.60%)* | 25,796 (25.06%) | **+8.94 s (+4.0%)** | **+34.77 m** | Surface couplets (Glasgow Bridge)|
| **Clyde Arc Alone** | South $\to$ North | 110,509 | 110,509 (100.0%) | 0 (0.00%) | 18,446 (16.69%) | **+13.55 s (+6.0%)** | **+262.41 m** | Kingston Bridge / George V |
| *(Western Crossing Severed)* | North $\to$ South | 107,892 | 107,892 (100.0%) | 0 (0.00%) | 16,810 (15.58%) | **+10.01 s (+4.4%)** | **+223.88 m** | Kingston Bridge / Victoria Bridge |

*\*Newly unreachable node pairs under Kingston Bridge closure are confirmed artifacts of the geographic bounding box truncating northern motorway mainline stubs and regional bypasses.*

### Key Insights
1. **Asymmetric Directional Couplet:** George V Bridge (northbound) and Glasgow Bridge (southbound) form a synchronized one-way pair. Severing George V Bridge impacts only South $\to$ North travel (+24.74 s mean on 69,693 pairs; 0 s North $\to$ South). Severing Glasgow Bridge impacts only North $\to$ South travel (+9.82 s mean on 30,488 pairs; 0 s South $\to$ North).
2. **Resilience Redundancy:** Even under the compound closure of both George V and Glasgow Bridges, **100.0% of cross-river node pairs remain reachable** via Victoria Bridge, Albert Bridge, and Kingston Bridge.
3. **Spatial Detector Realism:** Bivariate spatial cross-consistency tracking effectively filters out city-wide false alarms during severe weather or holiday flow drops, but achieves an absolute recall of **31.6% at 5% FDR** (PR-AUC 0.42–0.58), demonstrating that spatial correlation is a complementary filter rather than a standalone cure for localized sensor drift.

---

## 3. Geographic Scope & Central Corridor Domain

The road graph representation is strictly bounded to the central Glasgow Clyde crossing corridor:
- **Spatial Envelope:** Bounded by latitudes $[55.850^\circ\text{N}, 55.865^\circ\text{N}]$ and longitudes $[-4.285^\circ\text{W}, -4.240^\circ\text{W}]$.
- **Crossings Included:**
  * M8 Kingston Bridge Viaduct (10 lanes, grade-separated motorway)
  * King George V Bridge (4 lanes, northbound surface arterial)
  * Glasgow Bridge / Jamaica Bridge (4 lanes, southbound surface arterial)
  * Clyde Arc / "Squinty Bridge" (4 lanes, bidirectional surface arterial)
  * Victoria Bridge & Albert Bridge (eastern core crossings)
- **Topological Boundary Limitation:** The northern boundary terminates just south of Charing Cross ($55.865^\circ\text{N}$). Real-world motorway on-ramps (Junctions 17/18) and regional bypasses (M74 Northern Extension, M73, Clyde Tunnel A739) lie outside this boundary. As a result, 4,125 pairs destined for northern motorway stubs become unreachable inside the model when Kingston Bridge is closed. This is formally classified as a **geographic boundary truncation artifact**, not physical travel impossibility.

---

## 4. Repository Architecture

```text
CityPulse/
├── README.md                                  # Research overview, runbook, and findings
├── .gitignore                                 # Production Git ignore rules
├── citypulse/                                 # Core Python package
│   ├── __init__.py
│   ├── anomaly.py                             # Statistical & ML anomaly detectors
│   ├── corruption.py                          # Synthetic corruption injection engine
│   ├── data_layer.py                          # Temporal resampling & data ingestion
│   ├── experiment.py                          # Multi-seed scenario orchestrator
│   ├── resilience.py                          # Dijkstra pathfinding & graph resilience
│   ├── sensor_matcher.py                      # Spatial buffer sensor-to-link matching
│   ├── spatial.py                             # Bivariate spatial cross-consistency
│   └── uncertainty.py                         # Latin Hypercube Monte Carlo sampling
├── data/
│   ├── network/                               # Road graph data
│   │   ├── raw_osm/                           # Canonical OpenStreetMap XML extracts
│   │   │   ├── central_core.osm               # Central Clyde bridges & city core (17.1 MB)
│   │   │   └── clyde_arc_west.osm             # Clyde Arc western crossing (8.7 MB)
│   │   ├── reconstructed_network_nodes.csv    # 1,047 road junctions with WGS84 coords
│   │   ├── reconstructed_network_edges.csv    # 1,932 directed links (length, speed, time)
│   │   ├── source_manifest.json               # ODbL 1.0 license & OSM source metadata
│   │   └── glasgow_network_edges.csv          # [SUPERSEDED] Historical 18-edge synthetic graph
│   ├── raw/
│   │   └── traffic_flow_data.zip              # Raw SCOOT flow sensor archive (55.6 MB)
│   └── sample/                                # Preprocessed sensor time series
│       ├── locations.csv                      # Sensor spatial coordinates
│       └── flows/                             # Hourly resampled flow files (33,644 rows/sensor)
├── reports/                                   # Audit reports & empirical result tables
│   ├── final_research_summary.md              # Definitive research synthesis
│   ├── reproducibility_and_limitations.md     # 4-tier verification & scientific caveats
│   ├── final_experiment_inventory.csv         # Full audit log of all 14 project experiments
│   ├── phase4_3_final_results.md              # Definitive recalibrated resilience metrics
│   ├── phase4_3_bridge_closure_validation.md  # Directional couplet analysis & route examples
│   ├── phase4_3_boundary_sensitivity.md       # Forensic trace of boundary truncation
│   ├── phase4_3_routing_integrity_audit.md    # Grade separation, oneway, & parallel edge audit
│   └── phase4_3_test_log.md                   # Automated test suite execution log
├── scripts/                                   # Executable reproduction and audit scripts
│   ├── build_reconstructed_graph.py           # Ingests OSM XML into validated graph CSVs
│   ├── validate_reconstructed_graph.py        # Verifies topology, edge counts, components
│   ├── audit_separate_bridges.py              # Evaluates directional bridge couplets
│   ├── generate_route_examples.py             # Extracts before/after shortest-path routes
│   ├── calculate_distance_changes.py          # Computes exact detour distance & time deltas
│   ├── analyze_boundary_disconnect.py         # Forensic trace of unreachable motorway stubs
│   ├── audit_spatial_detector.py              # Evaluates spatial detector PR-AUC & recall
│   ├── audit_monte_carlo.py                   # Validates Latin Hypercube sample convergence
│   └── run_anomaly_benchmark.py               # Runs baseline univariate anomaly benchmark
└── tests/                                     # Automated unit test suite (56 passing tests)
    ├── test_data_layer.py                     # Hourly aggregation, UTC, missingness
    ├── test_corruption_engine.py              # Deterministic corruption generation
    ├── test_sensor_matcher.py                 # Spatial buffer & bearing assignment
    ├── test_bounded_resilience.py             # Pathfinding & disconnection penalties
    ├── test_anomaly_detectors.py              # z-score, EWMA, ESD, Isolation Forest, LOF
    ├── test_experiment_runner.py              # Multi-seed scenario calibration
    ├── test_spatial_cross_consistency.py      # Spatial neighbor & residual tracking
    ├── test_uncertainty_propagation.py        # Latin Hypercube sampling & variance
    └── test_reconstructed_graph.py            # OSM graph integrity & bridge edges
```

---

## 5. Offline Reproduction Runbook

The complete pipeline executes locally without external API dependencies or paid cloud services (£0 budget):

### Step 1: Run Full Automated Unit Test Suite
```powershell
python -m unittest discover tests
# Expected output: Ran 56 tests in ~8.6s — OK
```

### Step 2: Validate Road Network Topology Integrity
```powershell
python scripts/validate_reconstructed_graph.py
# Verifies 1,047 nodes, 1,932 edges, zero collapsed parallel edges, grade separation
```

### Step 3: Reproduce Directional Couplet Resilience Benchmark
```powershell
python scripts/audit_separate_bridges.py
# Evaluates 218,401 cross-river pairs across George V, Glasgow Bridge, Kingston, and Clyde Arc
```

### Step 4: Extract Concrete Route Diversion Examples
```powershell
python scripts/generate_route_examples.py
# Computes exact coordinates, lengths, and free-flow travel times before and after closures
```

### Step 5: Trace Boundary Truncation Mechanisms
```powershell
python scripts/analyze_boundary_disconnect.py
# Traces unreachable motorway stubs and verifies the 55.865°N boundary cutoff
```

---

## 6. Scientific Rigor & Methodological Limitations

In compliance with transport modeling and scientific software engineering best practices:

- **Free-Flow Speeds vs. Congestion Delays:** Shortest-path routing assumes unconstrained legal posted speed limits (30 mph urban, 50 mph motorway). The model does **not** simulate link volume-delay curves (BPR), intersection signal delays, or dynamic queue spillbacks. Free-flow time changes ($\Delta t_{\text{free}}$) represent routing resistance deltas, not empirical congestion delays.
- **Micro-Level Turn Restrictions:** 51 OSM turn restrictions are cataloged in the core but omitted in the node-based Dijkstra solver, causing an estimated 5–15 second underestimation of urban traversal resistance at complex junctions.
- **Unweighted OD Node Pairs:** Pairs $(u, v)$ represent theoretical topological vertices in the network graph, not counted commuters, observed trips, or surveyed demand matrices.
- **Synthetic Corruptions vs. Real Hardware Failures:** Anomalies are mathematically generated benchmarks (step offsets, multiplicative scale drift, zero dropouts) used to test algorithmic limits, not verified physical loop detector failures.
- **Statistical Flow Anomalies vs. Incidents:** Unsupervised flow outliers detected in historical data represent volume anomalies, not ground-truth verified traffic accidents.
- **Observability Risk Index:** The observability index is an exploratory topological heuristic combining betweenness centrality and sensor proximity. It is not an established civil resilience standard.

---

## 7. Data Provenance & Legal Licensing

- **Traffic Flow Data:** Derived from Glasgow City Council SCOOT traffic counts, licensed under the [Open Government Licence (OGL) v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
- **Road Network Data:** Derived from OpenStreetMap.
  - Attribution: *© OpenStreetMap contributors*
  - License: [Open Data Commons Open Database License (ODbL) 1.0](http://opendatacommons.org/licenses/odbl/1-0/)
  - Derivative Database Notice: Any distribution of `reconstructed_network_nodes.csv` or `reconstructed_network_edges.csv` must include this ODbL notice and attribution.
