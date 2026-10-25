# CITYPULSE Phase 4.2: Road Network Data Source & Provenance Audit

**Project:** `C:\Gaanav\Projects\CityPulse`  
**Milestone:** Phase 4.2 (Gate 1 Audit)  
**Author:** Transport-Network Data Scientist & Graph Engineer  
**Date:** October 2026  
**Status:** **GATE 1 COMPLETE — DEFECT AUDITED & REMEDIATION SOURCE IDENTIFIED**

---

## 1. Executive Summary

This audit investigates the source data, geometry, coordinate reference system, and topological representation of the existing road-edge dataset (`data/network/glasgow_network_edges.csv`) used during Phases 2, 3, and 4.

The Phase 4.1 independent scientific review identified a catastrophic structural defect: **98.44% of origin-destination (OD) pairs are topologically disconnected in baseline conditions before any disruption is introduced.**

This audit confirms that the defect stems from the foundational design of `glasgow_network_edges.csv`:
1. The 20 road links in the file were created as **isolated coordinate vectors for sensor spatial proximity matching**, not as an interconnected directed routing graph.
2. Every link was assigned distinct start and end node identifiers ($1001 \to 1002, 1003 \to 1004, \dots$). No two edges share an intersection node.
3. Crucial attributes required for network routing—including metric edge lengths (`length_m`), turn restrictions, bridge approach connectors, and junction cross-streets—are absent from the dataset.
4. The simulation was executing all-pairs shortest paths on **19 disconnected two-node subgraphs**, causing all closure impedance metrics to reduce to linear artifacts of the arbitrary disconnection penalty parameter ($M = 3,600\text{s}$).

To resolve this defect without inventing data, real OpenStreetMap (OSM) vector data for central Glasgow has been identified and verified under the Open Database License (ODbL 1.0).

---

## 2. Granular Audit of Existing Network File

### 2.1 File Specification & Schema
- **File Location:** `data/network/glasgow_network_edges.csv`
- **File Size:** 2,007 bytes
- **Record Count:** Exactly 20 edge records (frequently cited as "21 edges" in earlier reports due to counting the header line or indexing errors).
- **Node Count:** Exactly 38 unique node identifiers (integers 1001 to 1039).

| Column Name | Inferred Data Type | Populated Count | Missing / Null Count | Notes / Evaluation |
|---|---|---|---|---|
| `edge_id` | String | 20 / 20 | 0 | Alphanumeric identifier (e.g., `M8_KINGSTON_NB_1`) |
| `u` | Integer | 20 / 20 | 0 | Starting node ID (1001 to 1038) |
| `v` | Integer | 20 / 20 | 0 | Terminating node ID (1002 to 1039) |
| `u_lat` | Float64 | 20 / 20 | 0 | WGS84 Latitude of start point ($55.850 - 55.865$) |
| `u_lon` | Float64 | 20 / 20 | 0 | WGS84 Longitude of start point ($-4.275 - -4.245$) |
| `v_lat` | Float64 | 20 / 20 | 0 | WGS84 Latitude of end point |
| `v_lon` | Float64 | 20 / 20 | 0 | WGS84 Longitude of end point |
| `name` | String | 20 / 20 | 0 | Human-readable road name |
| `highway` | String | 20 / 20 | 0 | Road classification (`motorway`, `primary`, `trunk`, `secondary`) |
| `oneway` | Boolean | 20 / 20 | 0 | 17 `True`, 3 `False` (`ARGYLE_ST_WB`, `BROOMIELAW_A814`, `CLYDE_ARC_NB`) |
| `lanes` | Integer | 20 / 20 | 0 | Lane count ($2$ to $5$) |
| **`length_m`** | **Missing** | **0 / 20** | **20 (100%)** | **Column completely missing from CSV** |

### 2.2 Critical Missing Fields & Flawed Assumptions
1. **Missing Edge Lengths (`length_m`):**
   - The column `length_m` does not exist in `glasgow_network_edges.csv`.
   - Inspection of `citypulse/resilience/prototype.py` (line 46) and `citypulse/resilience/monte_carlo.py` (line 63) reveals:
     ```python
     length_m = float(r.get('length_m', 500.0))
     ```
   - Because `length_m` was missing, Python's `.get()` silently defaulted every single edge to **500.0 meters**.
   - As a consequence, the 1.5 km elevated M8 Kingston Bridge viaduct, the 120-meter George V Bridge, and 80-meter city-centre ramp approaches were all treated as identical 500-meter straight paths.
