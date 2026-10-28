import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from './views/Navbar';
import { Footer } from './views/Footer';
import { OverviewView } from './views/OverviewView';
import { ExplorerView } from './views/ExplorerView';
import { AnomalyView } from './views/AnomalyView';
import { NetworkView } from './views/NetworkView';
import { ClaimsView } from './views/ClaimsView';
import { FiguresView } from './views/FiguresView';

const SECTIONS = ['overview', 'explorer', 'anomaly', 'network', 'claims', 'figures'];

function App() {
  const [activeSection, setActiveSection] = useState('overview');
  const sectionRefs = useRef<Record<string, HTMLDivElement | null>>({});

  // Intersection observer to sync navbar with scroll position
  useEffect(() => {
    const observers: IntersectionObserver[] = [];
    SECTIONS.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      const obs = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) setActiveSection(id);
        },
        { rootMargin: '-40% 0px -55% 0px', threshold: 0 }
      );
      obs.observe(el);
      observers.push(obs);
    });
    return () => observers.forEach(o => o.disconnect());
  }, []);

  const handleNav = (section: string) => {
    const el = document.getElementById(section);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    setActiveSection(section);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Navbar activeSection={activeSection} onNav={handleNav} />
      <main>
        <OverviewView onNav={handleNav} />
        <ExplorerView />
        <AnomalyView />
        <NetworkView />
        <ClaimsView />
        <FiguresView />
      </main>
      <Footer />
    </div>
  );
}

export default App;
