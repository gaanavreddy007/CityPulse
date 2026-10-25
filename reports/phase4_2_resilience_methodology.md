# CITYPULSE Phase 4.2: Resilience Experiment Methodology & OD Specification

**Project:** `C:\Gaanav\Projects\CityPulse`  
**Milestone:** Phase 4.2 (Gate 4 Methodology)  
**Author:** Transport-Network Data Scientist & Graph Engineer  
**Date:** October 2026  
**Status:** **GATE 4 COMPLETE — METHODOLOGY FORMALIZED**

---

## 1. Executive Summary

This report establishes the rigorous experimental protocol for evaluating road-network resilience across the River Clyde Central Crossing Corridor using the reconstructed OpenStreetMap (OSM) topological graph.

In direct response to the methodology flaws identified in the Phase 4.1 audit, this framework eliminates artificial disconnection penalties, separates topological unreachability from real travel time detour delay, defines three defensible Origin-Destination (OD) evaluation cohorts, and grounds all impedance metrics in authentic graph shortest paths.

---

## 2. Experimental Principles & Strict Methodological Rules

### Rule 1: No Synthetic Disconnection Penalties in Primary Metrics
In the flawed Phase 4 model, disconnected pairs were assigned an arbitrary penalty of $M = 3,600\text{s}$, which comprised over 99.98% of the calculated impedance.
In Phase 4.2:
- Primary resilience metrics are computed strictly on the cohort of pairs that **remain reachable** in both baseline and severed networks:
  $$\Delta \mathcal{C}_{\text{detour}} = \frac{1}{|OD_{\text{still\_connected}}|} \sum_{(u, v) \in OD_{\text{still\_connected}}} \left[ d_{G \setminus \{e\}}(u, v) - d_G(u, v) \right]$$
- Topological disconnection is reported as an independent integer count and percentage ($\Delta N_{\text{disc}}, \%_{\text{disc}}$), never disguised as a measured travel delay.
- If a penalty $M$ is evaluated for sensitivity comparison, it is explicitly classified as an unverified scenario assumption.

### Rule 2: Fixed Pre-Defined OD Cohorts
To prevent sampling bias or survivorship distortion:
- All closure evaluations are performed on the exact same pre-defined OD cohort established before the closure is applied.
- The baseline reachable population is locked, and closures are evaluated against this identical cohort.

### Rule 3: Separation of Free-Flow Geometry from BPR Flow Models
- SCOOT detector loop flow cannot be equated to total link traffic volume without origin-destination matrices.
- Therefore, primary resilience results are evaluated on **true free-flow travel time (seconds)** derived from WebTAG speed limits and geodetic edge lengths, and on **geodetic distance (meters)**.
- BPR volume-delay modeling is retained strictly as an optional scenario sensitivity test, clearly separated from structural graph findings.

---

## 3. Definition of Evaluation OD Cohorts

To test resilience across different travel patterns, three distinct OD cohorts are defined:

### Cohort A: Cross-River Commuter Cohort (Primary Benchmark)
- **Definition:** Trips with origin $u$ on the South Bank of the River Clyde ($\text{latitude} < 55.854^\circ$) and destination $v$ on the North Bank ($\text{latitude} > 55.858^\circ$).
- **Rationale:** This cohort represents travelers who physically **must cross the River Clyde** to complete their trip. They are directly exposed to bridge disruptions and capture the full rerouting dynamics of the corridor.
- **Population:** 294 southside origin nodes $\times$ 485 northside destination nodes = $142,590$ candidate pairs.
- **Baseline Reachability:** **110,509 pairs (77.5%)** are fully reachable in baseline conditions.

### Cohort B: Core City-Centre Grid Sample (Local Circulation)
- **Definition:** A stratified random sample of $N = 1,000$ OD pairs drawn uniformly from the Giant Strongly Connected Component (911 nodes).
- **Rationale:** Evaluates whether river bridge closures cause collateral rerouting delays for local intra-city circulation on the north or south bank.
- **Baseline Reachability:** **1,000 pairs (100.0%)** reachable in baseline.

