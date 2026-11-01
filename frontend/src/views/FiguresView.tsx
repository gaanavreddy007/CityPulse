import React, { useState } from 'react';
import { ZoomIn, X, ExternalLink } from 'lucide-react';

interface Figure {
  id: string;
  filename: string;
  title: string;
  caption: string;
  section: string;
  figureNumber: string;
}

const FIGURES: Figure[] = [
  {
    id: 'fig1',
    figureNumber: 'Figure 1',
    filename: 'fig1_road_network_topology.png',
    title: 'Glasgow OSM Road Network Topology & River Clyde Crossings',
    caption: 'Directed graph of the Glasgow road network derived from OpenStreetMap via OSMnx (ODbL 1.0). Nodes represent junctions (1,327 total); edges represent road segments (3,201 total). Key crossings over the River Clyde are highlighted with directional indicators.',
    section: 'Network Topology',
  },
  {
    id: 'fig2',
    figureNumber: 'Figure 2',
    filename: 'fig2_directional_couplet_schematic.png',
    title: 'Directional Couplet Schematic: George V & Glasgow Bridge',
    caption: 'Schematic illustrating the synchronized one-way couplet system across the River Clyde. Northbound traffic flows exclusively via King George V Bridge, while southbound traffic flows across Glasgow Bridge, demonstrating the structural mechanism for route diversion asymmetries.',
    section: 'Network Resilience',
  },
  {
    id: 'fig3',
    figureNumber: 'Figure 3',
    filename: 'fig3_route_diversion_george_v.png',
    title: 'Route Diversion Paths Under King George V Bridge Severance',
    caption: 'Visualisation of modelled shortest-path diversions following simulated closure of King George V Bridge. Diverted trajectories shift toward the M8 Kingston Bridge flyover and downstream surface crossings. Based on free-flow edge weights.',
    section: 'Network Resilience',
  },
  {
    id: 'fig4',
    figureNumber: 'Figure 4',
    filename: 'fig4_boundary_truncation_map.png',
    title: 'Geographic Study Boundary & Motorway Truncation Map',
    caption: 'Demonstration of spatial edge artifacts caused by bounding box selection (55.865°N limit). Isolates northern motorway mainline stubs, explaining the 3.73% graph-unreachable OD node pairs under M8 Kingston Bridge closure as cartographic boundary truncations.',
    section: 'Sensitivity Analysis',
  },
  {
    id: 'fig5',
    figureNumber: 'Figure 5',
    filename: 'fig5_anomaly_detection_tradeoffs.png',
    title: 'Precision-Recall AUC Tradeoffs Across Anomaly Detection Models',
    caption: 'Comparative PR-AUC and false positive rate trajectories across five anomaly detection algorithms evaluated across 60 synthetic sensor corruption scenarios. Highlights the superior stability of Rolling Z-scores and Seasonal ESD on gradual calibration drift.',
    section: 'Anomaly Benchmarks',
  },
  {
    id: 'fig6',
    figureNumber: 'Figure 6',
    filename: 'fig6_cross_river_resilience_deltas.png',
    title: 'Cross-River Routing Cost Deltas Across Disruption Scenarios',
    caption: 'Monte Carlo evaluation of routing resistance shifts (mean delta seconds and 95% bootstrap confidence intervals) across 218,401 cross-river OD pairs. Confirms 100% reachability under central couplet closure.',
    section: 'Resilience Results',
  },
];

const SECTION_FILTERS = ['all', ...new Set(FIGURES.map(f => f.section))];

const DATA_SOURCES = [
  {
    title: 'SCOOT Traffic Flow',
    license: 'Open Government Licence (OGL v3.0)',
    desc: 'Raw Glasgow City Council / Transport Scotland inductive loop sensor observations archived on Zenodo.',
    link: 'https://doi.org/10.5281/zenodo.12100278',
    linkLabel: 'DOI: 10.5281/zenodo.12100278',
  },
  {
    title: 'Road Network Topology',
    license: 'Open Database License (ODbL 1.0)',
    desc: 'Cartographic road network graphs extracted via OSMnx. © OpenStreetMap contributors. 1,327 nodes, 3,201 edges.',
    link: 'https://www.openstreetmap.org/copyright',
    linkLabel: 'OSM Attribution Guidelines',
  },
  {
    title: 'Software & Benchmarks',
    license: 'MIT License (Code)',
    desc: 'Complete Python 3.13 analysis suite, automated unit tests (56/56 passing), simulation scripts, and React web app.',
    link: 'https://github.com/gaanavreddy007/CityPulse',
    linkLabel: 'GitHub Repository',
  },
];

