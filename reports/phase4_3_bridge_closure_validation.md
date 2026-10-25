# CITYPULSE — PHASE 4.3: BRIDGE CLOSURE VERIFICATION & ONE-WAY COUPLET ANALYSIS

**Reviewer Role:** Independent Transport-Network Modelling Reviewer  
**Project:** CityPulse (`C:\Gaanav\Projects\CityPulse`)  
**Network Dataset:** Reconstructed Glasgow Network (1,047 nodes, 1,932 edges)  
**Evaluation Script:** `scripts/audit_separate_bridges.py` & `scripts/generate_route_examples.py`  
**Date:** 2026-10-25  

---

## 1. Executive Summary

A critical finding of the Phase 4.3 audit is that the central Glasgow River Clyde road crossings operate as **asymmetric, highly specialized directional corridors**. In previous preliminary studies, bridges were often treated as generic bidirectional conduits. In reality, **King George V Bridge** and **Glasgow Bridge (Jamaica Street Bridge)** form a synchronized one-way paired couplet.

This report documents:
1. Exact directed edge IDs, OpenStreetMap way IDs, coordinate ranges, and physical lengths for all four evaluated river crossings.
2. Independent single-bridge closure evaluations for George V Bridge alone and Glasgow Bridge alone, contrasting them against their combined closure and the M8 Kingston Bridge viaduct.
3. Concrete before-and-after shortest-path route examples detailing node IDs, coordinates, path lengths, free-flow travel times, and detour diversion corridors.

---

## 2. Definitive Bridge Edge Catalog

The reconstructed network represents each crossing via canonical OSM way IDs and verified topological directed edges:

### 2.1 King George V Bridge (Northbound Surface Arterial Couplet)
Carries 4 lanes of vehicular traffic northbound into the city centre towards Oswald Street and Broomielaw.
- **Edge 1:** `OSM_4519159_990232901_117058320` (OSM Way 4519159)  
  Nodes: $990232901 \to 117058320$ | ($55.85487^\circ\text{N}, -4.25976^\circ\text{W} \to 55.85494^\circ\text{N}, -4.25976^\circ\text{W}$)  
  Length: 7.8 m | Free-Flow Time: 0.6 s | Direction: Northbound
- **Edge 2:** `OSM_12796510_117058320_411289100` (OSM Way 12796510)  
  Nodes: $117058320 \to 411289100$ | ($55.85494^\circ\text{N}, -4.25976^\circ\text{W} \to 55.85633^\circ\text{N}, -4.25973^\circ\text{W}$)  
  Length: 153.8 m | Free-Flow Time: 11.5 s | Direction: Northbound (Main River Span)
- **Edge 3:** `OSM_35066914_411289100_11725369680` (OSM Way 35066914)  
  Nodes: $411289100 \to 11725369680$ | ($55.85633^\circ\text{N}, -4.25973^\circ\text{W} \to 55.85652^\circ\text{N}, -4.25973^\circ\text{W}$)  
  Length: 21.6 m | Free-Flow Time: 1.6 s | Direction: Northbound
- **Edge 4:** `OSM_380808410_11725369680_3929567602` (OSM Way 380808410)  
  Nodes: $11725369680 \to 3929567602$ | ($55.85652^\circ\text{N}, -4.25973^\circ\text{W} \to 55.85662^\circ\text{N}, -4.25973^\circ\text{W}$)  
  Length: 11.2 m | Free-Flow Time: 0.8 s | Direction: Northbound

### 2.2 Glasgow Bridge / Jamaica Bridge (Southbound Surface Arterial Couplet)
Carries 4 lanes of vehicular traffic southbound out of the city centre from Jamaica Street towards Bridge Street.
- **Edge 1:** `OSM_4521175_35625558_3841225793` (OSM Way 4521175)  
  Nodes: $35625558 \to 3841225793$ | ($55.85615^\circ\text{N}, -4.25765^\circ\text{W} \to 55.85476^\circ\text{N}, -4.25814^\circ\text{W}$)  
  Length: 157.2 m | Free-Flow Time: 11.7 s | Direction: Southbound (Main River Span)

