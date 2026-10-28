import React from 'react';
import { ArrowDown, ArrowUpRight, Database, GitFork, ShieldCheck, FileText } from 'lucide-react';

interface OverviewViewProps {
  onNav: (section: string) => void;
}

const STATS = [
  { label: 'SCOOT Detectors', value: '470', detail: 'Inductive loop sensors across Glasgow' },
  { label: 'OSM Graph Nodes', value: '1,327', detail: 'Topological road network junctions' },
  { label: 'OSM Graph Edges', value: '3,201', detail: 'Directed traffic flow segments' },
  { label: 'Closure Scenarios', value: '6', detail: 'River Clyde crossing evaluations' },
  { label: 'Anomaly Benchmarks', value: '60', detail: 'Synthetic corruptions tested' },
  { label: 'Unit Test Suite', value: '56 / 56', detail: '100% offline reproducible passing' },
];

export const OverviewView: React.FC<OverviewViewProps> = ({ onNav }) => {
  return (
    <section id="overview" className="pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Research Category & Metadata Label */}
        <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-[#6B7280] mb-6">
          <span className="px-2 py-0.5 rounded bg-[#F4F1EA] text-[#C25E2E] font-semibold border border-[#E5E0D8]">
            Academic Research Paper & Portfolio
          </span>
          <span>·</span>
          <span>Glasgow, Scotland</span>
          <span>·</span>
          <span>SCOOT (OGL v3.0) & OSM (ODbL 1.0)</span>
        </div>

        {/* Hero Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start mb-16">
          <div className="lg:col-span-7">
            <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl font-normal tracking-tight text-[#111827] leading-[1.15] mb-6">
              Traffic Sensor Data Quality, Spatial Consistency & Road Network Resilience
            </h1>
            
            <p className="text-base sm:text-lg text-[#374151] leading-relaxed mb-6 font-normal">
              An empirical investigation into urban traffic sensor corruption, spatial cross-consistency anomaly detection, and graph-theoretic road network resilience in central Glasgow, Scotland.
            </p>

            <div className="text-xs sm:text-sm text-[#4B5563] space-y-3 leading-relaxed mb-8 border-l-2 border-[#C25E2E] pl-4">
              <p>
                Urban intelligent transportation systems depend heavily on automated sensor feeds. However, real-world physical detectors face calibration drift and missingness, while simplified network models often mask critical operational vulnerabilities.
              </p>
              <p>
                This portfolio provides a transparent, end-to-end evaluation: from raw SCOOT sensor counts and synthetic fault injections to directional couplet severance simulations on River Clyde bridges.
              </p>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={() => onNav('explorer')}
                className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium text-white bg-[#111827] rounded hover:bg-[#1F2937] transition-colors"
              >
                <span>Explore Sensor Data</span>
                <ArrowDown size={14} />
              </button>

              <button
                onClick={() => onNav('network')}
                className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium text-[#1F2937] bg-white border border-[#D1C9BE] rounded hover:border-[#111827] hover:bg-[#F4F1EA] transition-colors"
              >
                <span>Network Resilience</span>
                <ArrowDown size={14} />
              </button>

              <a
                href="https://github.com/gaanavreddy007/CityPulse"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-mono text-[#4B5563] hover:text-[#111827] transition-colors"
              >
                <GitFork size={13} className="text-[#C25E2E]" />
                <span>Source Code</span>
                <ArrowUpRight size={12} className="opacity-60" />
              </a>
            </div>
          </div>

          {/* Restrained Visual Element Grounded in Research (Figure 1 preview) */}
          <div className="lg:col-span-5">
            <div className="border border-[#E5E0D8] bg-white p-3 rounded shadow-xs">
              <div className="aspect-[4/3] bg-[#F4F1EA] overflow-hidden rounded relative flex items-center justify-center">
                <img
                  src="./figures/fig1_road_network_topology.png"
                  alt="Glasgow OSM Road Network Topology"
                  className="w-full h-full object-contain"
                  onError={(e) => {
                    // Fallback visual diagram if image path needs local preview resolution
                    const target = e.target as HTMLImageElement;
                    target.src = '/figures/fig1_road_network_topology.png';
                  }}
                />
              </div>
              <div className="pt-3 px-1">
                <div className="flex items-center justify-between text-[11px] font-mono text-[#6B7280] mb-1">
                  <span>Fig. 1 · Network Model</span>
                  <span>1,327 nodes · 3,201 edges</span>
                </div>
                <p className="text-xs text-[#4B5563] leading-snug">
                  Dijkstra road graph of central Glasgow derived from OpenStreetMap, highlighting River Clyde bridge crossings and directional couplets.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Evidence-Backed Metric Strip (Horizontal on desktop, responsive columns) */}
        <div className="border-y border-[#E5E0D8] bg-white py-6 px-4 sm:px-6 rounded mb-16 shadow-xs">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 divide-y lg:divide-y-0 lg:divide-x divide-[#E5E0D8]">
            {STATS.map(({ label, value, detail }, i) => (
              <div key={label} className={`${i > 0 ? 'lg:pl-6' : ''} ${i > 1 ? 'pt-4 md:pt-0' : ''}`}>
                <div className="font-serif text-2xl sm:text-3xl font-medium text-[#111827] tracking-tight mb-0.5">
                  {value}
                </div>
                <div className="text-xs font-semibold text-[#1F2937] mb-1">
                  {label}
                </div>
                <div className="text-[11px] text-[#6B7280] leading-snug">
                  {detail}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Four Research Questions Editorial Sequence */}
        <div className="mb-16">
          <div className="max-w-2xl mb-8">
            <span className="text-xs font-mono uppercase tracking-wider text-[#C25E2E] font-semibold">
              Research Inquiry
            </span>
            <h2 className="font-serif text-2xl sm:text-3xl text-[#111827] mt-1 mb-3">
              Four Core Research Questions
            </h2>
            <p className="text-xs sm:text-sm text-[#4B5563]">
              The study is organized around four specific methodological and empirical questions examining sensor limits and topological vulnerabilities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                id: 'RQ1',
                title: 'Sensor Fault Sensitivity',
                desc: 'How resilient are univariate time-series anomaly detection algorithms (Rolling Z-score, Seasonal ESD, Isolation Forest, LOF) to subtle, insidious sensor degradation (multiplicative scale drift, additive bias) compared to catastrophic dropouts?',
                badge: 'Signal Quality'
              },
              {
                id: 'RQ2',
                title: 'Spatial Cross-Consistency',
                desc: 'Can bivariate spatial cross-consistency tracking between neighboring sensors reliably isolate localized sensor faults from city-wide macro demand fluctuations such as severe weather or holiday periods?',
                badge: 'Spatial Analysis'
              },
              {
                id: 'RQ3',
                title: 'Network Resilience & Couplets',
                desc: 'How resilient is the central Glasgow River Clyde crossing network to critical bridge severances, and how do asymmetric directional couplets (King George V Bridge vs. Glasgow Bridge) govern rerouting?',
                badge: 'Graph Theory'
              },
              {
                id: 'RQ4',
                title: 'Spatial Bounding & Sensitivity',
                desc: 'How do geographic study boundaries and network representation assumptions introduce topological edge artifacts in modelled route choices and unreachable OD node pairs?',
                badge: 'Boundary Effects'
              },
            ].map(({ id, title, desc, badge }) => (
              <div key={id} className="p-6 rounded border border-[#E5E0D8] bg-white shadow-xs">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-[#F4F1EA] text-[#C25E2E] border border-[#E5E0D8]">
                    {id}
                  </span>
                  <span className="text-[11px] font-mono text-[#6B7280]">{badge}</span>
                </div>
                <h3 className="font-serif text-lg font-medium text-[#111827] mb-2">{title}</h3>
                <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Research Notice / Caveat Box */}
        <div className="border border-[#D1C9BE] bg-[#F4F1EA] p-5 rounded text-xs text-[#374151] flex items-start gap-4">
          <div className="p-1 rounded bg-[#E5E0D8] text-[#111827] shrink-0 mt-0.5">
            <ShieldCheck size={16} />
          </div>
          <div>
            <div className="font-semibold text-[#111827] mb-1">
              Methodological Context & Research Boundaries
            </div>
            <p className="leading-relaxed">
              This portfolio is an academic research demonstration conducted on historical SCOOT observations and open cartographic data. In compliance with transport engineering standards: shortest-path calculations reflect free-flow legal speed limits (not dynamic congestion queues), and anomaly detections reflect statistical volume deviations on synthetic benchmark corruptions rather than verified live municipal hardware incidents.
            </p>
          </div>
        </div>

      </div>
    </section>
  );
};
