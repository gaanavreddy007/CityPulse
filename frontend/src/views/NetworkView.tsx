import React, { useState, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import resilienceRaw from '../data/resilience_results.json';
import bridgesRaw from '../data/bridges.json';
import { MapPin, Navigation, Info, AlertTriangle } from 'lucide-react';

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

// Editorial scenario colors: Navy, Burnt Orange, Forest Green, Ochre, Charcoal
const SCENARIO_COLORS = ['#1E3A8A', '#C25E2E', '#2D6A4F', '#B45309', '#6B21A8', '#4B5563'];

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as ResilienceRecord;
  return (
    <div className="bg-white border border-[#D1C9BE] rounded px-3 py-2.5 shadow-sm text-xs font-mono max-w-xs">
      <div className="font-semibold text-[#111827] border-b border-[#E5E0D8] pb-1 mb-1.5">
        {scenarioLabel(d.scenario_name)}
      </div>
      <div className="space-y-1 text-[11px]">
        <div>Mean Routing Δ: <span className="font-semibold text-[#C25E2E]">+{d.mean_delta_cost.toFixed(2)} s</span></div>
        <div>95% Conf. Interval: <span className="text-[#4B5563]">[{d.ci_lower_2_5.toFixed(1)}, {d.ci_upper_97_5.toFixed(1)}] s</span></div>
        <div>Disconnected OD Pairs: <span className="font-semibold text-[#111827]">{d.disconnected_od_count.toLocaleString()} / {d.total_od_count.toLocaleString()}</span></div>
        <div className="text-[#6B7280]">Monte Carlo Draws: {d.n_draws.toLocaleString()}</div>
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

  const chartData = useMemo(() => {
    return filteredResilience.map((r, i) => ({
      ...r,
      label: scenarioLabel(r.scenario_name),
      value: metric === 'mean_delta' ? r.mean_delta_cost : r.disconnected_od_count,
      color: SCENARIO_COLORS[i % SCENARIO_COLORS.length],
    }));
  }, [filteredResilience, metric]);

  const filteredBridges = useMemo(() => {
    return bridgeFilter === 'all' ? BRIDGES : BRIDGES.filter(b => b.name === bridgeFilter);
  }, [bridgeFilter]);

  return (
    <section id="network" className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Heading */}
        <div className="max-w-3xl mb-8">
          <span className="text-xs font-mono uppercase tracking-wider text-[#C25E2E] font-semibold">
            Section 04 · Graph Topology & Resilience
          </span>
          <h2 className="font-serif text-2xl sm:text-3xl text-[#111827] mt-1 mb-2">
            Network Resilience Simulator: River Clyde Severances
          </h2>
          <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed">
            Monte Carlo shortest-path Dijkstra simulations evaluating network rerouting cost and unreachable origin-destination pairs under simulated closures of major River Clyde crossings in Glasgow.
          </p>
        </div>

        {/* Spatial Insight Panel: Directional Couplets */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8 items-start">
          <div className="lg:col-span-8 border border-[#E5E0D8] bg-white p-6 sm:p-8 rounded shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#E5E0D8] pb-4 mb-6 gap-3">
              <div>
                <h3 className="font-serif text-lg text-[#111827]">
                  Cross-River Closure Impact Comparison
                </h3>
                <p className="text-xs text-[#6B7280]">
                  Modelled free-flow resistance increase across 218,401 cross-river node pairs.
                </p>
              </div>

              {/* Controls */}
              <div className="flex items-center gap-3">
                <div className="flex items-center border border-[#D1C9BE] p-0.5 rounded bg-[#F4F1EA] text-xs">
                  <button
                    onClick={() => setMetric('mean_delta')}
                    className={`px-2.5 py-1 rounded transition-colors ${
                      metric === 'mean_delta' ? 'bg-white font-semibold text-[#111827] shadow-xs' : 'text-[#4B5563]'
                    }`}
                  >
                    Mean Δ Cost (s)
                  </button>
                  <button
                    onClick={() => setMetric('disconnected')}
                    className={`px-2.5 py-1 rounded transition-colors ${
                      metric === 'disconnected' ? 'bg-white font-semibold text-[#111827] shadow-xs' : 'text-[#4B5563]'
                    }`}
                  >
                    Unreachable ODs
                  </button>
                </div>

                <div className="flex items-center gap-1.5 text-xs font-mono text-[#6B7280]">
                  <span>Draws:</span>
                  <select
                    value={selectedDraws}
                    onChange={e => setSelectedDraws(Number(e.target.value))}
                    className="border border-[#D1C9BE] rounded px-2 py-1 bg-white text-[#111827] text-xs font-mono"
                  >
                    {DRAWS_OPTIONS.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Bar Chart Surface */}
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, bottom: 40, left: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" vertical={false} />
                  <XAxis
                    dataKey="label"
                    tick={{ fill: '#6B7280', fontSize: 11 }}
                    interval={0}
                    angle={-15}
                    textAnchor="end"
                    tickLine={false}
                    axisLine={{ stroke: '#D1C9BE' }}
                  />
                  <YAxis
                    tick={{ fill: '#6B7280', fontSize: 11 }}
                    tickLine={false}
                    axisLine={{ stroke: '#D1C9BE' }}
                    width={45}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                    {chartData.map((d, i) => (
                      <Cell key={i} fill={d.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Directional Couplet Explanatory Callout */}
          <div className="lg:col-span-4 border border-[#E5E0D8] bg-white p-6 rounded shadow-xs space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono text-[#C25E2E] font-semibold">
              <Navigation size={14} />
              <span>Couplet Asymmetry Finding</span>
            </div>
            <h4 className="font-serif text-base text-[#111827] leading-snug">
              King George V vs. Glasgow Bridge: One-Way Synchronization
            </h4>
            <div className="text-xs text-[#4B5563] space-y-2.5 leading-relaxed">
              <p>
                In central Glasgow, the King George V Bridge operates strictly northbound, while the adjacent Glasgow Bridge operates strictly southbound.
              </p>
              <p>
                <strong>Asymmetric disruption:</strong> Severing King George V Bridge impacts only South $\to$ North travel (+24.74 s mean on 69,693 rerouted pairs), causing 0.0 s delay in the reverse direction.
              </p>
              <p>
                <strong>Couplet Redundancy:</strong> Even when both bridges are severed simultaneously, 100.0% of OD pairs remain reachable via Victoria and Kingston crossings.
              </p>
            </div>

            <div className="pt-3 border-t border-[#E5E0D8] text-[11px] font-mono text-[#6B7280]">
              OSM Graph: 1,327 nodes · 3,201 edges
            </div>
          </div>
        </div>

        {/* Resilience Results Ledger */}
        <div className="border border-[#E5E0D8] bg-white rounded shadow-xs overflow-hidden mb-8">
          <div className="p-4 sm:p-5 border-b border-[#E5E0D8]">
            <h3 className="font-serif text-base text-[#111827]">
              Simulation Scenario Performance Ledger
            </h3>
            <p className="text-xs text-[#6B7280]">
              Dijkstra routing resistance evaluation with {selectedDraws.toLocaleString()} Monte Carlo draws.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs min-w-[700px]">
              <thead>
                <tr className="bg-[#F4F1EA] text-[#6B7280] font-mono text-[11px] border-b border-[#D1C9BE]">
                  <th className="text-left py-2.5 px-4 font-medium">Bridge Closure Scenario</th>
                  <th className="text-right py-2.5 px-4 font-medium">Mean Δ Time (s)</th>
                  <th className="text-right py-2.5 px-4 font-medium">95% CI Lower</th>
                  <th className="text-right py-2.5 px-4 font-medium">95% CI Upper</th>
                  <th className="text-right py-2.5 px-4 font-medium">Disconnected ODs</th>
                  <th className="text-right py-2.5 px-4 font-medium">Total Evaluated ODs</th>
                  <th className="text-right py-2.5 px-4 font-medium">% Severed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E0D8] font-mono text-[11px]">
                {filteredResilience.map((r, i) => (
                  <tr key={i} className="hover:bg-[#F4F1EA]/50 transition-colors">
                    <td className="py-2.5 px-4 font-medium text-[#111827]">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: SCENARIO_COLORS[i % SCENARIO_COLORS.length] }}></span>
                        <span>{scenarioLabel(r.scenario_name)}</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-4 text-right font-semibold text-[#C25E2E]">+{r.mean_delta_cost.toFixed(2)} s</td>
                    <td className="py-2.5 px-4 text-right text-[#4B5563]">{r.ci_lower_2_5.toFixed(2)}</td>
                    <td className="py-2.5 px-4 text-right text-[#4B5563]">{r.ci_upper_97_5.toFixed(2)}</td>
                    <td className="py-2.5 px-4 text-right font-medium text-[#111827]">{r.disconnected_od_count.toLocaleString()}</td>
                    <td className="py-2.5 px-4 text-right text-[#6B7280]">{r.total_od_count.toLocaleString()}</td>
                    <td className="py-2.5 px-4 text-right text-[#B45309]">
                      {((r.disconnected_od_count / r.total_od_count) * 100).toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* River Clyde Bridge Edge Catalog */}
        <div className="border border-[#E5E0D8] bg-white rounded shadow-xs overflow-hidden mb-6">
          <div className="p-4 sm:p-5 border-b border-[#E5E0D8] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="font-serif text-base text-[#111827]">
                River Clyde Crossing Edge Inventory
              </h3>
              <p className="text-xs text-[#6B7280]">
                Directed edges representing bridges across the River Clyde in the OSM graph.
              </p>
            </div>

            <div className="flex items-center gap-1.5 flex-wrap text-xs">
              <span className="font-mono text-[#6B7280]">Filter:</span>
              {['all', ...BRIDGE_NAMES].map(n => (
                <button
                  key={n}
                  onClick={() => setBridgeFilter(n)}
                  className={`px-2 py-0.5 text-xs font-mono rounded border transition-colors ${
                    bridgeFilter === n
                      ? 'border-[#111827] bg-[#111827] text-white font-medium'
                      : 'border-[#D1C9BE] text-[#4B5563] bg-white hover:border-[#111827]'
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
                <tr className="bg-[#F4F1EA] text-[#6B7280] font-mono text-[11px] border-b border-[#D1C9BE]">
                  <th className="text-left py-2 px-4 font-medium">Bridge Name</th>
                  <th className="text-left py-2 px-4 font-medium">Edge Identifier</th>
                  <th className="text-left py-2 px-4 font-medium">Highway Classification</th>
                  <th className="text-right py-2 px-4 font-medium">Length (m)</th>
                  <th className="text-right py-2 px-4 font-medium">Legal Speed (m/s)</th>
                  <th className="text-right py-2 px-4 font-medium">Free-Flow Time (s)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E0D8] font-mono text-[11px]">
                {filteredBridges.slice(0, 12).map((b, i) => (
                  <tr key={i} className="hover:bg-[#F4F1EA]/50 transition-colors">
                    <td className="py-2 px-4 font-medium text-[#111827]">{b.name}</td>
                    <td className="py-2 px-4 text-[#6B7280]">{b.edge_id}</td>
                    <td className="py-2 px-4 text-[#4B5563]">{b.highway}</td>
                    <td className="py-2 px-4 text-right text-[#111827]">{b.length_m.toFixed(1)}</td>
                    <td className="py-2 px-4 text-right text-[#4B5563]">{b.speed_mps.toFixed(1)}</td>
                    <td className="py-2 px-4 text-right font-medium text-[#111827]">{b.free_flow_time_sec.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Methodological Boundary Note */}
        <div className="border border-[#D1C9BE] bg-[#F4F1EA] p-4 rounded text-xs text-[#4B5563] flex items-start gap-3">
          <Info size={16} className="text-[#C25E2E] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <span className="font-semibold text-[#111827]">Boundary Truncation Note: </span>
            The disconnected OD node pairs under M8 Kingston Bridge severance (3.73% South $\to$ North) are confirmed boundary artifacts where the study bounding box truncates regional motorway bypasses north of the river, rather than complete civil isolation.
          </div>
        </div>

      </div>
    </section>
  );
};
