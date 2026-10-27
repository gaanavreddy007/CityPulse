# Resilience Uncertainty Propagation Design Note: CITYPULSE

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `./`  
**Document Status:** **METHODOLOGY DESIGN GATE (DECOUPLED FROM PHASE 3 BENCHMARK)**  

---

## 1. Executive Summary and Anti-Overclaiming Guardrail

A fundamental failure mode in urban traffic research is blindly feeding machine-learning predictions or anomaly scores into a traffic simulation model and describing the resulting spreads as "validated travel-time uncertainty."

In accordance with Phase 3 Gate 6, CITYPULSE **deliberately decouples** anomaly benchmark evaluation from road-network resilience propagation. This design document establishes the exact mathematical formulation, parameter taxonomy, and sensitivity protocols required before end-to-end coupling can be scientifically defended in Phase 4.

---

## 2. Rigorous Parameter and Input Taxonomy

To prevent conflation between empirical measurements and modeling assumptions, every quantity is categorized into a three-tier taxonomy:

### Table 1: Scientific Parameter Taxonomy

| Quantity | Symbol | Source / Provenance | Status in Model |
| :--- | :--- | :--- | :--- |
| **Monitored Link Flow Volume** | $y_e(t)$ | Glasgow SCOOT inductive loop counts | **Empirically Measured** (veh/hr, integer resolution) |
| **Link Geodesic Length** | $L_e$ | OpenStreetMap / WGS84 node distances | **Empirically Measured / Spatial** (meters) |
| **Sensor Measurement Residuals** | $\sigma_{\text{sensor}}$ | Historical MAD / residual variance from seasonal baseline | **Empirically Estimated Variance** |
| **Imputation Uncertainty** | $\sigma_{\text{impute}}$ | Ensemble variance from historical seasonal distribution | **Modeled Estimation Variance** |
| **Link Capacity** | $C_e$ | UK DfT WebTAG / DMRB design capacities ($1800$ veh/hr/lane motorway, $900$ primary, $600$ secondary) | **Engineering Norm / Assumed** |
| **Free-Flow Speed** | $v_{0,e}$ | UK urban speed limits ($22.2$ m/s motorway, $13.4$ m/s primary, $8.9$ m/s secondary) | **Engineering Norm / Assumed** |
| **Volume-Delay Curvature** | $\alpha, \beta$ | Bureau of Public Roads (BPR) formulation ($\alpha = 0.20, \beta = 2.0$) | **Assumed Parameter** |
| **Network Disconnection Penalty** | $M$ | Finite upper-bound penalty for severed OD pairs ($M = 3,600\text{ s} = 1\text{ h}$) | **Scenario Parameter** |
| **Bridge Corridor Closure** | $\mathcal{E}_{\text{closed}}$ | Multi-edge corridor removal (e.g., M8 Kingston Bridge 4-edge set) | **Hypothetical Scenario Definition** |

---

## 3. Mathematical Formulation of Uncertain Edge Impedance

The primary outcome of the road network model is the **Model-Based Accessibility Impedance Proxy ($\Delta \mathcal{C}$)**.

### 3.1 Edge Impedance Function
For road link $e$ with flow $y_e$, free-flow time $t_{0,e} = L_e / v_{0,e}$, and capacity $C_e$:
$$\tau_e(y_e) = t_{0,e} \left[1 + \alpha \left(\frac{y_e}{C_e}\right)^\beta\right]$$

### 3.2 Propagation of Flow Uncertainty
Under sensor noise, missingness imputation, or undetected calibration drift, the true link flow $y_e$ is an uncertain random variable:
$$y_e \sim \mathcal{D}\left(\hat{y}_e, \sigma_e^2\right)$$
Where:
$$\sigma_e^2 = \begin{cases} 
\sigma_{\text{sensor}, e}^2 & \text{if observation is valid and unflagged} \\
\sigma_{\text{impute}, e}^2 & \text{if observation was missing and imputed} \\
\sigma_{\text{drift}, e}^2 & \text{if sensor is in a state of undetected calibration drift}
\end{cases}$$

