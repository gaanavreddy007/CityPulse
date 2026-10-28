import React, { useState, useMemo } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import anomalyBenchmarksRaw from '../data/anomaly_benchmarks.json';
import spatialBenchmarksRaw from '../data/spatial_benchmarks.json';
import { FlaskConical, AlertCircle, BarChart3, HelpCircle } from 'lucide-react';

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

// Editorial Model Color Scheme: Navy, Terracotta, Forest Green, Deep Plum, Charcoal
const MODEL_COLORS: Record<string, string> = {
  'Rolling_IQR': '#1E3A8A',
  'Rolling_ZScore': '#C25E2E',
  'Seasonal_ESD': '#2D6A4F',
  'Isolation_Forest': '#6B21A8',
  'Local_Outlier_Factor': '#B45309',
  'CUSUM': '#4B5563',
  'Spatial_Bivariate': '#0F172A',
};

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as AnomalyRecord;
  return (
    <div className="bg-white border border-[#D1C9BE] rounded px-3 py-2.5 shadow-sm text-xs font-mono max-w-xs">
      <div className="flex items-center justify-between border-b border-[#E5E0D8] pb-1 mb-1.5">
        <span className="font-semibold text-[#111827]">{d.model}</span>
        <span className="text-[#6B7280] text-[10px]">{d.task_category}</span>
      </div>
      <p className="text-[11px] text-[#4B5563] mb-2 leading-tight">{d.corruption_desc}</p>
      <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px]">
        <div>PR-AUC: <span className="font-semibold text-[#111827]">{d.pr_auc_mean.toFixed(3)}</span></div>
        <div>Recall: <span className="font-semibold text-[#111827]">{d.recall_mean.toFixed(3)}</span></div>
        <div>Precision: <span className="font-semibold text-[#111827]">{d.precision_mean.toFixed(3)}</span></div>
        <div>FPR: <span className="font-semibold text-[#C25E2E]">{d.fpr_mean.toFixed(3)}</span></div>
      </div>
    </div>
  );
};

const SpatialTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as SpatialRecord;
  return (
    <div className="bg-white border border-[#D1C9BE] rounded px-3 py-2 shadow-sm text-xs font-mono max-w-xs">
      <div className="font-semibold text-[#111827] border-b border-[#E5E0D8] pb-1 mb-1">{d.model}</div>
      <p className="text-[11px] text-[#4B5563] mb-1.5">{d.drift_scenario} · {d.pattern}</p>
      <div className="text-[11px] space-y-0.5">
        <div>PR-AUC: <span className="font-semibold">{d.pr_auc_mean.toFixed(3)}</span></div>
        <div>Recall: <span className="font-semibold">{d.recall_mean.toFixed(3)}</span></div>
        <div>Precision: <span className="font-semibold">{d.precision_mean.toFixed(3)}</span></div>
      </div>
    </div>
  );
};

