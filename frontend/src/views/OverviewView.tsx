import React from 'react';
import { Activity, GitBranch, Map, FlaskConical, ArrowRight, ExternalLink, ShieldAlert, Database, Cpu } from 'lucide-react';

const STATS = [
  { label: 'SCOOT Detectors', value: '470', unit: 'sensors', color: 'cyan' },
  { label: 'OSM Network Nodes', value: '1,327', unit: 'nodes', color: 'violet' },
  { label: 'OSM Network Edges', value: '3,201', unit: 'edges', color: 'violet' },
  { label: 'Unit Tests', value: '56 / 56', unit: 'passing', color: 'emerald' },
  { label: 'Bridge Scenarios', value: '6', unit: 'modelled', color: 'amber' },
  { label: 'Anomaly Benchmarks', value: '60', unit: 'evaluated', color: 'rose' },
];

const PIPELINE = [
  { icon: Database,     title: 'Data Ingestion',    desc: 'Glasgow SCOOT CSV extraction, column normalisation, timezone handling.' },
  { icon: Activity,     title: 'EDA & Missingness', desc: 'Flow distributions, zero-flow rates, timestamp gap detection per detector.' },
  { icon: FlaskConical, title: 'Anomaly Detection', desc: 'IQR, Z-score, CUSUM, Isolation Forest benchmarked on injected corruption.' },
  { icon: Map,          title: 'Spatial Analysis',  desc: 'Bivariate cross-consistency across 30 detector pairs.' },
  { icon: GitBranch,    title: 'Network Resilience',desc: 'OSM graph construction, Dijkstra routing, Monte Carlo bridge closure simulation.' },
  { icon: Cpu,          title: 'Results & Figures', desc: '6 publication-quality figures generated and version-controlled.' },
];