Because the BPR function $\tau_e(y_e)$ is nonlinear (convex polynomial of degree $\beta = 2$), by Jensen's inequality:
$$\mathbb{E}[\tau_e(y_e)] \ge \tau_e(\mathbb{E}[y_e])$$
Flow uncertainty increases expected travel impedance even when mean flow is unbiased.

### 3.3 Network-Wide Impedance Cost Proxy
Across all origin-destination pairs $(u, v) \in \mathcal{OD}$:
$$\mathcal{C}(\mathbf{y}) = \sum_{(u, v) \in \mathcal{OD}} \min_{\mathcal{P}_{uv}} \sum_{e \in \mathcal{P}_{uv}} \tau_e(y_e)$$
When a bridge closure disconnects an OD pair ($\mathcal{P}_{uv} = \emptyset$), the finite penalty $M$ is applied.

The resilience impact delta under closure scenario $k$ is:
$$\Delta \mathcal{C}_k = \mathcal{C}(\mathbf{y} \mid \mathcal{E}_{\text{closed}}) - \mathcal{C}(\mathbf{y} \mid \text{baseline})$$

---

## 4. Monte Carlo Evaluation Protocol (Planned Phase 4 Architecture)

When end-to-end coupling is executed in Phase 4, the uncertainty in $\Delta \mathcal{C}_k$ must be generated via a structured Monte Carlo ensemble:

```
                  HISTORICAL RESIDUAL VARIANCE
                  IMPUTATION POSTERIOR ENSEMBLE
                                │
                                ▼
        ┌────────────────────────────────────────────────┐
        │        MONTE CARLO FLOW DRAWS (M = 100)        │
        │ y_e^{(m)} ~ N(y_hat_e, sigma_e^2)              │
        └───────────────────────┬────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────┐
        │          NETWORK IMPEDANCE COMPUTATION         │
        │ Dijkstra All-Pairs Shortest Paths on Graph G   │
        └───────────────────────┬────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
      [Baseline Impedance]            [Closure Impedance]
        C^{(m)}(baseline)            C^{(m)}(closure_k)
                │                               │
                └───────────────┬───────────────┘
                                ▼
              IMPACT DELTA: Delta C_k^{(m)}
                                │
                                ▼
        [Compute 95% Credible Interval & Sensitivity Indices]
```

### Protocol Standards:
1. **Ensemble Size:** $M = 100$ draws per evaluation window.
2. **Reporting Metrics:** Report the median impact delta and the empirical 2.5th and 97.5th percentiles:
   $$\Delta \mathcal{C}_k \in \left[\Delta \mathcal{C}_{k, 2.5\%}, \; \Delta \mathcal{C}_{k, 97.5\%}\right]$$
3. **Sensitivity Decomposition:** Conduct One-At-A-Time (OAT) parameter variation:
   - Vary $\alpha \in [0.15, 0.25]$ ($\pm 25\%$).
   - Vary $\beta \in [1.5, 3.0]$.
   - Vary $C_e \in [0.8 C_e, 1.2 C_e]$ ($\pm 20\%$).
   - Record the percentage of total variance attributable to sensor flow uncertainty versus capacity assumptions.

---

## 5. Explicit Limitations and Scope Boundaries

1. **Static Flow Proxy vs. Dynamic Traffic Assignment:**
   This formulation does not simulate micro-level dynamic queue spillback, signal phase splits, or lane changing. It provides a macro-level structural accessibility proxy.
2. **Trip Demand Matrix:**
   Central Glasgow OD matrices are not publicly published by Glasgow City Council. Equal OD weighting or distance-decay gravitational weighting will be evaluated as a sensitivity scenario.
3. **Decoupled Milestone Decision:**
   Because Phase 3 is dedicated to rigorous baseline anomaly detection and empirical validation, resilience simulation coupling is designated for **Phase 4**.
