# CITYPULSE Phase 4: Observability Risk Index Methodology & Results

## 1. Executive Summary

This report defines the mathematical formulation, formal proofs, and empirical evaluation of the **Observability Risk Index** ($\Omega_e$) for the 21 directed edges in the River Clyde Central Crossing Corridor graph.

Transportation networks often contain critical bottleneck segments that carry enormous traffic loads or serve as vital detour paths during disruptions, yet lack direct sensor instrumentation. The Observability Risk Index couples an edge's **systemic network criticality** (measured via the Network Robustness Index, $NRI$) with its **spatial sensor unobservability** (governed by its physical distance to the nearest reliable SCOOT detector).

### Key Empirical Findings:
1. **Critical Blind Spot Identified:** The single highest-risk road segment in the central Glasgow corridor is **`BROOMIELAW_A814`** ($\Omega_e = \mathbf{0.5766}$), followed by **`ARGYLE_ST_WB`** ($\Omega_e = \mathbf{0.2021}$).
   - Broomielaw is a 4-lane primary arterial that acts as the primary East-West relief corridor along the north bank of the Clyde. If severed, it causes the highest system-wide impedance surge ($\Delta \mathcal{C} = 7,125.37\text{s}$), yet its midpoint is **429.7 meters** from the nearest high-confidence detector, yielding an unobservability factor of $0.5766$.
2. **Well-Instrumented Motorway Crossings:** In contrast, the M8 Kingston Bridge carriageways (`M8_KINGSTON_SB_1` and `M8_KINGSTON_NB_1`) exhibit very low observability risk ($\Omega_e = \mathbf{0.0039}$ and $\mathbf{0.0038}$), despite their high traffic capacity, because they have direct SCOOT sensors located within 262–265 meters and normalized $NRI$ values near baseline in the single-edge closure ranking.
3. **Mathematical Rigor:** The index is strictly bounded within $[0, 1]$, non-decreasing with distance, vanishes at zero distance, and is completely scale-invariant.

---

## 2. Mathematical Formulation

### 2.1 Network Robustness Index (NRI)
For a road graph $G = (V, E)$, the systemic criticality of edge $e \in E$ is quantified by the Network Robustness Index ($NRI$), defined as the increase in total network-wide accessibility cost when edge $e$ is removed from the network:
$$NRI(e) = \mathcal{C}(G \setminus \{e\}) - \mathcal{C}(G)$$
where $\mathcal{C}(G)$ is the sum of shortest-path accessibility costs across all origin-destination pairs:
$$\mathcal{C}(G) = \sum_{u \in V} \sum_{v \in V,\, v \neq u} d_G(u, v)$$
with disconnected pairs penalized at $M = 3,600\text{s}$.

To ensure scale invariance, raw $NRI$ is min-max normalized across all edges in the network:
$$\widehat{NRI}(e) = \frac{NRI(e) - \min_{e' \in E} NRI(e')}{\max_{e' \in E} NRI(e') - \min_{e' \in E} NRI(e')}$$
If all edges have identical $NRI$, $\widehat{NRI}(e) \equiv 1.0$. By definition, $\widehat{NRI}(e) \in [0, 1]$.

### 2.2 Geodetic Spatial Distance
For edge $e$ with midpoint coordinates $(\text{lat}_e, \text{lon}_e)$ and candidate sensors $S$, the distance $\text{dist}_e$ is the minimum great-circle geodetic distance to any high-confidence detector $s \in S$, computed via the Haversine formula:
$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_e)\cos(\phi_s)\sin^2\left(\frac{\Delta \lambda}{2}\right)$$
$$\text{dist}_e = 2 R \cdot \arcsin\left(\sqrt{a}\right)$$
where $R \approx 6,371,000\text{ meters}$, $\phi = \frac{\pi \cdot \text{lat}}{180}$, and $\lambda = \frac{\pi \cdot \text{lon}}{180}$.

### 2.3 The Unobservability Factor & Index Definition
The physical unobservability factor $U(e)$ models the decay of sensor visibility over space using a characteristic correlation length scale $D_0 = 500.0\text{ meters}$:
$$U(e) = 1 - \exp\left(-\frac{\text{dist}_e}{D_0}\right)$$

