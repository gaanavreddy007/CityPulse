"""
CITYPULSE Phase 4.2: OpenStreetMap Graph Builder & Topology Constructor.
Parses official OSM XML tiles for the Glasgow Clyde corridor, identifies shared intersection
junctions, splits ways into topological edges, computes exact piecewise geodetic lengths,
applies directional restrictions, and outputs:
- data/network/reconstructed_network_nodes.csv
- data/network/reconstructed_network_edges.csv
"""

import os
import sys
import math
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any
import pandas as pd
import numpy as np

PROJECT_ROOT = r"C:\Gaanav\Projects\CityPulse"
raw_osm_dir = os.path.join(PROJECT_ROOT, "data", "network", "raw_osm")
network_dir = os.path.join(PROJECT_ROOT, "data", "network")

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two points in meters using Haversine formula."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

VEHICULAR_HIGHWAYS = {
    'motorway', 'motorway_link',
    'trunk', 'trunk_link',
    'primary', 'primary_link',
    'secondary', 'secondary_link',
    'tertiary', 'tertiary_link',
    'residential', 'unclassified'
}

SPEED_LOOKUP_MPS = {
    'motorway': 22.2,       # ~80 km/h (50 mph)
    'motorway_link': 13.4,  # ~48 km/h (30 mph)
    'trunk': 17.8,          # ~64 km/h (40 mph)
    'trunk_link': 11.1,     # ~40 km/h (25 mph)
    'primary': 13.4,        # ~48 km/h (30 mph)
    'primary_link': 11.1,
    'secondary': 11.1,      # ~40 km/h (25 mph)
    'secondary_link': 8.9,
    'tertiary': 8.9,        # ~32 km/h (20 mph)
    'tertiary_link': 8.9,
    'residential': 8.9,
    'unclassified': 8.9
}

CAPACITY_PER_LANE = {
    'motorway': 1800.0,
    'motorway_link': 1400.0,
    'trunk': 1400.0,
    'trunk_link': 1000.0,
    'primary': 900.0,
    'primary_link': 800.0,
    'secondary': 700.0,
    'secondary_link': 600.0,
    'tertiary': 500.0,
    'tertiary_link': 500.0,
    'residential': 400.0,
    'unclassified': 400.0
}

DEFAULT_LANES = {
    'motorway': 4,
    'motorway_link': 1,
    'trunk': 2,
    'trunk_link': 1,
    'primary': 2,
    'primary_link': 1,
    'secondary': 2,
    'secondary_link': 1,
    'tertiary': 1,
    'tertiary_link': 1,
    'residential': 1,
    'unclassified': 1
}

