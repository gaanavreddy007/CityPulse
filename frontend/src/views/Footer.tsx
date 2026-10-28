import React from 'react';
import { GitFork, ExternalLink, ShieldCheck, ArrowUpRight } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-[#D1C9BE] bg-[#F4F1EA] py-16 text-[#4B5563] text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          
          {/* Identity & Scope */}
          <div className="md:col-span-1 space-y-3">
            <div className="font-serif font-semibold text-lg text-[#111827]">
              CITYPULSE
            </div>
            <p className="leading-relaxed">
              An empirical research investigation into traffic sensor missingness, spatial cross-consistency anomaly detection, and graph-theoretic road network resilience in Glasgow, Scotland.
            </p>
            <div className="font-mono text-[11px] text-[#C25E2E]">
              MSc Data Science Research Portfolio
            </div>
          </div>

          {/* Research Sections */}
          <div>
            <h4 className="font-mono text-xs uppercase tracking-wider text-[#111827] font-semibold mb-3">
              Research Sections
            </h4>
            <ul className="space-y-2">
              {['1. Overview & Research Inquiry', '2. SCOOT Flow Analysis', '3. Anomaly Benchmarks', '4. Network Resilience Simulator', '5. Epistemic Claims Audit', '6. Figures & Data Provenance'].map(s => (
                <li key={s} className="hover:text-[#111827] transition-colors">{s}</li>
              ))}
            </ul>
          </div>

          {/* Data Sources & Licenses */}
          <div>
            <h4 className="font-mono text-xs uppercase tracking-wider text-[#111827] font-semibold mb-3">
              Data & Licenses
            </h4>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://doi.org/10.5281/zenodo.12100278"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 hover:text-[#111827] transition-colors"
                >
                  <span>Glasgow SCOOT (OGL v3.0)</span>
                  <ArrowUpRight size={11} className="opacity-60" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.openstreetmap.org/copyright"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 hover:text-[#111827] transition-colors"
                >
                  <span>OpenStreetMap Graph (ODbL 1.0)</span>
                  <ArrowUpRight size={11} className="opacity-60" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/gaanavreddy007/CityPulse"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 hover:text-[#111827] transition-colors"
                >
                  <span>MIT Software License</span>
                  <ArrowUpRight size={11} className="opacity-60" />
                </a>
              </li>
            </ul>
          </div>

          {/* Scientific Epistemic Standard */}
          <div>
            <h4 className="font-mono text-xs uppercase tracking-wider text-[#111827] font-semibold mb-3">
              Scientific Boundaries
            </h4>
            <p className="leading-relaxed mb-3">
              Shortest-path calculations represent free-flow legal traversal resistance on static cartographic graphs, not dynamic congestion delays or real-time commuter telemetry.
            </p>
            <div className="flex items-center gap-1.5 font-mono text-[11px] text-[#065F46]">
              <ShieldCheck size={14} />
              <span>100% Offline Reproducible Standard</span>
            </div>
          </div>

        </div>

        {/* Bottom Colophon */}
        <div className="pt-8 border-t border-[#D1C9BE] flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono text-[#6B7280]">
          <div>
            © 2026 Gaanavaditya Reddy Morramreddygari · CityPulse Research Portfolio
          </div>
          <div className="mt-2 sm:mt-0">
            Python 3.13 Verified · 56/56 Unit Tests Passing
          </div>
        </div>
      </div>
    </footer>
  );
};
