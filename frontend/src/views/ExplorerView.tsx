import React, { useState, useMemo } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import flowSamplesRaw from '../data/flow_samples.json';

interface DiurnalPoint { hour: number; mean: number; min: number; max: number; p50: number; p25: number; p75: number; }
interface WeekPoint { timestamp: string; full_dt: string; flow: number; }
interface SensorData {
  id: string;
  diurnal: DiurnalPoint[];
  week_slice: WeekPoint[];
  total_records: number;
  mean_flow: number;
  max_flow: number;
  zero_flow_pct: number;
}

const FLOW_MAP = flowSamplesRaw as Record<string, SensorData>;
const SAMPLES: SensorData[] = Object.values(FLOW_MAP);
const SENSOR_IDS = SAMPLES.map(s => s.id);
const COLORS = ['#22d3ee', '#a78bfa', '#34d399', '#fb923c', '#f472b6'];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-900/95 border border-slate-700 rounded-xl px-4 py-3 shadow-xl text-xs">
      <p className="text-slate-400 mb-2 font-mono">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }} className="mb-0.5">
          {p.name}: <span className="font-semibold">{typeof p.value === 'number' ? p.value.toFixed(1) : p.value}</span>
        </p>
      ))}
    </div>
  );
};

export const ExplorerView: React.FC = () => {
  const [selectedIds, setSelectedIds] = useState<string[]>([SENSOR_IDS[0]]);
  const [viewMode, setViewMode] = useState<'diurnal' | 'weekly' | 'stats'>('diurnal');

  const toggleSensor = (id: string) => {
    setSelectedIds(prev =>
      prev.includes(id)
        ? prev.length > 1 ? prev.filter(s => s !== id) : prev
        : [...prev, id].slice(-3)
    );
  };

  const selectedSamples = useMemo(
    () => SAMPLES.filter(s => selectedIds.includes(s.id)),
    [selectedIds]
  );

  const diurnalData = useMemo(() => {
    const base: Record<string, any>[] = Array.from({ length: 24 }, (_, h) => ({ hour: `${h}:00` }));
    selectedSamples.forEach(s => {
      s.diurnal.forEach(d => { base[d.hour][s.id] = d.mean; });
    });
    return base;
  }, [selectedSamples]);

  const weeklyData = useMemo(() => {
    return selectedSamples[0]?.week_slice.slice(0, 48).map((w, i) => {
      const row: Record<string, any> = { t: w.timestamp };
      selectedSamples.forEach(s => { row[s.id] = s.week_slice[i]?.flow ?? null; });
      return row;
    }) ?? [];
  }, [selectedSamples]);

  const statsData = useMemo(() =>
    SAMPLES.map(s => ({
      id: s.id,
      'Mean Flow': +s.mean_flow.toFixed(1),
      'Max Flow': +s.max_flow.toFixed(1),
      'Zero Flow %': +s.zero_flow_pct.toFixed(1),
    })),
    []
  );

  return (
    <section id="explorer" className="min-h-screen pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-2">Traffic Flow Explorer</h2>
          <p className="text-slate-400 text-sm max-w-2xl">
            Explore SCOOT loop-detector traffic flow counts (vehicles/interval) across Glasgow.
            Data reflects historical observations — not live telemetry. Flow is vehicle count, not speed or congestion.
          </p>
        </div>

        {/* Sensor selector */}
        <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-5 mb-6">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <span className="text-xs text-slate-400 font-medium">Select detectors (max 3):</span>
            {SENSOR_IDS.map((id, i) => (
              <button key={id} onClick={() => toggleSensor(id)}
                className="px-3 py-1 rounded-full text-xs font-mono border transition-all"
                style={selectedIds.includes(id)
                  ? { borderColor: COLORS[i % COLORS.length] + '99', color: COLORS[i % COLORS.length], background: COLORS[i % COLORS.length] + '18' }
                  : { borderColor: '#334155', color: '#64748b' }}
              >{id}</button>
            ))}
          </div>
          <p className="text-xs text-slate-600">Showing 5 detectors from 470 total. Full dataset: <a href="https://doi.org/10.5281/zenodo.12100278" target="_blank" rel="noreferrer" className="text-cyan-600 hover:underline">Zenodo DOI</a>.</p>
        </div>

        {/* View toggle */}
        <div className="flex gap-2 mb-6">
          {(['diurnal', 'weekly', 'stats'] as const).map(mode => (
            <button key={mode} onClick={() => setViewMode(mode)}
              className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                viewMode === mode ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-300' : 'bg-slate-800/60 border border-slate-700/60 text-slate-400 hover:text-slate-200'
              }`}>
              {mode === 'diurnal' ? '24-hr Profile' : mode === 'weekly' ? '1-Week Slice' : 'Detector Stats'}
            </button>
          ))}
        </div>

        {/* Chart */}
        <div className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-6 mb-8">
          {viewMode === 'diurnal' && (
            <>
              <h3 className="text-sm font-semibold text-slate-200 mb-1">Mean Diurnal Traffic Flow Profile</h3>
              <p className="text-xs text-slate-500 mb-5">Mean flow by hour of day. Source: SCOOT loop detectors (OGL v3.0).</p>
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={diurnalData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="hour" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} label={{ value: 'Flow (veh/interval)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11, dx: -8 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
                  {selectedSamples.map((s, i) => (
                    <Line key={s.id} type="monotone" dataKey={s.id} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </>
          )}
          {viewMode === 'weekly' && (
            <>
              <h3 className="text-sm font-semibold text-slate-200 mb-1">1-Week Continuous Flow Sample (first 48 intervals)</h3>
              <p className="text-xs text-slate-500 mb-5">Raw flow values from a continuous 7-day window. Gaps indicate missing observations.</p>
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={weeklyData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="t" tick={{ fill: '#94a3b8', fontSize: 10 }} interval={5} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} label={{ value: 'Flow (veh/interval)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11, dx: -8 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
                  {selectedSamples.map((s, i) => (
                    <Line key={s.id} type="monotone" dataKey={s.id} stroke={COLORS[i % COLORS.length]} strokeWidth={1.5} dot={false} connectNulls={false} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </>
          )}
          {viewMode === 'stats' && (
            <>
              <h3 className="text-sm font-semibold text-slate-200 mb-1">Detector Summary Statistics</h3>
              <p className="text-xs text-slate-500 mb-5">Mean flow, max observed flow, and zero-flow percentage per detector.</p>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={statsData} margin={{ top: 5, right: 20, bottom: 30, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="id" tick={{ fill: '#94a3b8', fontSize: 10 }} angle={-20} textAnchor="end" />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
                  <Bar dataKey="Mean Flow" fill="#22d3ee" radius={[3,3,0,0]} />
                  <Bar dataKey="Zero Flow %" fill="#f472b6" radius={[3,3,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </>
          )}
        </div>

        <div className="rounded-xl bg-slate-900/40 border border-slate-800/40 p-5 text-xs text-slate-400">
          <p className="font-semibold text-slate-300 mb-2">Methodology Notes</p>
          <ul className="space-y-1.5 list-disc list-inside">
            <li>Traffic flow is SCOOT vehicle count per measurement interval — not speed, density, or travel time.</li>
            <li>Zero-flow readings may reflect low genuine traffic, detector fault, or suppressed output — they are <em>not</em> distinguished in the source data.</li>
            <li>Missing timestamps are identified by gap detection; null values reflect genuine observation absence, not imputed zeros.</li>
            <li>Diurnal profiles use <code className="font-mono text-slate-300">mean</code> of observed records only; missing intervals are excluded.</li>
            <li>Source: Glasgow SCOOT dataset, DOI <a href="https://doi.org/10.5281/zenodo.12100278" target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline">10.5281/zenodo.12100278</a>, OGL v3.0.</li>
          </ul>
        </div>
      </div>
    </section>
  );
};