interface OverviewViewProps {
  onNav: (section: string) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ onNav }) => {
  return (
    <section id="overview" className="min-h-screen pt-20">
      {/* Hero */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-950/30 via-slate-900/0 to-violet-950/30 pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/50 text-cyan-300 text-xs font-mono mb-6">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
              Retrospective Research · Glasgow, Scotland · 2024
            </div>
            <h1 className="text-4xl md:text-6xl font-extrabold text-slate-100 leading-tight mb-6">
              City<span className="text-cyan-400">Pulse</span>
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 font-light leading-relaxed mb-4">
              Urban Traffic Resilience Analysis of Glasgow's Road Network
            </p>
            <p className="text-slate-400 text-base leading-relaxed mb-8 max-w-2xl">
              An end-to-end retrospective data science study using Glasgow SCOOT traffic-flow sensors and
              OpenStreetMap road network data to evaluate sensor data quality, anomaly detection methods,
              and simulated road-network resilience under bridge-closure scenarios.
            </p>

            <div className="flex flex-wrap gap-3 mb-6">
              <button
                onClick={() => onNav('explorer')}
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 text-sm font-semibold hover:bg-cyan-500/30 transition-all"
              >
                Explore Traffic Data <ArrowRight size={15} />
              </button>
              <button
                onClick={() => onNav('network')}
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-violet-500/20 border border-violet-500/40 text-violet-300 text-sm font-semibold hover:bg-violet-500/30 transition-all"
              >
                Network Resilience <Map size={15} />
              </button>
              <a
                href="https://github.com/gaanavreddy007/CityPulse"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60 text-slate-300 text-sm font-semibold hover:bg-slate-800 transition-all"
              >
                Source Code <ExternalLink size={15} />
              </a>
            </div>

            {/* Non-operational disclaimer */}
            <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-950/30 border border-amber-800/40 text-amber-300/90 text-xs max-w-2xl">
              <ShieldAlert size={16} className="shrink-0 mt-0.5" />
              <span>
                <strong>Research Notice:</strong> This is a retrospective study on historical data (Open Government Licence v3.0).
                It does not provide live traffic monitoring, real-time routing, or operational traffic management of any kind.
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats strip */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {STATS.map(({ label, value, unit, color }) => (
            <div key={label} className="rounded-xl bg-slate-900/60 border border-slate-800/60 p-4 text-center hover:border-slate-700/60 transition-all">
              <div className={`text-2xl font-bold ${
                color === 'cyan' ? 'text-cyan-400' :
                color === 'violet' ? 'text-violet-400' :
                color === 'emerald' ? 'text-emerald-400' :
                color === 'amber' ? 'text-amber-400' : 'text-rose-400'
              } mb-1`}>{value}</div>
              <div className="text-xs text-slate-300 font-medium leading-tight mb-0.5">{label}</div>
              <div className="text-xs text-slate-500">{unit}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Research Question */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800/60 p-8 md:p-10">
          <h2 className="text-xl font-bold text-slate-100 mb-2">Research Question</h2>
          <p className="text-slate-400 text-sm mb-6 max-w-xl">What this study set out to investigate</p>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { q: 'Data Quality', desc: 'How complete and reliable are Glasgow\'s SCOOT traffic-flow observations? What are the temporal missingness patterns across 470 detectors?' },
              { q: 'Anomaly Detection', desc: 'Which statistical and ML methods best identify both naturally occurring anomalies and deliberately injected synthetic corruption in sensor streams?' },
              { q: 'Network Resilience', desc: 'How does simulated closure of River Clyde bridges affect modelled routing costs, unreachable pairs, and network connectivity for origin-destination flows?' },
            ].map(({ q, desc }) => (
              <div key={q} className="p-5 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <h3 className="text-sm font-semibold text-cyan-300 mb-3">{q}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pipeline */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <h2 className="text-xl font-bold text-slate-100 mb-2">Research Pipeline</h2>
        <p className="text-slate-400 text-sm mb-8">End-to-end methodology — from raw SCOOT CSV to publication figures</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {PIPELINE.map(({ icon: Icon, title, desc }, i) => (
            <div key={title} className="flex gap-4 p-5 rounded-xl bg-slate-900/60 border border-slate-800/60 hover:border-cyan-800/40 transition-all group">
              <div className="shrink-0 h-9 w-9 rounded-lg bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center text-cyan-400 group-hover:bg-cyan-900/40 transition-all">
                <Icon size={16} />
              </div>
              <div>
                <div className="text-xs text-slate-500 font-mono mb-1">Step {i + 1}</div>
                <div className="text-sm font-semibold text-slate-200 mb-1">{title}</div>
                <div className="text-xs text-slate-400 leading-relaxed">{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dataset context */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800/60 p-8 md:p-10">
          <h2 className="text-xl font-bold text-slate-100 mb-6">Dataset & Provenance</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-sm font-semibold text-cyan-300 mb-3">Glasgow SCOOT Traffic Data</h3>
              <ul className="space-y-2 text-xs text-slate-400">
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">Source</span> Transport Scotland / Glasgow City Council via Zenodo</li>
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">DOI</span> <a href="https://doi.org/10.5281/zenodo.12100278" target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline">10.5281/zenodo.12100278</a></li>
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">Licence</span> Open Government Licence v3.0 (OGL)</li>
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">Measure</span> Traffic flow count (vehicles/interval) — not speed or congestion index</li>
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">Detectors</span> 470 SCOOT loop detectors across Glasgow</li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-violet-300 mb-3">OpenStreetMap Road Network</h3>
              <ul className="space-y-2 text-xs text-slate-400">
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">Source</span> © OpenStreetMap contributors via OSMnx</li>
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">Licence</span> Open Database Licence (ODbL 1.0)</li>
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">Graph</span> 1,327 nodes · 3,201 edges (directed)</li>
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">Routing</span> Dijkstra shortest-path on OSM travel-time weights — not measured journey times</li>
                <li className="flex gap-2"><span className="text-slate-600 font-mono w-20 shrink-0">Bridges</span> 6 River Clyde crossing scenarios modelled</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
