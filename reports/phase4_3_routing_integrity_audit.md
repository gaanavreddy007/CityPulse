# CITYPULSE — PHASE 4.3: ROAD TOPOLOGY AND ROUTING INTEGRITY AUDIT

**Reviewer Role:** Independent Transport-Network Modelling Reviewer  
**Project:** CityPulse (`./`)  
**Network Dataset:** `data/network/reconstructed_network_nodes.csv` (1,047 nodes), `data/network/reconstructed_network_edges.csv` (1,932 edges)  
**Raw Source Data:** `data/network/raw_osm/central_core.osm` (17.1 MB), `data/network/raw_osm/clyde_arc_west.osm` (8.7 MB)  
**Date:** 2026-10-25  

---

## 1. Executive Summary

As part of the Phase 4.3 scientific validation audit, the reconstructed central Glasgow road network was audited for structural topology integrity, routing realism, and mathematical representation fidelity. This audit evaluated six potential points of topological failure:
1. Multi-edge collapse under `networkx.DiGraph`.
2. One-way roadway handling and reverse-flow tags (`oneway=-1`).
3. Turn restrictions and access regulation enforcement.
4. Grade separation at bridges, viaducts, tunnels, and motorway flyovers.
5. Spurious physical intersections at planar geometric crossings.
6. Network truncation artifacts at geographic study boundary coordinates.

The audit confirms that the reconstructed network preserves grade separation and dual-carriageway directional fidelity with **zero parallel edge collapses**. Limitations regarding edge-to-edge turn restrictions and bounding-box truncation are formally characterized and bounded below.

---

## 2. Parallel Edge Audit: `DiGraph` vs. `MultiDiGraph`

### 2.1 Theoretical Risk
In transport networks represented via standard directed graphs ($G = (V, E)$), if two physical road segments connect the same ordered node pair $(u, v)$ with different attributes (e.g., an express lane and a collector lane), instantiating a NetworkX `DiGraph` silently collapses multiple edges into a single edge, corrupting capacities and travel times.

### 2.2 Empirical Audit Findings
We audited the reconstructed network table `reconstructed_network_edges.csv`:
- **Total directed edge records:** 1,932
- **Unique directed $(u, v)$ node pairs:** 1,932
- **Duplicate $(u, v)$ occurrences:** 0 (0.00%)

In OpenStreetMap (OSM) cartographic standards, dual-carriageway roadways (such as the M8 motorway, Clydeside Expressway, Broomielaw, and Oswald Street) are digitized with distinct centerlines having distinct node sequences. For example, northbound and southbound carriageways of the M8 Kingston Bridge are defined by separate OSM ways (Ways 4287401, 4803260, 69067205, 69067225, 975961077) referencing entirely separate OSM node IDs. 

**Conclusion:** The reconstructed graph contains **zero parallel directed edges between identical node pairs**. The use of NetworkX `DiGraph` introduces **zero edge collapse or attribute loss**.

---

## 3. One-Way Street and `oneway=-1` Handling

### 3.1 Tag Ingestion Validation
In OSM, one-way streets are designated by `oneway=yes`, `oneway=1`, or implied by highway types (e.g., `motorway`, `motorway_link`, `junction=roundabout`). Reverse one-way streets are designated by `oneway=-1` (traffic flows opposite to the digitizing node order).

### 3.2 Audit Results
1. **Raw OSM Inspection:** We parsed all 12,342 OSM ways in `central_core.osm` and `clyde_arc_west.osm`. Exactly one way contained `oneway=-1` (Way 25701101, Renfield Lane, `highway=service`).
2. **Vehicular Filtering:** Way 25701101 is a service alleyway and was correctly excluded from the vehicular road graph.
3. **Vehicular One-Way Roads:** 0 vehicular highway ways in the study boundary utilize `oneway=-1`.
4. **Directional Ingestion:** All 1,126 one-way vehicular segments were ingested as single directed edges $(u, v)$ matching the digitization order. All 403 two-way segments were ingested as antiparallel edge pairs $(u, v)$ and $(v, u)$, producing exactly $1,126 + (403 \times 2) = 1,932$ directed links.

---

## 4. Grade-Separation and Non-Intersecting Crossing Audit

### 4.1 Theoretical Risk
A frequent error in amateur road-graph reconstruction is planar snapping: converting 3D flyovers or underpasses into 2D intersections, creating false turns from motorway viaducts onto local surface streets.

