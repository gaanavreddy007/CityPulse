import React, { useState, useMemo } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import anomalyBenchmarksRaw from '../data/anomaly_benchmarks.json';
import spatialBenchmarksRaw from '../data/spatial_benchmarks.json';

// Real schema from anomaly_benchmarks.json
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

// Real schema from spatial_benchmarks.json
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

const MODEL_COLORS: Record<string, string> = {};
['#22d3ee','#a78bfa','#34d399','#fb923c','#f472b6','#fbbf24','#60a5fa'].forEach((c, i) => {
  if (MODELS[i]) MODEL_COLORS[MODELS[i]] = c;
});

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as AnomalyRecord;
  return (
    <div className="bg-slate-900/95 border border-slate-700 rounded-xl px-4 py-3 shadow-xl text-xs max-w-xs">
      <p className="text-slate-200 font-semibold mb-1">{d.model}</p>
      <p className="text-slate-400 mb-2 text-xs">{d.corruption_desc}</p>
      <p className="text-cyan-300">PR-AUC: {d.pr_auc_mean.toFixed(3)} ± {d.pr_auc_std.toFixed(3)}</p>
      <p className="text-emerald-300">Recall: {d.recall_mean.toFixed(3)}</p>
      <p className="text-violet-300">Precision: {d.precision_mean.toFixed(3)}</p>
      <p className="text-rose-300">FPR: {d.fpr_mean.toFixed(3)}</p>
      {d.f1_mean !== null && <p className="text-amber-300">F1: {d.f1_mean.toFixed(3)}</p>}
    </div>
  );
};

const SpatialTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as SpatialRecord;
  return (
    <div className="bg-slate-900/95 border border-slate-700 rounded-xl px-4 py-3 shadow-xl text-xs max-w-xs">
      <p className="text-slate-200 font-semibold mb-1">{d.model}</p>
      <p className="text-slate-400 mb-2">{d.drift_scenario} · {d.pattern}</p>
      <p className="text-cyan-300">PR-AUC: {d.pr_auc_mean.toFixed(3)}</p>
      <p className="text-emerald-300">Recall: {d.recall_mean.toFixed(3)}</p>
      <p className="text-violet-300">Precision: {d.precision_mean.toFixed(3)}</p>
      <p className="text-rose-300">FPR: {d.fpr_mean.toFixed(3)}</p>
    </div>
  );
};

