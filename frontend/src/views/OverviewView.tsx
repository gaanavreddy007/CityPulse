import React from 'react';
import { ArrowDown, ArrowUpRight, GitFork, ShieldCheck } from 'lucide-react';

interface OverviewViewProps {
  onNav: (section: string) => void;
}

const STATS = [
  { value: '470',     label: 'SCOOT Detectors',     sub: 'Inductive loop sensors' },
  { value: '1,327',   label: 'Road Graph Nodes',     sub: 'OSM junctions' },
  { value: '3,201',   label: 'Directed Edges',       sub: 'Traffic segments' },
  { value: '6',       label: 'Bridge Scenarios',     sub: 'River Clyde crossings' },
  { value: '60',      label: 'Anomaly Benchmarks',   sub: 'Synthetic corruptions' },
  { value: '56 / 56', label: 'Unit Tests',           sub: '100% offline pass rate' },
];

const RESEARCH_QUESTIONS = [
  {
    n: '01',
    title: 'Sensor Fault Sensitivity',
    body: 'How resilient are univariate time-series anomaly detectors — Rolling Z-score, Seasonal ESD, Isolation Forest, LOF — to subtle, insidious sensor degradation compared to catastrophic dropout events?',
    tag: 'Signal Quality',
  },
  {
    n: '02',
    title: 'Spatial Cross-Consistency',
    body: 'Can bivariate spatial cross-consistency tracking between neighbouring sensors reliably isolate localized hardware drift from city-wide macro demand fluctuations such as severe weather?',
    tag: 'Spatial Analysis',
  },
  {
    n: '03',
    title: 'Network Resilience & Couplets',
    body: 'How resilient is the Glasgow River Clyde crossing network to bridge severances, and how do asymmetric directional couplets — King George V vs. Glasgow Bridge — govern rerouting?',
    tag: 'Graph Theory',
  },
  {
    n: '04',
    title: 'Boundary Sensitivity',
    body: 'How do geographic study boundaries and network representation assumptions introduce topological edge artifacts in modelled route choices and unreachable origin-destination pairs?',
    tag: 'Boundary Effects',
  },
];

