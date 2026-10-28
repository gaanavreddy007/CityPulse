import React, { useState } from 'react';
import claimsAuditRaw from '../data/claims_audit.json';
import { ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle2, XCircle, Info } from 'lucide-react';

// Real schema from claims_audit.json
interface ClaimRecord {
  claim_id: string;
  proposed_headline_claim: string;
  supporting_evidence_artifact: string;
  verification_status: string;
  potential_overstatement_risk: string;
  scientifically_safe_portfolio_wording: string;
}

const CLAIMS = claimsAuditRaw as ClaimRecord[];

// Derive risk level from overstatement_risk text length/keywords
function riskLevel(c: ClaimRecord): 'low' | 'medium' | 'high' {
  const risk = c.potential_overstatement_risk.toLowerCase();
  if (risk.includes('conflat') || risk.includes('overstat') || risk.includes('implies') || risk.length > 250) return 'high';
  if (risk.includes('may') || risk.includes('could') || risk.length > 100) return 'medium';
  return 'low';
}

const RiskBadge: React.FC<{ level: string }> = ({ level }) => {
  const styles: Record<string, string> = {
    low: 'bg-emerald-950/60 text-emerald-300 border-emerald-800/40',
    medium: 'bg-amber-950/60 text-amber-300 border-amber-800/40',
    high: 'bg-rose-950/60 text-rose-300 border-rose-800/40',
  };
  const icons: Record<string, React.ReactNode> = {
    low: <CheckCircle2 size={11} />,
    medium: <AlertTriangle size={11} />,
    high: <XCircle size={11} />,
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border font-mono ${styles[level] ?? ''}`}>
      {icons[level]}
      {level}
    </span>
  );
};

const VerifiedBadge: React.FC<{ status: string }> = ({ status }) => {
  const ok = status === 'REPRODUCED_OFFLINE' || status === 'VERIFIED';
  return (
    <span className={`inline-flex items-center gap-1 text-xs ${ok ? 'text-emerald-400' : 'text-amber-400'}`}>
      {ok ? <ShieldCheck size={12}/> : <ShieldAlert size={12}/>}
      {status.replace(/_/g, ' ')}
    </span>
  );
};

export const ClaimsView: React.FC = () => {
  const [expanded, setExpanded] = useState<string | null>(null);
  const [riskFilter, setRiskFilter] = useState<string>('all');

  const claimsWithRisk = CLAIMS.map(c => ({ ...c, risk: riskLevel(c) }));
  const filtered = claimsWithRisk.filter(c => riskFilter === 'all' || c.risk === riskFilter);

  const counts = {
    low: claimsWithRisk.filter(c => c.risk === 'low').length,
    medium: claimsWithRisk.filter(c => c.risk === 'medium').length,
    high: claimsWithRisk.filter(c => c.risk === 'high').length,
  };

  return (
    <section id="claims" className="min-h-screen pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-2">Empirical Claims Integrity Audit</h2>
          <p className="text-slate-400 text-sm max-w-2xl">
            Every headline claim from the CITYPULSE research pipeline has been audited for potential over-statement.
            Each entry shows the original claim, risk assessment, and recommended scientifically precise wording.
          </p>
        </div>

        {/* Summary strip */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <button onClick={() => setRiskFilter(riskFilter === 'low' ? 'all' : 'low')}
            className="rounded-xl bg-emerald-950/30 border border-emerald-800/40 p-4 text-center hover:border-emerald-700/60 transition-all">
            <div className="text-2xl font-bold text-emerald-400 mb-1">{counts.low}</div>
            <div className="text-xs text-emerald-300 flex items-center justify-center gap-1"><CheckCircle2 size={12}/> Low Risk</div>
          </button>
          <button onClick={() => setRiskFilter(riskFilter === 'medium' ? 'all' : 'medium')}
            className="rounded-xl bg-amber-950/30 border border-amber-800/40 p-4 text-center hover:border-amber-700/60 transition-all">
            <div className="text-2xl font-bold text-amber-400 mb-1">{counts.medium}</div>
            <div className="text-xs text-amber-300 flex items-center justify-center gap-1"><AlertTriangle size={12}/> Medium Risk</div>
          </button>
          <button onClick={() => setRiskFilter(riskFilter === 'high' ? 'all' : 'high')}
            className="rounded-xl bg-rose-950/30 border border-rose-800/40 p-4 text-center hover:border-rose-700/60 transition-all">
            <div className="text-2xl font-bold text-rose-400 mb-1">{counts.high}</div>
            <div className="text-xs text-rose-300 flex items-center justify-center gap-1"><XCircle size={12}/> High Risk</div>
          </button>
        </div>

        {/* Active filter indicator */}
        {riskFilter !== 'all' && (
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xs text-slate-400">Filtering by:</span>
            <RiskBadge level={riskFilter} />
            <button onClick={() => setRiskFilter('all')} className="text-xs text-slate-500 hover:text-slate-300 underline">clear filter</button>
          </div>
        )}

        {/* Claims cards */}
        <div className="space-y-3 mb-8">
          {filtered.length === 0 && (
            <div className="rounded-xl bg-slate-900/40 border border-slate-800/40 p-8 text-center text-slate-500 text-sm">
              No claims match the selected filter.
            </div>
          )}
          {filtered.map(claim => (
            <div key={claim.claim_id}
              className={`rounded-xl border transition-all ${
                claim.risk === 'high' ? 'bg-rose-950/10 border-rose-800/30 hover:border-rose-700/50' :
                claim.risk === 'medium' ? 'bg-amber-950/10 border-amber-800/30 hover:border-amber-700/50' :
                'bg-slate-900/60 border-slate-800/60 hover:border-slate-700/60'
              }`}
            >
              <button
                className="w-full text-left p-5"
                onClick={() => setExpanded(expanded === claim.claim_id ? null : claim.claim_id)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <span className="text-xs font-mono text-slate-500">{claim.claim_id}</span>
                      <RiskBadge level={claim.risk} />
                      <VerifiedBadge status={claim.verification_status} />
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed line-clamp-2">{claim.proposed_headline_claim}</p>
                    <p className="text-xs text-slate-600 mt-1 font-mono">Source: {claim.supporting_evidence_artifact}</p>
                  </div>
                  <span className="text-slate-500 shrink-0 mt-1 text-xs">{expanded === claim.claim_id ? '▲' : '▼'}</span>
                </div>
              </button>

              {expanded === claim.claim_id && (
                <div className="px-5 pb-5 space-y-4 border-t border-slate-800/40 pt-4">
                  <div>
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 mb-2">
                      <ShieldAlert size={13} /> Over-statement Risk
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed bg-slate-800/30 rounded-lg p-3">
                      {claim.potential_overstatement_risk}
                    </p>
                  </div>
                  <div>
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 mb-2">
                      <CheckCircle2 size={13} /> Scientifically Safe Portfolio Wording
                    </div>
                    <p className="text-xs text-emerald-300/90 leading-relaxed bg-emerald-950/20 border border-emerald-900/40 rounded-lg p-3">
                      {claim.scientifically_safe_portfolio_wording}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="rounded-xl bg-slate-900/40 border border-slate-800/40 p-5 text-xs text-slate-400">
          <div className="flex items-center gap-2 mb-2">
            <Info size={14} className="text-cyan-400" />
            <p className="font-semibold text-slate-300">About This Audit</p>
          </div>
          <p className="leading-relaxed">
            This audit ensures all CITYPULSE findings are presented with appropriate epistemic precision.
            Risk levels reflect the potential for a reader to draw over-confident conclusions.
            Verification status "REPRODUCED_OFFLINE" means the claim was cross-checked against primary artefacts
            (saved results, report tables, or reproducible code outputs).
            No claims about live operations, real-time routing, or city-wide coverage are made.
          </p>
        </div>
      </div>
    </section>
  );
};
