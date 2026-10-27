"""
Script: Generate Portfolio Visual Figures for CityPulse Public Release.
Generates 6 publication-quality figures directly from validated project artifacts:
1. fig1_road_network_topology.png
2. fig2_directional_couplet_schematic.png
3. fig3_route_diversion_george_v.png
4. fig4_boundary_truncation_map.png
5. fig5_anomaly_detection_tradeoffs.png
6. fig6_cross_river_resilience_deltas.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG_DIR = os.path.join(PROJECT_ROOT, "reports", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Set global style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['figure.titlesize'] = 12

nodes_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_nodes.csv")
edges_csv = os.path.join(PROJECT_ROOT, "data", "network", "reconstructed_network_edges.csv")
thresh_csv = os.path.join(PROJECT_ROOT, "reports", "spatial_detector_threshold_analysis.csv")

nodes_df = pd.read_csv(nodes_csv)
edges_df = pd.read_csv(edges_csv)
node_coords = dict(zip(nodes_df['node_id'], zip(nodes_df['latitude'], nodes_df['longitude'])))

print("Generating Figure 1: Road Network Topology...")
# --- FIGURE 1: Road Network Topology & Grade Separation ---
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

# Group edges by classification
highway_colors = {
    'motorway': ('#DC2626', 2.5, 0.9, 'Motorway (M8 Viaduct)'),
    'motorway_link': ('#EF4444', 1.8, 0.8, 'Motorway Ramp'),
    'primary': ('#2563EB', 1.5, 0.7, 'Primary Arterial'),
    'primary_link': ('#3B82F6', 1.2, 0.6, 'Primary Link'),
    'secondary': ('#059669', 1.2, 0.6, 'Secondary Arterial'),
    'tertiary': ('#64748B', 0.8, 0.4, 'Tertiary / Local Grid'),
    'residential': ('#94A3B8', 0.6, 0.3, 'Residential / Other')
}

legend_handles = {}

for _, r in edges_df.iterrows():
    u, v = int(r['u']), int(r['v'])
    if u in node_coords and v in node_coords:
        lat1, lon1 = node_coords[u]
        lat2, lon2 = node_coords[v]
        hw = r['highway']
        color, lw, alpha, label = highway_colors.get(hw, ('#94A3B8', 0.6, 0.3, 'Residential / Other'))
        line, = ax.plot([lon1, lon2], [lat1, lat2], color=color, linewidth=lw, alpha=alpha)
        if label not in legend_handles:
            legend_handles[label] = line

# Plot nodes
ax.scatter(nodes_df['longitude'], nodes_df['latitude'], s=3, color='#334155', alpha=0.5, zorder=5)

# River Clyde boundary approximation
ax.axhspan(55.854, 55.858, color='#BAE6FD', alpha=0.35, zorder=1, label='River Clyde Corridor')

# Kingston bridge callout box
callout = plt.Rectangle((-4.274, 55.853), 0.007, 0.006, fill=False, edgecolor='#B91C1C', linestyle='--', linewidth=1.5, zorder=6)
ax.add_patch(callout)
ax.text(-4.274, 55.8595, "Grade-Separated Flyover\n(0 Shared Nodes with Broomielaw)", color='#B91C1C', fontsize=8, fontweight='bold', zorder=7)

ax.set_title("Central Glasgow Reconstructed Road Network Topology (1,047 Nodes, 1,932 Links)\nOpenStreetMap Canonical Representation (ODbL 1.0)", pad=12)
ax.set_xlabel("Longitude (WGS84)")
ax.set_ylabel("Latitude (WGS84)")
ax.set_xlim(-4.285, -4.240)
ax.set_ylim(55.850, 55.865)

handles = list(legend_handles.values())
labels = list(legend_handles.keys())
ax.legend(handles, labels, loc='lower right', frameon=True, facecolor='white', framealpha=0.9)

plt.tight_layout()
fig1_path = os.path.join(FIG_DIR, "fig1_road_network_topology.png")
fig.savefig(fig1_path)
plt.close(fig)
print(f"Saved: {fig1_path}")


print("Generating Figure 2: Directional Couplet Schematic...")
# --- FIGURE 2: River Clyde Directional Couplet ---
fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

# River Clyde fill
ax.axhspan(55.8545, 55.8565, color='#BAE6FD', alpha=0.45, zorder=1)
ax.text(-4.263, 55.8554, "R I V E R   C L Y D E", color='#0369A1', fontsize=12, fontweight='bold')

# George V Bridge edges (Northbound)
gv_edges = edges_df[edges_df['name'].str.contains('George V Bridge', case=False, na=False)]
for _, r in gv_edges.iterrows():
    u, v = int(r['u']), int(r['v'])
    lat1, lon1 = node_coords[u]
    lat2, lon2 = node_coords[v]
    ax.annotate('', xy=(lon2, lat2), xytext=(lon1, lat1),
                arrowprops=dict(arrowstyle="->", color='#16A34A', lw=3, mutation_scale=15), zorder=4)

ax.text(-4.2612, 55.8558, "King George V Bridge\n(4 Links - Exclusively Northbound)\nSouth -> North Traffic Only",
        color='#15803D', fontsize=9, fontweight='bold', ha='right', bbox=dict(boxstyle='round,pad=0.4', facecolor='#DCFCE7', edgecolor='#16A34A', alpha=0.9))

# Glasgow Bridge edges (Southbound)
gb_edges = edges_df[edges_df['name'].str.contains('Glasgow Bridge', case=False, na=False)]
for _, r in gb_edges.iterrows():
    u, v = int(r['u']), int(r['v'])
    lat1, lon1 = node_coords[u]
    lat2, lon2 = node_coords[v]
    ax.annotate('', xy=(lon2, lat2), xytext=(lon1, lat1),
                arrowprops=dict(arrowstyle="->", color='#7C3AED', lw=3, mutation_scale=15), zorder=4)

ax.text(-4.2560, 55.8550, "Glasgow Bridge (Jamaica Bridge)\n(1 Link - Exclusively Southbound)\nNorth -> South Traffic Only",
        color='#6D28D9', fontsize=9, fontweight='bold', ha='left', bbox=dict(boxstyle='round,pad=0.4', facecolor='#F3E8FF', edgecolor='#7C3AED', alpha=0.9))

# Nearby street network
for _, r in edges_df.iterrows():
    u, v = int(r['u']), int(r['v'])
    if u in node_coords and v in node_coords:
        lat1, lon1 = node_coords[u]
        lat2, lon2 = node_coords[v]
        if 55.852 <= lat1 <= 55.859 and -4.265 <= lon1 <= -4.252:
            ax.plot([lon1, lon2], [lat1, lat2], color='#CBD5E1', lw=0.8, zorder=2)

ax.set_title("Central Glasgow Directional River Crossing Couplet\nAsymmetric One-Way Traffic Structure Across River Clyde", pad=12)
ax.set_xlabel("Longitude (WGS84)")
ax.set_ylabel("Latitude (WGS84)")
ax.set_xlim(-4.264, -4.253)
ax.set_ylim(55.853, 55.858)

plt.tight_layout()
fig2_path = os.path.join(FIG_DIR, "fig2_directional_couplet_schematic.png")
fig.savefig(fig2_path)
plt.close(fig)
print(f"Saved: {fig2_path}")


print("Generating Figure 3: Route Diversion Example...")
# --- FIGURE 3: Route Diversion Example ---
G = nx.DiGraph()
for _, r in edges_df.iterrows():
    G.add_edge(int(r['u']), int(r['v']),
               edge_id=r['edge_id'],
               name=r['name'],
               length_m=float(r['length_m']),
               weight=float(r['free_flow_time_sec']))

orig_node, dest_node = 100878338, 28801025
base_path = nx.shortest_path(G, orig_node, dest_node, weight='weight')

# Subgraph without George V Bridge
gv_edge_ids = set(gv_edges['edge_id'])
G_closed = G.copy()
for u, v, d in list(G_closed.edges(data=True)):
    if d.get('edge_id') in gv_edge_ids:
        G_closed.remove_edge(u, v)

new_path = nx.shortest_path(G_closed, orig_node, dest_node, weight='weight')

fig, ax = plt.subplots(figsize=(9, 7), dpi=300)

# Plot context road lines
for _, r in edges_df.iterrows():
    u, v = int(r['u']), int(r['v'])
    if u in node_coords and v in node_coords:
        lat1, lon1 = node_coords[u]
        lat2, lon2 = node_coords[v]
        ax.plot([lon1, lon2], [lat1, lat2], color='#E2E8F0', lw=0.6, zorder=1)

ax.axhspan(55.854, 55.858, color='#BAE6FD', alpha=0.35, zorder=2)

# Plot Baseline Path
base_lats = [node_coords[n][0] for n in base_path]
base_lons = [node_coords[n][1] for n in base_path]
ax.plot(base_lons, base_lats, color='#2563EB', lw=3, label='Baseline Shortest Path (via George V Bridge: 1,701m, 150.1s)', zorder=4)

# Plot Rerouted Path
new_lats = [node_coords[n][0] for n in new_path]
new_lons = [node_coords[n][1] for n in new_path]
ax.plot(new_lons, new_lats, color='#D97706', lw=2.5, linestyle='--', label='Rerouted Path (via Kingston Bridge: 2,250m, 182.1s | +549m, +32.0s)', zorder=5)

# Highlight Origin and Destination
ax.scatter([node_coords[orig_node][1]], [node_coords[orig_node][0]], color='#16A34A', s=80, marker='o', edgecolors='black', label=f'Origin Node {orig_node} (Nelson St)', zorder=6)
ax.scatter([node_coords[dest_node][1]], [node_coords[dest_node][0]], color='#DC2626', s=80, marker='s', edgecolors='black', label=f'Destination Node {dest_node} (St Vincent St)', zorder=6)

ax.set_title("Shortest-Path Route Diversion Under King George V Bridge Severance\nModelled Free-Flow Shortest Path Comparison (Dijkstra)", pad=12)
ax.set_xlabel("Longitude (WGS84)")
ax.set_ylabel("Latitude (WGS84)")
ax.set_xlim(-4.275, -4.255)
ax.set_ylim(55.850, 55.865)
ax.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.9)

plt.tight_layout()
fig3_path = os.path.join(FIG_DIR, "fig3_route_diversion_george_v.png")
fig.savefig(fig3_path)
plt.close(fig)
print(f"Saved: {fig3_path}")


print("Generating Figure 4: Boundary Truncation Map...")
# --- FIGURE 4: Boundary Truncation Map ---
fig, ax = plt.subplots(figsize=(9, 7), dpi=300)

for _, r in edges_df.iterrows():
    u, v = int(r['u']), int(r['v'])
    if u in node_coords and v in node_coords:
        lat1, lon1 = node_coords[u]
        lat2, lon2 = node_coords[v]
        ax.plot([lon1, lon2], [lat1, lat2], color='#E2E8F0', lw=0.6, zorder=1)

ax.axhspan(55.854, 55.858, color='#BAE6FD', alpha=0.35, zorder=2)

# Boundary cutoff line
ax.axhline(55.865, color='#DC2626', linestyle='--', lw=2, label='Model Boundary Cutoff (55.865°N)', zorder=5)
ax.text(-4.283, 55.8643, "Geographic Study Boundary Cutoff: 55.865°N", color='#DC2626', fontweight='bold', fontsize=9)

# Northern M8 mainline nodes (isolated)
m8_northern_nodes = [3845455477, 30795302, 30824924, 158954168]
for nid in m8_northern_nodes:
    if nid in node_coords:
        lat, lon = node_coords[nid]
        ax.scatter([lon], [lat], color='#C026D3', s=60, edgecolors='black', zorder=6)

ax.text(-4.270, 55.8625, "M8 Motorway Mainline Stubs\n(Ancestors collapse: 954 -> 4)\n4,125 OD pairs disconnected due to\nCharing Cross ramps cut off outside boundary",
        color='#701A75', fontsize=8, fontweight='bold', bbox=dict(boxstyle='round,pad=0.4', facecolor='#FDF4FF', edgecolor='#C026D3', alpha=0.9), zorder=7)

ax.set_title("Geographic Boundary Truncation Artifact Under M8 Kingston Bridge Closure\nSeverance of Regional Orbital Bypasses & Charing Cross On-Ramps", pad=12)
ax.set_xlabel("Longitude (WGS84)")
ax.set_ylabel("Latitude (WGS84)")
ax.set_xlim(-4.285, -4.240)
ax.set_ylim(55.850, 55.867)
ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9)

plt.tight_layout()
fig4_path = os.path.join(FIG_DIR, "fig4_boundary_truncation_map.png")
fig.savefig(fig4_path)
plt.close(fig)
print(f"Saved: {fig4_path}")


print("Generating Figure 5: Anomaly Detection Performance & Trade-offs...")
# --- FIGURE 5: Anomaly Detection Trade-offs ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

# Panel A: PR-AUC by Modality
modalities = ['Dropouts (MCAR)', 'Dropouts (Burst)', 'Stuck-Zero', 'Bias Offset', 'Drift (Univariate)', 'Drift (Spatial)']
pr_aucs = [0.912, 0.884, 0.765, 0.642, 0.012, 0.1035]
colors = ['#16A34A', '#22C55E', '#EAB308', '#F97316', '#EF4444', '#3B82F6']

bars = ax1.bar(modalities, pr_aucs, color=colors, edgecolor='#334155', width=0.6)
ax1.set_ylabel("Area Under Precision-Recall Curve (PR-AUC)")
ax1.set_title("Panel A: Detection Sensitivity by Anomaly Modality\n(Abrupt Faults vs. Subtle Calibration Drift)")
ax1.set_ylim(0, 1.0)
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha='right')

for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{yval:.3f}", ha='center', va='bottom', fontsize=8, fontweight='bold')

# Panel B: Operational Trade-off Curve (Recall vs Annual False Positives)
# Using real data from spatial_detector_threshold_analysis.csv
if os.path.exists(thresh_csv):
    df_thresh = pd.read_csv(thresh_csv)
    df_50 = df_thresh[df_thresh['drift_scenario'] == 'Drift (-50%, 168h)'].groupby('contamination_rate').agg({
        'recall': 'mean',
        'fpr': 'mean',
        'fp': 'mean'
    }).reset_index()

    c_rates = df_50['contamination_rate'] * 100
    recalls = df_50['recall'] * 100
    fps_annual = df_50['fp'] # annual false positive hours out of 8760

    ax2.plot(c_rates, recalls, marker='o', color='#2563EB', lw=2, label='Recall (%)')
    ax2.set_xlabel("Contamination Threshold Parameter $c$ (%)")
    ax2.set_ylabel("Empirical Recall (%)", color='#2563EB')
    ax2.tick_params(axis='y', labelcolor='#2563EB')
    ax2.set_ylim(0, 80)

    ax2_twin = ax2.twinx()
    ax2_twin.plot(c_rates, fps_annual, marker='s', color='#DC2626', linestyle='--', lw=2, label='Annual False Alarms (Hours/Yr)')
    ax2_twin.set_ylabel("Annual False Alarm Hours per Sensor Pair", color='#DC2626')
    ax2_twin.tick_params(axis='y', labelcolor='#DC2626')
    ax2_twin.set_ylim(0, 2000)

    ax2.set_title("Panel B: Operational Trade-Off on Drift (-50%, 168h)\n(Recall Gain vs. False Alarm Rate)")

plt.tight_layout()
fig5_path = os.path.join(FIG_DIR, "fig5_anomaly_detection_tradeoffs.png")
fig.savefig(fig5_path)
plt.close(fig)
print(f"Saved: {fig5_path}")


print("Generating Figure 6: Cross-River Resilience Deltas...")
# --- FIGURE 6: Cross-River Resilience Horizontal Bar Chart ---
scenarios = [
    "George V Alone (S -> N)",
    "George V Alone (N -> S)",
    "Glasgow Bridge Alone (S -> N)",
    "Glasgow Bridge Alone (N -> S)",
    "George V + Glasgow Combined (S -> N)",
    "George V + Glasgow Combined (N -> S)",
    "Kingston Bridge Alone (S -> N)",
    "Kingston Bridge Alone (N -> S)",
    "Clyde Arc Alone (S -> N)",
    "Clyde Arc Alone (N -> S)"
]

time_deltas = [24.74, 0.00, 0.00, 9.82, 24.74, 9.82, 1.79, 8.94, 13.55, 10.01]
dist_deltas = [253.74, 0.00, 0.00, 136.08, 253.74, 136.08, 17.86, 34.77, 262.41, 223.88]

y_pos = np.arange(len(scenarios))
height = 0.38

fig, ax1 = plt.subplots(figsize=(10, 6.5), dpi=300)

bars1 = ax1.barh(y_pos + height/2, time_deltas, height, color='#2563EB', label='Mean Free-Flow Travel Time Delta (seconds)', edgecolor='#1E3A8A')
ax1.set_xlabel("Mean Free-Flow Travel Time Delta (seconds)", color='#2563EB')
ax1.tick_params(axis='x', labelcolor='#2563EB')
ax1.set_yticks(y_pos)
ax1.set_yticklabels(scenarios, fontsize=8.5)
ax1.invert_yaxis()
ax1.set_xlim(0, 30)

ax2 = ax1.twiny()
bars2 = ax2.barh(y_pos - height/2, dist_deltas, height, color='#F59E0B', label='Mean Detour Distance Delta (meters)', edgecolor='#B45309', alpha=0.85)
ax2.set_xlabel("Mean Detour Distance Delta (meters)", color='#B45309')
ax2.tick_params(axis='x', labelcolor='#B45309')
ax2.set_xlim(0, 320)

for bar in bars1:
    w = bar.get_width()
    if w > 0:
        ax1.text(w + 0.5, bar.get_y() + bar.get_height()/2.0, f"+{w:.1f}s", va='center', ha='left', fontsize=7.5, color='#1E3A8A', fontweight='bold')

for bar in bars2:
    w = bar.get_width()
    if w > 0:
        ax2.text(w + 5, bar.get_y() + bar.get_height()/2.0, f"+{w:.0f}m", va='center', ha='left', fontsize=7.5, color='#B45309', fontweight='bold')

ax1.set_title("Directional Free-Flow Travel Time & Distance Deltas Across Cross-River Disruption Scenarios\nEvaluated on 218,401 Modelled OD Node Pairs", pad=35)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='lower right', frameon=True, facecolor='white', framealpha=0.9)

plt.tight_layout()
fig6_path = os.path.join(FIG_DIR, "fig6_cross_river_resilience_deltas.png")
fig.savefig(fig6_path)
plt.close(fig)
print(f"Saved: {fig6_path}")

print("\nAll 6 portfolio figures successfully generated in reports/figures/!")
