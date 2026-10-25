r"""
CITYPULSE Observability Risk Index Calculation Module.
Formally defines and calculates:
    Omega_e = hat{NRI}(e) * [1 - exp(-dist_e / D_0)]
Where hat{NRI}(e) is normalized structural link criticality from all-pairs network impedance,
and dist_e is metric distance to the nearest high-confidence traffic sensor.
"""

import math
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
import networkx as nx

def geodetic_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes geodetic planar distance in meters calibrated for Glasgow latitude."""
    mean_lat_rad = math.radians((lat1 + lat2) / 2.0)
    dy = (lat2 - lat1) * 111320.0
    dx = (lon2 - lon1) * 111320.0 * math.cos(mean_lat_rad)
    return math.hypot(dx, dy)

class ObservabilityRiskCalculator:
    """
    Computes Network Robustness Index (NRI) and Observability Risk Index (Omega_e)
    across all road network edges.
    """
    def __init__(
        self,
        edges_df: pd.DataFrame,
        sensors_df: pd.DataFrame,
        d0_meters: float = 500.0,
        disconnection_penalty: float = 3600.0
    ):
        self.edges_df = edges_df.copy()
        self.sensors_df = sensors_df.copy()
        self.d0 = d0_meters
        self.penalty = disconnection_penalty
        
        # Filter sensors to high-confidence matches
        if 'status' in self.sensors_df.columns:
            self.high_conf_sensors = self.sensors_df[
                self.sensors_df['status'] == 'MATCHED_HIGH_CONFIDENCE'
            ].copy()
        else:
            self.high_conf_sensors = self.sensors_df.copy()

    def _build_graph(self) -> nx.DiGraph:
        """Constructs deterministic baseline graph with normative free-flow impedance."""
        G = nx.DiGraph()
        for _, r in self.edges_df.iterrows():
            edge_id = str(r['edge_id'])
            u, v = int(r['u']), int(r['v'])
            length_m = float(r.get('length_m', 500.0))
            h_type = str(r.get('highway', 'secondary'))
            
            if 'motorway' in h_type:
                speed_mps = 22.2
            elif 'trunk' in h_type:
                speed_mps = 17.8
            elif 'primary' in h_type:
                speed_mps = 13.4
            else:
                speed_mps = 8.9
                
            free_flow_sec = length_m / max(1.0, speed_mps)
            G.add_edge(u, v, id=edge_id, weight=free_flow_sec)
            if not bool(r.get('oneway', False)):
                G.add_edge(v, u, id=f"{edge_id}_rev", weight=free_flow_sec)
        return G

    def compute_all_pairs_cost(self, G: nx.DiGraph, od_pairs: List[Tuple[int, int]]) -> float:
        """Computes all-pairs shortest path impedance across OD pairs."""
        total = 0.0
        lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight'))
        for u, v in od_pairs:
            if u in lengths and v in lengths[u]:
                total += lengths[u][v]
            else:
                total += self.penalty
        return total

    def compute_nri(self) -> Dict[str, float]:
        r"""
        Calculates Network Robustness Index for each edge:
            NRI(e) = C(G \ {e}) - C(G)
        """
        G_base = self._build_graph()
        nodes = list(G_base.nodes)
        od_pairs = [(u, v) for u in nodes for v in nodes if u != v]
        
        base_cost = self.compute_all_pairs_cost(G_base, od_pairs)
        nri_scores = {}
        
        for _, r in self.edges_df.iterrows():
            edge_id = str(r['edge_id'])
            u, v = int(r['u']), int(r['v'])
            
            G_sub = G_base.copy()
            if G_sub.has_edge(u, v):
                G_sub.remove_edge(u, v)
            if G_sub.has_edge(v, u) and not bool(r.get('oneway', False)):
                G_sub.remove_edge(v, u)
                
            disrupted_cost = self.compute_all_pairs_cost(G_sub, od_pairs)
            raw_nri = max(0.0, disrupted_cost - base_cost)
            nri_scores[edge_id] = raw_nri
            
        return nri_scores

    def compute_edge_distances_to_sensors(self) -> Dict[str, float]:
        """
        Calculates minimum distance from edge midpoint to nearest high-confidence sensor.
        """
        distances = {}
        sensor_pts = [
            (float(row['latitude']), float(row['longitude']))
            for _, row in self.high_conf_sensors.iterrows()
        ]
        
        for _, r in self.edges_df.iterrows():
            edge_id = str(r['edge_id'])
            # Edge midpoint
            mid_lat = (float(r['u_lat']) + float(r['v_lat'])) / 2.0
            mid_lon = (float(r['u_lon']) + float(r['v_lon'])) / 2.0
            
            if not sensor_pts:
                # If no high-confidence sensors exist, set distance to infinite
                distances[edge_id] = 10000.0
                continue
                
            min_d = min(geodetic_distance_m(mid_lat, mid_lon, slat, slon) for slat, slon in sensor_pts)
            distances[edge_id] = min_d
            
        return distances

    def compute_observability_index(self) -> pd.DataFrame:
        """
        Computes normalized NRI, unobservability discount, and final Observability Risk Index.
        Returns a DataFrame sorted by Observability Risk descending.
        """
        nri_dict = self.compute_nri()
        dist_dict = self.compute_edge_distances_to_sensors()
        
        # Normalization of NRI to [0, 1]
        nri_vals = list(nri_dict.values())
        min_nri = min(nri_vals)
        max_nri = max(nri_vals)
        nri_range = max(1e-6, max_nri - min_nri)
        
        records = []
        for _, r in self.edges_df.iterrows():
            edge_id = str(r['edge_id'])
            name = str(r['name'])
            h_type = str(r['highway'])
            lanes = int(r.get('lanes', 2))
            
            raw_nri = nri_dict[edge_id]
            norm_nri = (raw_nri - min_nri) / nri_range
            
            dist_m = dist_dict[edge_id]
            # Unobservability factor U(e) = 1 - exp(-dist / D0)
            unobservability = 1.0 - math.exp(-dist_m / self.d0)
            
            # Observability Risk Index Omega_e = norm_nri * unobservability
            omega = norm_nri * unobservability
            
            records.append({
                "edge_id": edge_id,
                "name": name,
                "highway": h_type,
                "lanes": lanes,
                "raw_nri_seconds": round(raw_nri, 2),
                "normalized_nri": round(norm_nri, 4),
                "dist_to_sensor_meters": round(dist_m, 1),
                "unobservability_factor": round(unobservability, 4),
                "observability_risk_index": round(omega, 4)
            })
            
        df = pd.DataFrame(records)
        df.sort_values(by="observability_risk_index", ascending=False, inplace=True)
        return df.reset_index(drop=True)
