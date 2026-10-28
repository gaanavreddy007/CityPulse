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

  useEffect(() => {
    const observers: IntersectionObserver[] = [];
    SECTIONS.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      const obs = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) setActiveSection(id);
        },
        { rootMargin: '-20% 0px -60% 0px', threshold: 0 }
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
    <div className="min-h-screen bg-[#FBF9F5] text-[#1F2937] selection:bg-[#FBE8DE] selection:text-[#C25E2E]">
      <Navbar activeSection={activeSection} onNav={handleNav} />
      <main className="divide-y divide-[#E5E0D8]">
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
