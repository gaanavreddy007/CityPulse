"""
CITYPULSE - Phase 1 Dataset Inspection Script
Audits Glasgow SCOOT traffic flow data and spatial metadata.
Operates 100% offline on extracted sample or raw files.
"""

import os
import glob
import json
import pandas as pd

def inspect_locations(locations_path: str) -> dict:
    if not os.path.exists(locations_path):
        raise FileNotFoundError(f"Locations file not found: {locations_path}")
    
    df = pd.read_csv(locations_path)
    assert set(['id', 'latitude', 'longitude']).issubset(df.columns), "Missing required columns"
    
    return {
        "total_sensors": len(df),
        "lat_min": float(df['latitude'].min()),
        "lat_max": float(df['latitude'].max()),
        "lon_min": float(df['longitude'].min()),
        "lon_max": float(df['longitude'].max()),
        "null_coords": int(df['latitude'].isnull().sum() + df['longitude'].isnull().sum()),
        "unique_junctions": int(df['id'].apply(lambda x: x.split('_')[0]).nunique())
    }

def inspect_flow_file(flow_path: str, start_dt: str = "2019-10-01 00:00:00", end_dt: str = "2023-09-30 23:00:00") -> dict:
    if not os.path.exists(flow_path):
        raise FileNotFoundError(f"Flow file not found: {flow_path}")
    
    df = pd.read_csv(flow_path)
    assert set(['date', 'time', 'flow']).issubset(df.columns), "Missing required columns"
    
    # Construct continuous timeline
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'].astype(str) + ':00:00')
    full_idx = pd.date_range(start=start_dt, end=end_dt, freq='h')
    
    missing_hours = len(full_idx) - len(df)
    zero_flows = int((df['flow'] == 0).sum())
    negative_flows = int((df['flow'] < 0).sum())
    
    return {
        "sensor_id": os.path.basename(flow_path).replace('.csv', ''),
        "total_records": len(df),
        "expected_hours": len(full_idx),
        "missing_hours": missing_hours,
        "missing_percentage": round((missing_hours / len(full_idx)) * 100, 2),
        "zero_flow_records": zero_flows,
        "zero_flow_percentage": round((zero_flows / len(df)) * 100, 2),
        "negative_flows": negative_flows,
        "mean_flow": round(float(df['flow'].mean()), 2),
        "max_flow": int(df['flow'].max()),
        "p50_flow": float(df['flow'].median())
    }

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_dir = os.path.join(base_dir, "data", "sample")
    loc_path = os.path.join(sample_dir, "locations.csv")
    
    print(f"=== CITYPULSE DATASET INSPECTION ===")
    print(f"Inspecting sample directory: {sample_dir}")
    
    loc_metrics = inspect_locations(loc_path)
    print("\n--- Spatial Metadata (locations.csv) ---")
    print(json.dumps(loc_metrics, indent=2))
    
    flow_files = sorted(glob.glob(os.path.join(sample_dir, "flows", "*.csv")))
    print(f"\n--- Flow Time-Series Files ({len(flow_files)} files examined) ---")
    flow_summaries = []
    for ff in flow_files:
        summary = inspect_flow_file(ff)
        flow_summaries.append(summary)
        print(f"Sensor {summary['sensor_id']}: rows={summary['total_records']}, missing={summary['missing_hours']} ({summary['missing_percentage']}%), mean={summary['mean_flow']}, max={summary['max_flow']}")
    
    output_path = os.path.join(base_dir, "reports", "sample_inspection_summary.json")
    with open(output_path, "w") as out:
        json.dump({"spatial_metadata": loc_metrics, "sample_flows": flow_summaries}, out, indent=2)
    print(f"\nAudit summary written to: {output_path}")

if __name__ == "__main__":
    main()
