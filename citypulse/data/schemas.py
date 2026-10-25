"""
CITYPULSE Data Layer Schemas and Constants
Defines canonical split boundaries, corruption enums, and data models.
"""

from dataclasses import dataclass
from enum import Enum
import pandas as pd

class SplitName(str, Enum):
    TRAIN = "train"
    VAL = "validation"
    TEST = "test"

class CorruptionType(str, Enum):
    MCAR = "missing_completely_at_random"
    BURST = "burst_outage"
    DRIFT = "calibration_drift"
    STUCK_ZERO = "stuck_at_zero"
    STUCK_MEAN = "stuck_at_mean"

class SplitBounds:
    """Canonical chronological boundaries for Glasgow SCOOT data partitions."""
    TRAIN_START = pd.Timestamp("2019-10-01 00:00:00")
    TRAIN_END   = pd.Timestamp("2021-09-30 23:00:00")
    
    VAL_START   = pd.Timestamp("2021-10-01 00:00:00")
    VAL_END     = pd.Timestamp("2022-09-30 23:00:00")
    
    TEST_START  = pd.Timestamp("2022-10-01 00:00:00")
    TEST_END    = pd.Timestamp("2023-09-30 23:00:00")
    
    EXPECTED_CALENDAR_HOURS = {
        SplitName.TRAIN: 17544,
        SplitName.VAL:   8760,
        SplitName.TEST:  8760,
        "total":         35064
    }

@dataclass
class MissingnessReport:
    """Rigorous accounting of calendar hours vs observed records vs missing data."""
    sensor_id: str
    calendar_hours: int
    observed_records: int
    missing_hours: int
    missing_percentage: float
    zero_flow_records: int
    zero_flow_percentage: float
    min_flow: float
    max_flow: float
    mean_flow: float
