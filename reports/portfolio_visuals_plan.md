# CITYPULSE: PORTFOLIO VISUALS SPECIFICATION PLAN

**Author:** Gaanav Reddy (`gaanavreddy007`)  
**Project:** CityPulse (`./`)  
**Purpose:** Technical Presentation & Academic Portfolio Figure Specifications  
**Date:** 2026-10-25  

---

## 1. Overview & Visual Design Principles

To ensure complete scientific integrity in academic presentations, dissertation appendices, and graduate employment interviews, all proposed visual figures must:
1. **Trace directly to saved, reproducible data artifacts** (no fabricated plots, mockups, or synthetic extrapolations).
2. **Explicitly visualize directional asymmetries and physical constraints** (e.g., one-way couplets, grade-separated flyovers).
3. **Include explicit units, spatial coordinates, and boundary markers**.
4. **State modeling limitations directly within captions** (e.g., noting static free-flow speeds vs. dynamic congestion).

Below is the definitive visual design specification for the six primary portfolio figures.

---

## 2. Definitive Figure Specifications

### Figure 1: Central Glasgow Road Network Topology & Grade Separation
- **Figure Type:** Geospatial Directed Network Map with Inset Callout.
- **Coordinate Reference System:** WGS84 (EPSG:4326).
- **Spatial Envelope:** Longitude $[-4.285^\circ\text{W}, -4.240^\circ\text{W}]$, Latitude $[55.850^\circ\text{N}, 55.865^\circ\text{N}]$.
- **Data Layers & Symbology:**
  * **Nodes (1,047 points):** Small circular markers ($r=1.5\text{ pt}$), light slate grey (`#64748B`).
  * **Motorway / Flyover Links (88 edges):** Deep crimson (`#DC2626`), stroke width $2.5\text{ pt}$.
  * **Primary & Secondary Arterials (612 edges):** Royal cobalt (`#2563EB`), stroke width $1.8\text{ pt}$.
  * **Tertiary & Residential Links (1,232 edges):** Muted steel (`#94A3B8`), stroke width $0.8\text{ pt}$.
  * **River Clyde Polygon:** Subtle cyan fill (`#E0F2FE`) running east-west between $55.854^\circ\text{N}$ and $55.858^\circ\text{N}$.
- **Callout Inset (Zoom: $55.853^\circ\text{N}$ to $55.858^\circ\text{N}$, $-4.272^\circ\text{W}$ to $-4.268^\circ\text{W}$):**
  * Highlights the elevated M8 Kingston Bridge crossing directly over A814 Broomielaw and Argyle Street.
  * Visual annotation indicating **0 shared junction nodes**; on-ramps and off-ramps clearly marked with green ingress/egress arrows.
- **Exact Source Files:**
  * [`data/network/reconstructed_network_nodes.csv`](../data/network/reconstructed_network_nodes.csv)
  * [`data/network/reconstructed_network_edges.csv`](../data/network/reconstructed_network_edges.csv)
- **Caption:** *Figure 1: Reconstructed road network graph of central Glasgow (1,047 nodes, 1,932 directed edges) extracted from OpenStreetMap. The inset confirms strict topological grade separation: the elevated 10-lane M8 Kingston Bridge passes over surface streets without planar intersection nodes.*

---

### Figure 2: The Directional River Clyde Bridge Couplet Schematic
- **Figure Type:** Micro-Corridor Directional Vector Diagram.
- **Coordinate Envelope:** Longitude $[-4.262^\circ\text{W}, -4.255^\circ\text{W}]$, Latitude $[55.853^\circ\text{N}, 55.858^\circ\text{N}]$.
- **Visual Design:**
  * **King George V Bridge:** Four directed edges in green (`#16A34A`), oriented strictly **Northbound** ($990232901 \to 3929567602$; length 194.4 m) leading directly into Oswald Street.
  * **Glasgow Bridge (Jamaica Bridge):** One directed edge in purple (`#9333EA`), oriented strictly **Southbound** ($35625558 \to 3841225793$; length 157.2 m) leading out of Jamaica Street into Bridge Street.
  * Directional flow arrows indicating legal traffic movement.
  * Adjacent crossings (Victoria Bridge to the east, Kingston Bridge to the west) shown with dashed grey connectors.
- **Exact Source Files:**
  * [`reports/phase4_3_bridge_closure_validation.md`](./phase4_3_bridge_closure_validation.md)
  * [`data/network/reconstructed_network_edges.csv`](../data/network/reconstructed_network_edges.csv)
