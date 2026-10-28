import React from 'react';
import { GitFork, Database, ShieldAlert, ArrowUpRight } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-md pt-12 pb-16 text-slate-400 text-sm mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
              <span className="text-lg font-bold text-slate-100 tracking-wider">CITYPULSE</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Retrospective urban mobility resilience research examining sensor missingness,
              spatial cross-consistency, and simulated bridge disruptions across Glasgow's road network.
            </p>
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono bg-cyan-950/60 text-cyan-300 border border-cyan-800/50">
              MIT License (Code) · OGL v3.0 / ODbL 1.0 (Data)
            </span>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4">Core Modules</h4>
            <ul className="space-y-2 text-xs">
              {['SCOOT Traffic Flow Extraction','Missingness & Anomaly Lab','OSM Network Graph (1,327 nodes)','River Clyde Bridge Scenarios','Empirical Claims Integrity Audit'].map(m => (
                <li key={m} className="text-slate-400">{m}</li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4">Primary Sources</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="https://doi.org/10.5281/zenodo.12100278" target="_blank" rel="noreferrer"
                   className="flex items-center gap-1 hover:text-cyan-400 transition-colors">
                  <Database size={13} /><span>Glasgow SCOOT (Zenodo)</span><ArrowUpRight size={11} className="opacity-70" />
                </a>
              </li>
              <li>
                <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer"
                   className="flex items-center gap-1 hover:text-cyan-400 transition-colors">
                  <Database size={13} /><span>OpenStreetMap (ODbL 1.0)</span><ArrowUpRight size={11} className="opacity-70" />
                </a>
              </li>
              <li>
                <a href="https://github.com/gaanavreddy007/CityPulse" target="_blank" rel="noreferrer"
                   className="flex items-center gap-1 hover:text-cyan-400 transition-colors">
                  <GitFork size={13} /><span>GitHub Repository</span><ArrowUpRight size={11} className="opacity-70" />
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4">Scientific Integrity</h4>
            <p className="text-xs text-slate-400 leading-relaxed mb-3">
              This platform visualises empirical artefacts from published reports. No live traffic telemetry,
              automated routing control, or municipal deployment is implied.
            </p>
            <div className="flex items-center gap-2 text-xs text-amber-400/90 font-mono">
              <ShieldAlert size={14} />
              <span>Non-operational research platform</span>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-900/80 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400">
          <p>© 2026 Gaanavaditya Reddy Morramreddygari. Released under the MIT License.</p>
          <p className="mt-2 sm:mt-0 font-mono">Baseline: commit ef85934 · Python 3.13 Verified · 56/56 tests pass</p>
        </div>
      </div>
    </footer>
  );
};
