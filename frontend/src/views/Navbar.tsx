import React, { useState, useEffect } from 'react';
import { GitFork, Menu, X } from 'lucide-react';

interface NavbarProps {
  activeSection: string;
  onNav: (section: string) => void;
}

const SECTIONS = [
  { id: 'overview',  label: 'Overview' },
  { id: 'explorer',  label: 'Sensor Flow' },
  { id: 'anomaly',   label: 'Anomaly Lab' },
  { id: 'network',   label: 'Network' },
  { id: 'claims',    label: 'Evidence Audit' },
  { id: 'figures',   label: 'Figures' },
];

export const Navbar: React.FC<NavbarProps> = ({ activeSection, onNav }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
        scrolled
          ? 'bg-[#FAF8F4]/97 backdrop-blur-sm border-b border-[#E2DDD5] shadow-[0_1px_0_#E2DDD5]'
          : 'bg-transparent border-b border-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 h-13 flex items-center justify-between" style={{ height: '3.25rem' }}>

        {/* Wordmark */}
        <button
          onClick={() => onNav('overview')}
          className="flex items-baseline gap-2.5 group"
          aria-label="Return to top"
        >
          <span
            className="font-serif font-medium text-base tracking-tight text-[#0D1117] group-hover:text-[#C25E2E] transition-colors"
            style={{ letterSpacing: '0.06em', fontVariantCaps: 'all-small-caps', fontSize: '1.05rem' }}
          >
            CITYPULSE
          </span>
          <span className="hidden sm:block font-mono text-[10px] text-[#718096] uppercase tracking-[0.12em] leading-none">
            Urban Systems
          </span>
        </button>

        {/* Desktop Nav */}
        <div className="hidden lg:flex items-center">
          {SECTIONS.map(({ id, label }, i) => {
            const isActive = activeSection === id;
            return (
              <button
                key={id}
                onClick={() => onNav(id)}
                className={`relative px-3.5 py-2 text-[11px] font-medium tracking-wide transition-colors ${
                  isActive
                    ? 'text-[#C25E2E]'
                    : 'text-[#4A5568] hover:text-[#0D1117]'
                }`}
              >
                {label}
                {isActive && (
                  <span className="absolute bottom-0 left-3.5 right-3.5 h-px bg-[#C25E2E]" />
                )}
              </button>
            );
          })}
        </div>

        {/* Right: GitHub + hamburger */}
        <div className="flex items-center gap-2">
          <a
            href="https://github.com/gaanavreddy007/CityPulse"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 text-[11px] font-mono px-2.5 py-1.5 rounded border border-[#CEC8BD] bg-white/80 text-[#1A202C] hover:border-[#0D1117] hover:bg-white transition-all"
            title="View source on GitHub"
          >
            <GitFork size={11} className="text-[#C25E2E]" />
            <span>GitHub</span>
          </a>

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="lg:hidden p-1.5 text-[#4A5568] hover:text-[#0D1117] rounded"
            aria-label="Toggle navigation"
          >
            {mobileOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="lg:hidden border-t border-[#E2DDD5] bg-[#FAF8F4] px-5 py-3 space-y-px">
          {SECTIONS.map(({ id, label }) => {
            const isActive = activeSection === id;
            return (
              <button
                key={id}
                onClick={() => { onNav(id); setMobileOpen(false); }}
                className={`w-full text-left px-3 py-2.5 text-xs font-medium rounded transition-colors ${
                  isActive
                    ? 'text-[#C25E2E] bg-[#FDF0EA]'
                    : 'text-[#4A5568] hover:text-[#0D1117] hover:bg-[#F2EEE6]'
                }`}
              >
                {label}
              </button>
            );
          })}
          <div className="pt-2 border-t border-[#E2DDD5]">
            <a
              href="https://github.com/gaanavreddy007/CityPulse"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-2 text-xs font-mono text-[#4A5568] hover:text-[#0D1117]"
            >
              <GitFork size={12} className="text-[#C25E2E]" />
              <span>GitHub Repository</span>
            </a>
          </div>
        </div>
      )}
    </nav>
  );
};
