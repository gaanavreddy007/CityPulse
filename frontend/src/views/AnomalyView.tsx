import React, { useState, useMemo } from 'react';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';
import anomalyBenchmarksRaw from '../data/anomaly_benchmarks.json';
import spatialBenchmarksRaw from '../data/spatial_benchmarks.json';
import { AlertCircle } from 'lucide-react';

interface AnomalyRecord {
  model: string;
  task_category: string;
  corruption_desc: string;
  pr_auc_mean: number;
  pr_auc_std: number;
  f1_mean: number | null;
  f1_std: number | null;
  mcc_mean: number;
  mcc_std: number;
  fpr_mean: number;
  recall_mean: number;
  precision_mean: number;
  eval_time_ms: number;
}

interface SpatialRecord {
  model: string;
  drift_scenario: string;
  pattern: string;
  pr_auc_mean: number;
  pr_auc_std: number;
  recall_mean: number;
  precision_mean: number;
  f1_mean: number | null;
  mcc_mean: number;
  fpr_mean: number;
}

const BENCHMARKS = anomalyBenchmarksRaw as AnomalyRecord[];
const SPATIAL = spatialBenchmarksRaw as SpatialRecord[];

const MODELS = [...new Set(BENCHMARKS.map(b => b.model))];
const TASK_CATS = [...new Set(BENCHMARKS.map(b => b.task_category))];

const MODEL_COLORS: Record<string, string> = {
  'Rolling_IQR':           '#1E3A8A',
  'Rolling_ZScore':        '#C25E2E',
  'Seasonal_ESD':          '#2D6A4F',
  'Isolation_Forest':      '#6B21A8',
  'Local_Outlier_Factor':  '#B45309',
  'CUSUM':                 '#4B5563',
  'Spatial_Bivariate':     '#0F172A',
};

const AnomalyTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as AnomalyRecord;
  return (
    <div className="bg-white border border-[#CEC8BD] rounded px-3 py-2.5 shadow-sm text-xs font-mono max-w-xs">
      <div className="flex items-center justify-between border-b border-[#E2DDD5] pb-1 mb-1.5">
        <span className="font-semibold text-[#0D1117]">{d.model.replace(/_/g, ' ')}</span>
        <span className="text-[#718096] text-[10px]">{d.task_category}</span>
      </div>
      <p className="text-[11px] text-[#4A5568] mb-2 leading-tight">{d.corruption_desc}</p>
      <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px]">
        <div>PR-AUC: <span className="font-semibold text-[#0D1117]">{d.pr_auc_mean.toFixed(3)}</span></div>
        <div>Recall: <span className="font-semibold text-[#0D1117]">{d.recall_mean.toFixed(3)}</span></div>
        <div>Precision: <span className="font-semibold text-[#0D1117]">{d.precision_mean.toFixed(3)}</span></div>
        <div>FPR: <span className="font-semibold text-[#C25E2E]">{d.fpr_mean.toFixed(3)}</span></div>
      </div>
    </div>
  );
};

const SpatialTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as SpatialRecord;
  return (
    <div className="bg-white border border-[#CEC8BD] rounded px-3 py-2 shadow-sm text-xs font-mono max-w-xs">
      <div className="font-semibold text-[#0D1117] border-b border-[#E2DDD5] pb-1 mb-1">{d.model.replace(/_/g, ' ')}</div>
      <p className="text-[11px] text-[#4A5568] mb-1.5">{d.drift_scenario} · {d.pattern}</p>
      <div className="text-[11px] space-y-0.5">
        <div>PR-AUC: <span className="font-semibold">{d.pr_auc_mean.toFixed(3)}</span></div>
        <div>Recall: <span className="font-semibold">{d.recall_mean.toFixed(3)}</span></div>
        <div>FPR: <span className="font-semibold text-[#C25E2E]">{d.fpr_mean.toFixed(3)}</span></div>
      </div>
    </div>
  );
};