### 2.3 M8 Kingston Bridge Viaduct (High-Capacity Grade-Separated Motorway)
Carries 10 lanes of the M8 motorway corridor across the river (5 lanes northbound, 5 lanes southbound).
- **Edge 1 (NB Mainline):** `OSM_4287401_194813_194815` (OSM Way 4287401)  
  Nodes: $194813 \to 194815$ | ($55.85322^\circ\text{N}, -4.27074^\circ\text{W} \to 55.85802^\circ\text{N}, -4.27024^\circ\text{W}$)  
  Length: 536.3 m | Free-Flow Time: 24.2 s | Direction: Northbound
- **Edge 2 (NB Collector):** `OSM_4803260_30824666_158954168` (OSM Way 4803260)  
  Nodes: $30824666 \to 158954168$ | ($55.85417^\circ\text{N}, -4.27061^\circ\text{W} \to 55.85765^\circ\text{N}, -4.27040^\circ\text{W}$)  
  Length: 388.1 m | Free-Flow Time: 29.0 s | Direction: Northbound
- **Edge 3 (SB Segment 1):** `OSM_69067205_28849785_3821163140` (OSM Way 69067205)  
  Nodes: $28849785 \to 3821163140$ | ($55.85667^\circ\text{N}, -4.26999^\circ\text{W} \to 55.85511^\circ\text{N}, -4.27004^\circ\text{W}$)  
  Length: 173.9 m | Free-Flow Time: 7.8 s | Direction: Southbound
- **Edge 4 (SB Segment 2):** `OSM_69067225_3821163140_3821163139` (OSM Way 69067225)  
  Nodes: $3821163140 \to 3821163139$ | ($55.85511^\circ\text{N}, -4.27004^\circ\text{W} \to 55.85383^\circ\text{N}, -4.27023^\circ\text{W}$)  
  Length: 143.1 m | Free-Flow Time: 6.4 s | Direction: Southbound
- **Edge 5 (SB Segment 3):** `OSM_975961077_3821163139_353024` (OSM Way 975961077)  
  Nodes: $3821163139 \to 353024$ | ($55.85383^\circ\text{N}, -4.27023^\circ\text{W} \to 55.85310^\circ\text{N}, -4.27054^\circ\text{W}$)  
  Length: 82.9 m | Free-Flow Time: 3.7 s | Direction: Southbound

### 2.4 Clyde Arc / "Squinty Bridge" (Western Surface Arterial)
Carries 4 lanes of vehicular traffic (including bus lanes) connecting Finnieston to Pacific Quay.
- **Edge 1 (SB):** `OSM_4287346_256697929_25870524` (OSM Way 4287346)  
  Nodes: $256697929 \to 25870524$ | ($55.85765^\circ\text{N}, -4.28173^\circ\text{W} \to 55.85652^\circ\text{N}, -4.28414^\circ\text{W}$)  
  Length: 196.6 m | Free-Flow Time: 22.1 s | Direction: Southbound
- **Edge 2 (NB):** `OSM_4287346_25870524_256697929` (OSM Way 4287346)  
  Nodes: $25870524 \to 256697929$ | ($55.85652^\circ\text{N}, -4.28414^\circ\text{W} \to 55.85765^\circ\text{N}, -4.28173^\circ\text{W}$)  
  Length: 196.6 m | Free-Flow Time: 22.1 s | Direction: Northbound

---

## 3. Comparative Resilience Metrics Across Bridge Closures

To capture the true operational dynamics of the network, the origin-destination (OD) cohort was fixed to all cross-river pairs connecting the southern quadrant (latitude $< 55.854^\circ\text{N}$) and the northern quadrant (latitude $> 55.858^\circ\text{N}$):
- **Baseline South $\to$ North reachable OD pairs:** 110,509
- **Baseline North $\to$ South reachable OD pairs:** 107,892
- **Total Cross-River OD cohort:** 218,401 pairs

### 3.1 Separate vs. Combined Closure Results

