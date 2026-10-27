# Methodology Risks and Assumption Stress-Testing: CITYPULSE

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026 (Updated with Phase 2 Gate Boundaries)  
**Primary Project Directory:** `./`  
**Document Purpose:** Systematic scientific audit of core methodology assumptions, identification of modeling vulnerabilities, and definition of necessary remediations.

---

## 1. Overview of Methodology Risks & Gate Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       METHODOLOGY RISK AUDIT MATRIX                         │
├────┬─────────────────────────────┬─────────────────┬────────────────────────┤
│ ID │ Scientific Assumption       │ Severity / Risk │ Phase 2 Gate Status    │
├────┼─────────────────────────────┼─────────────────┼────────────────────────┤
│ A  │ Synthetic Sensor Faults     │ HIGH            │ BOUNDED TO SYNTHETIC   │
│    │ as Ground Truth             │                 │ LABELS (Gate 5)        │
├────┼─────────────────────────────┼─────────────────┼────────────────────────┤
│ B  │ Real-World Traffic Incident │ CRITICAL        │ REAL-WORLD CLAIMS      │
│    │ Detection                   │                 │ DISCLAIMED (Gate 5)    │
├────┼─────────────────────────────┼─────────────────┼────────────────────────┤
│ C  │ BPR Travel Times from       │ HIGH            │ REDESIGNED TO ACCESSI- │
│    │ SCOOT Volume Alone          │                 │ BILITY PROXY (Gate 4)  │
├────┼─────────────────────────────┼─────────────────┼────────────────────────┤
│ D  │ Sensor-to-Road Segment      │ MEDIUM-HIGH     │ CANDIDATE WORKFLOW     │
│    │ Snapping Fidelity           │                 │ IMPLEMENTED (Gate 3)   │
├────┼─────────────────────────────┼─────────────────┼────────────────────────┤
│ E  │ Population Zones as         │ MEDIUM          │ LABELED AS CONNECTIVITY│
│    │ Observed OD Demand          │                 │ PROXY (Gate 4)         │
├────┼─────────────────────────────┼─────────────────┼────────────────────────┤
│ F  │ Bridge Closures as Single   │ HIGH            │ MULTI-EDGE CORRIDOR    │
│    │ Graph Edge Deletions        │                 │ SETS REMOVED (Gate 4)  │
├────┼─────────────────────────────┼─────────────────┼────────────────────────┤
│ G  │ Linear Product Metric       │ HIGH            │ NORMALIZED EXPONENTIAL │
│    │ for Observability Deficit   │                 │ RISK INDEX (Gate 1)    │
└────┴─────────────────────────────┴─────────────────┴────────────────────────┘
```

---

## 2. Detailed Assumption Inquiries & Remediations

### A. Synthetic Sensor Faults vs. Physical Hardware Reality
* **Investigation:** Synthetic perturbations (MCAR dropouts, contiguous burst outages, calibration offset drift, frozen readings) generate mathematically unambiguous labels. However, they cannot establish validation against complex, unmodeled physical degradation modes (such as grounding loops, thermal expansion, moisture ingress in pavement sawcuts).
* **Bound Enforced (Gate 5):** All synthetic experiments are explicitly labeled as **"Controlled Synthetic Degradation Benchmarks"**. Claims are restricted to algorithm sensitivity against specified perturbation functions.

### B. Lack of Independent Ground Truth for Real-World Traffic Incidents
* **Investigation:** The Glasgow SCOOT dataset contains no police accident logs, highway dispatch logs, or roadwork notices. Any unperturbed volume drop could be an accident, weather-induced slowdown, sporting event diversion, or detector glitch.
* **Bound Enforced (Gate 5):** **Zero claims of validated real-world incident detection.** Anomalies in raw data are designated strictly as *"Statistical Flow Anomalies"*. The previous metric "Hardware Fault vs. Traffic Incident Disambiguation Rate" is formally removed and replaced with a spatial consistency filter benchmark.

### C. SCOOT Counts Alone Do Not Yield Travel Times (Gate 4 Resolution)
* **Investigation:** SCOOT data contains volume ($q$, veh/hr), but lacks observed speeds ($v$) and link travel times ($t$). Inverting the parabolic fundamental diagram is impossible from volume alone without occupancy. Standard BPR parameters ($\alpha, \beta$) cannot be calibrated empirically.
* **Bound Enforced (Gate 4):** Model inputs are anchored in UK WebTAG and DMRB standards ($C_e = \text{lanes} \times C_{\text{lane}}$, $t_e^0 = L_e / v_e^{\text{max}}$). The primary outcome is explicitly redesigned as a **Model-Based Accessibility Impedance Proxy** ($\Delta \mathcal{C}$), disclaiming real-world travel time measurement.

### D. Sensor-to-Road Snapping (Gate 3 Resolution)
* **Investigation:** 470 detectors represent only 195 junctions. Naive snapping collapses opposing approach legs onto the same directed edge.
* **Bound Enforced (Gate 3):** Implemented a non-forcing candidate matcher in `citypulse.map.matcher`. Snaps are classified as `MATCHED_HIGH`, `MATCHED_MEDIUM`, `AMBIGUOUS_MULTI_CANDIDATE`, or `UNMATCHED_DISTANCE_EXCEEDED`. Equidistant crossroads and multi-detector conflicts are flagged for review.

### E. Origin-Destination Demand (Gate 4 Resolution)
* **Investigation:** Scottish census zones give static residential counts, not time-stamped vehicle trips.
* **Bound Enforced (Gate 4):** Origin-destination trip matrices are explicitly declared as a **Synthetic Accessibility Demand Proxy** ($W_{od} = 1 / d_{od}^\gamma$ across network centroids), evaluating structural connectivity rather than actual commuting volumes.

### F. Multi-Edge River Crossing Closures (Gate 4 Resolution)
* **Investigation:** Major bridges (e.g., M8 Kingston Bridge, Clyde Arc) consist of multiple directed carriageways, on-ramps, and off-ramps. Single-edge deletion leaves opposing lanes and ramps floating.
* **Bound Enforced (Gate 4):** Closures are defined as multi-edge corridor sets (e.g., removing `M8_KINGSTON_NB_1`, `M8_KINGSTON_SB_1`, and access slips simultaneously). Disconnected OD pairs are penalized with a finite 1-hour impedance penalty ($M_{\text{disconnect}} = 3,600\text{s}$) rather than discarded.

### G. Dimensional Inconsistency of Observability Metrics
* **Investigation:** The product $VOD = NRI \cdot \text{dist}$ yields meaningless physical units ($hours \times meters$) and introduces extreme sensitivity to remote peripheral edges.
* **Bound Enforced (Gate 1):** Replaced with a dimensionless Observability Risk Index $\Omega_e = \widehat{NRI}(e) \cdot [1 - \exp(-\text{dist} / 500\text{m})]$, ensuring strict non-dimensionalization in $[0, 1]$.