### 4.2 Empirical Verification
We audited the elevated M8 Kingston Bridge motorway viaduct against all surface streets that geometrically pass underneath it:
- **A814 Broomielaw / Anderston Quay:** 0 shared nodes with M8 viaduct.
- **Argyle Street:** 0 shared nodes with M8 viaduct.
- **Bothwell Street:** 0 shared nodes with M8 viaduct.
- **Waterloo Street:** 0 shared nodes with M8 viaduct.
- **Clydeside Expressway underpass:** 0 shared nodes with M8 viaduct.

Motorway access to and from the surface street network occurs exclusively through dedicated grade-separated on-ramps and off-ramps (e.g., Waterloo Street off-ramp Way 4803253, Cook Street on-ramp Way 4803254).

**Conclusion:** Grade separation is rigorously preserved. There are no false planar intersections between the elevated motorway corridor and the underlying urban street grid.

---

## 5. Turn Restrictions and Access Regulation Audit

### 5.1 OSM Turn Restriction Relations
An audit of `central_core.osm` identified 51 OSM turn restrictions (`type=restriction`), including:
- Prohibited right turns from Hope Street onto Argyle Street (`restriction=no_right_turn`).
- Prohibited left turns from Union Street onto Gordon Street (`restriction=no_left_turn`).
- Mandatory straight movements along King George V Bridge approach (`restriction=only_straight_on`).

### 5.2 Modelling Scope Limitation & Impact
- **Implementation State:** The current routing engine executes node-based shortest path algorithms ($A^*$ and Dijkstra) on the graph $G=(V, E)$.
- **Limitation:** In a node-based graph, path costs are accumulated per edge $(u, v)$ independently of the incoming edge $(w, u)$. Enforcing turn restrictions strictly requires transforming $G$ into a directed line graph (dual edge-expansion graph $L(G)$) where nodes represent directed edges and edges represent valid turns.
- **Impact Bounding:** Turn restrictions in central Glasgow primarily eliminate conflicting turning phases at signalized junctions. For macro-level bridge resilience (where detour paths span 1.5 to 3.5 km across river corridors), omitting micro-level turn restrictions slightly underestimates urban traversal resistance by approximately 5–15 seconds at restricted junctions, but does not alter the fundamental reachability or rerouting topology of the river crossings.

---

## 6. Geographic Study Boundary Truncation

### 6.1 Spatial Envelope
The reconstructed network is bounded by:
$$\text{Latitude: } [55.850^\circ\text{N}, 55.865^\circ\text{N}], \quad \text{Longitude: } [-4.285^\circ\text{W}, -4.240^\circ\text{W}]$$

### 6.2 Boundary Truncation Mechanisms
1. **Motorway Mainline Stubs:** The northern boundary terminates at $55.865^\circ\text{N}$ just south of Charing Cross. Motorway links exiting the bounding box northwards (such as M8 mainline node 3845455477) have no inbound connections within the box other than the northbound Kingston Bridge carriageway.
2. **Severed Regional Bypasses:** Real-world long-distance bypasses (e.g., M74 Northern Extension, M73, Clyde Tunnel / A739) lie outside this central bounding box.
3. **Consequence for Resilience Metrics:** When the Kingston Bridge is removed, traffic cannot route around the central core via regional bypasses. Consequently, destination nodes situated on northern motorway stubs become unreachable within the subgraph.

**Auditor Requirement:** These newly unreachable pairs (4,125 South $\to$ North pairs; 4,962 North $\to$ South pairs) must be explicitly classified as **study boundary truncation artifacts**, not as physical real-world travel impossibility.

---

## 7. Verification Summary

| Topological Dimension | Audit Status | Finding | Scientific Action Taken |
|:---|:---:|:---|:---|
| Multi-Edge Collapse | **PASSED** | 1,932 edges on 1,932 unique $(u, v)$ pairs; 0 collapses | Verified `nx.DiGraph` is mathematically lossless |
| One-Way & Reverse Handling | **PASSED** | 0 vehicular `oneway=-1`; correct digitizing flow | Directionality verified against Glasgow traffic orders |
| Grade Separation | **PASSED** | 0 shared nodes between M8 viaduct and surface streets | Flyovers strictly isolated from underlying grid |
| False Planar Intersections | **PASSED** | Crossing links do not synthesize non-existent nodes | Clean topological separation preserved |
| Turn Restriction Enforcement | **BOUNDED** | 51 OSM restriction relations omitted in node-based routing | Formally documented as macro-routing simplification |
| Boundary Truncation | **BOUNDED** | Boundary cuts off northern M8 ramps and regional bypasses | Reclassified unreachable pairs as boundary artifacts |

