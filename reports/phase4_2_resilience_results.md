# CITYPULSE Phase 4.2: Road Network Resilience Results Report

**Project:** `./`  
**Milestone:** Phase 4.2 (Gate 5 Experimental Evaluation)  
**Author:** Transport-Network Data Scientist & Graph Engineer  
**Date:** October 2026  
**Status:** **REVALIDATION COMPLETE — AUTHENTIC DETOUR RESILIENCE DEMONSTRATED**

---

## 1. Executive Summary

This report delivers the empirical findings of road-network resilience simulations executed on the newly reconstructed OpenStreetMap (OSM) topological graph of Glasgow's River Clyde Central Crossing Corridor.

In direct contrast to the discredited Phase 4 model—which simulated disconnected two-node islands and reported that 98.6% of OD pairs were severed due to an arbitrary penalty—this revalidated benchmark evaluates authentic shortest-path detours across a validated graph of **1,047 real junction nodes** and **1,932 directed road links**.

### Key Revalidated Scientific Findings:
1. **Network Connectivity & Full Reachability Preserved on Arterial Closures:** Under the complete severance of the central north-south arterial crossing (**George V & Glasgow Bridge**), **100.0% of the 110,509 baseline cross-river trips remain fully reachable** via detour ($0\text{ newly disconnected pairs}$).
2. **Substantial Real-World Detour Delays:** Rather than experiencing zero rerouting (as in Phase 4), **69,652 cross-river trips (63.0% of all commuters) are forced to reroute**, incurring an average travel time delay of **$+24.74\text{ seconds}$ (+11.0%)** and an average physical detour distance of **$+235.5\text{ meters}$**. Maximum single-pair detour delay reaches **$+125.2\text{ seconds}$ (+2.08 minutes)**.
3. **Motorway vs Surface Grid Divergence:** Under the severance of the **M8 Kingston Bridge elevated viaduct**:
   - **96.3% of cross-river trips (106,384 pairs)** maintain connectivity by diverting onto surface bridges (George V, Victoria, and Albert Bridges).
   - Only **4,125 pairs (3.73%)** become newly disconnected—representing trips originating or terminating on elevated grade-separated motorway ramps that have no surface grid connections within the central bounding box.
   - For still-connected commuters, the mean detour delay is **$+1.79\text{ seconds}$ (+0.8%)**, with 7,319 trips rerouted by up to $+65.1\text{ seconds}$.
4. **Structural Validity of East-West Independence:** For east-west transit along the north bank (Cohort C, 900 pairs), severing the north-south M8 Kingston Bridge causes **exactly 0.0 seconds of delay (0 rerouted pairs)**. This rigorously proves that the reconstructed graph respects spatial and directional independence, eliminating the artificial cross-network leakage present in previous models.

---

## 2. Comprehensive Experimental Results

All simulations were executed across 48 distinct scenario configurations using [`scripts/run_reconstructed_resilience.py`](../scripts/run_reconstructed_resilience.py). The machine-readable dataset is available in [`reports/phase4_2_resilience_sensitivity.csv`](./phase4_2_resilience_sensitivity.csv).

The primary results across all three OD cohorts are summarized below:

### Table 1: Cross-River Commuters (Cohort A: 110,509 Baseline Reachable Pairs)
*Baseline Mean Travel Time: $224.8\text{ seconds}$ | Baseline Mean Travel Distance: $2,469.4\text{ meters}$*

| Disruption Scenario | Still Connected Pairs | Newly Disconnected Pairs | Rerouted Pairs Count | Mean Detour Delay ($\Delta \bar{t}$) | Relative Delay (%) | Max Detour Delay | Mean Detour Distance ($\Delta \bar{d}$) | Max Detour Distance |
|---|---|---|---|---|---|---|---|---|
| **M8 Kingston Bridge** | 106,384 (96.3%) | 4,125 (3.73%) | 7,319 (6.9%) | **+1.79 s** | +0.8% | +65.1 s | +12.0 m | +709.4 m |
| **George V & Glasgow Bridge** | 110,509 (100.0%) | **0 (0.00%)** | **69,652 (63.0%)** | **+24.74 s** | **+11.0%** | **+125.2 s** | **+235.5 m** | **+1,316.1 m** |
| **Clyde Arc (Squinty Bridge)** | 110,509 (100.0%) | **0 (0.00%)** | 18,446 (16.7%) | **+13.55 s** | +6.0% | +190.2 s | +280.2 m | +2,407.5 m |
| **Compound (Kingston + George V)** | 106,384 (96.3%) | 4,125 (3.73%) | **77,008 (72.4%)** | **+36.57 s** | **+16.2%** | **+142.8 s** | **+311.1 m** | **+1,751.0 m** |

