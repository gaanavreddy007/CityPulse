import React from 'react';
import { GitFork, ArrowUpRight, ShieldCheck } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-[#E2DDD5] bg-[#0D1117] text-[#9CA3AF]">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 pt-16 pb-10">

        {/* Top grid: identity + links */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 mb-12 pb-10 border-b border-[#1F2937]">

          {/* Identity column */}
          <div className="md:col-span-5 space-y-4">
            <div
              className="text-[#F7F6F3] font-serif font-medium text-xl"
              style={{ letterSpacing: '0.06em', fontVariantCaps: 'all-small-caps' }}
            >
              CITYPULSE
            </div>
            <p className="text-sm text-[#6B7280] leading-relaxed" style={{ maxWidth: '38ch' }}>
              An empirical research investigation into traffic sensor missingness, spatial cross-consistency anomaly detection, and graph-theoretic road network resilience in Glasgow, Scotland.
            </p>
            <div className="font-mono text-[10px] text-[#C25E2E] uppercase tracking-widest">
              MSc Data Science Research Portfolio
            </div>

            {/* GitHub link */}
            <a
              href="https://github.com/gaanavreddy007/CityPulse"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 text-xs font-mono text-[#6B7280] hover:text-[#F7F6F3] transition-colors mt-2"
            >
              <GitFork size={12} className="text-[#C25E2E]" />
              <span>gaanavreddy007/CityPulse</span>
              <ArrowUpRight size={11} className="opacity-60" />
            </a>
          </div>

          {/* Research sections */}
          <div className="md:col-span-3">
            <h4 className="font-mono text-[10px] uppercase tracking-widest text-[#4A5568] font-semibold mb-4">
              Research Sections
            </h4>
            <ul className="space-y-2.5">
              {[
                '01. Overview & Research Inquiry',
                '02. SCOOT Flow Analysis',
                '03. Anomaly Detection Lab',
                '04. Network Resilience Simulator',
                '05. Epistemic Claims Audit',
                '06. Figures & Data Provenance',
              ].map(s => (
                <li key={s}>
                  <span className="text-xs text-[#6B7280] hover:text-[#9CA3AF] transition-colors cursor-default">{s}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Data & scientific boundaries */}
          <div className="md:col-span-4 space-y-6">
            <div>
              <h4 className="font-mono text-[10px] uppercase tracking-widest text-[#4A5568] font-semibold mb-4">
                Data & Licences
              </h4>
              <ul className="space-y-2.5">
                <li>
                  <a href="https://doi.org/10.5281/zenodo.12100278" target="_blank" rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-[#6B7280] hover:text-[#9CA3AF] transition-colors">
                    <span>Glasgow SCOOT (OGL v3.0)</span>
                    <ArrowUpRight size={10} className="opacity-60" />
                  </a>
                </li>
                <li>
                  <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-[#6B7280] hover:text-[#9CA3AF] transition-colors">
                    <span>OpenStreetMap (ODbL 1.0)</span>
                    <ArrowUpRight size={10} className="opacity-60" />
                  </a>
                </li>
                <li>
                  <a href="https://github.com/gaanavreddy007/CityPulse" target="_blank" rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-[#6B7280] hover:text-[#9CA3AF] transition-colors">
                    <span>Software — MIT License</span>
                    <ArrowUpRight size={10} className="opacity-60" />
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-mono text-[10px] uppercase tracking-widest text-[#4A5568] font-semibold mb-4">
                Scientific Boundaries
              </h4>
              <p className="text-xs text-[#6B7280] leading-relaxed" style={{ maxWidth: '36ch' }}>
                Shortest-path calculations represent free-flow legal traversal resistance on static cartographic graphs — not dynamic congestion delays or real-time commuter telemetry.
              </p>
              <div className="flex items-center gap-1.5 font-mono text-[10px] text-[#065F46] mt-3">
                <ShieldCheck size={12} />
                <span>100% Offline Reproducible</span>
              </div>
            </div>
          </div>
        </div>

        {/* Retrospective disclaimer */}
        <div className="mb-8 text-[11px] text-[#4A5568] leading-relaxed font-mono border-l border-[#1F2937] pl-4" style={{ maxWidth: '72ch' }}>
          Retrospective academic research on historical 2019–2023 SCOOT observations and open cartographic data. Anomaly detections reflect statistical volume deviations on synthetic benchmark corruptions, not verified live municipal hardware incidents. This is not a live operations system.
        </div>

        {/* Colophon */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-[10px] font-mono text-[#4A5568]">
          <div>© 2026 Gaanavaditya Reddy Morramreddygari · CityPulse Research Portfolio</div>
          <div className="flex items-center gap-4">
            <span>Python 3.13 Verified</span>
            <span className="text-[#065F46]">56 / 56 Unit Tests Passing</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