The **Observability Risk Index** $\Omega_e$ is the product of systemic network criticality and spatial unobservability:
$$\Omega_e = \widehat{NRI}(e) \cdot \left[1 - \exp\left(-\frac{\text{dist}_e}{D_0}\right)\right]$$

---

## 3. Mathematical Properties & Proofs

### Property 1: Bounded Range
**Claim:** $\forall e \in E, \quad \Omega_e \in [0, 1]$.
- *Proof:* By construction, $\widehat{NRI}(e) \in [0, 1]$. For physical distance $\text{dist}_e \ge 0$ and $D_0 > 0$, the ratio $\frac{\text{dist}_e}{D_0} \ge 0$. Since the exponential function satisfies $\exp(-x) \in (0, 1]$ for $x \ge 0$, it follows that $1 - \exp(-\text{dist}_e / D_0) \in [0, 1)$. The product of two values in $[0, 1]$ is strictly contained in $[0, 1]$. $\blacksquare$

### Property 2: Zero-Distance Limit (Perfect Observability)
**Claim:** $\lim_{\text{dist}_e \to 0} \Omega_e = 0$.
- *Proof:* As $\text{dist}_e \to 0$, $\exp(-\text{dist}_e / D_0) \to \exp(0) = 1$. Thus, $U(e) \to 1 - 1 = 0$. Consequently, $\Omega_e = \widehat{NRI}(e) \times 0 = 0$. An edge with a co-located sensor has zero unobservability risk regardless of its criticality. $\blacksquare$

### Property 3: Monotonicity with Distance
**Claim:** For any edge with positive criticality ($\widehat{NRI}(e) > 0$), $\Omega_e$ is strictly monotonically increasing with distance $\text{dist}_e$.
- *Proof:* Differentiating $\Omega_e$ with respect to $\text{dist}_e$:
  $$\frac{\partial \Omega_e}{\partial \text{dist}_e} = \widehat{NRI}(e) \cdot \frac{1}{D_0} \exp\left(-\frac{\text{dist}_e}{D_0}\right)$$
  Since $D_0 > 0$, $\exp(-x) > 0$ for all real $x$, and $\widehat{NRI}(e) > 0$, the derivative is strictly positive ($\frac{\partial \Omega_e}{\partial \text{dist}_e} > 0$). $\blacksquare$

### Property 4: Saturation Limit (Infinite Unobservability)
**Claim:** $\lim_{\text{dist}_e \to \infty} \Omega_e = \widehat{NRI}(e)$.
- *Proof:* As $\text{dist}_e \to \infty$, $\exp(-\text{dist}_e / D_0) \to 0$, so $U(e) \to 1$. Thus, the observability risk approaches the full normalized network criticality of the edge. $\blacksquare$

---

## 4. Empirical Evaluation across the Clyde Crossing Corridor

The 21 directed edges of the River Clyde Central Crossing Corridor graph were evaluated using `scripts/run_resilience_experiments.py`. The complete results, ranked by descending Observability Risk Index ($\Omega_e$), are detailed below:

