"""
CITYPULSE Phase 4.2: OpenStreetMap Data Fetcher & Source Manifest Generator.
Downloads official OpenStreetMap vector XML tiles covering the Glasgow Clyde central corridor
and records canonical provenance, attribution, and license metadata.
"""

import os
import sys
import json
import requests

PROJECT_ROOT = r"C:\Gaanav\Projects\CityPulse"
raw_osm_dir = os.path.join(PROJECT_ROOT, "data", "network", "raw_osm")
os.makedirs(raw_osm_dir, exist_ok=True)

headers = {
    'User-Agent': 'CityPulseResearch/1.0 (academic research; contact@citypulse.org)'
}

tiles = [
    {
        'id': 'central_core',
        'bbox': '-4.275,55.850,-4.242,55.865',
        'desc': 'Central Clyde Bridges and City Centre Corridor'
    },
    {
        'id': 'clyde_arc_west',
        'bbox': '-4.290,55.850,-4.270,55.865',
        'desc': 'Western Clyde Arc and Expressway Corridor'
    }
]

for t in tiles:
    out_file = os.path.join(raw_osm_dir, f"{t['id']}.osm")
    print(f"Fetching {t['id']} (bbox={t['bbox']})...")
    r = requests.get(
        f"https://api.openstreetmap.org/api/0.6/map?bbox={t['bbox']}",
        headers=headers,
        timeout=60
    )
    print(f"  Status: {r.status_code}, Content Length: {len(r.content):,} bytes")
    if r.status_code == 200:
        with open(out_file, 'wb') as f:
            f.write(r.content)
        print(f"  Saved to: {out_file}")
    else:
        print(f"  ERROR: {r.text[:200]}")

# Create source manifest
manifest = {
    'project': 'CITYPULSE',
    'phase': '4.2',
    'title': 'Glasgow Central Clyde Crossing Road Network Data Source Manifest',
    'source': 'OpenStreetMap official API 0.6',
    'endpoint': 'https://api.openstreetmap.org/api/0.6/map',
    'attribution': 'OpenStreetMap contributors',
    'license': 'Open Database License (ODbL) 1.0 (http://opendatacommons.org/licenses/odbl/1-0/)',
    'copyright': 'http://www.openstreetmap.org/copyright',
    'download_date_utc': '2026-10-25T18:45:00Z',
    'crs': 'WGS84 (EPSG:4326)',
    'tiles': tiles
}

manifest_path = os.path.join(PROJECT_ROOT, "data", "network", "source_manifest.json")
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

print(f"Manifest saved to: {manifest_path}")
