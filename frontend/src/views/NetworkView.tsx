import React, { useState, useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';
import resilienceRaw from '../data/resilience_results.json';
import bridgesRaw from '../data/bridges.json';
import { Info, Navigation } from 'lucide-react';

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
const DRAWS_OPTIONS = [...new Set(RESILIENCE.map(r => r.n_draws))].sort((a, b) => a - b);

const scenarioLabel = (s: string) => s.replace(/_/g, ' ').replace('CLOSURE', '').trim();

const SCENARIO_COLORS = ['#1E3A8A', '#C25E2E', '#2D6A4F', '#B45309', '#6B21A8', '#4B5563'];

const ResilienceTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as ResilienceRecord & { label: string };
  return (
    <div className="bg-white border border-[#CEC8BD] rounded px-3 py-2.5 shadow-sm text-xs font-mono max-w-xs">
      <div className="font-semibold text-[#0D1117] border-b border-[#E2DDD5] pb-1 mb-1.5">{d.label}</div>
      <div className="space-y-1 text-[11px]">
        <div>Mean Routing Δ: <span className="font-semibold text-[#C25E2E]">+{d.mean_delta_cost.toFixed(2)} s</span></div>
        <div>95% CI: <span className="text-[#4A5568]">[{d.ci_lower_2_5.toFixed(1)}, {d.ci_upper_97_5.toFixed(1)}] s</span></div>
        <div>Disconnected ODs: <span className="font-semibold text-[#0D1117]">{d.disconnected_od_count.toLocaleString()} / {d.total_od_count.toLocaleString()}</span></div>
        <div className="text-[#718096]">Monte Carlo Draws: {d.n_draws.toLocaleString()}</div>
      </div>
    </div>
  );
};