2. **Absence of Shared Junction Nodes:**
   - In urban traffic networks, intersection topology is formed by edges sharing common vertex IDs (e.g., edge $A \to B$ and edge $B \to C$ meet at node $B$).
   - In `glasgow_network_edges.csv`, every link was defined as an isolated tuple:
     - Edge `M8_KINGSTON_NB_1`: $1001 \to 1002$
     - Edge `M8_KINGSTON_SB_1`: $1003 \to 1004$
     - Edge `GEORGE_V_BRIDGE_SB`: $1010 \to 1011$
     - Edge `GLASGOW_BRIDGE_NB`: $1012 \to 1013$
     - Edge `BROOMIELAW_A814`: $1032 \to 1033$
   - Node 1002 does not connect to 1003, 1011, or 1032. Even though Broomielaw passes directly under Kingston Bridge and intersects the George V Bridge approach, **zero edges connect these nodes**.

---

## 3. Provenance & Original Intent: Schematic vs Geographic

### 3.1 Original Intent
Reviewing the Phase 2 reports (`reports/sensor_matching_validation.md` and `reports/resilience_feasibility_note.md`) reveals why this file was constructed this way:
- In Phase 2, the primary objective was **sensor spatial snapping**: matching SCOOT detector coordinates ($lat, lon$) to the nearest road centerline within 15–350 meters.
- To test the candidate matcher algorithm, 20 prominent central Glasgow road segments were transcribed with approximate start and end coordinates.
- **The file was designed as a spatial lookup table of isolated line segments for distance calculations, NOT as a routable network graph.**

### 3.2 The Flawed Transition to Network Resilience
When Phase 3 and Phase 4 began evaluating network resilience:
- The prototype ingested `glasgow_network_edges.csv` directly into NetworkX via `G.add_edge(u, v)`.
- Because nodes were numbered sequentially, NetworkX created 19 disconnected subgraphs.
- All-pairs Dijkstra shortest-path calculations were executed across all $38 \times 37 = 1,406$ ordered pairs $(u, v)$.
- Since only 22 pairs had a directed path (the direct start-to-end nodes of each segment), 1,384 pairs failed, triggering the fallback disconnection penalty ($M = 3,600\text{s}$).
- The resulting network resilience calculations were not evaluating traffic rerouting; they were evaluating the arithmetic formula:
  $$\Delta \mathcal{C} = \Delta N_{\text{disc}} \times 3,600\text{s} - \sum \tau_e$$

---

## 4. Remediation Strategy & Open Data Source Identification

To reconstruct a scientifically defensible road network without inventing junctions or manual coordinates:

### 4.1 Data Source: OpenStreetMap (OSM)
- **Source:** Canonical OpenStreetMap XML via the official OpenStreetMap REST API (`api.openstreetmap.org/api/0.6/map`).
- **Licence:** Open Database License (ODbL 1.0) / OpenStreetMap contributors.
- **Coverage Extent:** Central Glasgow Clyde Crossing Corridor spanning:
  - Latitude: $55.850^\circ\text{N}$ to $55.865^\circ\text{N}$ (North-South: Tradeston/Gorbals south bank to Anderston/City Centre north bank).
  - Longitude: $-4.290^\circ\text{W}$ to $-4.242^\circ\text{W}$ (East-West: Clyde Arc / SECC in the west to Victoria and Albert Bridges in the east).
- **Data Volume:** Two verified, overlapping XML tiles totaling 25.7 MB of vector data:
  1. `glasgow_central_core.osm` (17.1 MB): Kingston Bridge, George V Bridge, Glasgow/Jamaica Bridge, Victoria Bridge, Albert Bridge, Broomielaw, Argyle St, Newton St, North St.
  2. `glasgow_clyde_arc.osm` (8.7 MB): Clyde Arc (Squinty Bridge), Finnieston Street, Govan Road approach.

### 4.2 Reconstruction Principles
1. **Topological Junction Extraction:** Two road segments intersect if and only if they share an identical OSM Node ID. Endpoints will meet at physical junctions with zero geometric tolerance error.
2. **True Geodetic Edge Lengths:** Link lengths will be calculated along the piecewise great-circle coordinates of the OSM way nodes using the WGS84 ellipsoidal distance formula, eliminating the 500-meter default.
3. **Strict One-Way & Highway Hierarchy:** One-way tags (`oneway=yes`, `oneway=-1`, roundabouts) and highway classifications (`motorway`, `trunk`, `primary`, `secondary`, `tertiary`, `motorway_link`) will be extracted directly from OSM tags.
4. **Preservation of Historical Evidence:** The original `data/network/glasgow_network_edges.csv` and previous reports will be retained unmodified for historical audit integrity. The reconstructed graph will be stored in `data/network/reconstructed_network_edges.csv` and `data/network/reconstructed_network_nodes.csv`.

---

### Gate 1 Conclusion:
A defensible, open-access, geometrically complete data source has been verified. Gate 1 is satisfied, and graph reconstruction (Gate 2) may proceed.