def parse_osm_files():
    osm_files = [
        os.path.join(raw_osm_dir, "central_core.osm"),
        os.path.join(raw_osm_dir, "clyde_arc_west.osm")
    ]
    
    nodes: Dict[int, Tuple[float, float]] = {}
    ways: Dict[int, Dict[str, Any]] = {}
    node_usage = defaultdict(int)

    for osm_file in osm_files:
        print(f"Parsing: {osm_file}...")
        context = ET.iterparse(osm_file, events=('end',))
        for event, elem in context:
            if elem.tag == 'node':
                node_id = int(elem.attrib['id'])
                lat = float(elem.attrib['lat'])
                lon = float(elem.attrib['lon'])
                nodes[node_id] = (lat, lon)
                elem.clear()
            elif elem.tag == 'way':
                way_id = int(elem.attrib['id'])
                if way_id in ways:
                    elem.clear()
                    continue
                
                tags = {}
                nd_refs = []
                for child in elem:
                    if child.tag == 'nd':
                        nd_refs.append(int(child.attrib['ref']))
                    elif child.tag == 'tag':
                        tags[child.attrib['k']] = child.attrib['v']
                
                h_type = tags.get('highway')
                if h_type in VEHICULAR_HIGHWAYS and len(nd_refs) >= 2:
                    ways[way_id] = {
                        'id': way_id,
                        'nodes': nd_refs,
                        'tags': tags,
                        'highway': h_type
                    }
                    for n in nd_refs:
                        node_usage[n] += 1
                elem.clear()

    print(f"Total Unique Nodes in Bounding Box: {len(nodes):,}")
    print(f"Total Vehicular Ways: {len(ways):,}")
    
    # Identify intersection junctions
    intersection_nodes = set()
    for way_id, w in ways.items():
        refs = w['nodes']
        # Endpoints are always topological junctions
        intersection_nodes.add(refs[0])
        intersection_nodes.add(refs[-1])
        # Internal nodes appearing in multiple ways are junctions
        for n in refs[1:-1]:
            if node_usage[n] > 1:
                intersection_nodes.add(n)
                
    print(f"Identified Shared Intersection Junction Nodes: {len(intersection_nodes):,}")
    
    # Split ways into topological graph edges between junctions
    edges = []
    active_nodes = set()
    edge_counter = 0

    for way_id, w in ways.items():
        refs = w['nodes']
        tags = w['tags']
        h_type = w['highway']
        name = tags.get('name', tags.get('ref', f"Unnamed {h_type}"))
        is_bridge = (tags.get('bridge') == 'yes')
        
        # Determine lanes
        try:
            lanes = int(tags.get('lanes', DEFAULT_LANES.get(h_type, 2)))
        except (ValueError, TypeError):
            lanes = DEFAULT_LANES.get(h_type, 2)
            
        # Determine one-way rule
        oneway_tag = tags.get('oneway', '').lower()
        junction_tag = tags.get('junction', '').lower()
        if oneway_tag in ['yes', '1', 'true']:
            is_oneway = True
            is_reverse = False
        elif oneway_tag in ['-1', 'reverse']:
            is_oneway = True
            is_reverse = True
        elif junction_tag == 'roundabout':
            is_oneway = True
            is_reverse = False
        elif h_type in ['motorway', 'motorway_link'] and oneway_tag != 'no':
            is_oneway = True
            is_reverse = False
        else:
            is_oneway = False
            is_reverse = False

        # Segment way between consecutive intersection junctions
        segment_nodes = [refs[0]]
        for n in refs[1:]:
            segment_nodes.append(n)
            if n in intersection_nodes:
                # We have reached an intersection junction
                u = segment_nodes[0]
                v = segment_nodes[-1]
                
                if u != v and u in nodes and v in nodes:
                    # Compute piecewise geodetic length
                    length_m = 0.0
                    valid_geom = True
                    for i in range(len(segment_nodes) - 1):
                        n1, n2 = segment_nodes[i], segment_nodes[i+1]
                        if n1 in nodes and n2 in nodes:
                            lat1, lon1 = nodes[n1]
                            lat2, lon2 = nodes[n2]
                            length_m += haversine_distance_m(lat1, lon1, lat2, lon2)
                        else:
                            valid_geom = False
                            break
                            
                    if valid_geom and length_m > 0.5: # filter degenerate sub-meter artifacts
                        speed_mps = SPEED_LOOKUP_MPS.get(h_type, 8.9)
                        free_flow_sec = length_m / max(1.0, speed_mps)
                        cap_lane = CAPACITY_PER_LANE.get(h_type, 700.0)
                        capacity = lanes * cap_lane
                        
                        def add_edge_dir(start_n, end_n, dir_suffix):
                            nonlocal edge_counter
                            edge_counter += 1
                            edge_id = f"OSM_{way_id}_{start_n}_{end_n}"
                            edges.append({
                                'edge_id': edge_id,
                                'u': start_n,
                                'v': end_n,
                                'u_lat': nodes[start_n][0],
                                'u_lon': nodes[start_n][1],
                                'v_lat': nodes[end_n][0],
                                'v_lon': nodes[end_n][1],
                                'osm_way_id': way_id,
                                'name': name,
                                'highway': h_type,
                                'oneway': is_oneway,
                                'lanes': lanes,
                                'length_m': round(length_m, 2),
                                'speed_mps': round(speed_mps, 2),
                                'free_flow_time_sec': round(free_flow_sec, 2),
                                'capacity': round(capacity, 1),
                                'bridge': is_bridge
                            })
                            active_nodes.add(start_n)
                            active_nodes.add(end_n)

                        if is_reverse:
                            add_edge_dir(v, u, "rev")
                        elif is_oneway:
                            add_edge_dir(u, v, "fwd")
                        else:
                            add_edge_dir(u, v, "fwd")
                            add_edge_dir(v, u, "rev")

                # Reset for next segment
                segment_nodes = [n]

    edges_df = pd.DataFrame(edges)
    # Deduplicate in case identical (u, v) from way overlaps
    edges_df.drop_duplicates(subset=['u', 'v', 'highway'], inplace=True)
    
    # Filter active nodes
    nodes_df = pd.DataFrame([
        {'node_id': n, 'latitude': nodes[n][0], 'longitude': nodes[n][1]}
        for n in active_nodes if n in nodes
    ])
    
    out_edges_csv = os.path.join(network_dir, "reconstructed_network_edges.csv")
    out_nodes_csv = os.path.join(network_dir, "reconstructed_network_nodes.csv")
    
    edges_df.to_csv(out_edges_csv, index=False)
    nodes_df.to_csv(out_nodes_csv, index=False)
    
    print("\n" + "=" * 80)
    print("RECONSTRUCTED GLASGOW CLYDE CORRIDOR ROAD GRAPH SUMMARY")
    print("=" * 80)
    print(f"Total Active Graph Nodes: {len(nodes_df):,}")
    print(f"Total Directed Graph Edges: {len(edges_df):,}")
    print(f"Total One-Way Directed Edges: {(edges_df['oneway'] == True).sum():,}")
    print(f"Total Two-Way Directed Edges: {(edges_df['oneway'] == False).sum():,}")
    print(f"Bridge Edges Identified: {(edges_df['bridge'] == True).sum():,}")
    print(f"Edge Length Summary (meters): Min = {edges_df['length_m'].min():.1f}m, "
          f"Median = {edges_df['length_m'].median():.1f}m, "
          f"Mean = {edges_df['length_m'].mean():.1f}m, "
          f"Max = {edges_df['length_m'].max():.1f}m")
    print(f"Saved Edges CSV to: {out_edges_csv}")
    print(f"Saved Nodes CSV to: {out_nodes_csv}")
    
    # Check Bridge Identifications
    print("\n--- Key Bridge Representation Verification ---")
    bridge_names = [
        "Kingston Bridge", "George V Bridge", "Glasgow Bridge",
        "Victoria Bridge", "Albert Bridge", "Clyde Arc",
        "Broomielaw", "Argyle Street"
    ]
    for b in bridge_names:
        matches = edges_df[edges_df['name'].str.contains(b, case=False, na=False)]
        print(f"  {b:20s}: {len(matches):3d} directed edges | "
              f"Lanes: {matches['lanes'].unique().tolist()} | "
              f"Length: {matches['length_m'].sum():.1f}m total")

if __name__ == '__main__':
    parse_osm_files()
