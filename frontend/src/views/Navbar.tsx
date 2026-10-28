import React from 'react';
import { Activity, GitBranch, Map, FlaskConical, Shield, BarChart3, BookOpen, GitFork } from 'lucide-react';

interface NavbarProps {
  activeSection: string;
  onNav: (section: string) => void;
}

const LINKS = [
  { id: 'overview',  label: 'Overview',      icon: Activity },
  { id: 'explorer',  label: 'Flow Explorer', icon: BarChart3 },
  { id: 'anomaly',   label: 'Anomaly Lab',   icon: FlaskConical },
  { id: 'network',   label: 'Network',       icon: Map },
  { id: 'claims',    label: 'Claims Audit',  icon: Shield },
  { id: 'figures',   label: 'Figures',       icon: BookOpen },
];

export const Navbar: React.FC<NavbarProps> = ({ activeSection, onNav }) => {
  const [menuOpen, setMenuOpen] = React.useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-14">
        {/* Logo */}
        <button onClick={() => onNav('overview')} className="flex items-center gap-2 group">
          <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
          <span className="text-base font-bold tracking-widest text-slate-100 group-hover:text-cyan-400 transition-colors">
            CITYPULSE
          </span>
          <span className="hidden sm:inline text-xs text-slate-500 font-mono ml-1">Glasgow · 2024</span>
        </button>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-1">
          {LINKS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => onNav(id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                activeSection === id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon size={13} />
              {label}
            </button>
          ))}
          <a
            href="https://github.com/gaanavreddy007/CityPulse"
            target="_blank"
            rel="noreferrer"
            className="ml-2 flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-all"
          >
            <GitFork size={13} />
            GitHub
          </a>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden text-slate-400 hover:text-slate-200"
          onClick={() => setMenuOpen(v => !v)}
          aria-label="Toggle menu"
        >
          <div className="space-y-1">
            <span className={`block w-5 h-0.5 bg-current transition-transform ${menuOpen ? 'rotate-45 translate-y-1.5' : ''}`}></span>
            <span className={`block w-5 h-0.5 bg-current transition-opacity ${menuOpen ? 'opacity-0' : ''}`}></span>
            <span className={`block w-5 h-0.5 bg-current transition-transform ${menuOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
          </div>
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-slate-950/95 border-t border-slate-800/60 px-4 py-3 space-y-1">
          {LINKS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => { onNav(id); setMenuOpen(false); }}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                activeSection === id
                  ? 'bg-cyan-500/20 text-cyan-300'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon size={15} />
              {label}
            </button>
          ))}
        </div>
      )}
    </nav>
  );
};