- **Caption:** *Figure 2: Topological structure of the central Glasgow River Clyde couplet. King George V Bridge operates exclusively northbound (4 links), while Glasgow Bridge operates exclusively southbound (1 link). Severing one crossing induces zero disruption in the opposing direction.*

---

### Figure 3: Shortest-Path Route Diversion Under Bridge Severance
- **Figure Type:** Comparative Dijkstra Route Overlay.
- **Map Context:** Central Glasgow street grid spanning south and north of the river.
- **Path Specifications:**
  * **Origin:** Node $100878338$ ($55.85193^\circ\text{N}, -4.26078^\circ\text{W}$, Nelson St / Commerce St).
  * **Destination:** Node $28801025$ ($55.86237^\circ\text{N}, -4.26433^\circ\text{W}$, St Vincent St / Douglas St).
  * **Baseline Route (Solid Blue, `#2563EB`):** 25 nodes, **1,701.5 m**, free-flow travel time **150.1 s** (2 min 30 s) crossing via George V Bridge.
  * **Rerouted Route Under Closure (Dashed Amber, `#D97706`):** 18 nodes, **2,250.7 m**, free-flow travel time **182.1 s** (3 min 02 s) diverting via Cook St on-ramp, M8 Kingston Bridge northbound, and Waterloo St off-ramp.
  * **Closure Marker:** Prominent red "X" (`#DC2626`) on King George V Bridge main span.
- **Exact Source Files:**
  * [`scripts/generate_route_examples.py`](../scripts/generate_route_examples.py)
  * [`reports/phase4_3_bridge_closure_validation.md`](./phase4_3_bridge_closure_validation.md)
- **Caption:** *Figure 3: Empirical shortest-path diversion under King George V Bridge closure. The path diverts from the central surface couplet to the elevated M8 Kingston Bridge motorway corridor, adding +549.2 m (+32.3%) in distance and +32.0 s (+21.3%) in free-flow traversal time.*

---

### Figure 4: Geographic Study Boundary Truncation & Cul-de-Sac Map
- **Figure Type:** Spatial Connectivity & Upstream Ancestor Heatmap.
- **Spatial Bounds:** Northern boundary highlighted at Latitude $55.865^\circ\text{N}$.
- **Visual Design:**
  * **Truncation Boundary:** Heavy dashed red line at $\text{lat} = 55.865^\circ\text{N}$ labeled *"Northern Study Perimeter Cutoff"*.
  * **Isolated M8 Motorway Links:** Highlighted in magenta (`#C026D3`), terminating at node $3845455477$ ($55.86498^\circ\text{N}$).
  * **Ancestor Count Badge:** Annotated bubble showing upstream reachable ancestors collapsing from **954 nodes (baseline)** to **4 nodes (Kingston Bridge closed)**.
  * **Phantom Connectors (Ghosted Lines):** Dotted lines extending north past $55.865^\circ\text{N}$ to Charing Cross on-ramps (Junctions 17/18) and west to the Clyde Tunnel, visually demonstrating the severed regional bypasses.
- **Exact Source Files:**
  * [`scripts/analyze_boundary_disconnect.py`](../scripts/analyze_boundary_disconnect.py)
  * [`reports/phase4_3_boundary_sensitivity.md`](./phase4_3_boundary_sensitivity.md)
- **Caption:** *Figure 4: Mechanism of the 4,125 unreachable OD node pairs under M8 Kingston Bridge closure. Truncating the model boundary at 55.865°N isolates northern motorway mainline stubs from Charing Cross surface on-ramps and regional bypasses, creating an artificial topological cul-de-sac.*

---

### Figure 5: Anomaly Detection Performance & Operational Trade-Offs
- **Figure Type:** Two-Panel Statistical Evaluation Plot.
- **Panel A: Precision-Recall Curves by Anomaly Modality:**
  * **X-Axis:** Recall ($[0.0, 1.0]$).
  * **Y-Axis:** Precision ($[0.0, 1.0]$).
  * **Curves:**
    - Catastrophic Zero Dropout (LOF / Seasonal ESD): Curve stays high, **PR-AUC = 0.88–0.92**.
    - Calibration Drift -50% (Univariate Models): Curve hugs the origin, **PR-AUC = 0.012**.
    - Calibration Drift -50% (Bivariate Spatial Detector): **PR-AUC = 0.1035** (order-of-magnitude gain).