export const NetworkView: React.FC = () => {
  const [selectedDraws, setSelectedDraws] = useState<number>(DRAWS_OPTIONS[DRAWS_OPTIONS.length - 1] ?? 500);
  const [metric, setMetric] = useState<'mean_delta' | 'disconnected'>('mean_delta');
  const [bridgeFilter, setBridgeFilter] = useState<string>('all');

  const filteredResilience = useMemo(
    () => RESILIENCE.filter(r => r.n_draws === selectedDraws),
    [selectedDraws]
  );

  const chartData = useMemo(() =>
    filteredResilience.map((r, i) => ({
      ...r,
      label: scenarioLabel(r.scenario_name),
      value: metric === 'mean_delta' ? r.mean_delta_cost : r.disconnected_od_count,
      color: SCENARIO_COLORS[i % SCENARIO_COLORS.length],
    })),
    [filteredResilience, metric]
  );

  const filteredBridges = useMemo(() =>
    bridgeFilter === 'all' ? BRIDGES : BRIDGES.filter(b => b.name === bridgeFilter),
    [bridgeFilter]
  );

  return (
    <section id="network" className="py-16 lg:py-20 border-t border-[#E2DDD5]">
      <div className="cp-container">

        {/* ── Section heading ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 mb-8 items-end">
          <div className="lg:col-span-4">
            <div className="text-section-label mb-2">04 · Graph Topology & Resilience</div>
            <h2 className="text-headline">Network Resilience Simulator</h2>
          </div>
          <div className="lg:col-span-8">
            <p className="text-sm text-[#4A5568] leading-relaxed max-w-2xl">
              Monte Carlo Dijkstra simulations evaluating rerouting cost and unreachable origin-destination pairs under simulated closures of major River Clyde crossings. Modelled at free-flow legal speed limits — not dynamic congestion queues.
            </p>
          </div>
        </div>

        {/* ── Key finding callout — editorial asymmetry ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8 items-start">

          {/* Chart surface */}
          <div className="lg:col-span-8 bg-white border border-[#E2DDD5] rounded overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E2DDD5] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="font-serif text-lg text-[#0D1117]">Cross-River Closure Impact</h3>
                <p className="text-xs text-[#718096] mt-0.5">
                  Modelled free-flow resistance increase across 218,401 cross-river node pairs.
                </p>
              </div>
              {/* Controls */}
              <div className="flex items-center gap-2.5 flex-wrap">
                <div className="flex items-center border border-[#CEC8BD] p-0.5 rounded bg-[#F2EEE6] text-xs">
                  <button
                    onClick={() => setMetric('mean_delta')}
                    className={`px-2.5 py-1 rounded transition-colors ${metric === 'mean_delta' ? 'bg-white font-semibold text-[#0D1117] shadow-sm' : 'text-[#4A5568]'}`}
                  >
                    Mean Δ Time (s)
                  </button>
                  <button
                    onClick={() => setMetric('disconnected')}
                    className={`px-2.5 py-1 rounded transition-colors ${metric === 'disconnected' ? 'bg-white font-semibold text-[#0D1117] shadow-sm' : 'text-[#4A5568]'}`}
                  >
                    Disconnected ODs
                  </button>
                </div>
                <div className="flex items-center gap-1.5 text-xs font-mono text-[#718096]">
                  <span>Draws:</span>
                  <select
                    value={selectedDraws}
                    onChange={e => setSelectedDraws(Number(e.target.value))}
                    className="border border-[#CEC8BD] rounded px-2 py-1 bg-white text-[#0D1117] text-xs font-mono"
                  >
                    {DRAWS_OPTIONS.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            <div className="p-4 sm:p-5">
              <div className="h-[280px] sm:h-[320px] w-full min-w-0">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, bottom: 44, left: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" vertical={false} />
                    <XAxis
                      dataKey="label"
                      tick={{ fill: '#718096', fontSize: 10 }}
                      interval={0}
                      angle={-18}
                      textAnchor="end"
                      tickLine={false}
                      axisLine={{ stroke: '#CEC8BD' }}
                    />
                    <YAxis tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }} width={45} />
                    <Tooltip content={<ResilienceTooltip />} />
                    <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                      {chartData.map((d, i) => (
                        <Cell key={i} fill={d.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Couplet asymmetry callout */}
          <div className="lg:col-span-4 space-y-4">
            <div className="bg-[#FAF8F4] border border-[#E2DDD5] rounded p-5">
              <div className="flex items-center gap-2 text-xs font-mono text-[#C25E2E] font-semibold mb-2">
                <Navigation size={13} />
                <span>Couplet Asymmetry Finding</span>
              </div>
              <h4 className="font-serif text-base text-[#0D1117] leading-snug mb-2">
                King George V vs. Glasgow Bridge
              </h4>
              <div className="text-xs text-[#4A5568] space-y-2 leading-relaxed">
                <p>
                  In central Glasgow, King George V Bridge operates strictly <strong className="text-[#0D1117]">northbound</strong>; Glasgow Bridge operates strictly <strong className="text-[#0D1117]">southbound</strong>.
                </p>
                <p>
                  Severing King George V Bridge impacts only South → North travel (+24.74 s mean on 69,693 rerouted pairs), causing 0.0 s delay in the reverse direction.
                </p>
                <p>
                  Even when both bridges are severed simultaneously, 100.0% of OD pairs remain reachable via Victoria and Kingston crossings.
                </p>
              </div>
              <div className="pt-2.5 mt-2.5 border-t border-[#E2DDD5] text-[10px] font-mono text-[#718096]">
                OSM Graph · 1,327 nodes · 3,201 edges
              </div>
            </div>

            {/* Small fig6 preview */}
            <div className="bg-white border border-[#E2DDD5] rounded overflow-hidden">
              <div className="bg-[#F2EEE6] p-2 flex items-center justify-center" style={{ height: '110px' }}>
                <img
                  src="./figures/fig6_cross_river_resilience_deltas.png"
                  alt="Cross-river resilience deltas"
                  className="h-full w-full object-contain"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/figures/fig6_cross_river_resilience_deltas.png';
                  }}
                />
              </div>
              <div className="px-3 py-1.5 border-t border-[#E2DDD5]">
                <p className="font-mono text-[10px] text-[#718096]">Fig. 6 · Cross-River Resilience Deltas</p>
              </div>
            </div>
          </div>
        </div>

        {/* ── Resilience results ledger ── */}
        <div className="bg-white border border-[#E2DDD5] rounded overflow-hidden mb-6">
          <div className="px-5 py-3 border-b border-[#E2DDD5] flex items-baseline justify-between">
            <h3 className="font-serif text-base text-[#0D1117]">Simulation Scenario Ledger</h3>
            <span className="text-xs font-mono text-[#718096]">
              Dijkstra · {selectedDraws.toLocaleString()} Monte Carlo draws
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs min-w-[650px]">
              <thead>
                <tr className="bg-[#FAF8F4] text-[#718096] font-mono text-[10px] border-b border-[#CEC8BD]">
                  <th className="text-left py-2 px-4 font-medium">Bridge Closure Scenario</th>
                  <th className="text-right py-2 px-2.5 font-medium">Mean Δ Time (s)</th>
                  <th className="text-right py-2 px-2.5 font-medium">95% CI Lower</th>
                  <th className="text-right py-2 px-2.5 font-medium">95% CI Upper</th>
                  <th className="text-right py-2 px-2.5 font-medium">Disconnected ODs</th>
                  <th className="text-right py-2 px-2.5 font-medium">Total ODs</th>
                  <th className="text-right py-2 px-4 font-medium">% Severed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2DDD5] font-mono text-[11px]">
                {filteredResilience.map((r, i) => (
                  <tr key={i} className="hover:bg-[#FAF8F4] transition-colors">
                    <td className="py-2 px-4 font-medium text-[#0D1117]">
                      <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: SCENARIO_COLORS[i % SCENARIO_COLORS.length] }} />
                        <span className="truncate">{scenarioLabel(r.scenario_name)}</span>
                      </div>
                    </td>
                    <td className="py-2 px-2.5 text-right font-semibold text-[#C25E2E]">+{r.mean_delta_cost.toFixed(2)} s</td>
                    <td className="py-2 px-2.5 text-right text-[#4A5568]">{r.ci_lower_2_5.toFixed(2)}</td>
                    <td className="py-2 px-2.5 text-right text-[#4A5568]">{r.ci_upper_97_5.toFixed(2)}</td>
                    <td className="py-2 px-2.5 text-right font-medium text-[#0D1117]">{r.disconnected_od_count.toLocaleString()}</td>
                    <td className="py-2 px-2.5 text-right text-[#718096]">{r.total_od_count.toLocaleString()}</td>
                    <td className="py-2 px-4 text-right text-[#B45309]">
                      {((r.disconnected_od_count / r.total_od_count) * 100).toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ── Bridge edge inventory ── */}
        <div className="bg-white border border-[#E2DDD5] rounded overflow-hidden mb-6">
          <div className="px-5 py-3 border-b border-[#E2DDD5] flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
            <div>
              <h3 className="font-serif text-base text-[#0D1117]">River Clyde Crossing Edge Inventory</h3>
              <p className="text-xs text-[#718096]">Directed edges in the OSM graph.</p>
            </div>
            <div className="flex items-center gap-1.5 flex-wrap text-xs">
              <span className="font-mono text-[#718096] text-[10px] uppercase tracking-wider">Filter:</span>
              {['all', ...BRIDGE_NAMES].map(n => (
                <button
                  key={n}
                  onClick={() => setBridgeFilter(n)}
                  className={`px-2 py-0.5 text-[11px] font-mono rounded border transition-colors ${
                    bridgeFilter === n
                      ? 'border-[#0D1117] bg-[#0D1117] text-white'
                      : 'border-[#CEC8BD] text-[#4A5568] bg-white hover:border-[#0D1117]'
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs min-w-[650px]">
              <thead>
                <tr className="bg-[#FAF8F4] text-[#718096] font-mono text-[10px] border-b border-[#CEC8BD]">
                  <th className="text-left py-2 px-4 font-medium">Bridge Name</th>
                  <th className="text-left py-2 px-2.5 font-medium">Edge ID</th>
                  <th className="text-left py-2 px-2.5 font-medium">Highway Class</th>
                  <th className="text-right py-2 px-2.5 font-medium">Length (m)</th>
                  <th className="text-right py-2 px-2.5 font-medium">Speed (m/s)</th>
                  <th className="text-right py-2 px-4 font-medium">Free-Flow (s)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2DDD5] font-mono text-[11px]">
                {filteredBridges.slice(0, 12).map((b, i) => (
                  <tr key={i} className="hover:bg-[#FAF8F4] transition-colors">
                    <td className="py-2 px-4 font-medium text-[#0D1117]">{b.name}</td>
                    <td className="py-2 px-2.5 text-[#718096]">{b.edge_id}</td>
                    <td className="py-2 px-2.5 text-[#4A5568]">{b.highway}</td>
                    <td className="py-2 px-2.5 text-right text-[#0D1117]">{b.length_m.toFixed(1)}</td>
                    <td className="py-2 px-2.5 text-right text-[#4A5568]">{b.speed_mps.toFixed(1)}</td>
                    <td className="py-2 px-4 text-right font-medium text-[#0D1117]">{b.free_flow_time_sec.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Boundary note */}
        <div className="border-t border-[#E2DDD5] pt-5 flex items-start gap-2.5 text-xs text-[#4A5568]">
          <Info size={14} className="text-[#C25E2E] shrink-0 mt-0.5" />
          <p className="leading-relaxed max-w-3xl">
            <span className="font-semibold text-[#0D1117]">Boundary Truncation Note: </span>
            The disconnected OD node pairs under M8 Kingston Bridge severance (3.73%) are confirmed boundary artifacts where the study bounding box truncates regional motorway bypasses north of the river — not complete civil isolation of affected areas.
          </p>
        </div>

      </div>
    </section>
  );
};
