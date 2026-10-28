import React, { useState, useMemo } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import flowSamplesRaw from '../data/flow_samples.json';
import { Info, SlidersHorizontal } from 'lucide-react';

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

// Editorial data palette: Deep Navy, Burnt Orange, Slate Green, Ochre, Rose Slate
const PALETTE = ['#1E3A8A', '#C25E2E', '#2D6A4F', '#B45309', '#6B21A8'];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-[#D1C9BE] rounded px-3 py-2 shadow-sm text-xs font-mono">
      <p className="text-[#6B7280] font-semibold border-b border-[#E5E0D8] pb-1 mb-1.5">{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex items-center justify-between gap-4 py-0.5">
          <span style={{ color: p.color }} className="font-medium">{p.name}:</span>
          <span className="font-semibold text-[#111827]">
            {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export const ExplorerView: React.FC = () => {
  const [selectedIds, setSelectedIds] = useState<string[]>([SENSOR_IDS[0], SENSOR_IDS[1] || SENSOR_IDS[0]]);
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
      selectedSamples.forEach(s => {
        row[s.id] = s.week_slice[i]?.flow ?? null;
      });
      return row;
    });
  }, [selectedSamples]);

  const statsData = useMemo(() => {
    return selectedSamples.map(s => ({
      id: s.id,
      'Mean Flow': parseFloat(s.mean_flow.toFixed(1)),
      'Max Flow': s.max_flow,
      'Zero Flow %': parseFloat(s.zero_flow_pct.toFixed(1)),
    }));
  }, [selectedSamples]);

  return (
    <section id="explorer" className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Heading */}
        <div className="max-w-3xl mb-8">
          <span className="text-xs font-mono uppercase tracking-wider text-[#C25E2E] font-semibold">
            Section 02 · Empirical Observations
          </span>
          <h2 className="font-serif text-2xl sm:text-3xl text-[#111827] mt-1 mb-2">
            Traffic Flow Explorer: SCOOT Inductive Detectors
          </h2>
          <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed">
            Examination of baseline flow profiles across representative SCOOT detectors in Glasgow. Detectors measure traffic volume count per sampling interval under Open Government Licence (OGL v3.0).
          </p>
        </div>

        {/* View Controls & Filter Bar */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 rounded border border-[#E5E0D8] bg-white mb-6 shadow-xs">
          {/* Mode Switcher */}
          <div className="flex items-center gap-1.5 border border-[#D1C9BE] p-1 rounded bg-[#F4F1EA]">
            {[
              { id: 'diurnal', label: 'Diurnal Profile (24h Mean)' },
              { id: 'weekly', label: 'Weekly Continuous Slice' },
              { id: 'stats', label: 'Detector Summary Metrics' },
            ].map(({ id, label }) => (
              <button
                key={id}
                onClick={() => setViewMode(id as any)}
                className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                  viewMode === id
                    ? 'bg-white text-[#111827] font-semibold shadow-xs'
                    : 'text-[#4B5563] hover:text-[#111827]'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Sensor Selectors */}
          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="font-mono text-[#6B7280] flex items-center gap-1 text-[11px]">
              <SlidersHorizontal size={12} /> Compare (Max 3):
            </span>
            {SENSOR_IDS.map(id => {
              const isSelected = selectedIds.includes(id);
              const colorIdx = selectedIds.indexOf(id);
              const badgeColor = isSelected ? PALETTE[colorIdx % PALETTE.length] : undefined;
              return (
                <button
                  key={id}
                  onClick={() => toggleSensor(id)}
                  className={`px-2.5 py-1 text-xs font-mono rounded border transition-all ${
                    isSelected
                      ? 'border-transparent text-white font-semibold shadow-xs'
                      : 'border-[#D1C9BE] text-[#4B5563] bg-white hover:border-[#111827]'
                  }`}
                  style={isSelected ? { backgroundColor: badgeColor } : {}}
                >
                  {id}
                </button>
              );
            })}
          </div>
        </div>

        {/* Chart Surface Container */}
        <div className="border border-[#E5E0D8] bg-white p-6 sm:p-8 rounded shadow-xs mb-8">
          {viewMode === 'diurnal' && (
            <div>
              <div className="flex flex-col sm:flex-row sm:items-baseline justify-between border-b border-[#E5E0D8] pb-4 mb-6 gap-2">
                <div>
                  <h3 className="font-serif text-lg text-[#111827]">
                    Mean Diurnal Traffic Flow by Hour
                  </h3>
                  <p className="text-xs text-[#6B7280]">
                    Aggregated vehicle count per interval across the 24-hour cycle. Clear morning and evening commuter peaks are observable.
                  </p>
                </div>
                <span className="text-xs font-mono text-[#6B7280]">Unit: veh / interval</span>
              </div>

              <div className="h-[340px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={diurnalData} margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" vertical={false} />
                    <XAxis
                      dataKey="hour"
                      tick={{ fill: '#6B7280', fontSize: 11 }}
                      tickLine={false}
                      axisLine={{ stroke: '#D1C9BE' }}
                    />
                    <YAxis
                      tick={{ fill: '#6B7280', fontSize: 11 }}
                      tickLine={false}
                      axisLine={{ stroke: '#D1C9BE' }}
                      width={40}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ paddingTop: '16px', fontSize: '12px' }} />
                    {selectedSamples.map((s, i) => (
                      <Line
                        key={s.id}
                        type="monotone"
                        dataKey={s.id}
                        stroke={PALETTE[i % PALETTE.length]}
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4 }}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {viewMode === 'weekly' && (
            <div>
              <div className="flex flex-col sm:flex-row sm:items-baseline justify-between border-b border-[#E5E0D8] pb-4 mb-6 gap-2">
                <div>
                  <h3 className="font-serif text-lg text-[#111827]">
                    Continuous 7-Day Time-Series Window
                  </h3>
                  <p className="text-xs text-[#6B7280]">
                    Sequential observation trace showing weekend drops, night-time nadirs, and occasional detector dropouts.
                  </p>
                </div>
                <span className="text-xs font-mono text-[#6B7280]">First 48 intervals displayed</span>
              </div>

              <div className="h-[340px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weeklyData} margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" vertical={false} />
                    <XAxis
                      dataKey="t"
                      tick={{ fill: '#6B7280', fontSize: 10 }}
                      interval={5}
                      tickLine={false}
                      axisLine={{ stroke: '#D1C9BE' }}
                    />
                    <YAxis
                      tick={{ fill: '#6B7280', fontSize: 11 }}
                      tickLine={false}
                      axisLine={{ stroke: '#D1C9BE' }}
                      width={40}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ paddingTop: '16px', fontSize: '12px' }} />
                    {selectedSamples.map((s, i) => (
                      <Line
                        key={s.id}
                        type="monotone"
                        dataKey={s.id}
                        stroke={PALETTE[i % PALETTE.length]}
                        strokeWidth={1.5}
                        dot={false}
                        connectNulls={false}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {viewMode === 'stats' && (
            <div>
              <div className="flex flex-col sm:flex-row sm:items-baseline justify-between border-b border-[#E5E0D8] pb-4 mb-6 gap-2">
                <div>
                  <h3 className="font-serif text-lg text-[#111827]">
                    Comparative Detector Characteristics
                  </h3>
                  <p className="text-xs text-[#6B7280]">
                    Mean flow versus zero-flow reading percentage across selected loop detectors.
                  </p>
                </div>
                <span className="text-xs font-mono text-[#6B7280]">Source: Pre-processed SCOOT records</span>
              </div>

              <div className="h-[340px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={statsData} margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" vertical={false} />
                    <XAxis
                      dataKey="id"
                      tick={{ fill: '#6B7280', fontSize: 11 }}
                      tickLine={false}
                      axisLine={{ stroke: '#D1C9BE' }}
                    />
                    <YAxis
                      tick={{ fill: '#6B7280', fontSize: 11 }}
                      tickLine={false}
                      axisLine={{ stroke: '#D1C9BE' }}
                      width={40}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ paddingTop: '16px', fontSize: '12px' }} />
                    <Bar dataKey="Mean Flow" fill="#1E3A8A" radius={[2, 2, 0, 0]} />
                    <Bar dataKey="Zero Flow %" fill="#C25E2E" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>

        {/* Editorial Field Notes / Methodology */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs text-[#4B5563]">
          <div className="border border-[#E5E0D8] bg-[#F4F1EA] p-4 rounded">
            <h4 className="font-serif font-semibold text-[#111827] text-sm mb-1">Observation Metric</h4>
            <p className="leading-relaxed">
              SCOOT detector counts record vehicle passes per fixed logging interval. These represent discrete flux counts rather than vehicle speed, queue occupancy, or travel-time delays.
            </p>
          </div>
          <div className="border border-[#E5E0D8] bg-[#F4F1EA] p-4 rounded">
            <h4 className="font-serif font-semibold text-[#111827] text-sm mb-1">Zero-Flow Ambiguity</h4>
            <p className="leading-relaxed">
              Zero-flow records can indicate genuine absence of nocturnal traffic or an unflagged sensor power failure. Raw municipal telemetry does not disambiguate these states.
            </p>
          </div>
          <div className="border border-[#E5E0D8] bg-[#F4F1EA] p-4 rounded">
            <h4 className="font-serif font-semibold text-[#111827] text-sm mb-1">Provenance</h4>
            <p className="leading-relaxed">
              Extracted from Zenodo archive (DOI: 10.5281/zenodo.12100278) licensed under the UK Open Government Licence v3.0 (Glasgow City Council / Transport Scotland).
            </p>
          </div>
        </div>

      </div>
    </section>
  );
};
