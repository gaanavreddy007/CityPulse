import React, { useState } from 'react';
import { GitFork, ExternalLink, Menu, X } from 'lucide-react';

interface NavbarProps {
  activeSection: string;
  onNav: (section: string) => void;
}

const SECTIONS = [
  { id: 'overview', label: '1. Overview' },
  { id: 'explorer', label: '2. Sensor Flow' },
  { id: 'anomaly', label: '3. Anomaly Benchmarks' },
  { id: 'network', label: '4. Network Resilience' },
  { id: 'claims', label: '5. Claims & Evidence' },
  { id: 'figures', label: '6. Figures & Data' },
];

export const Navbar: React.FC<NavbarProps> = ({ activeSection, onNav }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 bg-[#FBF9F5]/95 backdrop-blur-sm border-b border-[#E5E0D8] transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        {/* Brand / Title */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNav('overview')}
            className="text-left group flex items-baseline gap-2"
          >
            <span className="font-serif font-semibold text-lg tracking-tight text-[#111827] group-hover:text-[#C25E2E] transition-colors">
              CITYPULSE
            </span>
            <span className="hidden sm:inline text-xs font-mono text-[#6B7280] uppercase tracking-wider">
              Glasgow Mobility Research
            </span>
          </button>
        </div>

        {/* Desktop Section Links */}
        <div className="hidden lg:flex items-center gap-1">
          {SECTIONS.map(({ id, label }) => {
            const isActive = activeSection === id;
            return (
              <button
                key={id}
                onClick={() => onNav(id)}
                className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                  isActive
                    ? 'text-[#C25E2E] bg-[#F4F1EA] font-semibold'
                    : 'text-[#4B5563] hover:text-[#111827] hover:bg-[#F4F1EA]/60'
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>

        {/* Right CTA / GitHub */}
        <div className="flex items-center gap-2">
          <a
            href="https://github.com/gaanavreddy007/CityPulse"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded border border-[#D1C9BE] bg-white text-[#1F2937] hover:border-[#111827] hover:bg-[#F4F1EA] transition-all"
            title="View Code on GitHub"
          >
            <GitFork size={12} className="text-[#C25E2E]" />
            <span className="hidden sm:inline">GitHub</span>
          </a>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="lg:hidden p-1.5 text-[#4B5563] hover:text-[#111827] rounded hover:bg-[#F4F1EA]"
            aria-label="Toggle navigation"
          >
            {mobileOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="lg:hidden border-b border-[#E5E0D8] bg-[#FBF9F5] px-4 py-3 space-y-1">
          {SECTIONS.map(({ id, label }) => {
            const isActive = activeSection === id;
            return (
              <button
                key={id}
                onClick={() => {
                  onNav(id);
                  setMobileOpen(false);
                }}
                className={`w-full text-left px-3 py-2 text-xs font-medium rounded ${
                  isActive
                    ? 'text-[#C25E2E] bg-[#F4F1EA] font-semibold'
                    : 'text-[#4B5563] hover:bg-[#F4F1EA]'
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>
      )}
    </nav>
  );
};
