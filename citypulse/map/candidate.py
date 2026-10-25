"""
CITYPULSE Sensor-to-Road Matching Data Structures
Defines candidates, mapping statuses, and reviewable audit models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

class MappingStatus(str, Enum):
    MATCHED_HIGH_CONFIDENCE = "MATCHED_HIGH_CONFIDENCE"
    MATCHED_MEDIUM_CONFIDENCE = "MATCHED_MEDIUM_CONFIDENCE"
    AMBIGUOUS_MULTI_CANDIDATE = "AMBIGUOUS_MULTI_CANDIDATE"
    UNMATCHED_DISTANCE_EXCEEDED = "UNMATCHED_DISTANCE_EXCEEDED"
    MANUALLY_REVIEWED = "MANUALLY_REVIEWED"

@dataclass
class CandidateEdge:
    """Represents a candidate directed road edge near a sensor."""
    edge_id: str
    u: int
    v: int
    name: str
    highway_type: str
    oneway: bool
    distance_meters: float
    bearing_degrees: Optional[float] = None
    lanes: Optional[int] = None

@dataclass
class SensorMappingRecord:
    """Comprehensive, reviewable record for a single detector's mapping results."""
    sensor_id: str
    latitude: float
    longitude: float
    candidate_count: int
    candidate_summary: str
    selected_edge_id: Optional[str]
    selected_edge_name: Optional[str]
    min_distance_meters: float
    status: MappingStatus
    mapping_confidence: float  # [0.0, 1.0]
    rationale: str
    junction_prefix: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "junction_prefix": self.junction_prefix,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status.value,
            "mapping_confidence": round(self.mapping_confidence, 3),
            "selected_edge_id": self.selected_edge_id or "UNMATCHED",
            "selected_edge_name": self.selected_edge_name or "NONE",
            "min_distance_meters": round(self.min_distance_meters, 2),
            "candidate_count": self.candidate_count,
            "candidate_summary": self.candidate_summary,
            "rationale": self.rationale
        }