| Edge ID | Name | Road Class | Lanes | Raw NRI (s) | Normalized $\widehat{NRI}$ | Dist to Sensor (m) | Unobservability $U(e)$ | Observability Risk $\Omega_e$ |
|---|---|---|---|---|---|---|---|---|
| **`BROOMIELAW_A814`** | Broomielaw (A814) | primary | 4 | 7,125.37 | 1.0000 | 429.7 | 0.5766 | **0.5766** |
| **`ARGYLE_ST_WB`** | Argyle Street | secondary | 2 | 7,087.64 | 0.9895 | 114.2 | 0.2043 | **0.2021** |
| `CLYDESIDE_EXPRESSWAY_WB` | Clydeside Expressway (A814 WB) | trunk | 3 | 3,571.91 | 0.0078 | 659.5 | 0.7326 | 0.0057 |
| `M8_RAMP_BROOMIELAW_OFF` | M8 Off-Ramp to Broomielaw | motorway_link | 2 | 3,577.48 | 0.0094 | 376.4 | 0.5290 | 0.0050 |
| `ALBERT_BRIDGE_NB` | Albert Bridge | primary | 2 | 3,562.69 | 0.0053 | 914.0 | 0.8393 | 0.0044 |
| `VICTORIA_BRIDGE_SB` | Victoria Bridge | primary | 2 | 3,562.69 | 0.0053 | 657.6 | 0.7316 | 0.0039 |
| `M8_KINGSTON_SB_1` | M8 Kingston Bridge (Southbound) | motorway | 5 | 3,577.48 | 0.0094 | 264.6 | 0.4109 | 0.0039 |
| `M8_KINGSTON_NB_1` | M8 Kingston Bridge (Northbound) | motorway | 5 | 3,577.48 | 0.0094 | 262.4 | 0.4084 | 0.0038 |
| `M8_RAMP_ANDERSTON_ON` | M8 On-Ramp from Anderston/North St | motorway_link | 2 | 3,577.48 | 0.0094 | 251.4 | 0.3952 | 0.0037 |
| `GEORGE_V_BRIDGE_SB` | George V Bridge | primary | 3 | 3,562.69 | 0.0053 | 161.8 | 0.2764 | 0.0015 |
| `NORTH_ST_A804_SB` | North Street (A804) | primary | 3 | 3,562.69 | 0.0053 | 107.7 | 0.1938 | 0.0010 |
| `GLASGOW_BRIDGE_NB` | Glasgow Bridge (Jamaica Bridge) | primary | 4 | 3,562.69 | 0.0053 | 101.3 | 0.1834 | 0.0010 |
| `HOPE_ST_NB` | Hope Street | primary | 2 | 3,562.69 | 0.0053 | 107.9 | 0.1942 | 0.0010 |
| `NEWTON_ST_A804_NB` | Newton Street (A804) | primary | 3 | 3,562.69 | 0.0053 | 39.7 | 0.0763 | 0.0004 |
| `CLYDE_ARC_NB` | Clyde Arc (Squinty Bridge NB) | secondary | 2 | 3,543.82 | 0.0000 | 73.6 | 0.1369 | 0.0000 |
| `CLYDE_ARC_SB` | Clyde Arc (Squinty Bridge SB) | secondary | 2 | 3,543.82 | 0.0000 | 73.6 | 0.1369 | 0.0000 |
| `ST_VINCENT_ST_WB` | St Vincent Street (Westbound) | secondary | 2 | 3,543.82 | 0.0000 | 83.7 | 0.1541 | 0.0000 |
| `ST_VINCENT_ST_EB` | St Vincent Street (Eastbound) | secondary | 2 | 3,543.82 | 0.0000 | 104.1 | 0.1880 | 0.0000 |
| `BOTHWELL_ST` | Bothwell Street | secondary | 2 | 3,543.82 | 0.0000 | 277.8 | 0.4263 | 0.0000 |
| `WATERLOO_ST` | Waterloo Street | secondary | 2 | 3,543.82 | 0.0000 | 268.0 | 0.4149 | 0.0000 |

---

## 5. Transportation Planning Implications

### 5.1 The Broomielaw Risk Exposure
The ranking exposes a major structural vulnerability in Glasgow's traffic sensing infrastructure:
- **`BROOMIELAW_A814`** carries critical multi-lane arterial flows channeling vehicles from Glasgow City Centre westward to the SEC, Hydro, and Clydeside Expressway. 
- Because raw $NRI$ is highest here ($7,125.37\text{s}$), any failure or unobserved incident on Broomielaw causes massive rerouting congestion.
- With the nearest sensor situated nearly half a kilometer away ($429.7\text{m}$), urban traffic controllers have almost no real-time automated visibility into flow deterioration on this link.

### 5.2 Sensor Placement Recommendations
The Observability Risk Index provides an objective, data-driven methodology for municipal capital investment:
1. **Priority 1 (Urgent):** Install an inductive loop detector or virtual camera sensor on the A814 Broomielaw between Oswald Street and Kingston Bridge approach. This would drop $\text{dist}_e$ from $429.7\text{m}$ to $< 50\text{m}$, reducing $\Omega_e$ from $0.5766$ to $< 0.09$.
2. **Priority 2:** Add sensor coverage along Argyle Street westbound to secure city-centre bus and commercial delivery corridors.