export const AnomalyView: React.FC = () => {
  const [tab, setTab] = useState<'benchmarks' | 'spatial'>('benchmarks');
  const [selectedModel, setSelectedModel] = useState<string>('all');
  const [selectedTask, setSelectedTask] = useState<string>('all');

  const filtered = useMemo(() =>
    BENCHMARKS.filter(b => {
      const matchModel = selectedModel === 'all' || b.model === selectedModel;
      const matchTask  = selectedTask  === 'all' || b.task_category === selectedTask;
      return matchModel && matchTask;
    }),
    [selectedModel, selectedTask]
  );

  const modelAggregates = useMemo(() =>
    MODELS.map(m => {
      const rows = BENCHMARKS.filter(b => b.model === m);
      const avg = (k: keyof AnomalyRecord) =>
        rows.reduce((sum, r) => sum + (typeof r[k] === 'number' ? (r[k] as number) : 0), 0) / (rows.length || 1);
      return { model: m, count: rows.length, pr_auc: avg('pr_auc_mean'), recall: avg('recall_mean'), precision: avg('precision_mean'), fpr: avg('fpr_mean'), mcc: avg('mcc_mean') };
    }).sort((a, b) => b.pr_auc - a.pr_auc),
    []
  );

  return (
    <section id="anomaly" className="py-16 lg:py-20 border-t border-[#E2DDD5]">
      <div className="cp-container">

        {/* ── Section heading ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 mb-8 items-end">
          <div className="lg:col-span-4">
            <div className="text-section-label mb-2">03 · Algorithmic Benchmarks</div>
            <h2 className="text-headline">Anomaly Detection Lab</h2>
          </div>
          <div className="lg:col-span-8">
            <p className="text-sm text-[#4A5568] leading-relaxed max-w-2xl">
              Benchmarking statistical and machine-learning anomaly detectors against controlled synthetic corruptions — step offsets, multiplicative scale drift, and zero dropouts — evaluated strictly on synthetic ground-truth labels.
            </p>
          </div>
        </div>

        {/* ── Tab bar ── */}
        <div className="flex items-center gap-0 border-b border-[#E2DDD5] mb-6">
          {[
            { id: 'benchmarks', label: 'Corruption Benchmarks', meta: '60 Scenarios' },
            { id: 'spatial',    label: 'Spatial Cross-Consistency', meta: '30 Scenarios' },
          ].map(({ id, label, meta }) => {
            const isActive = tab === id;
            return (
              <button
                key={id}
                onClick={() => setTab(id as any)}
                className={`relative px-4 py-2.5 text-xs font-medium transition-colors ${
                  isActive ? 'text-[#0D1117]' : 'text-[#718096] hover:text-[#0D1117]'
                }`}
              >
                {label}
                <span className="ml-2 font-mono text-[10px] text-[#9CA3AF]">{meta}</span>
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-px bg-[#0D1117]" />
                )}
              </button>
            );
          })}
        </div>

        {tab === 'benchmarks' && (
          <>
            {/* Filters */}
            <div className="flex flex-wrap items-start justify-between gap-4 py-3 border-y border-[#E2DDD5] mb-6">
              <div className="flex items-center gap-2 flex-wrap text-xs">
                <span className="font-mono text-[10px] text-[#718096] uppercase tracking-wider">Model:</span>
                {['all', ...MODELS].map(m => (
                  <button
                    key={m}
                    onClick={() => setSelectedModel(m)}
                    className={`px-2 py-1 text-[11px] font-mono rounded border transition-colors ${
                      selectedModel === m
                        ? 'border-[#0D1117] bg-[#0D1117] text-white'
                        : 'border-[#CEC8BD] text-[#4A5568] bg-white hover:border-[#0D1117]'
                    }`}
                  >
                    {m === 'all' ? 'All' : m.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-2 flex-wrap text-xs">
                <span className="font-mono text-[10px] text-[#718096] uppercase tracking-wider">Corruption:</span>
                {['all', ...TASK_CATS].map(c => (
                  <button
                    key={c}
                    onClick={() => setSelectedTask(c)}
                    className={`px-2 py-1 text-[11px] font-mono rounded border transition-colors ${
                      selectedTask === c
                        ? 'border-[#C25E2E] bg-[#C25E2E] text-white'
                        : 'border-[#CEC8BD] text-[#4A5568] bg-white hover:border-[#C25E2E]'
                    }`}
                  >
                    {c === 'all' ? 'All' : c}
                  </button>
                ))}
              </div>
            </div>

            {/* Scatter + table grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">

              {/* Scatter chart */}
              <div className="lg:col-span-7 bg-white border border-[#E2DDD5] rounded overflow-hidden">
                <div className="px-5 py-4 border-b border-[#E2DDD5]">
                  <h3 className="font-serif text-lg text-[#0D1117]">PR-AUC vs. Recall Tradeoff</h3>
                  <p className="text-xs text-[#718096] mt-0.5">
                    Precision-Recall AUC against Recall across benchmark scenarios. Top-right = superior recovery.
                  </p>
                </div>
                <div className="p-4 sm:p-5">
                  <div className="h-[260px] sm:h-[280px] w-full min-w-0">
                    <ResponsiveContainer width="100%" height="100%">
                      <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                        <CartesianGrid strokeDasharray="2 2" />
                        <XAxis
                          dataKey="recall_mean" type="number" domain={[0, 1]}
                          tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }}
                          label={{ value: 'Recall', position: 'insideBottom', offset: -10, fill: '#718096', fontSize: 11 }}
                        />
                        <YAxis
                          dataKey="pr_auc_mean" type="number" domain={[0, 1]}
                          tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }}
                          width={40}
                          label={{ value: 'PR-AUC', angle: -90, position: 'insideLeft', fill: '#718096', fontSize: 11 }}
                        />
                        <Tooltip content={<AnomalyTooltip />} />
                        <Scatter data={filtered}>
                          {filtered.map((b, i) => (
                            <Cell key={i} fill={MODEL_COLORS[b.model] || '#1E3A8A'} fillOpacity={0.8} />
                          ))}
                        </Scatter>
                      </ScatterChart>
                    </ResponsiveContainer>
                  </div>
                  {/* Legend */}
                  <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-[#E2DDD5] text-[11px] font-mono text-[#4A5568]">
                    {MODELS.map(m => (
                      <div key={m} className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: MODEL_COLORS[m] || '#1E3A8A' }} />
                        <span>{m.replace(/_/g, ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Aggregate rankings table */}
              <div className="lg:col-span-5 bg-white border border-[#E2DDD5] rounded overflow-hidden">
                <div className="px-5 py-4 border-b border-[#E2DDD5]">
                  <h3 className="font-serif text-lg text-[#0D1117]">Model Rankings</h3>
                  <p className="text-xs text-[#718096] mt-0.5">Mean metrics averaged across all corruption regimes.</p>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-[#CEC8BD] text-[#718096] font-mono text-[10px]">
                        <th className="text-left py-2.5 px-4 font-medium">Model</th>
                        <th className="text-right py-2.5 px-2.5 font-medium">PR-AUC</th>
                        <th className="text-right py-2.5 px-2.5 font-medium">Recall</th>
                        <th className="text-right py-2.5 px-4 font-medium">FPR</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E2DDD5] font-mono">
                      {modelAggregates.map((agg, idx) => (
                        <tr key={agg.model} className="hover:bg-[#FAF8F4] transition-colors">
                          <td className="py-2.5 px-4 font-medium text-[#0D1117]">
                            <div className="flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: MODEL_COLORS[agg.model] }} />
                              <span className="text-[11px] truncate">{agg.model.replace(/_/g, ' ')}</span>
                              {idx === 0 && <span className="text-[9px] font-mono font-semibold text-[#C25E2E] ml-1">BEST</span>}
                            </div>
                          </td>
                          <td className="py-2.5 px-2.5 text-right font-semibold text-[#0D1117] text-[11px]">{agg.pr_auc.toFixed(3)}</td>
                          <td className="py-2.5 px-2.5 text-right text-[#4A5568] text-[11px]">{agg.recall.toFixed(3)}</td>
                          <td className="py-2.5 px-4 text-right text-[#C25E2E] text-[11px]">{agg.fpr.toFixed(3)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Scenario ledger */}
            <div className="bg-white border border-[#E2DDD5] rounded overflow-hidden mb-6">
              <div className="px-5 py-3 border-b border-[#E2DDD5] flex items-baseline justify-between">
                <h3 className="font-serif text-base text-[#0D1117]">Benchmark Scenario Ledger</h3>
                <span className="text-xs font-mono text-[#718096]">
                  {Math.min(15, filtered.length)} of {filtered.length} scenarios
                </span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs min-w-[650px]">
                  <thead>
                    <tr className="bg-[#FAF8F4] text-[#718096] font-mono text-[10px] border-b border-[#CEC8BD]">
                      <th className="text-left py-2 px-4 font-medium">Model</th>
                      <th className="text-left py-2 px-2.5 font-medium">Category</th>
                      <th className="text-left py-2 px-2.5 font-medium">Corruption Description</th>
                      <th className="text-right py-2 px-2.5 font-medium">PR-AUC</th>
                      <th className="text-right py-2 px-2.5 font-medium">Recall</th>
                      <th className="text-right py-2 px-4 font-medium">FPR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2DDD5] font-mono text-[11px]">
                    {filtered.slice(0, 15).map((b, i) => (
                      <tr key={i} className="hover:bg-[#FAF8F4] transition-colors">
                        <td className="py-2 px-4 font-medium text-[#0D1117]">
                          <div className="flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: MODEL_COLORS[b.model] }} />
                            {b.model.replace(/_/g, ' ')}
                          </div>
                        </td>
                        <td className="py-2 px-2.5 text-[#4A5568]">{b.task_category}</td>
                        <td className="py-2 px-2.5 text-[#1A202C] font-sans max-w-[200px] truncate">{b.corruption_desc}</td>
                        <td className="py-2 px-2.5 text-right font-semibold text-[#0D1117]">{b.pr_auc_mean.toFixed(3)}</td>
                        <td className="py-2 px-2.5 text-right text-[#4A5568]">{b.recall_mean.toFixed(3)}</td>
                        <td className="py-2 px-4 text-right text-[#C25E2E]">{b.fpr_mean.toFixed(3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {tab === 'spatial' && (
          <div className="space-y-6">
            <div className="bg-white border border-[#E2DDD5] rounded overflow-hidden">
              <div className="px-5 py-4 border-b border-[#E2DDD5]">
                <h3 className="font-serif text-lg text-[#0D1117]">Spatial Cross-Consistency & Neighbour Drift</h3>
                <p className="text-xs text-[#718096] mt-0.5">
                  Bivariate correlation tracking between neighbouring detectors — isolating sensor drift from macro city-wide volume dips.
                </p>
              </div>
              <div className="p-4 sm:p-5">
                <div className="h-[280px] w-full min-w-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                      <CartesianGrid strokeDasharray="2 2" />
                      <XAxis
                        dataKey="recall_mean" type="number" domain={[0, 1]}
                        tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }}
                        label={{ value: 'Recall', position: 'insideBottom', offset: -10, fill: '#718096', fontSize: 11 }}
                      />
                      <YAxis
                        dataKey="pr_auc_mean" type="number" domain={[0, 1]}
                        tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }}
                        width={40}
                        label={{ value: 'PR-AUC', angle: -90, position: 'insideLeft', fill: '#718096', fontSize: 11 }}
                      />
                      <Tooltip content={<SpatialTooltip />} />
                      <Scatter data={SPATIAL}>
                        {SPATIAL.map((r, i) => (
                          <Cell key={i} fill={MODEL_COLORS[r.model] || '#1E3A8A'} fillOpacity={0.8} />
                        ))}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="bg-white border border-[#E2DDD5] rounded overflow-x-auto">
              <table className="w-full text-xs min-w-[650px]">
                <thead>
                  <tr className="bg-[#FAF8F4] text-[#718096] font-mono text-[10px] border-b border-[#CEC8BD]">
                    <th className="text-left py-2.5 px-6 font-medium">Model</th>
                    <th className="text-left py-2.5 px-3 font-medium">Drift Scenario</th>
                    <th className="text-left py-2.5 px-3 font-medium">Pattern</th>
                    <th className="text-right py-2.5 px-3 font-medium">PR-AUC</th>
                    <th className="text-right py-2.5 px-3 font-medium">Recall</th>
                    <th className="text-right py-2.5 px-6 font-medium">FPR</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2DDD5] font-mono text-[11px]">
                  {SPATIAL.map((r, i) => (
                    <tr key={i} className="hover:bg-[#FAF8F4] transition-colors">
                      <td className="py-2.5 px-6 font-medium text-[#0D1117]">{r.model.replace(/_/g, ' ')}</td>
                      <td className="py-2.5 px-3 text-[#4A5568]">{r.drift_scenario}</td>
                      <td className="py-2.5 px-3 text-[#718096]">{r.pattern}</td>
                      <td className="py-2.5 px-3 text-right font-semibold text-[#0D1117]">{r.pr_auc_mean.toFixed(3)}</td>
                      <td className="py-2.5 px-3 text-right text-[#4A5568]">{r.recall_mean.toFixed(3)}</td>
                      <td className="py-2.5 px-6 text-right text-[#C25E2E]">{r.fpr_mean.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Benchmarking caveat */}
        <div className="mt-8 border-t border-[#E2DDD5] pt-6 flex items-start gap-3 text-xs text-[#4A5568]">
          <AlertCircle size={14} className="text-[#C25E2E] shrink-0 mt-0.5" />
          <p className="leading-relaxed max-w-3xl">
            <span className="font-semibold text-[#0D1117]">Benchmarking Caveat: </span>
            Ground-truth labels correspond to mathematical fault injection only. Unsupervised detectors evaluate deviations from baseline distributions — they do not verify physical hardware faults. Real-world detector drift often co-occurs with weather and congestion artifacts.
          </p>
        </div>

      </div>
    </section>
  );
};