export const OverviewView: React.FC<OverviewViewProps> = ({ onNav }) => {
  return (
    <section id="overview" style={{ paddingTop: '3.25rem' }}>

      {/* ── Hero ─────────────────────────────────────────── */}
      <div className="relative overflow-hidden bg-[#FAF8F4]">

        {/* Fine decorative rule top */}
        <div className="absolute top-0 left-0 right-0 h-px bg-[#E2DDD5]" />

        <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 pt-16 pb-20 lg:pb-24">

          {/* Eyebrow meta row */}
          <div className="flex flex-wrap items-center gap-3 mb-10 animate-fade-up">
            <span className="text-section-label">Urban Systems · Research Series</span>
            <span className="text-[#CEC8BD]">—</span>
            <span className="font-mono text-[10px] text-[#718096] uppercase tracking-widest">Glasgow, Scotland</span>
            <span className="text-[#CEC8BD]">—</span>
            <span className="font-mono text-[10px] text-[#718096]">SCOOT (OGL v3.0) · OSM (ODbL 1.0)</span>
          </div>

          {/* Main hero grid: 7/5 split */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">

            {/* Left: Editorial text column */}
            <div className="lg:col-span-7 animate-fade-up delay-100">

              <h1 className="text-display mb-7" style={{ maxWidth: '18ch' }}>
                Traffic Resilience&nbsp;&amp; Sensor Integrity in Central Glasgow
              </h1>

              <p className="text-base text-[#4A5568] leading-relaxed mb-5 font-light" style={{ maxWidth: '52ch' }}>
                An empirical investigation into urban traffic sensor corruption, spatial cross-consistency anomaly detection, and graph-theoretic road network resilience — conducted on historical SCOOT and OpenStreetMap data.
              </p>

              <div className="pull-quote mb-8" style={{ maxWidth: '44ch' }}>
                From raw inductive loop counts and synthetic fault injections to directional couplet severance simulations on River Clyde bridges.
              </div>

              {/* CTA row */}
              <div className="flex flex-wrap items-center gap-3 mb-10">
                <button
                  onClick={() => onNav('explorer')}
                  className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-[#0D1117] rounded hover:bg-[#1A202C] transition-colors"
                >
                  Explore Sensor Data
                  <ArrowDown size={14} />
                </button>

                <button
                  onClick={() => onNav('network')}
                  className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-[#0D1117] bg-white border border-[#CEC8BD] rounded hover:border-[#0D1117] hover:bg-[#F2EEE6] transition-all"
                >
                  Network Resilience
                  <ArrowDown size={14} />
                </button>

                <a
                  href="https://github.com/gaanavreddy007/CityPulse"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-2.5 text-xs font-mono text-[#4A5568] hover:text-[#C25E2E] transition-colors"
                >
                  <GitFork size={12} className="text-[#C25E2E]" />
                  <span>Source</span>
                  <ArrowUpRight size={11} className="opacity-60" />
                </a>
              </div>

              {/* Retrospective disclaimer — visible but unobtrusive */}
              <div className="flex items-start gap-3 text-[11px] text-[#718096] font-mono max-w-lg">
                <ShieldCheck size={13} className="text-[#9CA3AF] shrink-0 mt-0.5" />
                <span className="leading-relaxed">
                  Retrospective academic research on historical 2019–2023 SCOOT data. Not a live operations system or dynamic commuter tracker.
                </span>
              </div>
            </div>

            {/* Right: Network figure — large and prominent */}
            <div className="lg:col-span-5 animate-fade-up delay-300">
              <div className="relative">
                {/* Figure badge */}
                <div className="absolute -top-3 left-4 z-10">
                  <span className="inline-block font-mono text-[10px] font-semibold px-2.5 py-1 bg-[#0D1117] text-[#F7F6F3] rounded-sm">
                    Fig. 1 · Network Topology
                  </span>
                </div>

                {/* Main figure frame */}
                <div className="border border-[#E2DDD5] bg-[#F2EEE6] rounded overflow-hidden">
                  <div className="aspect-[4/3] flex items-center justify-center">
                    <img
                      src="./figures/fig1_road_network_topology.png"
                      alt="Glasgow OSM Road Network Topology — 1,327 nodes, 3,201 directed edges"
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = '/figures/fig1_road_network_topology.png';
                      }}
                    />
                  </div>

                  {/* Caption strip */}
                  <div className="px-4 py-3 border-t border-[#E2DDD5] bg-white">
                    <p className="text-[11px] text-[#4A5568] leading-snug font-mono">
                      Dijkstra road graph of central Glasgow derived from OpenStreetMap, highlighting River Clyde bridge crossings and directional couplets.
                    </p>
                    <div className="mt-1.5 flex items-center justify-between text-[10px] font-mono text-[#718096]">
                      <span>1,327 nodes · 3,201 edges</span>
                      <span>OSMnx · ODbL 1.0</span>
                    </div>
                  </div>
                </div>

                {/* Small fig preview — couplet schematic */}
                <div className="mt-3 border border-[#E2DDD5] bg-white rounded overflow-hidden">
                  <div className="flex items-center gap-3 p-3">
                    <div className="w-16 h-16 bg-[#F2EEE6] rounded overflow-hidden flex-shrink-0 flex items-center justify-center">
                      <img
                        src="./figures/fig2_directional_couplet_schematic.png"
                        alt="Directional couplet schematic"
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/figures/fig2_directional_couplet_schematic.png';
                        }}
                      />
                    </div>
                    <div>
                      <div className="font-mono text-[9px] text-[#C25E2E] font-semibold uppercase tracking-wider mb-0.5">Key Finding</div>
                      <p className="text-xs text-[#1A202C] font-medium leading-snug">King George V ↑ / Glasgow Bridge ↓ directional couplet asymmetry</p>
                      <button onClick={() => onNav('network')} className="text-[10px] font-mono text-[#718096] hover:text-[#C25E2E] mt-0.5 transition-colors">Explore resilience →</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Evidence Strip ────────────────────────────────── */}
      <div className="border-y border-[#E2DDD5] bg-white">
        <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">
          <div className="flex flex-wrap lg:flex-nowrap">
            {STATS.map(({ value, label, sub }, i) => (
              <div
                key={label}
                className={`py-6 px-6 flex-1 min-w-[140px] ${
                  i > 0 ? 'border-l border-[#E2DDD5]' : ''
                }`}
              >
                <div
                  className="font-serif text-[2rem] font-light text-[#0D1117] tracking-tight mb-0.5"
                  style={{ lineHeight: 1 }}
                >
                  {value}
                </div>
                <div className="text-[11px] font-semibold text-[#1A202C] mb-0.5">{label}</div>
                <div className="text-[10px] font-mono text-[#718096] leading-snug">{sub}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Research Narrative ────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 py-20">

        {/* Section intro */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 mb-16">
          <div className="lg:col-span-4">
            <div className="text-section-label mb-3">Research Inquiry</div>
            <h2 className="text-headline mb-4">Four Core Questions</h2>
          </div>
          <div className="lg:col-span-8 flex items-end">
            <p className="text-sm text-[#4A5568] leading-relaxed max-w-2xl">
              The study is organized around four specific methodological and empirical questions examining the limits of inductive loop sensor networks and the topological vulnerabilities of Glasgow's road network under bridge severance scenarios.
            </p>
          </div>
        </div>

        {/* Questions — ruled list, not cards */}
        <div className="border-t border-[#E2DDD5]">
          {RESEARCH_QUESTIONS.map(({ n, title, body, tag }) => (
            <div
              key={n}
              className="grid grid-cols-1 lg:grid-cols-12 gap-6 py-10 border-b border-[#E2DDD5] group"
            >
              {/* Number + tag column */}
              <div className="lg:col-span-2 flex lg:flex-col lg:items-start items-center gap-4">
                <span
                  className="font-mono text-[2.5rem] font-light text-[#E2DDD5] group-hover:text-[#C25E2E] transition-colors leading-none"
                  aria-hidden="true"
                >
                  {n}
                </span>
                <span className="font-mono text-[9px] font-semibold uppercase tracking-widest text-[#718096] mt-auto">
                  {tag}
                </span>
              </div>

              {/* Content column */}
              <div className="lg:col-span-10">
                <h3 className="font-serif text-xl font-medium text-[#0D1117] mb-3">{title}</h3>
                <p className="text-sm text-[#4A5568] leading-relaxed" style={{ maxWidth: '62ch' }}>{body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Methodological Context ────────────────────────── */}
      <div className="border-t border-[#E2DDD5] bg-[#F2EEE6]">
        <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 py-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-1 flex justify-center lg:justify-start pt-0.5">
              <ShieldCheck size={20} className="text-[#9CA3AF]" />
            </div>
            <div className="lg:col-span-11">
              <div className="font-mono text-xs font-semibold text-[#0D1117] uppercase tracking-wider mb-2">
                Methodological Context & Research Boundaries
              </div>
              <p className="text-xs text-[#4A5568] leading-relaxed max-w-4xl">
                This portfolio is an academic research demonstration conducted on historical SCOOT observations and open cartographic data. Shortest-path calculations reflect free-flow legal speed limits — not dynamic congestion queues. Anomaly detections reflect statistical volume deviations on synthetic benchmark corruptions rather than verified live municipal hardware incidents.
              </p>
            </div>
          </div>
        </div>
      </div>

    </section>
  );
};