### Cohort C: East-West Corridor Gateway Cohort (Through-Traffic)
- **Definition:** Trips between western gateway nodes (SECC, Finnieston, Clydeside Expressway) and eastern gateway nodes (Saltmarket, Glasgow Green, High Street).
- **Rationale:** Evaluates the resilience of east-west bypass corridors (Broomielaw, Argyle Street) when north-south crossings are closed.

---

## 4. Bridge Disruption Scenario Definitions

Closures are executed by removing specific directed edge sets verified from the OpenStreetMap way identifiers:

### Scenario 1: M8 Kingston Bridge Dual-Carriageway Severance
- **Description:** Complete closure of the 10-lane elevated motorway viaduct carrying the M8 across the River Clyde.
- **Severed Edges:** All 5 directed edges matching `Kingston Bridge` (OSM Ways 4614138, 4614139, 4614140, etc.), including Northbound and Southbound carriageways totaling $1,324.2\text{ meters}$ of road deck.
- **Remaining Crossings:** George V Bridge, Glasgow Bridge (Jamaica Bridge), Victoria Bridge, Albert Bridge, Clyde Arc (Squinty Bridge).

### Scenario 2: George V & Glasgow Bridge (Jamaica Bridge) Arterial Severance
- **Description:** Complete closure of the primary north-south central city-centre arterial axis directly linking Glasgow Central Station to Bridge Street / Tradeston.
- **Severed Edges:** All 5 directed edges matching `George V Bridge` (southbound, OSM Way 4614134) and `Glasgow Bridge` (northbound, OSM Way 4614135).
- **Remaining Crossings:** M8 Kingston Bridge, Victoria Bridge, Albert Bridge, Clyde Arc.

### Scenario 3: Western Corridor Severance (Clyde Arc / Squinty Bridge)
- **Description:** Complete closure of the western local relief crossing linking Finnieston to Govan Road.
- **Severed Edges:** All directed edges matching `Clyde Arc` (OSM Way 23075252).
- **Remaining Crossings:** M8 Kingston Bridge, George V Bridge, Glasgow Bridge, Victoria Bridge, Albert Bridge.

### Scenario 4: Compound Disruption (M8 Kingston + George V Bridges)
- **Description:** Catastrophic compound disruption severing both the motorway crossing and the primary central arterial bridge simultaneously.
- **Remaining Crossings:** Victoria Bridge, Albert Bridge, Clyde Arc.

---

## 5. Output Metrics Specification

For each scenario evaluated on a cohort of $N_{\text{base}}$ baseline reachable pairs:
1. **Newly Unreachable Pairs ($\Delta N_{\text{disc}}$):** Number of OD pairs that become topologically disconnected.
2. **Disconnection Percentage ($\%_{\text{disc}}$):** $\frac{\Delta N_{\text{disc}}}{N_{\text{base}}} \times 100\%$.
3. **Still-Connected Pair Count ($N_{\text{conn}}$):** Number of pairs that remain reachable via detour.
4. **Mean Detour Delay ($\Delta \bar{t}_{\text{detour}}$):** Mean increase in free-flow travel time (seconds) among still-connected pairs:
   $$\Delta \bar{t}_{\text{detour}} = \frac{1}{N_{\text{conn}}} \sum \left( t_{\text{closure}} - t_{\text{base}} \right)$$
5. **Relative Detour Delay ($\%_{\text{delay}}$):** $\frac{\Delta \bar{t}_{\text{detour}}}{\bar{t}_{\text{base}}} \times 100\%$.
6. **Maximum Detour Delay ($\Delta t_{\max}$):** Worst-case single-pair detour penalty (seconds).
7. **Rerouted Pair Count ($N_{\text{rerouted}}$):** Number of pairs experiencing detour delay $> 0.1\text{s}$.
8. **Rerouted Pair Share ($\%_{\text{rerouted}}$):** Percentage of still-connected travelers forced to divert.
9. **Arbitrary Penalty Sensitivity:** Total impedance under $M \in [600, 1800, 3600, 7200\text{s}]$, labeled explicitly as an engineering assumption.

---

### Gate 4 Conclusion:
The methodology is formally specified, eliminating artificial penalties from primary metrics and establishing realistic OD evaluation cohorts. Gate 4 is satisfied.