export const AnomalyView: React.FC = () => {
  const [tab, setTab] = useState<'benchmarks' | 'spatial'>('benchmarks');
  const [selectedModel, setSelectedModel] = useState<string>('all');
  const [selectedTask, setSelectedTask] = useState<string>('all');

  const filtered = useMemo(() => {
    return BENCHMARKS.filter(b => {
      const matchModel = selectedModel === 'all' || b.model === selectedModel;
      const matchTask = selectedTask === 'all' || b.task_category === selectedTask;
      return matchModel && matchTask;
    });
  }, [selectedModel, selectedTask]);

  // Aggregate model rankings
  const modelAggregates = useMemo(() => {
    return MODELS.map(m => {
      const rows = BENCHMARKS.filter(b => b.model === m);
      const avg = (k: keyof AnomalyRecord) =>
        rows.reduce((sum, r) => sum + (typeof r[k] === 'number' ? (r[k] as number) : 0), 0) / (rows.length || 1);
      return {
        model: m,
        count: rows.length,
        pr_auc: avg('pr_auc_mean'),
        recall: avg('recall_mean'),
        precision: avg('precision_mean'),
        fpr: avg('fpr_mean'),
        mcc: avg('mcc_mean'),
      };
    }).sort((a, b) => b.pr_auc - a.pr_auc);
  }, []);

  return (
    <section id="anomaly" className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Heading */}
        <div className="max-w-3xl mb-8">
          <span className="text-xs font-mono uppercase tracking-wider text-[#C25E2E] font-semibold">
            Section 03 · Algorithmic Benchmarks
          </span>
          <h2 className="font-serif text-2xl sm:text-3xl text-[#111827] mt-1 mb-2">
            Anomaly Detection Lab & Synthetic Corruptions
          </h2>
          <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed">
            Benchmarking statistical and machine-learning anomaly detectors against controlled synthetic corruptions: step offsets, multiplicative scale drift, and zero dropouts. Evaluated strictly on synthetic ground-truth labels.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-2 border-b border-[#E5E0D8] pb-4 mb-6">
          <button
            onClick={() => setTab('benchmarks')}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
              tab === 'benchmarks'
                ? 'bg-[#111827] text-white font-semibold'
                : 'text-[#4B5563] hover:text-[#111827] hover:bg-[#F4F1EA]'
            }`}
          >
            1. Corruption Benchmarks (60 Scenarios)
          </button>
          <button
            onClick={() => setTab('spatial')}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
              tab === 'spatial'
                ? 'bg-[#111827] text-white font-semibold'
                : 'text-[#4B5563] hover:text-[#111827] hover:bg-[#F4F1EA]'
            }`}
          >
            2. Spatial Cross-Consistency (30 Scenarios)
          </button>
        </div>

        {tab === 'benchmarks' && (
          <>
            {/* Filter Controls */}
            <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded border border-[#E5E0D8] bg-white mb-6 shadow-xs">
              <div className="flex items-center gap-2 flex-wrap text-xs">
                <span className="font-mono text-[#6B7280]">Model:</span>
                {['all', ...MODELS].map(m => (
                  <button
                    key={m}
                    onClick={() => setSelectedModel(m)}
                    className={`px-2.5 py-1 text-xs font-mono rounded border transition-colors ${
                      selectedModel === m
                        ? 'border-[#111827] bg-[#111827] text-white font-semibold'
                        : 'border-[#D1C9BE] text-[#4B5563] bg-white hover:border-[#111827]'
                    }`}
                  >
                    {m.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-2 flex-wrap text-xs">
                <span className="font-mono text-[#6B7280]">Corruption:</span>
                {['all', ...TASK_CATS].map(c => (
                  <button
                    key={c}
                    onClick={() => setSelectedTask(c)}
                    className={`px-2.5 py-1 text-xs font-mono rounded border transition-colors ${
                      selectedTask === c
                        ? 'border-[#C25E2E] bg-[#C25E2E] text-white font-semibold'
                        : 'border-[#D1C9BE] text-[#4B5563] bg-white hover:border-[#C25E2E]'
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            {/* Visualisations Grid: Scatter Chart & Aggregate Table */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
              {/* Scatter Chart Surface */}
              <div className="lg:col-span-7 border border-[#E5E0D8] bg-white p-6 rounded shadow-xs">
                <div className="border-b border-[#E5E0D8] pb-3 mb-4">
                  <h3 className="font-serif text-lg text-[#111827]">
                    PR-AUC vs. Recall Tradeoff
                  </h3>
                  <p className="text-xs text-[#6B7280]">
                    Precision-Recall Area Under Curve plotted against Recall across benchmark scenarios. Top-right indicates superior class-imbalance recovery.
                  </p>
                </div>

                <div className="h-[280px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                      <CartesianGrid strokeDasharray="2 2" />
                      <XAxis
                        dataKey="recall_mean"
                        type="number"
                        domain={[0, 1]}
                        tick={{ fill: '#6B7280', fontSize: 11 }}
                        tickLine={false}
                        axisLine={{ stroke: '#D1C9BE' }}
                        label={{ value: 'Recall', position: 'insideBottom', offset: -10, fill: '#6B7280', fontSize: 11 }}
                      />
                      <YAxis
                        dataKey="pr_auc_mean"
                        type="number"
                        domain={[0, 1]}
                        tick={{ fill: '#6B7280', fontSize: 11 }}
                        tickLine={false}
                        axisLine={{ stroke: '#D1C9BE' }}
                        width={40}
                        label={{ value: 'PR-AUC', angle: -90, position: 'insideLeft', fill: '#6B7280', fontSize: 11 }}
                      />
                      <Tooltip content={<CustomTooltip />} />
                      <Scatter data={filtered}>
                        {filtered.map((b, i) => (
                          <Cell
                            key={i}
                            fill={MODEL_COLORS[b.model] || '#1E3A8A'}
                            fillOpacity={0.8}
                          />
                        ))}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>

                {/* Legend */}
                <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-[#E5E0D8] text-[11px] font-mono text-[#4B5563]">
                  {MODELS.map(m => (
                    <div key={m} className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: MODEL_COLORS[m] || '#1E3A8A' }}></span>
                      <span>{m.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Model Mean Performance Rankings */}
              <div className="lg:col-span-5 border border-[#E5E0D8] bg-white p-6 rounded shadow-xs overflow-x-auto">
                <div className="border-b border-[#E5E0D8] pb-3 mb-4">
                  <h3 className="font-serif text-lg text-[#111827]">
                    Model Aggregate Scores
                  </h3>
                  <p className="text-xs text-[#6B7280]">
                    Mean metrics averaged across all evaluated corruption regimes.
                  </p>
                </div>

                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-[#D1C9BE] text-[#6B7280] font-mono text-[11px]">
                      <th className="text-left pb-2 font-medium">Model</th>
                      <th className="text-right pb-2 font-medium">PR-AUC</th>
                      <th className="text-right pb-2 font-medium">Recall</th>
                      <th className="text-right pb-2 font-medium">FPR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E5E0D8] font-mono">
                    {modelAggregates.map(agg => (
                      <tr key={agg.model} className="hover:bg-[#F4F1EA]/60 transition-colors">
                        <td className="py-2.5 font-medium text-[#111827]">
                          <div className="flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: MODEL_COLORS[agg.model] }}></span>
                            <span>{agg.model.replace(/_/g, ' ')}</span>
                          </div>
                        </td>
                        <td className="py-2.5 text-right font-semibold text-[#111827]">{agg.pr_auc.toFixed(3)}</td>
                        <td className="py-2.5 text-right text-[#4B5563]">{agg.recall.toFixed(3)}</td>
                        <td className="py-2.5 text-right text-[#C25E2E]">{agg.fpr.toFixed(3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Individual Scenario Ledger */}
            <div className="border border-[#E5E0D8] bg-white rounded shadow-xs overflow-hidden mb-6">
              <div className="p-4 sm:p-5 border-b border-[#E5E0D8] flex items-center justify-between">
                <div>
                  <h3 className="font-serif text-base text-[#111827]">
                    Detailed Benchmark Scenario Ledger
                  </h3>
                  <p className="text-xs text-[#6B7280]">
                    Viewing {Math.min(15, filtered.length)} of {filtered.length} benchmark outcomes.
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs min-w-[700px]">
                  <thead>
                    <tr className="bg-[#F4F1EA] text-[#6B7280] font-mono text-[11px] border-b border-[#D1C9BE]">
                      <th className="text-left py-2.5 px-4 font-medium">Model</th>
                      <th className="text-left py-2.5 px-4 font-medium">Task Category</th>
                      <th className="text-left py-2.5 px-4 font-medium">Corruption Description</th>
                      <th className="text-right py-2.5 px-4 font-medium">PR-AUC</th>
                      <th className="text-right py-2.5 px-4 font-medium">Recall</th>
                      <th className="text-right py-2.5 px-4 font-medium">Precision</th>
                      <th className="text-right py-2.5 px-4 font-medium">FPR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E5E0D8] font-mono text-[11px]">
                    {filtered.slice(0, 15).map((b, i) => (
                      <tr key={i} className="hover:bg-[#F4F1EA]/50 transition-colors">
                        <td className="py-2 px-4 font-medium text-[#111827]">{b.model.replace(/_/g, ' ')}</td>
                        <td className="py-2 px-4 text-[#4B5563]">{b.task_category}</td>
                        <td className="py-2 px-4 text-[#1F2937] font-sans max-w-xs truncate">{b.corruption_desc}</td>
                        <td className="py-2 px-4 text-right font-semibold text-[#111827]">{b.pr_auc_mean.toFixed(3)}</td>
                        <td className="py-2 px-4 text-right text-[#4B5563]">{b.recall_mean.toFixed(3)}</td>
                        <td className="py-2 px-4 text-right text-[#4B5563]">{b.precision_mean.toFixed(3)}</td>
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
            <div className="border border-[#E5E0D8] bg-white p-6 rounded shadow-xs">
              <div className="border-b border-[#E5E0D8] pb-3 mb-4">
                <h3 className="font-serif text-lg text-[#111827]">
                  Spatial Cross-Consistency & Neighbor Drift
                </h3>
                <p className="text-xs text-[#6B7280]">
                  Evaluating whether bivariate correlation tracking between neighboring detectors isolates true sensor drift from macro city-wide volume dips (e.g., severe storm events).
                </p>
              </div>

              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" />
                    <XAxis
                      dataKey="recall_mean"
                      type="number"
                      domain={[0, 1]}
                      tick={{ fill: '#6B7280', fontSize: 11 }}
                      tickLine={false}
                      axisLine={{ stroke: '#D1C9BE' }}
                      label={{ value: 'Recall', position: 'insideBottom', offset: -10, fill: '#6B7280', fontSize: 11 }}
                    />
                    <YAxis
                      dataKey="pr_auc_mean"
                      type="number"
                      domain={[0, 1]}
                      tick={{ fill: '#6B7280', fontSize: 11 }}
                      tickLine={false}
                      axisLine={{ stroke: '#D1C9BE' }}
                      width={40}
                      label={{ value: 'PR-AUC', angle: -90, position: 'insideLeft', fill: '#6B7280', fontSize: 11 }}
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

            {/* Spatial Table */}
            <div className="border border-[#E5E0D8] bg-white rounded shadow-xs overflow-x-auto">
              <table className="w-full text-xs min-w-[650px]">
                <thead>
                  <tr className="bg-[#F4F1EA] text-[#6B7280] font-mono text-[11px] border-b border-[#D1C9BE]">
                    <th className="text-left py-2.5 px-4 font-medium">Model</th>
                    <th className="text-left py-2.5 px-4 font-medium">Drift Scenario</th>
                    <th className="text-left py-2.5 px-4 font-medium">Pattern</th>
                    <th className="text-right py-2.5 px-4 font-medium">PR-AUC</th>
                    <th className="text-right py-2.5 px-4 font-medium">Recall</th>
                    <th className="text-right py-2.5 px-4 font-medium">Precision</th>
                    <th className="text-right py-2.5 px-4 font-medium">FPR</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E5E0D8] font-mono text-[11px]">
                  {SPATIAL.map((r, i) => (
                    <tr key={i} className="hover:bg-[#F4F1EA]/50 transition-colors">
                      <td className="py-2 px-4 font-medium text-[#111827]">{r.model.replace(/_/g, ' ')}</td>
                      <td className="py-2 px-4 text-[#4B5563]">{r.drift_scenario}</td>
                      <td className="py-2 px-4 text-[#6B7280]">{r.pattern}</td>
                      <td className="py-2 px-4 text-right font-semibold text-[#111827]">{r.pr_auc_mean.toFixed(3)}</td>
                      <td className="py-2 px-4 text-right text-[#4B5563]">{r.recall_mean.toFixed(3)}</td>
                      <td className="py-2 px-4 text-right text-[#4B5563]">{r.precision_mean.toFixed(3)}</td>
                      <td className="py-2 px-4 text-right text-[#C25E2E]">{r.fpr_mean.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Rigorous Caveat Callout */}
        <div className="border border-[#D1C9BE] bg-[#F4F1EA] p-4 rounded text-xs text-[#4B5563] mt-8 flex items-start gap-3">
          <AlertCircle size={16} className="text-[#C25E2E] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <span className="font-semibold text-[#111827]">Benchmarking Caveat: </span>
            Ground-truth labels correspond to mathematical fault injection. Unsupervised detectors evaluate deviations from baseline distributions; they do not verify physical hardware faults. Real-world detector drift often co-occurs with weather and congestion artifacts.
          </div>
        </div>

      </div>
    </section>
  );
};