- **Panel B: Operational Trade-Off (Recall vs. False Alarm Rate):**
  * **X-Axis:** Contamination Rate Calibration ($c \in [0.001, 0.20]$).
  * **Y-Axis 1 (Left, Solid):** Recall ($[0.0, 0.80]$).
  * **Y-Axis 2 (Right, Dashed):** Annual False Alarms per Detector Pair (Hours/Year, $[0, 1800]$).
  * **Annotation Points:**
    - $c = 0.01$ (1% FPR): Recall = **4.96%**, Annual False Alarms = **71 hours/yr**.
    - $c = 0.05$ (5% FPR): Recall = **35.51%**, Annual False Alarms = **423 hours/yr** (FDR = 92.94%).
    - $c = 0.10$ (10% FPR): Recall = **56.55%**, Annual False Alarms = **872 hours/yr**.
- **Exact Source Files:**
  * [`reports/anomaly_benchmark_results.csv`](./anomaly_benchmark_results.csv)
  * [`reports/spatial_detector_threshold_analysis.csv`](./spatial_detector_threshold_analysis.csv)
- **Caption:** *Figure 5: Anomaly detection benchmark across 900 scenarios. While catastrophic dropouts are readily identified, subtle decalibration drifts remain elusive. Bivariate spatial tracking improves relative detection (PR-AUC 0.1035 vs 0.012), but raising recall above 35% triggers over 400 false alarms per year, necessitating multi-hour persistence filtering.*

---

### Figure 6: Cross-River Network Resilience (Time and Distance Deltas)
- **Figure Type:** Paired Horizontal Bar Chart.
- **Y-Axis (Scenarios & Directions):**
  1. *King George V Bridge Alone (South $\to$ North)*
  2. *King George V Bridge Alone (North $\to$ South)*
  3. *Glasgow Bridge Alone (South $\to$ North)*
  4. *Glasgow Bridge Alone (North $\to$ South)*
  5. *George V + Glasgow Combined (South $\to$ North)*
  6. *George V + Glasgow Combined (North $\to$ South)*
  7. *M8 Kingston Bridge Alone (South $\to$ North)*
  8. *M8 Kingston Bridge Alone (North $\to$ South)*
  9. *Clyde Arc Alone (South $\to$ North)*
  10. *Clyde Arc Alone (North $\to$ South)*
- **X-Axis 1 (Top Bar, Blue):** Mean Shortest-Path Free-Flow Travel Time Delta ($\Delta t_{\text{free}}$, seconds; range $[0, 30\text{ s}]$).
- **X-Axis 2 (Bottom Bar, Amber):** Mean Detour Distance Delta ($\Delta \text{dist}$, meters; range $[0, 300\text{ m}]$).
- **Exact Values Plotted:**
  * George V (S $\to$ N): **+24.74 s**, **+253.74 m** (69,693 pairs rerouted).
  * George V (N $\to$ S): **+0.00 s**, **+0.00 m** (0 pairs rerouted).
  * Glasgow Bridge (S $\to$ N): **+0.00 s**, **+0.00 m** (0 pairs rerouted).
  * Glasgow Bridge (N $\to$ S): **+9.82 s**, **+136.08 m** (30,488 pairs rerouted).
  * Kingston Bridge (S $\to$ N): **+1.79 s**, **+17.86 m** (7,319 pairs rerouted; 4,125 boundary disconnected).
  * Kingston Bridge (N $\to$ S): **+8.94 s**, **+34.77 m** (25,796 pairs rerouted; 4,962 boundary disconnected).
  * Clyde Arc (S $\to$ N): **+13.55 s**, **+262.41 m** (18,446 pairs rerouted).
  * Clyde Arc (N $\to$ S): **+10.01 s**, **+223.88 m** (16,810 pairs rerouted).
- **Exact Source Files:**
  * [`reports/phase4_3_final_results.md`](./phase4_3_final_results.md)
  * [`scripts/calculate_distance_changes.py`](../scripts/calculate_distance_changes.py)
- **Caption:** *Figure 6: Directional shortest-path travel time and distance deltas across 218,401 cross-river OD pairs. The chart quantifies the complete directional decoupling of the central arterial couplets (George V and Glasgow Bridge) and highlights the contrasting high-speed vs. surface street rerouting trade-offs.*

---

## 3. Implementation Runbook for Generating Figures

When generating publication-ready figures using Python (`matplotlib`, `seaborn`, `geopandas`, or `contextily`), execute the following offline script template:

```python
import os
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = r"."

# Load validated source artifacts
edges_df = pd.read_csv(os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_edges.csv"))
nodes_df = pd.read_csv(os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_nodes.csv"))
threshold_df = pd.read_csv(os.path.join(PROJECT_ROOT, "reports", "spatial_detector_threshold_analysis.csv"))
resilience_df = pd.read_csv(os.path.join(PROJECT_ROOT, "reports", "phase4_2_resilience_sensitivity.csv"))

# Style configuration for academic publications
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
```
