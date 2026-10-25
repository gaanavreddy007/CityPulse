"""
CITYPULSE Candidate-Based Sensor-to-Road Matching Engine
Implements non-forcing candidate generation, proximity scoring, ambiguity flagging,
and multi-sensor junction conflict detection.
Operates 100% offline.
"""

import math
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

from .candidate import CandidateEdge, SensorMappingRecord, MappingStatus

def geodetic_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes planar distance in meters calibrated for Glasgow latitude (55.86 N)."""
    # 1 deg lat = 111,320 m; 1 deg lon = 111,320 * cos(lat) = 62,450 m
    mean_lat_rad = math.radians((lat1 + lat2) / 2.0)
    dy = (lat2 - lat1) * 111320.0
    dx = (lon2 - lon1) * 111320.0 * math.cos(mean_lat_rad)
    return math.hypot(dx, dy)

def point_to_segment_distance_meters(
    p_lat: float, p_lon: float,
    u_lat: float, u_lon: float,
    v_lat: float, v_lon: float
) -> Tuple[float, float]:
    """
    Computes minimum perpendicular distance in meters from point P to line segment U-V,
    along with segment bearing in degrees [0, 360).
    """
    mean_lat_rad = math.radians(p_lat)
    kx = 111320.0 * math.cos(mean_lat_rad)
    ky = 111320.0
    
    # Project to metric coordinates relative to P
    px, py = 0.0, 0.0
    ux, uy = (u_lon - p_lon) * kx, (u_lat - p_lat) * ky
    vx, vy = (v_lon - p_lon) * kx, (v_lat - p_lat) * ky
    
    seg_dx = vx - ux
    seg_dy = vy - uy
    seg_len_sq = seg_dx**2 + seg_dy**2
    
    # Bearing of segment from U to V
    bearing = (math.degrees(math.atan2(seg_dx, seg_dy)) + 360.0) % 360.0
    
    if seg_len_sq < 1e-6:
        # Segment is effectively a point
        dist = math.hypot(ux, uy)
        return dist, bearing
    
    # Projection factor t of point P onto segment U-V
    t = max(0.0, min(1.0, -(ux * seg_dx + uy * seg_dy) / seg_len_sq))
    proj_x = ux + t * seg_dx
    proj_y = uy + t * seg_dy
    dist = math.hypot(proj_x, proj_y)
    
    return dist, bearing

class CandidateMatcher:
    """
    Matches traffic detectors to road network edges using a candidate ranking paradigm.
    Does NOT force single edge assignments where ambiguity exists.
    """
    def __init__(self, edges_df: pd.DataFrame, max_search_radius_m: float = 40.0):
        self.edges_df = edges_df.copy()
        self.max_radius = max_search_radius_m
        self._validate_network()

    def _validate_network(self):
        req = {'edge_id', 'u_lat', 'u_lon', 'v_lat', 'v_lon', 'name', 'highway', 'oneway'}
        missing = req - set(self.edges_df.columns)
        if missing:
            raise ValueError(f"Network edges missing required columns: {missing}")

    def find_candidates(self, lat: float, lon: float) -> List[CandidateEdge]:
        """Finds all directed edges within max_search_radius_m of detector point."""
        candidates = []
        for _, row in self.edges_df.iterrows():
            dist, bearing = point_to_segment_distance_meters(
                lat, lon,
                row['u_lat'], row['u_lon'],
                row['v_lat'], row['v_lon']
            )
            if dist <= self.max_radius:
                candidates.append(CandidateEdge(
                    edge_id=str(row['edge_id']),
                    u=int(row.get('u', 0)),
                    v=int(row.get('v', 0)),
                    name=str(row['name']),
                    highway_type=str(row['highway']),
                    oneway=bool(row['oneway']),
                    distance_meters=dist,
                    bearing_degrees=bearing,
                    lanes=int(row['lanes']) if 'lanes' in row and pd.notnull(row['lanes']) else None
                ))
        
        # Sort candidates strictly by distance ascending
        candidates.sort(key=lambda c: c.distance_meters)
        return candidates

    def match_detector(self, sensor_id: str, lat: float, lon: float) -> SensorMappingRecord:
        """Evaluates candidates for a single detector and assigns status and confidence."""
        junction_prefix = sensor_id.split('_')[0]
        candidates = self.find_candidates(lat, lon)
        
        if len(candidates) == 0:
            return SensorMappingRecord(
                sensor_id=sensor_id,
                latitude=lat,
                longitude=lon,
                candidate_count=0,
                candidate_summary="No road edges within search radius",
                selected_edge_id=None,
                selected_edge_name=None,
                min_distance_meters=self.max_radius,
                status=MappingStatus.UNMATCHED_DISTANCE_EXCEEDED,
                mapping_confidence=0.0,
                rationale=f"No edges within {self.max_radius}m radius",
                junction_prefix=junction_prefix
            )
            
        summary_str = " | ".join([f"{c.edge_id}:{c.name} ({c.distance_meters:.1f}m)" for c in candidates[:3]])
        c1 = candidates[0]
        
        if len(candidates) == 1:
            conf = 0.92 if c1.distance_meters <= 15.0 else 0.78
            status = MappingStatus.MATCHED_HIGH_CONFIDENCE if conf >= 0.85 else MappingStatus.MATCHED_MEDIUM_CONFIDENCE
            return SensorMappingRecord(
                sensor_id=sensor_id,
                latitude=lat,
                longitude=lon,
                candidate_count=1,
                candidate_summary=summary_str,
                selected_edge_id=c1.edge_id,
                selected_edge_name=c1.name,
                min_distance_meters=c1.distance_meters,
                status=status,
                mapping_confidence=conf,
                rationale="Unique proximate road edge within search radius",
                junction_prefix=junction_prefix
            )
            
        c2 = candidates[1]
        dist_gap = abs(c2.distance_meters - c1.distance_meters)
        
        # Ambiguity condition: two close candidates on different streets/carriageways
        if dist_gap < 6.0 and c1.name != c2.name:
            return SensorMappingRecord(
                sensor_id=sensor_id,
                latitude=lat,
                longitude=lon,
                candidate_count=len(candidates),
                candidate_summary=summary_str,
                selected_edge_id=c1.edge_id,  # provisional closest, but flagged
                selected_edge_name=c1.name,
                min_distance_meters=c1.distance_meters,
                status=MappingStatus.AMBIGUOUS_MULTI_CANDIDATE,
                mapping_confidence=0.48,
                rationale=f"Ambiguous: Competing edges '{c1.name}' ({c1.distance_meters:.1f}m) vs '{c2.name}' ({c2.distance_meters:.1f}m) differ by only {dist_gap:.1f}m",
                junction_prefix=junction_prefix
            )
            
        # Distinct dominant candidate
        if c1.distance_meters <= 12.0 and dist_gap >= 12.0:
            return SensorMappingRecord(
                sensor_id=sensor_id,
                latitude=lat,
                longitude=lon,
                candidate_count=len(candidates),
                candidate_summary=summary_str,
                selected_edge_id=c1.edge_id,
                selected_edge_name=c1.name,
                min_distance_meters=c1.distance_meters,
                status=MappingStatus.MATCHED_HIGH_CONFIDENCE,
                mapping_confidence=0.88,
                rationale=f"Dominant closest edge with {dist_gap:.1f}m margin to next candidate",
                junction_prefix=junction_prefix
            )
            
        # Medium confidence match
        return SensorMappingRecord(
            sensor_id=sensor_id,
            latitude=lat,
            longitude=lon,
            candidate_count=len(candidates),
            candidate_summary=summary_str,
            selected_edge_id=c1.edge_id,
            selected_edge_name=c1.name,
            min_distance_meters=c1.distance_meters,
            status=MappingStatus.MATCHED_MEDIUM_CONFIDENCE,
            mapping_confidence=0.68,
            rationale=f"Closest candidate with moderate distance separation ({dist_gap:.1f}m)",
            junction_prefix=junction_prefix
        )

    def match_batch(self, sensors_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Matches a batch of detectors and executes junction cross-validation."""
        records = []
        for _, row in sensors_df.iterrows():
            rec = self.match_detector(row['id'], row['latitude'], row['longitude'])
            records.append(rec)
            
        # Junction cross-validation: check for identical edge assignments at same junction
        edge_junction_usage: Dict[str, List[str]] = {}
        for r in records:
            if r.selected_edge_id:
                edge_junction_usage.setdefault(r.selected_edge_id, []).append(r.sensor_id)
                
        # Flag conflicting multi-sensor matches on same directed edge
        for r in records:
            if r.selected_edge_id and len(edge_junction_usage[r.selected_edge_id]) > 1:
                competing = [s for s in edge_junction_usage[r.selected_edge_id] if s != r.sensor_id]
                # Check if sensors share junction prefix
                shared = [s for s in competing if s.split('_')[0] == r.junction_prefix]
                if shared:
                    r.status = MappingStatus.AMBIGUOUS_MULTI_CANDIDATE
                    r.mapping_confidence = min(r.mapping_confidence, 0.40)
                    r.rationale += f" | Conflict: Multiple junction detectors ({', '.join(shared)}) snapped to same edge {r.selected_edge_id}"

        results_df = pd.DataFrame([r.to_dict() for r in records])
        
        # Summary statistics
        stats = {
            "total_detectors": len(results_df),
            "matched_high": int((results_df['status'] == MappingStatus.MATCHED_HIGH_CONFIDENCE.value).sum()),
            "matched_medium": int((results_df['status'] == MappingStatus.MATCHED_MEDIUM_CONFIDENCE.value).sum()),
            "ambiguous": int((results_df['status'] == MappingStatus.AMBIGUOUS_MULTI_CANDIDATE.value).sum()),
            "unmatched": int((results_df['status'] == MappingStatus.UNMATCHED_DISTANCE_EXCEEDED.value).sum()),
            "mean_confidence": round(float(results_df['mapping_confidence'].mean()), 3),
            "mean_min_distance_m": round(float(results_df['min_distance_meters'].mean()), 2)
        }
        return results_df, stats