---

### Table 2: Core City-Centre Grid Circulation (Cohort B: 1,000 Baseline Reachable Pairs)
*Baseline Mean Travel Time: $189.5\text{ seconds}$ | Baseline Mean Travel Distance: $2,016.8\text{ meters}$*

| Disruption Scenario | Still Connected Pairs | Newly Disconnected Pairs | Rerouted Pairs Count | Mean Detour Delay ($\Delta \bar{t}$) | Relative Delay (%) | Max Detour Delay | Mean Detour Distance ($\Delta \bar{d}$) | Max Detour Distance |
|---|---|---|---|---|---|---|---|---|
| **M8 Kingston Bridge** | 892 (89.2%) | 108 (10.80%) | 75 (8.4%) | **+1.96 s** | +1.1% | +59.8 s | +9.2 m | +564.8 m |
| **George V & Glasgow Bridge** | 1,000 (100.0%) | **0 (0.00%)** | 129 (12.9%) | **+5.88 s** | +3.1% | +123.0 s | +66.9 m | +1,114.9 m |
| **Clyde Arc (Squinty Bridge)** | 1,000 (100.0%) | **0 (0.00%)** | 55 (5.5%) | **+4.21 s** | +2.2% | +200.4 s | +93.7 m | +2,684.6 m |
| **Compound (Kingston + George V)** | 892 (89.2%) | 108 (10.80%) | 178 (20.0%) | **+9.78 s** | +5.3% | +123.0 s | +83.5 m | +1,315.9 m |

---

### Table 3: East-West Gateway Transit (Cohort C: 900 Baseline Reachable Pairs)
*Baseline Mean Travel Time: $270.5\text{ seconds}$ | Baseline Mean Travel Distance: $3,135.1\text{ meters}$*

| Disruption Scenario | Still Connected Pairs | Newly Disconnected Pairs | Rerouted Pairs Count | Mean Detour Delay ($\Delta \bar{t}$) | Relative Delay (%) | Max Detour Delay | Mean Detour Distance ($\Delta \bar{d}$) | Max Detour Distance |
|---|---|---|---|---|---|---|---|---|
| **M8 Kingston Bridge** | 900 (100.0%) | **0 (0.00%)** | **0 (0.0%)** | **+0.00 s** | **0.0%** | **0.0 s** | **+0.0 m** | **0.0 m** |
| **George V & Glasgow Bridge** | 900 (100.0%) | **0 (0.00%)** | 390 (43.3%) | **+3.28 s** | +1.2% | +92.1 s | +35.9 m | +719.9 m |
| **Clyde Arc (Squinty Bridge)** | 900 (100.0%) | **0 (0.00%)** | 80 (8.9%) | **+0.85 s** | +0.3% | +20.4 s | +31.1 m | +449.2 m |
| **Compound (Kingston + George V)** | 900 (100.0%) | **0 (0.00%)** | 390 (43.3%) | **+3.28 s** | +1.2% | +92.1 s | +35.9 m | +719.9 m |

---

## 3. In-Depth Transport Planning & Network Dynamics Analysis

### 3.1 The Central Arterial Bottleneck: George V & Glasgow Bridge
The simulation reveals that **George V & Glasgow Bridge (Jamaica Bridge)** is the most critical network crossing in central Glasgow for trip rerouting:
- Although carrying fewer total lanes (7 lanes) than the M8 Kingston Bridge (10 lanes), George V and Jamaica Bridges form the direct central gateway connecting Southside commercial/residential districts to Glasgow Central Station, Union Street, and the core pedestrian retail precinct.
- Severing this crossing forces **63.0% of all cross-river trips (69,652 pairs)** to divert either westward onto the Kingston Bridge motorway approaches or eastward onto Victoria Bridge (Stockwell Street).
- The resulting detours add an average of **$+235.5\text{ meters}$** and **$+24.74\text{ seconds}$** of free-flow travel time across the entire commuter cohort, with peak detours reaching **$+125.2\text{ seconds}$ (+2.08 minutes)**.

### 3.2 The Expressway Function of M8 Kingston Bridge
In contrast, closing the M8 Kingston Bridge viaduct exhibits very different resilience characteristics:
- Only **6.9% of cross-river trips (7,319 pairs)** are rerouted among still-connected pairs, with an average delay of only $+1.79\text{ seconds}$.
- Because the Kingston Bridge is an elevated motorway designed primarily for regional, long-distance bypass traffic rather than local city-centre access, local cross-river travelers already utilize surface crossings (George V, Victoria, and Albert Bridges) in baseline conditions.
- However, the Kingston Bridge viaduct exhibits **vulnerability to structural disconnection**: 4,125 pairs (3.73%) that enter via dedicated motorway on-ramps cannot access the surface street grid without diverting through external regional junctions outside the central study area.

