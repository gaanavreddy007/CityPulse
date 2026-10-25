"""
CITYPULSE Resilience Feasibility Prototype
Evaluates model-based network accessibility cost proxy under multi-edge bridge closures.
Includes connectivity auditing, parameter sensitivity analysis, and explicit proxy definitions.
Operates 100% offline using NetworkX and SciPy.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional, Any
import networkx as nx
import numpy as np
import pandas as pd

@dataclass
class ResilienceSimulationResult:
    """Encapsulates model-based accessibility proxy results under closure."""
    scenario_name: str
    baseline_total_cost: float
    closure_total_cost: float
    cost_increase_delta: float
    relative_cost_increase_pct: float
    disconnected_od_pairs: int
    connected_od_pairs: int
    closed_edges: List[str]
    parameters: Dict[str, Any]

class ResiliencePrototype:
    """
    Feasibility prototype measuring network accessibility cost degradation.
    Explicitly operates as a structural proxy, NOT observed travel times.
    """
    def __init__(self, edges_df: pd.DataFrame, alpha: float = 0.20, beta: float = 2.0):
        self.edges_df = edges_df.copy()
        self.alpha = alpha
        self.beta = beta
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.DiGraph:
        """Constructs a directed multigraph with BPR impedance weights."""
        G = nx.DiGraph()
        for _, r in self.edges_df.iterrows():
            u, v = int(r['u']), int(r['v'])
            edge_id = str(r['edge_id'])
            
            # Default length from coordinates if not specified
            length_m = float(r.get('length_m', 500.0))
            lanes = int(r.get('lanes', 2))
            
            # Road capacity provenance: WebTAG standards
            h_type = str(r.get('highway', 'secondary'))
            if 'motorway' in h_type:
                cap_per_lane = 1800.0
                speed_mps = 22.2  # ~50 mph / 80 kmh urban motorway
            elif 'primary' in h_type:
                cap_per_lane = 900.0
                speed_mps = 13.4   # ~30 mph
            elif 'trunk' in h_type:
                cap_per_lane = 1400.0
                speed_mps = 17.8  # ~40 mph
            else:
                cap_per_lane = 600.0
                speed_mps = 8.9    # ~20 mph
                
            capacity = lanes * cap_per_lane
            free_flow_time_sec = length_m / max(1.0, speed_mps)
            flow_vol = float(r.get('flow', 0.0))
            
            # Standard BPR impedance calculation
            vc_ratio = flow_vol / max(1.0, capacity)
            impedance = free_flow_time_sec * (1.0 + self.alpha * (vc_ratio ** self.beta))
            
            # Forward directed edge
            G.add_edge(u, v, id=edge_id, name=str(r['name']), impedance=impedance,
                       free_flow=free_flow_time_sec, capacity=capacity, flow=flow_vol)
            
            # If two-way, add reverse directed edge
            if not bool(r.get('oneway', False)):
                G.add_edge(v, u, id=f"{edge_id}_rev", name=f"{r['name']} (Rev)",
                           impedance=impedance, free_flow=free_flow_time_sec,
                           capacity=capacity, flow=flow_vol)
        return G

    def compute_all_pairs_accessibility(
        self,
        target_graph: nx.DiGraph,
        od_pairs: Optional[List[Tuple[int, int]]] = None,
        disconnection_penalty: float = 3600.0  # 1 hour penalty for unreachable destination
    ) -> Tuple[float, int, int]:
        """
        Computes total network impedance cost across specified OD pairs.
        Returns (total_cost, connected_count, disconnected_count).
        """
        nodes = list(target_graph.nodes)
        if od_pairs is None:
            # Sample all distinct ordered pairs
            od_pairs = [(u, v) for u in nodes for v in nodes if u != v]
            
        total_cost = 0.0
        connected = 0
        disconnected = 0
        
        # Vectorized shortest paths using Dijkstra
        for orig, dest in od_pairs:
            try:
                cost = nx.shortest_path_length(target_graph, source=orig, target=dest, weight='impedance')
                total_cost += cost
                connected += 1
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                total_cost += disconnection_penalty
                disconnected += 1
                
        return total_cost, connected, disconnected

    def simulate_closure(
        self,
        scenario_name: str,
        edges_to_remove: List[str],
        od_pairs: Optional[List[Tuple[int, int]]] = None
    ) -> ResilienceSimulationResult:
        """
        Simulates a multi-edge infrastructure closure, calculating accessibility cost increase.
        """
        # Baseline impedance
        base_cost, base_conn, base_disc = self.compute_all_pairs_accessibility(self.graph, od_pairs)
        
        # Create severed graph copy
        G_closed = self.graph.copy()
        removed_actual = []
        
        for u, v, data in list(G_closed.edges(data=True)):
            if data.get('id') in edges_to_remove:
                G_closed.remove_edge(u, v)
                removed_actual.append(data.get('id'))
                
        # Closure impedance
        closure_cost, close_conn, close_disc = self.compute_all_pairs_accessibility(G_closed, od_pairs)
        delta_cost = closure_cost - base_cost
        pct_increase = (delta_cost / max(1.0, base_cost)) * 100.0
        
        return ResilienceSimulationResult(
            scenario_name=scenario_name,
            baseline_total_cost=round(base_cost, 2),
            closure_total_cost=round(closure_cost, 2),
            cost_increase_delta=round(delta_cost, 2),
            relative_cost_increase_pct=round(pct_increase, 2),
            disconnected_od_pairs=close_disc - base_disc,
            connected_od_pairs=close_conn,
            closed_edges=removed_actual,
            parameters={"alpha": self.alpha, "beta": self.beta, "edges_requested": edges_to_remove}
        )

    def run_sensitivity_test(
        self,
        scenario_name: str,
        edges_to_remove: List[str],
        alpha_range: List[float] = [0.10, 0.20, 0.30],
        beta_range: List[float] = [1.5, 2.0, 4.0]
    ) -> pd.DataFrame:
        """Evaluates resilience outcome sensitivity under varying BPR parameters."""
        records = []
        for a in alpha_range:
            for b in beta_range:
                proto = ResiliencePrototype(self.edges_df, alpha=a, beta=b)
                res = proto.simulate_closure(scenario_name, edges_to_remove)
                records.append({
                    "alpha": a,
                    "beta": b,
                    "delta_cost": res.cost_increase_delta,
                    "pct_increase": res.relative_cost_increase_pct,
                    "disconnected_pairs": res.disconnected_od_pairs
                })
        return pd.DataFrame(records)