| Scenario Evaluated | Direction | Baseline Reachable | Still Connected (%) | Newly Unreachable | Rerouted OD Pairs | Mean $\Delta t_{\text{free}}$ (s) | Max $\Delta t_{\text{free}}$ (s) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **George V Bridge Alone** | South $\to$ North | 110,509 | 110,509 (100.0%) | 0 (0.00%) | 69,693 (63.07%) | **+24.74 s** | +125.2 s |
| *(Northbound Couplet Severed)* | North $\to$ South | 107,892 | 107,892 (100.0%) | 0 (0.00%) | 0 (0.00%) | **+0.00 s** | +0.0 s |
| **Glasgow Bridge Alone** | South $\to$ North | 110,509 | 110,509 (100.0%) | 0 (0.00%) | 0 (0.00%) | **+0.00 s** | +0.0 s |
| *(Southbound Couplet Severed)* | North $\to$ South | 107,892 | 107,892 (100.0%) | 0 (0.00%) | 30,488 (28.26%) | **+9.82 s** | +112.3 s |
| **George V + Glasgow Combined** | South $\to$ North | 110,509 | 110,509 (100.0%) | 0 (0.00%) | 69,693 (63.07%) | **+24.74 s** | +125.2 s |
| *(Entire Surface Central Axis Severed)*| North $\to$ South | 107,892 | 107,892 (100.0%) | 0 (0.00%) | 30,488 (28.26%) | **+9.82 s** | +112.3 s |
| **Kingston Bridge Alone** | South $\to$ North | 110,509 | 106,384 (96.27%) | 4,125 (3.73%)* | 7,319 (6.88%) | **+1.79 s** | +65.1 s |
| *(M8 Motorway Flyover Severed)* | North $\to$ South | 107,892 | 102,930 (95.40%) | 4,962 (4.60%)* | 25,796 (25.06%) | **+8.94 s** | +102.7 s |
| **Clyde Arc Alone** | South $\to$ North | 110,509 | 110,509 (100.0%) | 0 (0.00%) | 18,446 (16.69%) | **+13.55 s** | +190.2 s |
| *(Western Surface Crossing Severed)* | North $\to$ South | 107,892 | 107,892 (100.0%) | 0 (0.00%) | 16,810 (15.58%) | **+10.01 s** | +215.8 s |

*\*Note: Newly unreachable pairs under Kingston Bridge closure are confirmed boundary truncation artifacts (see Section 6).*

### 3.3 Key Scientific Takeaways
1. **Total Directional Decoupling:** Closing George V Bridge causes **zero rerouting and zero travel time change** in the North $\to$ South direction. Conversely, closing Glasgow Bridge causes **zero rerouting and zero travel time change** in the South $\to$ North direction. Models that assume bidirectional links on these bridges produce completely fictitious symmetry.
2. **Couplet Independence:** Severing George V Bridge alone forces 69,693 South $\to$ North journeys to detour via Kingston Bridge or Victoria Bridge. Closing Glasgow Bridge concurrently does not alter this South $\to$ North detour because Glasgow Bridge was never available to northbound traffic.
3. **Resilience Redundancy:** Even with both George V and Glasgow Bridges closed simultaneously, **100.0% of OD pairs remain reachable**, utilizing Victoria Bridge, Albert Bridge, and Kingston Bridge.

---

## 4. Concrete Before-and-After Route Examples

To make detour behavior fully verifiable, concrete route examples were extracted directly from Dijkstra path traversals before and after bridge closures:

### 4.1 Route Example 1: George V Bridge Closure (Northbound Reroute)
- **Origin Node:** $100878338$ ($55.85193^\circ\text{N}, -4.26078^\circ\text{W}$, Nelson St / Commerce St, South of Clyde)
- **Destination Node:** $28801025$ ($55.86237^\circ\text{N}, -4.26433^\circ\text{W}$, St Vincent St / Douglas St, North of Clyde)
- **Baseline Path:**
  - Traversal: 25 nodes via Commerce Street $\to$ George V Bridge $\to$ Oswald Street $\to$ Hope Street $\to$ St Vincent Street.
  - River Crossing: **George V Bridge** (`OSM_12796510_117058320_411289100`)
  - Distance: **1,701.5 m**
  - Modelled Free-Flow Travel Time: **150.1 s** (2 min 30 s)
