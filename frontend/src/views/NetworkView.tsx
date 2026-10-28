import React, { useState, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ErrorBar } from 'recharts';
import resilienceRaw from '../data/resilience_results.json';
import bridgesRaw from '../data/bridges.json';

// Real schema from resilience_results.json
interface ResilienceRecord {
  scenario_name: string;
  n_draws: number;
  mean_delta_cost: number;
  std_delta_cost: number;
  sem_delta_cost: number;
  ci_lower_2_5: number;
  ci_upper_97_5: number;
  median_delta_cost: number;
  baseline_mean_cost: number;
  closure_mean_cost: number;
  disconnected_od_count: number;
  total_od_count: number;
  runtime_seconds: number;
}

// Real schema from bridges.json
interface BridgeRecord {
  edge_id: string;
  u: number;
  v: number;
  u_lat: number;
  u_lon: number;
  v_lat: number;
  v_lon: number;
  name: string;
  highway: string;
  length_m: number;
  speed_mps: number;
  free_flow_time_sec: number;
}

const RESILIENCE = resilienceRaw as ResilienceRecord[];
const BRIDGES = bridgesRaw as BridgeRecord[];
const BRIDGE_NAMES = [...new Set(BRIDGES.map(b => b.name))];
const DRAWS_OPTIONS = [...new Set(RESILIENCE.map(r => r.n_draws))].sort((a,b) => a-b);
const SCENARIO_COLORS = ['#22d3ee','#a78bfa','#34d399','#fb923c','#f472b6','#fbbf24'];

// Human-readable scenario label
const scenarioLabel = (s: string) => s.replace(/_/g,' ').replace('CLOSURE','').trim();

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as ResilienceRecord;
  return (
    <div className="bg-slate-900/95 border border-slate-700 rounded-xl px-4 py-3 shadow-xl text-xs">
      <p className="text-slate-200 font-semibold mb-2">{scenarioLabel(d.scenario_name)}</p>
      <p className="text-cyan-300">Mean Δ cost: +{d.mean_delta_cost.toFixed(1)} s</p>
      <p className="text-violet-300">95% CI: [{d.ci_lower_2_5.toFixed(1)}, {d.ci_upper_97_5.toFixed(1)}]</p>
      <p className="text-rose-300">Disconnected OD pairs: {d.disconnected_od_count.toLocaleString()} / {d.total_od_count.toLocaleString()}</p>
      <p className="text-amber-300">n_draws: {d.n_draws.toLocaleString()}</p>
    </div>
  );
};

type MetricKey = 'mean_delta_cost' | 'disconnected_od_count' | 'closure_mean_cost' | 'baseline_mean_cost';

const METRIC_LABELS: Record<MetricKey, string> = {
  mean_delta_cost: 'Mean Routing Cost Δ (s)',
  disconnected_od_count: 'Disconnected OD Pairs',
  closure_mean_cost: 'Post-closure Mean Cost (s)',
  baseline_mean_cost: 'Baseline Mean Cost (s)',
};

