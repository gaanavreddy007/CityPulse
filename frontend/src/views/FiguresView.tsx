import React, { useState } from 'react';
import { ZoomIn, X, ExternalLink, Download, FileText, BookOpen } from 'lucide-react';

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

const SECTIONS = ['all', ...new Set(FIGURES.map(f => f.section))];

export const FiguresView: React.FC = () => {
  const [activeSection, setActiveSection] = useState('all');
  const [modal, setModal] = useState<Figure | null>(null);

  const filtered = activeSection === 'all'
    ? FIGURES
    : FIGURES.filter(f => f.section === activeSection);

  return (
    <section id="figures" className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Heading */}
        <div className="max-w-3xl mb-8">
          <span className="text-xs font-mono uppercase tracking-wider text-[#C25E2E] font-semibold">
            Section 06 · Publication Figures & Provenance
          </span>
          <h2 className="font-serif text-2xl sm:text-3xl text-[#111827] mt-1 mb-2">
            Research Figures & Dataset Provenance
          </h2>
          <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed">
            High-resolution analytical figures generated directly from the underlying Glasgow SCOOT and OpenStreetMap pipelines, alongside primary data licenses and offline reproduction protocols.
          </p>
        </div>

        {/* Section Filter Tags */}
        <div className="flex items-center gap-1.5 flex-wrap border-b border-[#E5E0D8] pb-4 mb-8">
          {SECTIONS.map(s => (
            <button
              key={s}
              onClick={() => setActiveSection(s)}
              className={`px-3 py-1.5 text-xs rounded transition-colors capitalize ${
                activeSection === s
                  ? 'bg-[#111827] text-white font-medium'
                  : 'text-[#4B5563] hover:text-[#111827] hover:bg-[#F4F1EA]'
              }`}
            >
              {s === 'all' ? 'All 6 Publication Figures' : s}
            </button>
          ))}
        </div>

        {/* 2-Column Responsive Figures Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {filtered.map(fig => (
            <div
              key={fig.id}
              className="border border-[#E5E0D8] bg-white rounded shadow-xs overflow-hidden flex flex-col group hover:border-[#111827] transition-all"
            >
              {/* Figure Image Container */}
              <div
                className="aspect-[16/10] bg-[#F4F1EA] relative overflow-hidden flex items-center justify-center cursor-pointer"
                onClick={() => setModal(fig)}
              >
                <img
                  src={`./figures/${fig.filename}`}
                  alt={fig.title}
                  className="w-full h-full object-contain p-2"
                  onError={e => {
                    const img = e.target as HTMLImageElement;
                    img.src = `/figures/${fig.filename}`;
                  }}
                />
                
                {/* Enlarge Overlay Indicator */}
                <div className="absolute inset-0 bg-[#111827]/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-white/95 text-[#111827] text-xs font-medium shadow-sm border border-[#D1C9BE]">
                    <ZoomIn size={14} className="text-[#C25E2E]" />
                    <span>Click to Enlarge</span>
                  </span>
                </div>

                <div className="absolute top-3 left-3">
                  <span className="font-mono text-[11px] font-semibold px-2 py-0.5 rounded bg-white text-[#111827] border border-[#D1C9BE] shadow-xs">
                    {fig.figureNumber}
                  </span>
                </div>
              </div>

              {/* Caption & Title */}
              <div className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="font-serif text-base text-[#111827] mb-2 leading-snug">
                    {fig.title}
                  </h3>
                  <p className="text-xs text-[#4B5563] leading-relaxed line-clamp-3">
                    {fig.caption}
                  </p>
                </div>

                <div className="pt-4 mt-4 border-t border-[#E5E0D8] flex items-center justify-between text-[11px] font-mono text-[#6B7280]">
                  <span>{fig.section}</span>
                  <button
                    onClick={() => setModal(fig)}
                    className="text-[#C25E2E] hover:underline font-medium"
                  >
                    View Details & Caption →
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Primary Data Provenance & Methodology Table */}
        <div className="border border-[#E5E0D8] bg-white rounded shadow-xs p-6 sm:p-8 mb-12">
          <div className="max-w-2xl mb-6">
            <span className="text-xs font-mono uppercase tracking-wider text-[#C25E2E] font-semibold">
              Data & Licenses
            </span>
            <h3 className="font-serif text-xl text-[#111827] mt-1 mb-2">
              Primary Data Provenance & Legal Licensing
            </h3>
            <p className="text-xs text-[#4B5563]">
              All research data sources are archived under permissive open licenses for independent scientific auditing.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-5 rounded border border-[#E5E0D8] bg-[#F4F1EA]">
              <div className="font-serif font-semibold text-base text-[#111827] mb-1">
                SCOOT Traffic Flow
              </div>
              <div className="text-xs font-mono text-[#C25E2E] mb-3">
                Open Government Licence (OGL v3.0)
              </div>
              <p className="text-xs text-[#4B5563] leading-relaxed mb-4">
                Raw Glasgow City Council / Transport Scotland inductive loop sensor observations archived on Zenodo.
              </p>
              <a
                href="https://doi.org/10.5281/zenodo.12100278"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs font-mono text-[#111827] hover:text-[#C25E2E] transition-colors"
              >
                <span>DOI: 10.5281/zenodo.12100278</span>
                <ExternalLink size={11} />
              </a>
            </div>

            <div className="p-5 rounded border border-[#E5E0D8] bg-[#F4F1EA]">
              <div className="font-serif font-semibold text-base text-[#111827] mb-1">
                Road Network Topology
              </div>
              <div className="text-xs font-mono text-[#C25E2E] mb-3">
                Open Database License (ODbL 1.0)
              </div>
              <p className="text-xs text-[#4B5563] leading-relaxed mb-4">
                Cartographic road network graphs extracted via OSMnx. © OpenStreetMap contributors. 1,327 nodes, 3,201 edges.
              </p>
              <a
                href="https://www.openstreetmap.org/copyright"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs font-mono text-[#111827] hover:text-[#C25E2E] transition-colors"
              >
                <span>OSM Attribution Guidelines</span>
                <ExternalLink size={11} />
              </a>
            </div>

            <div className="p-5 rounded border border-[#E5E0D8] bg-[#F4F1EA]">
              <div className="font-serif font-semibold text-base text-[#111827] mb-1">
                Software & Benchmarks
              </div>
              <div className="text-xs font-mono text-[#C25E2E] mb-3">
                MIT License (Code)
              </div>
              <p className="text-xs text-[#4B5563] leading-relaxed mb-4">
                Complete Python 3.13 analysis suite, automated unit tests (56/56 passing), simulation scripts, and React web app.
              </p>
              <a
                href="https://github.com/gaanavreddy007/CityPulse"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs font-mono text-[#111827] hover:text-[#C25E2E] transition-colors"
              >
                <span>GitHub Repository</span>
                <ExternalLink size={11} />
              </a>
            </div>
          </div>
        </div>

      </div>

      {/* Modal Lightbox for High-Res Inspection */}
      {modal && (
        <div
          className="fixed inset-0 z-50 bg-[#111827]/80 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6"
          onClick={() => setModal(null)}
        >
          <div
            className="relative max-w-4xl w-full bg-white rounded border border-[#D1C9BE] shadow-2xl overflow-hidden max-h-[90vh] flex flex-col"
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="p-4 border-b border-[#E5E0D8] flex items-center justify-between bg-[#F4F1EA]">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-white text-[#C25E2E] border border-[#E5E0D8]">
                  {modal.figureNumber}
                </span>
                <span className="font-serif font-medium text-sm text-[#111827]">{modal.title}</span>
              </div>
              <button
                onClick={() => setModal(null)}
                className="p-1 rounded text-[#4B5563] hover:text-[#111827] hover:bg-[#E5E0D8]"
                aria-label="Close image modal"
              >
                <X size={18} />
              </button>
            </div>

            {/* Image Surface */}
            <div className="p-4 bg-[#FBF9F5] overflow-auto flex-1 flex items-center justify-center">
              <img
                src={`./figures/${modal.filename}`}
                alt={modal.title}
                className="max-h-[60vh] object-contain rounded"
                onError={e => {
                  const img = e.target as HTMLImageElement;
                  img.src = `/figures/${modal.filename}`;
                }}
              />
            </div>

            {/* Detailed Caption */}
            <div className="p-5 border-t border-[#E5E0D8] bg-white text-xs text-[#374151] space-y-2">
              <p className="leading-relaxed font-normal">
                {modal.caption}
              </p>
              <div className="flex items-center justify-between text-[11px] font-mono text-[#6B7280] pt-2 border-t border-[#E5E0D8]">
                <span>Section: {modal.section}</span>
                <span>Filename: {modal.filename}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