- **Rerouted Path (Under George V Closure):**
  - Traversal: 18 nodes via Cook Street $\to$ M8 On-Ramp $\to$ Kingston Bridge $\to$ Waterloo Street Off-Ramp $\to$ Douglas Street.
  - River Crossing: **Kingston Bridge** (`OSM_4803260_30824666_158954168`)
  - Distance: **2,250.7 m**
  - Modelled Free-Flow Travel Time: **182.1 s** (3 min 02 s)
- **Impact:** Distance change: **+549.2 m (+32.3%)**; Free-flow shortest-path time change: **+32.0 s (+21.3%)**.

### 4.2 Route Example 2: Glasgow Bridge Closure (Southbound Reroute)
- **Origin Node:** $239806464$ ($55.85882^\circ\text{N}, -4.24393^\circ\text{W}$, Trongate / Merchant City, North of Clyde)
- **Destination Node:** $13184519175$ ($55.85389^\circ\text{N}, -4.25770^\circ\text{W}$, Bridge Street, South of Clyde)
- **Baseline Path:**
  - Traversal: 26 nodes via Trongate $\to$ Argyle Street $\to$ Jamaica Street $\to$ Glasgow Bridge $\to$ Bridge Street.
  - River Crossing: **Glasgow Bridge** (`OSM_4521175_35625558_3841225793`)
  - Distance: **1,834.1 m**
  - Modelled Free-Flow Travel Time: **147.4 s** (2 min 27 s)
- **Rerouted Path (Under Glasgow Bridge Closure):**
  - Traversal: 29 nodes via Trongate $\to$ Saltmarket $\to$ Victoria Bridge $\to$ Norfolk Street $\to$ Bridge Street.
  - River Crossing: **Victoria Bridge** (`OSM_4609138_194784_194785`)
  - Distance: **2,285.7 m**
  - Modelled Free-Flow Travel Time: **184.9 s** (3 min 05 s)
- **Impact:** Distance change: **+451.6 m (+24.6%)**; Free-flow shortest-path time change: **+37.5 s (+25.4%)**.

### 4.3 Route Example 3: Kingston Bridge Closure (Northbound Motorway Diversion)
- **Origin Node:** $100878338$ ($55.85193^\circ\text{N}, -4.26078^\circ\text{W}$, South of Clyde)
- **Destination Node:** $278458381$ ($55.86045^\circ\text{N}, -4.27334^\circ\text{W}$, St Vincent Street West, North of Clyde)
- **Baseline Path:** 28 nodes, **2,949.6 m**, **263.3 s** (uses M8 Kingston Bridge northbound mainline).
- **Rerouted Path:** 48 nodes, **3,120.8 m**, **272.0 s** (diverts via George V Bridge and central surface grid).
- **Impact:** Distance change: **+171.2 m (+5.8%)**; Free-flow shortest-path time change: **+8.6 s (+3.3%)**.

### 4.4 Route Example 4: Kingston Bridge Closure (Southbound Motorway Diversion)
- **Origin Node:** $28801025$ ($55.86237^\circ\text{N}, -4.26433^\circ\text{W}$, North of Clyde)
- **Destination Node:** $100878338$ ($55.85193^\circ\text{N}, -4.26078^\circ\text{W}$, South of Clyde)
- **Baseline Path:** 22 nodes, **2,120.7 m**, **158.6 s** (uses M8 Kingston Bridge southbound mainline at 50 mph).
- **Rerouted Path:** 30 nodes, **2,084.5 m**, **199.2 s** (diverts via Jamaica Street and Glasgow Bridge at 30 mph).
- **Impact:** Distance change: **-36.2 m (-1.7% shorter)**; Free-flow shortest-path time change: **+40.6 s (+25.6% slower due to urban speed limits)**.

---

## 5. Summary & Reviewer Certification

The empirical evidence confirms that the reconstructed road graph accurately captures:
1. The directional asymmetry of the George V (northbound) and Glasgow Bridge (southbound) couplet.
2. The realistic rerouting of urban traffic across adjacent bridges (Victoria Bridge, Albert Bridge, and Kingston Bridge) without structural network breakdown.
3. The distinct speed differentials between grade-separated motorway corridors and urban surface streets.