export const NetworkView: React.FC = () => {
  const [selectedDraws, setSelectedDraws] = useState<number>(DRAWS_OPTIONS[DRAWS_OPTIONS.length - 1]);
  const [metric, setMetric] = useState<MetricKey>('mean_delta_cost');
  const [bridgeFilter, setBridgeFilter] = useState('all');

  const filteredResilience = useMemo(() =>
    RESILIENCE.filter(r => r.n_draws === selectedDraws),
    [selectedDraws]
  );

  const chartData = useMemo(() =>
    filteredResilience.map((r, i) => ({
      ...r,
      label: scenarioLabel(r.scenario_name),
      value: r[metric],
      color: SCENARIO_COLORS[i % SCENARIO_COLORS.length],
    })),
    [filteredResilience, metric]
  );

  const filteredBridges = useMemo(() =>
    BRIDGES.filter(b => bridgeFilter === 'all' || b.name === bridgeFilter),
    [bridgeFilter]
  );

  return (
    <section id="network" className="min-h-screen pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-2">Glasgow Road Network & Bridge Resilience</h2>
          <p className="text-slate-400 text-sm max-w-2xl">
            Simulated River Clyde bridge-closure scenarios on an OSM-derived road network (1,327 nodes, 3,201 edges).
            Results show Dijkstra-modelled routing cost changes and OD pair disconnections — not measured real-world travel times.
          </p>
        </div>

        {/* Network stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Graph Nodes', value: '1,327', color: 'cyan' },
            { label: 'Graph Edges', value: '3,201', color: 'violet' },
            { label: 'Bridge Edges Modelled', value: BRIDGES.length.toString(), color: 'amber' },
            { label: 'Unique Bridge Crossings', value: BRIDGE_NAMES.length.toString(), color: 'emerald' },
          ].map(({ label, value, color }) => (
            <div key={label} className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-4 text-center">
              <div className={`text-xl font-bold mb-1 ${
                color === 'cyan' ? 'text-cyan-400' : color === 'violet' ? 'text-violet-400' :
                color === 'amber' ? 'text-amber-400' : 'text-emerald-400'
              }`}>{value}</div>
              <div className="text-xs text-slate-400">{label}</div>
            </div>
          ))}
        </div>

        {/* Monte Carlo results chart */}
        <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-6 mb-6">
          <h3 className="text-sm font-semibold text-slate-200 mb-1">Monte Carlo Bridge-Closure Simulation Results</h3>
          <p className="text-xs text-slate-500 mb-5">
            Modelled routing impact of each bridge closure. Costs are in seconds on OSM free-flow travel-time edge weights.
            These are modelled differences — not measured real-world journey time changes.
          </p>

          <div className="flex flex-wrap gap-4 mb-6">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Monte Carlo draws:</span>
              {DRAWS_OPTIONS.map(d => (
                <button key={d} onClick={() => setSelectedDraws(d)}
                  className={`px-3 py-1 rounded-full text-xs font-mono border transition-all ${
                    selectedDraws === d ? 'border-violet-500/60 text-violet-300 bg-violet-950/40' : 'border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-400'
                  }`}>{d.toLocaleString()}</button>
              ))}
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-slate-400">Metric:</span>
              {(Object.entries(METRIC_LABELS) as [MetricKey, string][]).map(([key, label]) => (
                <button key={key} onClick={() => setMetric(key)}
                  className={`px-3 py-1 rounded-lg text-xs border transition-all ${
                    metric === key ? 'border-amber-500/60 text-amber-300 bg-amber-950/40' : 'border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-400'
                  }`}>{label}</button>
              ))}
            </div>
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 30, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="label" tick={{ fill: '#94a3b8', fontSize: 10 }} angle={-15} textAnchor="end" interval={0} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" name={METRIC_LABELS[metric]} radius={[4,4,0,0]}>
                {chartData.map((d, i) => (
                  <Cell key={i} fill={d.color} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Results table */}
        <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-6 mb-6 overflow-x-auto">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">
            Scenario Results — {selectedDraws.toLocaleString()} draws
          </h3>
          <table className="w-full text-xs min-w-[700px]">
            <thead>
              <tr className="text-slate-500 border-b border-slate-800">
                <th className="text-left py-2 font-medium">Scenario</th>
                <th className="text-right py-2 font-medium">Mean Δ (s)</th>
                <th className="text-right py-2 font-medium">95% CI lower</th>
                <th className="text-right py-2 font-medium">95% CI upper</th>
                <th className="text-right py-2 font-medium">Disconnected OD</th>
                <th className="text-right py-2 font-medium">Total OD</th>
                <th className="text-right py-2 font-medium">% Disconnected</th>
              </tr>
            </thead>
            <tbody>
              {filteredResilience.map((r, i) => (
                <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30">
                  <td className="py-2 font-semibold" style={{ color: SCENARIO_COLORS[i % SCENARIO_COLORS.length] }}>
                    {scenarioLabel(r.scenario_name)}
                  </td>
                  <td className="text-right py-2 text-cyan-300">+{r.mean_delta_cost.toFixed(2)}</td>
                  <td className="text-right py-2 text-slate-400">{r.ci_lower_2_5.toFixed(2)}</td>
                  <td className="text-right py-2 text-slate-400">{r.ci_upper_97_5.toFixed(2)}</td>
                  <td className="text-right py-2 text-rose-300">{r.disconnected_od_count.toLocaleString()}</td>
                  <td className="text-right py-2 text-slate-400">{r.total_od_count.toLocaleString()}</td>
                  <td className="text-right py-2 text-amber-300">
                    {((r.disconnected_od_count / r.total_od_count) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Bridge edge inventory */}
        <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-6 mb-6 overflow-x-auto">
          <h3 className="text-sm font-semibold text-slate-200 mb-1">River Clyde Bridge Edge Inventory</h3>
          <p className="text-xs text-slate-500 mb-4">OSM-derived crossing edges (ODbL 1.0 — © OpenStreetMap contributors). Multiple edges per bridge reflect directional road graph.</p>
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="text-xs text-slate-400">Filter:</span>
            {['all', ...BRIDGE_NAMES].map(n => (
              <button key={n} onClick={() => setBridgeFilter(n)}
                className={`px-3 py-1 rounded-full text-xs border transition-all ${
                  bridgeFilter === n ? 'border-cyan-500/60 text-cyan-300 bg-cyan-950/40' : 'border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-400'
                }`}>{n}</button>
            ))}
          </div>
          <table className="w-full text-xs min-w-[650px]">
            <thead>
              <tr className="text-slate-500 border-b border-slate-800">
                <th className="text-left py-2 font-medium">Name</th>
                <th className="text-left py-2 font-medium">Edge ID</th>
                <th className="text-left py-2 font-medium">Road Type</th>
                <th className="text-right py-2 font-medium">Length (m)</th>
                <th className="text-right py-2 font-medium">Speed (m/s)</th>
                <th className="text-right py-2 font-medium">Free-flow (s)</th>
              </tr>
            </thead>
            <tbody>
              {filteredBridges.slice(0, 20).map((b, i) => (
                <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30">
                  <td className="py-2 font-semibold text-slate-300">{b.name}</td>
                  <td className="py-2 font-mono text-slate-500 text-xs">{b.edge_id}</td>
                  <td className="py-2 text-slate-400">{b.highway}</td>
                  <td className="text-right py-2 text-slate-300">{b.length_m.toFixed(0)}</td>
                  <td className="text-right py-2 text-slate-400">{b.speed_mps.toFixed(1)}</td>
                  <td className="text-right py-2 text-slate-400">{b.free_flow_time_sec.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredBridges.length > 20 && <p className="text-xs text-slate-600 mt-2">Showing 20 of {filteredBridges.length} edges.</p>}
        </div>

        <div className="rounded-xl bg-slate-900/40 border border-slate-800/40 p-5 text-xs text-slate-400">
          <p className="font-semibold text-slate-300 mb-2">Network & Routing Assumptions</p>
          <ul className="space-y-1.5 list-disc list-inside">
            <li>Road network extracted from OpenStreetMap (ODbL 1.0) via OSMnx. Reflects OSM data at extraction time.</li>
            <li>Routing uses Dijkstra shortest-path on OSM travel-time edge weights — not empirically calibrated journey-time data.</li>
            <li>Simulated closures remove identified bridge edges; cascading failures and traffic redistribution are not modelled.</li>
            <li>Cost deltas are in modelled free-flow seconds — not measured real-world travel time increases.</li>
            <li>"Disconnected OD pairs" are graph-theoretically unreachable after edge removal, not observed traffic interruptions.</li>
          </ul>
        </div>
      </div>
    </section>
  );
};
