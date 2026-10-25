"""
CITYPULSE Data Loader Module
Handles reading, validating, reindexing, and partitioning Glasgow SCOOT traffic flow data.
Enforces explicit separation between observed records, reindexed calendar series, and missing values.
"""

import os
import zipfile
from typing import Dict, Optional, Union
import numpy as np
import pandas as pd

from .schemas import SplitName, SplitBounds, MissingnessReport

def load_sensor_locations(source_path: str) -> pd.DataFrame:
    """
    Loads spatial sensor metadata from locations.csv or within a zip file.
    Validates required columns, coordinates, and bounding box.
    """
    if source_path.endswith('.zip'):
        with zipfile.ZipFile(source_path, 'r') as z:
            with z.open('locations.csv') as f:
                df = pd.read_csv(f)
    else:
        df = pd.read_csv(source_path)
    
    required_cols = {'id', 'latitude', 'longitude'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"locations file missing required columns: {required_cols - set(df.columns)}")
    
    if df['latitude'].isnull().any() or df['longitude'].isnull().any():
        raise ValueError("locations contains null coordinates")
    
    # Validation of Glasgow bounding box
    if not ((df['latitude'] >= 55.70).all() and (df['latitude'] <= 56.05).all()):
        raise ValueError("Sensor latitude out of expected Glasgow range [55.70, 56.05]")
    if not ((df['longitude'] >= -4.55).all() and (df['longitude'] <= -4.00).all()):
        raise ValueError("Sensor longitude out of expected Glasgow range [-4.55, -4.00]")
    
    return df

def load_sensor_flow(source_path: str, sensor_id: str) -> pd.DataFrame:
    """
    Loads raw flow records for a specified sensor from a CSV file or zip archive.
    Validates date/time columns, non-negative integer flows, and row integrity.
    """
    rel_csv = f"flows/{sensor_id}.csv" if not sensor_id.endswith('.csv') else f"flows/{sensor_id}"
    
    if source_path.endswith('.zip'):
        with zipfile.ZipFile(source_path, 'r') as z:
            if rel_csv not in z.namelist():
                raise FileNotFoundError(f"Sensor file {rel_csv} not found in zip archive")
            with z.open(rel_csv) as f:
                df = pd.read_csv(f)
    else:
        full_path = os.path.join(source_path, rel_csv) if not source_path.endswith(rel_csv) else source_path
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Sensor file not found: {full_path}")
        df = pd.read_csv(full_path)
    
    required_cols = {'date', 'time', 'flow'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Flow data missing required columns: {required_cols - set(df.columns)}")
    
    if (df['flow'] < 0).any():
        raise ValueError(f"Sensor {sensor_id} contains negative flow values")
    
    if not ((df['time'] >= 0) & (df['time'] <= 23)).all():
        raise ValueError(f"Sensor {sensor_id} contains invalid time hours (must be 0-23)")
    
    return df

def reindex_sensor_flow(
    df: pd.DataFrame,
    start_dt: pd.Timestamp = SplitBounds.TRAIN_START,
    end_dt: pd.Timestamp = SplitBounds.TEST_END
) -> pd.Series:
    """
    Constructs a complete continuous hourly calendar index and aligns observed records.
    Omitted timestamps are populated with np.nan without converting legitimate zeros to NaN.
    Returns a float32 pd.Series indexed by continuous DatetimeIndex.
    """
    df_copy = df.copy()
    df_copy['datetime'] = pd.to_datetime(df_copy['date'] + ' ' + df_copy['time'].astype(str) + ':00:00')
    
    # Check for duplicates in raw data
    if df_copy['datetime'].duplicated().any():
        raise ValueError("Raw flow data contains duplicate timestamps")
    
    full_index = pd.date_range(start=start_dt, end=end_dt, freq='h')
    
    series = df_copy.set_index('datetime')['flow'].astype('float32')
    reindexed_series = series.reindex(full_index)
    reindexed_series.name = "flow"
    
    return reindexed_series

def compute_missingness_report(sensor_id: str, raw_df: pd.DataFrame, reindexed_series: pd.Series) -> MissingnessReport:
    """
    Computes a strict accounting report distinguishing calendar hours, observed records,
    and missing hours.
    """
    cal_hours = len(reindexed_series)
    obs_records = len(raw_df)
    missing_hours = int(reindexed_series.isnull().sum())
    missing_pct = round((missing_hours / cal_hours) * 100.0, 3)
    
    zero_records = int((raw_df['flow'] == 0).sum())
    zero_pct = round((zero_records / obs_records) * 100.0, 3) if obs_records > 0 else 0.0
    
    return MissingnessReport(
        sensor_id=sensor_id,
        calendar_hours=cal_hours,
        observed_records=obs_records,
        missing_hours=missing_hours,
        missing_percentage=missing_pct,
        zero_flow_records=zero_records,
        zero_flow_percentage=zero_pct,
        min_flow=float(raw_df['flow'].min()),
        max_flow=float(raw_df['flow'].max()),
        mean_flow=round(float(raw_df['flow'].mean()), 2)
    )

def split_chronological(reindexed_series: pd.Series) -> Dict[SplitName, pd.Series]:
    """
    Partitions the continuous reindexed series into non-overlapping chronological splits.
    Guarantees zero data leakage and exact calendar-hour boundaries.
    """
    train = reindexed_series.loc[SplitBounds.TRAIN_START:SplitBounds.TRAIN_END].copy()
    val   = reindexed_series.loc[SplitBounds.VAL_START:SplitBounds.VAL_END].copy()
    test  = reindexed_series.loc[SplitBounds.TEST_START:SplitBounds.TEST_END].copy()
    
    assert len(train) == SplitBounds.EXPECTED_CALENDAR_HOURS[SplitName.TRAIN], \
        f"Train split calendar hours mismatch: {len(train)} vs {SplitBounds.EXPECTED_CALENDAR_HOURS[SplitName.TRAIN]}"
    assert len(val) == SplitBounds.EXPECTED_CALENDAR_HOURS[SplitName.VAL], \
        f"Val split calendar hours mismatch: {len(val)} vs {SplitBounds.EXPECTED_CALENDAR_HOURS[SplitName.VAL]}"
    assert len(test) == SplitBounds.EXPECTED_CALENDAR_HOURS[SplitName.TEST], \
        f"Test split calendar hours mismatch: {len(test)} vs {SplitBounds.EXPECTED_CALENDAR_HOURS[SplitName.TEST]}"
    
    return {
        SplitName.TRAIN: train,
        SplitName.VAL:   val,
        SplitName.TEST:  test
    }