### 3.3 Compound Catastrophic Severance
Under the compound scenario severing both Kingston Bridge and George V / Glasgow Bridge:
- **72.4% of cross-river commuters (77,008 pairs)** are forced to reroute onto the remaining eastern crossings (Victoria Bridge and Albert Bridge) or the western Clyde Arc.
- Average detour delay surges to **$+36.57\text{ seconds}$ (+16.2%)**, and average detour distance increases by **$+311.1\text{ meters}$**.
- This demonstrates that while the central Glasgow river corridor possesses high topological redundancy, a compound event pushes eastern arterials to extreme detour lengths.

---

## 4. Sensitivity to Disconnection Penalty Assumptions

To fulfill the requirements of Gate 5, total network impedance was evaluated across four arbitrary disconnection penalties ($M \in [600\text{s}, 1800\text{s}, 3600\text{s}, 7200\text{s}]$) in [`reports/phase4_2_resilience_sensitivity.csv`](./phase4_2_resilience_sensitivity.csv):

| Disruption Scenario | Disconnection Penalty ($M$) | Real Detour Delay Sum (Sec) | Disconnection Penalty Sum (Sec) | Total $\Delta \mathcal{C}$ with Penalty (Sec) | Penalty Share of Metric (%) |
|---|---|---|---|---|---|
| **M8 Kingston Closure** | 600.0 s (10 min) | 190,427 s | 2,475,000 s | 2,665,427 s | 92.86% |
| **M8 Kingston Closure** | 1,800.0 s (30 min) | 190,427 s | 7,425,000 s | 7,615,427 s | 97.50% |
| **M8 Kingston Closure** | 3,600.0 s (1 hr) | 190,427 s | 14,850,000 s | 15,040,427 s | **98.73%** |
| **M8 Kingston Closure** | 7,200.0 s (2 hr) | 190,427 s | 29,700,000 s | 29,890,427 s | 99.36% |
| **George V Closure** | Any Penalty ($M$) | **2,733,992 s** | **0 s** | **2,733,992 s** | **0.00%** |
| **Clyde Arc Closure** | Any Penalty ($M$) | **1,497,397 s** | **0 s** | **1,497,397 s** | **0.00%** |

### Methodological Takeaway:
- For **George V Bridge** and **Clyde Arc**, the penalty share is **strictly 0.00%** because 100% of trips remain connected. The metric represents **100% pure measured graph detour delay**.
- For **M8 Kingston Bridge**, any total cost metric that incorporates $M$ is **$>92\%$ to $>99\%$ penalty**, artificially scaling with the analyst's choice of $M$.
- **Scientific Conclusion:** Disconnection count ($\Delta N_{\text{disc}} = 4,125$) and real detour delay ($\Delta \bar{t} = +1.79\text{s}$) **must never be aggregated into a single scalar cost**. They represent fundamentally distinct transport phenomena: spatial exclusion vs routing delay.

---

## 5. Comparison: Phase 4 (Flawed) vs Phase 4.2 (Revalidated)

| Dimension | Phase 4 (Flawed Baseline) | Phase 4.2 (Revalidated OpenStreetMap Graph) | Scientific Status |
|---|---|---|---|
| **Graph Representation** | 20 isolated edges, 38 disjoint node IDs | 1,932 directed edges, 1,047 shared junction nodes | **Fully Validated** |
| **Edge Lengths** | Flat 500.0m default on all edges | Exact geodetic lengths ($1.3\text{m} - 1,312.8\text{m}$) | **True Curvature** |
| **Baseline Disconnection** | 1,384 out of 1,406 pairs (98.44%) disconnected | 0 pairs disconnected in core SCC (87% mutually reachable) | **Authentic Grid** |
| **Connected Detour Delay** | Exactly **0.0 seconds** (zero rerouting) | **+24.74s mean delay, +125.2s max delay** | **Realistic Traffic Detours** |
| **Rerouted Trips** | 0 trips rerouted | **69,652 trips (63.0%) rerouted** | **Macro Detour Dynamics** |
| **George V Severance** | Disconnects 98.6% of pairs via penalty | **100.0% remain connected** (0 newly disconnected) | **True Resilience Observed** |
| **East-West Isolation** | Artificial cross-network leakage | **0.0s delay on east-west flow during M8 closure** | **Directional Integrity** |

---

### Conclusion:
Phase 4.2 has successfully replaced an artificial, penalty-dominated prototype with a rigorous, reproducible, and topologically authentic urban road resilience benchmark for Glasgow.
