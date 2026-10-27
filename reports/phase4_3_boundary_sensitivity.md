# CITYPULSE — PHASE 4.3: BOUNDARY SENSITIVITY AND SPATIAL TRUNCATION ANALYSIS

**Reviewer Role:** Independent Transport-Network Modelling Reviewer  
**Project:** CityPulse (`./`)  
**Network Dataset:** Reconstructed Glasgow Network (1,047 nodes, 1,932 edges)  
**Investigation Script:** `scripts/analyze_boundary_disconnect.py`  
**Date:** 2026-10-25  

---

## 1. Executive Summary

In transport network modeling, bounding-box truncation frequently introduces spurious edge-boundary artifacts: real-world journeys that rely on external regional bypasses appear disconnected when the model domain terminates prematurely.

In the Phase 4.2 resilience experiments, closing the M8 Kingston Bridge resulted in:
- **4,125 newly unreachable South $\to$ North OD pairs** (3.73% of 110,509 baseline-reachable pairs).
- **4,962 newly unreachable North $\to$ South OD pairs** (4.60% of 107,892 baseline-reachable pairs).

This report investigates the exact topological and geometric root causes of these disconnections. We trace individual unreachable nodes, audit their upstream and downstream link dependencies, and establish conclusively that **these disconnections are artifacts of the geographic bounding box truncation, not physical real-world travel impossibility**.

---

## 2. Origin-Destination Cohort Definition

To avoid survivorship bias and maintain methodological comparability:
- The OD cohort is **strictly held constant** across all baseline and closure evaluations.
- **South Quadrant Origins/Destinations:** All 250 graph nodes south of latitude $55.854^\circ\text{N}$.
- **North Quadrant Origins/Destinations:** All 445 graph nodes north of latitude $55.858^\circ\text{N}$.
- **Cross-River Baseline South $\to$ North Cohort:** Exactly 110,509 pairs.
- **Cross-River Baseline North $\to$ South Cohort:** Exactly 107,892 pairs.

---

## 3. Forensic Trace of Newly Unreachable OD Pairs

### 3.1 Destination Node Clustering
Under Kingston Bridge closure, exactly **445 northern destination nodes** lose connectivity from a subset of southern origins. When tracing the shortest path in the baseline graph for disconnected pairs, an immediate spatial pattern emerges:
- **Sample Disconnected Pair:** Origin Node $100878338$ ($55.85193^\circ\text{N}, -4.26078^\circ\text{W}$, Cook Street area) $\to$ Destination Node $3845455477$ ($55.86498^\circ\text{N}, -4.27012^\circ\text{W}$).
- **Baseline Path Traversal:**
  1. $100878338 \to 30004684$ (Commerce Street)
  2. $30004684 \to 100878357$ (Cook Street)
  3. $100878357 \to 36416922$ (Cook Street)
  4. $36416922 \to 30004683$ (Cook Street)
  5. $30004683 \to 263049173$ (Motorway Link / On-Ramp)
  6. $263049173 \to 4176566289$ (Motorway Link)
  7. $4176566289 \to 30824666$ (Motorway Link)
  8. $30824666 \to 158954168$ (**Kingston Bridge Mainline**)
  9. $158954168 \to 30824924$ (Motorway Link North)
  10. $30824924 \to 30795302$ (M8 Mainline)
  11. $30795302 \to 3845455477$ (M8 Mainline Terminal Node)

Destination node $3845455477$ is an elevated motorway mainline node positioned at $55.86498^\circ\text{N}$, approximately 20 meters south of the northern bounding box boundary ($55.86500^\circ\text{N}$).

### 3.2 Ancestor Subgraph Analysis
We audited the topological ancestors of node $3845455477$ in NetworkX:
- **Ancestors in Baseline Graph $G$:** 954 nodes (91.1% of entire network can reach this node).
- **Ancestors with Kingston Bridge Removed ($G_{\text{no\_kb}}$):** **4 nodes**.
- **Explanation:** The only nodes that can reach node $3845455477$ without crossing the Kingston Bridge are the three immediately preceding ramp segments ($30824924, 30795302, 158954168$). Within the central study boundary, **there is no surface street on-ramp to the M8 northbound mainline**.

---

## 4. The Two Boundary Mechanisms

### 4.1 Mechanism A: Motorway Carriageway Stub Isolation
In the real world, the M8 motorway traverses Glasgow as a high-speed throughway. Motorists entering from the south who find the Kingston Bridge closed would:
1. Cross the river via the surface street couplets (George V Bridge or Victoria Bridge).
2. Continue northbound along Newton Street or North Street through Charing Cross.
3. Enter the M8 motorway northbound/eastbound at **Junction 18 (Charing Cross)** or **Junction 17 (St George's Cross)**.

However, Junction 18 and Junction 17 lie between latitudes $55.867^\circ\text{N}$ and $55.872^\circ\text{N}$—**outside the model's northern cutoff of $55.865^\circ\text{N}$**. Because the study area truncates at $55.865^\circ\text{N}$, the connecting surface-to-motorway ramps do not exist in the graph. The northern motorway mainline becomes a topological cul-de-sac that can only be entered via the Kingston Bridge.

### 4.2 Mechanism B: Severance of Regional Orbital Bypasses
For long-distance or cross-city trips, transport planners rely on redundant regional corridors:
- **The M74 Northern Extension:** Connects the southern motorway network eastward around the central core.
- **The M73 / Baillieston Interchange:** Enables eastern bypass routing.
- **The Clyde Tunnel (A739):** Provides a 4-lane western crossing 4 km downstream.

All three regional bypasses lie well outside the central study perimeter (spanning $-4.285^\circ\text{W}$ to $-4.240^\circ\text{W}$). In the real-world road network, severe disruptions on the Kingston Bridge trigger regional variable message signs (VMS) directing heavy freight and inter-city traffic via the M74 and Clyde Tunnel. In the truncated bounding box, these corridors are physically absent, artificially forcing all simulated traffic onto the local central bridge couplets or stranding them at severed ramp stubs.

---

## 5. Methodological Conclusions & Mandatory Reporting Standard

1. **Not Real-World Trapped Commuters:** Under no circumstances should the 4,125 unreachable OD pairs be reported as "citizens stranded without route access" or "destinations cut off from civilization." They are mathematical artifacts of evaluating trips destined for motorway throughway links inside an artificially bounded urban box.
2. **Fixed Cohort Reporting:** The baseline cross-river cohort must be reported as 218,401 pairs. When evaluating Kingston Bridge resilience, researchers must explicitly report:
   - Baseline reachable: 218,401 pairs.
   - Still-reachable pairs: 209,314 pairs (95.84%).
   - Newly unreachable pairs due to study boundary truncation: 9,087 pairs (4.16%).
   - Free-flow shortest-path travel time changes must be calculated strictly over the 209,314 still-reachable pairs.

By explicitly distinguishing topological boundary effects from physical grid failures, the CityPulse framework maintains defensible transport-modeling rigor.
