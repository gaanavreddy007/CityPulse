import React, { useState, useMemo } from 'react';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';
import flowSamplesRaw from '../data/flow_samples.json';
import { SlidersHorizontal } from 'lucide-react';

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

// Editorial palette: deep navy, vermilion, forest, ochre, plum
const PALETTE = ['#1E3A8A', '#C25E2E', '#2D6A4F', '#B45309', '#6B21A8'];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-[#CEC8BD] rounded px-3 py-2 shadow-sm text-xs font-mono">
      <p className="text-[#718096] font-semibold border-b border-[#E2DDD5] pb-1 mb-1.5">{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex items-center justify-between gap-4 py-0.5">
          <span style={{ color: p.color }} className="font-medium">{p.name}:</span>
          <span className="font-semibold text-[#0D1117]">
            {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}
          </span>
        </div>
      ))}
    </div>
  );
};

const VIEW_MODES = [
  { id: 'diurnal', label: 'Diurnal Profile (24h Mean)' },
  { id: 'weekly',  label: 'Weekly Continuous Slice' },
  { id: 'stats',   label: 'Detector Summary' },
] as const;

type ViewMode = typeof VIEW_MODES[number]['id'];

export const ExplorerView: React.FC = () => {
  const [selectedIds, setSelectedIds] = useState<string[]>([SENSOR_IDS[0], SENSOR_IDS[1] || SENSOR_IDS[0]]);
  const [viewMode, setViewMode] = useState<ViewMode>('diurnal');

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
    const base: Record<string, any>[] = Array.from({ length: 24 }, (_, h) => ({ hour: `${String(h).padStart(2, '0')}:00` }));
    selectedSamples.forEach(s => {
      s.diurnal.forEach(d => { base[d.hour][s.id] = d.mean; });
    });
    return base;
  }, [selectedSamples]);

  const weeklyData = useMemo(() => {
    if (!selectedSamples.length) return [];
    const maxLen = Math.min(48, Math.max(...selectedSamples.map(s => s.week_slice.length)));
    return Array.from({ length: maxLen }, (_, i) => {
      const row: Record<string, any> = { t: selectedSamples[0].week_slice[i]?.timestamp || `T${i}` };
      selectedSamples.forEach(s => { row[s.id] = s.week_slice[i]?.flow ?? null; });
      return row;
    });
  }, [selectedSamples]);

  const statsData = useMemo(() =>
    selectedSamples.map(s => ({
      id: s.id,
      'Mean Flow': parseFloat(s.mean_flow.toFixed(1)),
      'Max Flow': s.max_flow,
      'Zero Flow %': parseFloat(s.zero_flow_pct.toFixed(1)),
    })),
    [selectedSamples]
  );

  return (
    <section id="explorer" className="py-16 lg:py-20 border-t border-[#E2DDD5]">
      <div className="cp-container">

        {/* ── Section heading ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 mb-8 items-end">
          <div className="lg:col-span-4">
            <div className="text-section-label mb-2">02 · Empirical Observations</div>
            <h2 className="text-headline">Sensor Flow Explorer</h2>
          </div>
          <div className="lg:col-span-8">
            <p className="text-sm text-[#4A5568] leading-relaxed mb-3 max-w-2xl">
              Baseline flow profiles across representative SCOOT inductive loop detectors in Glasgow. Counts record vehicle passes per fixed logging interval under Open Government Licence.
            </p>
            {/* Methodology notes inline */}
            <div className="flex flex-wrap gap-4 text-[11px] font-mono text-[#718096]">
              <span><span className="text-[#0D1117] font-semibold">Metric:</span> Vehicle count / interval</span>
              <span><span className="text-[#0D1117] font-semibold">Source:</span> Zenodo 10.5281/zenodo.12100278</span>
              <span><span className="text-[#0D1117] font-semibold">Licence:</span> OGL v3.0</span>
            </div>
          </div>
        </div>

        {/* ── Controls bar ── */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border-y border-[#E2DDD5] py-3 mb-6">
          {/* Mode toggle */}
          <div className="flex items-center gap-1 border border-[#CEC8BD] p-0.5 rounded bg-[#F2EEE6]">
            {VIEW_MODES.map(({ id, label }) => (
              <button
                key={id}
                onClick={() => setViewMode(id)}
                className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                  viewMode === id
                    ? 'bg-white text-[#0D1117] font-semibold shadow-sm'
                    : 'text-[#4A5568] hover:text-[#0D1117]'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Sensor selector */}
          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="font-mono text-[#718096] flex items-center gap-1 text-[11px]">
              <SlidersHorizontal size={11} /> Compare up to 3:
            </span>
            {SENSOR_IDS.map(id => {
              const isSelected = selectedIds.includes(id);
              const colorIdx = selectedIds.indexOf(id);
              const badgeColor = isSelected ? PALETTE[colorIdx % PALETTE.length] : undefined;
              return (
                <button
                  key={id}
                  onClick={() => toggleSensor(id)}
                  className={`px-2 py-1 text-[11px] font-mono rounded border transition-all ${
                    isSelected
                      ? 'border-transparent text-white font-semibold'
                      : 'border-[#CEC8BD] text-[#4A5568] bg-white hover:border-[#0D1117]'
                  }`}
                  style={isSelected ? { backgroundColor: badgeColor } : {}}
                >
                  {id}
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Chart ── */}
        <div className="bg-white border border-[#E2DDD5] rounded overflow-hidden mb-8">

          {/* Chart header */}
          <div className="px-5 py-4 border-b border-[#E2DDD5] flex flex-col sm:flex-row sm:items-baseline justify-between gap-2">
            <div>
              <h3 className="font-serif text-lg text-[#0D1117]">
                {viewMode === 'diurnal' && 'Mean Diurnal Traffic Flow by Hour'}
                {viewMode === 'weekly'  && 'Continuous 7-Day Time-Series Window'}
                {viewMode === 'stats'   && 'Comparative Detector Characteristics'}
              </h3>
              <p className="text-xs text-[#718096] mt-0.5">
                {viewMode === 'diurnal' && 'Aggregated vehicle count across the 24-hour cycle. Morning and evening commuter peaks visible.'}
                {viewMode === 'weekly'  && 'Sequential trace showing weekend drops, night-time nadirs, and occasional detector dropouts.'}
                {viewMode === 'stats'   && 'Mean flow versus zero-flow reading percentage across selected loop detectors.'}
              </p>
            </div>
            <span className="text-[11px] font-mono text-[#718096] flex-shrink-0">
              {viewMode === 'weekly' ? 'First 48 intervals' : 'Unit: veh / interval'}
            </span>
          </div>

          <div className="p-4 sm:p-5">
            <div className="h-[280px] sm:h-[320px] lg:h-[350px] w-full min-w-0">
              <ResponsiveContainer width="100%" height="100%">
                {viewMode === 'diurnal' ? (
                  <LineChart data={diurnalData} margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" vertical={false} />
                    <XAxis dataKey="hour" tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }} />
                    <YAxis tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }} width={40} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ paddingTop: '16px', fontSize: '11px', fontFamily: 'JetBrains Mono, monospace' }} />
                    {selectedSamples.map((s, i) => (
                      <Line key={s.id} type="monotone" dataKey={s.id} stroke={PALETTE[i % PALETTE.length]} strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                    ))}
                  </LineChart>
                ) : viewMode === 'weekly' ? (
                  <LineChart data={weeklyData} margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" vertical={false} />
                    <XAxis dataKey="t" tick={{ fill: '#718096', fontSize: 10 }} interval={5} tickLine={false} axisLine={{ stroke: '#CEC8BD' }} />
                    <YAxis tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }} width={40} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ paddingTop: '16px', fontSize: '11px', fontFamily: 'JetBrains Mono, monospace' }} />
                    {selectedSamples.map((s, i) => (
                      <Line key={s.id} type="monotone" dataKey={s.id} stroke={PALETTE[i % PALETTE.length]} strokeWidth={1.5} dot={false} connectNulls={false} />
                    ))}
                  </LineChart>
                ) : (
                  <BarChart data={statsData} margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" vertical={false} />
                    <XAxis dataKey="id" tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }} />
                    <YAxis tick={{ fill: '#718096', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#CEC8BD' }} width={40} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ paddingTop: '16px', fontSize: '11px', fontFamily: 'JetBrains Mono, monospace' }} />
                    <Bar dataKey="Mean Flow" fill="#1E3A8A" radius={[2, 2, 0, 0]} />
                    <Bar dataKey="Zero Flow %" fill="#C25E2E" radius={[2, 2, 0, 0]} />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* ── Field notes — inline, not cards ── */}
        <div className="border-t border-[#E2DDD5] pt-8 grid grid-cols-1 md:grid-cols-3 gap-8 text-xs text-[#4A5568]">
          <div>
            <h4 className="font-mono text-[10px] font-semibold uppercase tracking-widest text-[#0D1117] mb-2">Observation Metric</h4>
            <p className="leading-relaxed">
              SCOOT detector counts record vehicle passes per fixed logging interval — discrete flux counts, not speed, queue occupancy, or travel-time delays.
            </p>
          </div>
          <div>
            <h4 className="font-mono text-[10px] font-semibold uppercase tracking-widest text-[#0D1117] mb-2">Zero-Flow Ambiguity</h4>
            <p className="leading-relaxed">
              Zero-flow records may indicate genuine nocturnal absence of traffic or an unflagged sensor power failure. Raw municipal telemetry does not disambiguate these states.
            </p>
          </div>
          <div>
            <h4 className="font-mono text-[10px] font-semibold uppercase tracking-widest text-[#0D1117] mb-2">Provenance</h4>
            <p className="leading-relaxed">
              Extracted from Zenodo archive (DOI: 10.5281/zenodo.12100278) under UK Open Government Licence v3.0 — Glasgow City Council / Transport Scotland.
            </p>
          </div>
        </div>

      </div>
    </section>
  );
};