export const AnomalyView: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState('all');
  const [selectedTask, setSelectedTask] = useState('all');
  const [tab, setTab] = useState<'benchmarks' | 'spatial'>('benchmarks');

  const filtered = useMemo(() =>
    BENCHMARKS.filter(b =>
      (selectedModel === 'all' || b.model === selectedModel) &&
      (selectedTask === 'all' || b.task_category === selectedTask)
    ),
    [selectedModel, selectedTask]
  );

  // Per-model averages
  const modelAvgs = useMemo(() =>
    MODELS.map(model => {
      const rows = BENCHMARKS.filter(b => b.model === model);
      const avg = (key: keyof AnomalyRecord) =>
        rows.reduce((s, r) => s + ((r[key] as number) ?? 0), 0) / rows.length;
      return {
        model,
        pr_auc: avg('pr_auc_mean'),
        recall: avg('recall_mean'),
        precision: avg('precision_mean'),
        fpr: avg('fpr_mean'),
        mcc: avg('mcc_mean'),
      };
    }),
    []
  );

  return (
    <section id="anomaly" className="min-h-screen pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-2">Anomaly Detection Lab</h2>
          <p className="text-slate-400 text-sm max-w-2xl">
            Benchmark results for anomaly detection methods across 60 evaluated scenarios with deliberately injected
            synthetic corruption. Metrics computed on synthetic labels — not claimed operational fault detections.
          </p>
        </div>

        {/* Tab toggle */}
        <div className="flex gap-2 mb-8">
          {([['benchmarks', 'Method Benchmarks'], ['spatial', 'Spatial Drift Benchmarks']] as const).map(([k, label]) => (
            <button key={k} onClick={() => setTab(k)}
              className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                tab === k ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-300' : 'bg-slate-800/60 border border-slate-700/60 text-slate-400 hover:text-slate-200'
              }`}>{label}</button>
          ))}
        </div>

        {tab === 'benchmarks' && (
          <>
            {/* Filters */}
            <div className="flex flex-wrap gap-4 mb-6">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs text-slate-400">Model:</span>
                {['all', ...MODELS].map(m => (
                  <button key={m} onClick={() => setSelectedModel(m)}
                    className="px-3 py-1 rounded-full text-xs font-mono border transition-all"
                    style={selectedModel === m
                      ? { borderColor: (MODEL_COLORS[m] ?? '#22d3ee') + '99', color: MODEL_COLORS[m] ?? '#22d3ee', background: (MODEL_COLORS[m] ?? '#22d3ee') + '18' }
                      : { borderColor: '#334155', color: '#64748b' }}
                  >{m}</button>
                ))}
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs text-slate-400">Category:</span>
                {['all', ...TASK_CATS].map(c => (
                  <button key={c} onClick={() => setSelectedTask(c)}
                    className={`px-3 py-1 rounded-full text-xs font-mono border transition-all ${
                      selectedTask === c ? 'border-violet-500/60 text-violet-300 bg-violet-950/40' : 'border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-400'
                    }`}>{c}</button>
                ))}
              </div>
            </div>

            {/* Scatter + summary table */}
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-6">
                <h3 className="text-sm font-semibold text-slate-200 mb-1">PR-AUC vs Recall Scatter</h3>
                <p className="text-xs text-slate-500 mb-4">Each point is one benchmark scenario. Colour = model.</p>
                <ResponsiveContainer width="100%" height={260}>
                  <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="recall_mean" name="Recall" type="number" domain={[0,1]} tick={{ fill: '#94a3b8', fontSize: 11 }}
                      label={{ value: 'Recall', position: 'insideBottom', fill: '#64748b', fontSize: 11, dy: 15 }} />
                    <YAxis dataKey="pr_auc_mean" name="PR-AUC" type="number" domain={[0,1]} tick={{ fill: '#94a3b8', fontSize: 11 }}
                      label={{ value: 'PR-AUC', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Scatter data={filtered}>
                      {filtered.map((b, i) => (
                        <Cell key={i} fill={MODEL_COLORS[b.model] ?? '#94a3b8'} fillOpacity={0.75} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
                <div className="flex flex-wrap gap-3 mt-3">
                  {MODELS.map(m => (
                    <div key={m} className="flex items-center gap-1.5 text-xs text-slate-400">
                      <span className="h-2 w-2 rounded-full" style={{ background: MODEL_COLORS[m] ?? '#94a3b8' }}></span>{m}
                    </div>
                  ))}
                </div>
              </div>

              {/* Per-model averages table */}
              <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-6">
                <h3 className="text-sm font-semibold text-slate-200 mb-1">Average Metrics per Model</h3>
                <p className="text-xs text-slate-500 mb-4">Averaged across all corruption scenarios.</p>
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-500 border-b border-slate-800">
                      <th className="text-left py-2 font-medium">Model</th>
                      <th className="text-right py-2 font-medium">PR-AUC</th>
                      <th className="text-right py-2 font-medium">Recall</th>
                      <th className="text-right py-2 font-medium">Precision</th>
                      <th className="text-right py-2 font-medium">FPR</th>
                      <th className="text-right py-2 font-medium">MCC</th>
                    </tr>
                  </thead>
                  <tbody>
                    {modelAvgs.sort((a,b) => b.pr_auc - a.pr_auc).map(d => (
                      <tr key={d.model} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                        <td className="py-2 font-mono" style={{ color: MODEL_COLORS[d.model] }}>{d.model}</td>
                        <td className="text-right py-2 text-cyan-300">{d.pr_auc.toFixed(3)}</td>
                        <td className="text-right py-2 text-emerald-300">{d.recall.toFixed(3)}</td>
                        <td className="text-right py-2 text-violet-300">{d.precision.toFixed(3)}</td>
                        <td className="text-right py-2 text-rose-300">{d.fpr.toFixed(3)}</td>
                        <td className="text-right py-2 text-amber-300">{d.mcc.toFixed(3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Full results table */}
            <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-6 mb-6 overflow-x-auto">
              <h3 className="text-sm font-semibold text-slate-200 mb-4">Filtered Results ({filtered.length} scenarios)</h3>
              <table className="w-full text-xs min-w-[700px]">
                <thead>
                  <tr className="text-slate-500 border-b border-slate-800">
                    <th className="text-left py-2 font-medium">Model</th>
                    <th className="text-left py-2 font-medium">Category</th>
                    <th className="text-left py-2 font-medium">Corruption</th>
                    <th className="text-right py-2 font-medium">PR-AUC</th>
                    <th className="text-right py-2 font-medium">Recall</th>
                    <th className="text-right py-2 font-medium">Precision</th>
                    <th className="text-right py-2 font-medium">FPR</th>
                    <th className="text-right py-2 font-medium">MCC</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.slice(0, 20).map((b, i) => (
                    <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30">
                      <td className="py-2 font-mono" style={{ color: MODEL_COLORS[b.model] ?? '#94a3b8' }}>{b.model}</td>
                      <td className="py-2 text-slate-500 text-xs">{b.task_category}</td>
                      <td className="py-2 text-slate-400 max-w-[180px] truncate" title={b.corruption_desc}>{b.corruption_desc}</td>
                      <td className="text-right py-2 text-cyan-300">{b.pr_auc_mean.toFixed(3)}</td>
                      <td className="text-right py-2 text-emerald-300">{b.recall_mean.toFixed(3)}</td>
                      <td className="text-right py-2 text-violet-300">{b.precision_mean.toFixed(3)}</td>
                      <td className="text-right py-2 text-rose-300">{b.fpr_mean.toFixed(3)}</td>
                      <td className="text-right py-2 text-amber-300">{b.mcc_mean.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filtered.length > 20 && <p className="text-xs text-slate-600 mt-2">Showing 20 of {filtered.length} — apply filters to narrow.</p>}
            </div>

            <div className="rounded-xl bg-slate-900/40 border border-slate-800/40 p-5 text-xs text-slate-400">
              <p className="font-semibold text-slate-300 mb-2">Benchmark Interpretation Notes</p>
              <ul className="space-y-1.5 list-disc list-inside">
                <li>All anomaly labels are from <em>deliberately injected synthetic corruption</em>, not ground-truth operational faults.</li>
                <li>PR-AUC = area under precision-recall curve. Higher is better for class-imbalanced detection.</li>
                <li>MCC = Matthews Correlation Coefficient — more robust than accuracy for imbalanced datasets.</li>
                <li>FPR = false positive rate. These are distinct from FDR (false discovery rate).</li>
                <li>Results apply to this Glasgow SCOOT sample — generalisation to other cities is unverified.</li>
              </ul>
            </div>
          </>
        )}

        {tab === 'spatial' && (
          <>
            <div className="mb-6">
              <p className="text-sm text-slate-400 max-w-2xl">
                Spatial drift benchmark results across 30 evaluated scenarios. Tests detector cross-consistency
                under different drift scenarios and temporal patterns using the same anomaly detection models.
              </p>
            </div>

            {/* Scatter */}
            <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-6 mb-6">
              <h3 className="text-sm font-semibold text-slate-200 mb-1">Spatial PR-AUC vs Recall</h3>
              <p className="text-xs text-slate-500 mb-4">Colour = model. Each point = one drift scenario.</p>
              <ResponsiveContainer width="100%" height={260}>
                <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="recall_mean" name="Recall" type="number" domain={[0,1]} tick={{ fill: '#94a3b8', fontSize: 11 }}
                    label={{ value: 'Recall', position: 'insideBottom', fill: '#64748b', fontSize: 11, dy: 15 }} />
                  <YAxis dataKey="pr_auc_mean" name="PR-AUC" type="number" domain={[0,1]} tick={{ fill: '#94a3b8', fontSize: 11 }}
                    label={{ value: 'PR-AUC', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
                  <Tooltip content={<SpatialTooltip />} />
                  <Scatter data={SPATIAL}>
                    {SPATIAL.map((r, i) => (
                      <Cell key={i} fill={MODEL_COLORS[r.model] ?? '#94a3b8'} fillOpacity={0.75} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>

            {/* Table */}
            <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-6 overflow-x-auto mb-6">
              <table className="w-full text-xs min-w-[600px]">
                <thead>
                  <tr className="text-slate-500 border-b border-slate-800">
                    <th className="text-left py-2 font-medium">Model</th>
                    <th className="text-left py-2 font-medium">Drift Scenario</th>
                    <th className="text-left py-2 font-medium">Pattern</th>
                    <th className="text-right py-2 font-medium">PR-AUC</th>
                    <th className="text-right py-2 font-medium">Recall</th>
                    <th className="text-right py-2 font-medium">Precision</th>
                    <th className="text-right py-2 font-medium">FPR</th>
                  </tr>
                </thead>
                <tbody>
                  {SPATIAL.map((r, i) => (
                    <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30">
                      <td className="py-2 font-mono" style={{ color: MODEL_COLORS[r.model] ?? '#94a3b8' }}>{r.model}</td>
                      <td className="py-2 text-slate-400">{r.drift_scenario}</td>
                      <td className="py-2 text-slate-500">{r.pattern}</td>
                      <td className="text-right py-2 text-cyan-300">{r.pr_auc_mean.toFixed(3)}</td>
                      <td className="text-right py-2 text-emerald-300">{r.recall_mean.toFixed(3)}</td>
                      <td className="text-right py-2 text-violet-300">{r.precision_mean.toFixed(3)}</td>
                      <td className="text-right py-2 text-rose-300">{r.fpr_mean.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="rounded-xl bg-slate-900/40 border border-slate-800/40 p-5 text-xs text-slate-400">
              <p className="font-semibold text-slate-300 mb-2">Spatial Benchmark Notes</p>
              <ul className="space-y-1.5 list-disc list-inside">
                <li>Drift scenarios test whether anomaly models remain robust under gradual distributional shifts between sensor pairs.</li>
                <li>Pattern refers to temporal structure of the injected drift (e.g., sudden vs. gradual).</li>
                <li>All labels are synthetic — no real inter-detector fault ground-truth is available for comparison.</li>
              </ul>
            </div>
          </>
        )}
      </div>
    </section>
  );
};