export const FiguresView: React.FC = () => {
  const [activeSection, setActiveSection] = useState('all');
  const [modal, setModal] = useState<Figure | null>(null);

  const filtered = activeSection === 'all'
    ? FIGURES
    : FIGURES.filter(f => f.section === activeSection);

  return (
    <section id="figures" className="py-16 lg:py-20 border-t border-[#E2DDD5]">
      <div className="cp-container">

        {/* ── Section heading ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 mb-8 items-end">
          <div className="lg:col-span-4">
            <div className="text-section-label mb-2">06 · Publication Figures & Provenance</div>
            <h2 className="text-headline">Research Figures</h2>
          </div>
          <div className="lg:col-span-8">
            <p className="text-sm text-[#4A5568] leading-relaxed max-w-2xl">
              High-resolution analytical figures generated directly from the underlying Glasgow SCOOT and OpenStreetMap pipelines, alongside primary data licenses and offline reproduction protocols.
            </p>
          </div>
        </div>

        {/* ── Section filter tabs ── */}
        <div className="flex items-center gap-0 border-b border-[#E2DDD5] mb-8 overflow-x-auto">
          {SECTION_FILTERS.map(s => {
            const isActive = activeSection === s;
            return (
              <button
                key={s}
                onClick={() => setActiveSection(s)}
                className={`relative px-3.5 py-2 text-xs font-medium capitalize transition-colors whitespace-nowrap ${
                  isActive ? 'text-[#0D1117]' : 'text-[#718096] hover:text-[#0D1117]'
                }`}
              >
                {s === 'all' ? 'All 6 Figures' : s}
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-px bg-[#0D1117]" />
                )}
              </button>
            );
          })}
        </div>

        {/* ── Figures grid ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-12">
          {filtered.map(fig => (
            <div
              key={fig.id}
              className="group border border-[#E2DDD5] bg-white rounded overflow-hidden flex flex-col hover:border-[#0D1117] transition-all cursor-pointer"
              onClick={() => setModal(fig)}
            >
              {/* Figure thumbnail */}
              <div className="relative bg-[#F2EEE6] overflow-hidden" style={{ aspectRatio: '16/10' }}>
                <img
                  src={`./figures/${fig.filename}`}
                  alt={fig.title}
                  className="w-full h-full object-contain p-2 transition-transform duration-300 group-hover:scale-[1.02]"
                  onError={e => {
                    (e.target as HTMLImageElement).src = `/figures/${fig.filename}`;
                  }}
                />
                {/* Enlarge overlay */}
                <div className="absolute inset-0 bg-[#0D1117]/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-white/95 text-[#0D1117] text-[11px] font-medium border border-[#CEC8BD]">
                    <ZoomIn size={13} className="text-[#C25E2E]" />
                    Enlarge
                  </span>
                </div>
                {/* Figure number badge */}
                <div className="absolute top-2 left-2">
                  <span className="font-mono text-[10px] font-semibold px-2 py-0.5 rounded bg-[#0D1117] text-white">
                    {fig.figureNumber}
                  </span>
                </div>
              </div>

              {/* Caption */}
              <div className="p-3.5 flex-1 flex flex-col">
                <h3 className="font-serif text-sm text-[#0D1117] leading-snug mb-1.5">{fig.title}</h3>
                <p className="text-[11px] text-[#4A5568] leading-relaxed line-clamp-3 flex-1">{fig.caption}</p>
                <div className="pt-2.5 mt-2.5 border-t border-[#E2DDD5] flex items-center justify-between">
                  <span className="font-mono text-[10px] text-[#718096]">{fig.section}</span>
                  <span className="text-[10px] font-mono text-[#C25E2E] group-hover:underline">View →</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* ── Data Provenance ── */}
        <div className="border-t border-[#E2DDD5] pt-8 mb-3">
          <div className="text-section-label mb-2">Data & Licenses</div>
          <h3 className="font-serif text-xl sm:text-2xl text-[#0D1117] mb-5">Primary Data Provenance</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border border-[#E2DDD5] rounded overflow-hidden mb-6">
          {DATA_SOURCES.map((ds, i) => (
            <div
              key={ds.title}
              className={`p-5 ${i > 0 ? 'md:border-l border-t md:border-t-0 border-[#E2DDD5]' : ''}`}
            >
              <div className="font-serif font-medium text-base text-[#0D1117] mb-0.5">{ds.title}</div>
              <div className="text-[10px] font-mono text-[#C25E2E] mb-2 uppercase tracking-wider">{ds.license}</div>
              <p className="text-xs text-[#4A5568] leading-relaxed mb-3">{ds.desc}</p>
              <a
                href={ds.link}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-[11px] font-mono text-[#0D1117] hover:text-[#C25E2E] transition-colors"
                onClick={e => e.stopPropagation()}
              >
                <span>{ds.linkLabel}</span>
                <ExternalLink size={10} />
              </a>
            </div>
          ))}
        </div>

      </div>

      {/* ── Figure modal ── */}
      {modal && (
        <div
          className="fixed inset-0 z-50 bg-[#0D1117]/85 backdrop-blur-sm flex items-center justify-center p-4 sm:p-8"
          onClick={() => setModal(null)}
        >
          <div
            className="relative max-w-5xl w-full bg-white rounded border border-[#CEC8BD] shadow-2xl overflow-hidden flex flex-col"
            style={{ maxHeight: '90vh' }}
            onClick={e => e.stopPropagation()}
          >
            {/* Modal header */}
            <div className="px-5 py-4 border-b border-[#E2DDD5] flex items-center justify-between bg-[#FAF8F4]">
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-[10px] font-semibold px-2 py-0.5 rounded bg-[#0D1117] text-white">
                  {modal.figureNumber}
                </span>
                <span className="font-serif text-sm text-[#0D1117]">{modal.title}</span>
              </div>
              <button
                onClick={() => setModal(null)}
                className="p-1.5 rounded text-[#4A5568] hover:text-[#0D1117] hover:bg-[#E2DDD5] transition-colors"
                aria-label="Close"
              >
                <X size={16} />
              </button>
            </div>

            {/* Image */}
            <div className="flex-1 overflow-auto bg-[#F2EEE6] flex items-center justify-center p-4">
              <img
                src={`./figures/${modal.filename}`}
                alt={modal.title}
                className="max-h-[60vh] object-contain rounded"
                onError={e => {
                  (e.target as HTMLImageElement).src = `/figures/${modal.filename}`;
                }}
              />
            </div>

            {/* Caption */}
            <div className="px-5 py-4 border-t border-[#E2DDD5] bg-white">
              <p className="text-xs text-[#374151] leading-relaxed mb-2">{modal.caption}</p>
              <div className="flex items-center justify-between text-[10px] font-mono text-[#718096]">
                <span>Section: {modal.section}</span>
                <span>{modal.filename}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
