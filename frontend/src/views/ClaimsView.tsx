import React, { useState, useMemo } from 'react';
import claimsAuditRaw from '../data/claims_audit.json';
import { ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle2, Search, ChevronDown, ChevronUp } from 'lucide-react';

interface ClaimRecord {
  claim_id: string;
  proposed_headline_claim: string;
  supporting_evidence_artifact: string;
  verification_status: string;
  potential_overstatement_risk: string;
  scientifically_safe_portfolio_wording: string;
}

const CLAIMS = claimsAuditRaw as ClaimRecord[];

function riskLevel(c: ClaimRecord): 'low' | 'medium' | 'high' {
  const risk = c.potential_overstatement_risk.toLowerCase();
  if (risk.includes('conflat') || risk.includes('overstat') || risk.includes('implies') || risk.length > 250) return 'high';
  if (risk.includes('may') || risk.includes('could') || risk.length > 100) return 'medium';
  return 'low';
}

const RISK_CONFIG = {
  high:   { color: '#C25E2E', bg: '#FDF0EA', border: '#E8B9A2', label: 'HIGH',   Icon: AlertTriangle },
  medium: { color: '#B45309', bg: '#FFFBEB', border: '#FDE68A', label: 'MEDIUM', Icon: ShieldAlert },
  low:    { color: '#065F46', bg: '#ECFDF5', border: '#A7F3D0', label: 'LOW',    Icon: CheckCircle2 },
};

export const ClaimsView: React.FC = () => {
  const [expanded, setExpanded] = useState<string | null>(CLAIMS[0]?.claim_id || null);
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const claimsWithRisk = useMemo(() => CLAIMS.map(c => ({ ...c, risk: riskLevel(c) })), []);

  const filtered = useMemo(() =>
    claimsWithRisk.filter(c => {
      const matchRisk   = riskFilter === 'all' || c.risk === riskFilter;
      const matchSearch = searchQuery === '' ||
        c.proposed_headline_claim.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.scientifically_safe_portfolio_wording.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.claim_id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchRisk && matchSearch;
    }),
    [claimsWithRisk, riskFilter, searchQuery]
  );

  const riskCounts = useMemo(() => ({
    all:    claimsWithRisk.length,
    high:   claimsWithRisk.filter(c => c.risk === 'high').length,
    medium: claimsWithRisk.filter(c => c.risk === 'medium').length,
    low:    claimsWithRisk.filter(c => c.risk === 'low').length,
  }), [claimsWithRisk]);

  return (
    <section id="claims" className="py-24 border-t border-[#E2DDD5]">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">

        {/* ── Section heading ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-14">
          <div className="lg:col-span-4">
            <div className="text-section-label mb-3">05 · Scientific Epistemics</div>
            <h2 className="text-headline">Claims & Evidence Audit</h2>
          </div>
          <div className="lg:col-span-8 flex items-end">
            <p className="text-sm text-[#4A5568] leading-relaxed max-w-2xl">
              A comprehensive line-by-line audit documenting each scientific finding, its overstatement risks, primary evidence artifacts, and the safe phrasing required for peer review and data-science portfolio evaluation.
            </p>
          </div>
        </div>

        {/* ── Filter bar ── */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 border-y border-[#E2DDD5] py-4 mb-8">
          {/* Search */}
          <div className="relative flex-1 max-w-sm">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#718096]" />
            <input
              type="text"
              placeholder="Search claims, artifacts or metrics…"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded border border-[#CEC8BD] bg-white text-[#0D1117] placeholder-[#9CA3AF] focus:outline-none focus:border-[#C25E2E]"
            />
          </div>

          {/* Risk filter tabs */}
          <div className="flex items-center gap-1">
            <span className="font-mono text-[10px] text-[#718096] uppercase tracking-wider mr-1">Risk:</span>
            {(['all', 'high', 'medium', 'low'] as const).map(r => {
              const isActive = riskFilter === r;
              return (
                <button
                  key={r}
                  onClick={() => setRiskFilter(r)}
                  className={`px-3 py-1.5 text-[11px] font-mono capitalize rounded border transition-colors ${
                    isActive
                      ? 'bg-[#0D1117] text-white border-[#0D1117]'
                      : 'border-[#CEC8BD] text-[#4A5568] bg-white hover:border-[#0D1117]'
                  }`}
                >
                  {r}
                  <span className={`ml-1.5 font-normal ${isActive ? 'text-[#9CA3AF]' : 'text-[#9CA3AF]'}`}>
                    {riskCounts[r]}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Claims accordion list ── */}
        <div className="divide-y divide-[#E2DDD5] border-t border-[#E2DDD5] mb-10">
          {filtered.length === 0 ? (
            <div className="py-12 text-center text-xs text-[#718096] font-mono">
              No claims matching the selected filters.
            </div>
          ) : (
            filtered.map(claim => {
              const isExpanded = expanded === claim.claim_id;
              const cfg = RISK_CONFIG[claim.risk];
              const { Icon } = cfg;
              return (
                <div key={claim.claim_id} className="group">
                  <button
                    onClick={() => setExpanded(isExpanded ? null : claim.claim_id)}
                    className="w-full text-left py-6 flex items-start justify-between gap-6 hover:bg-[#FAF8F4] transition-colors -mx-2 px-2 rounded"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <span className="font-mono text-[10px] text-[#718096] font-semibold uppercase tracking-wider">
                          {claim.claim_id}
                        </span>

                        {/* Risk badge */}
                        <span
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-semibold border"
                          style={{ color: cfg.color, backgroundColor: cfg.bg, borderColor: cfg.border }}
                        >
                          <Icon size={10} />
                          {cfg.label} RISK
                        </span>

                        <span className="inline-flex items-center gap-1 font-mono text-[10px] text-[#065F46]">
                          <ShieldCheck size={11} />
                          {claim.verification_status.replace(/_/g, ' ')}
                        </span>
                      </div>

                      <h3 className="font-serif text-lg text-[#0D1117] leading-snug mb-1.5">
                        {claim.proposed_headline_claim}
                      </h3>

                      <p className="font-mono text-[10px] text-[#718096] truncate">
                        Artifact: {claim.supporting_evidence_artifact}
                      </p>
                    </div>

                    <span className="text-[#718096] shrink-0 pt-1">
                      {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </span>
                  </button>

                  {isExpanded && (
                    <div className="pb-6 -mx-2 px-2">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="border border-[#E8B9A2] bg-[#FDF0EA] rounded p-5">
                          <div className="flex items-center gap-1.5 text-[10px] font-mono font-semibold text-[#C25E2E] mb-2 uppercase tracking-wider">
                            <AlertTriangle size={12} />
                            Potential Overstatement Risk
                          </div>
                          <p className="text-xs text-[#4A5568] leading-relaxed">
                            {claim.potential_overstatement_risk}
                          </p>
                        </div>

                        <div className="border border-[#A7F3D0] bg-[#ECFDF5] rounded p-5">
                          <div className="flex items-center gap-1.5 text-[10px] font-mono font-semibold text-[#065F46] mb-2 uppercase tracking-wider">
                            <ShieldCheck size={12} />
                            Scientifically Safe Wording
                          </div>
                          <p className="text-xs text-[#065F46] leading-relaxed font-medium">
                            {claim.scientifically_safe_portfolio_wording}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Verification protocol note */}
        <div className="border-t border-[#E2DDD5] pt-8 grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-2">
            <ShieldCheck size={20} className="text-[#065F46]" />
          </div>
          <div className="lg:col-span-10">
            <div className="font-mono text-xs font-semibold text-[#0D1117] uppercase tracking-wider mb-2">
              Verification Protocol: REPRODUCED_OFFLINE Standard
            </div>
            <p className="text-xs text-[#4A5568] leading-relaxed max-w-3xl">
              All 6 primary research claims have been verified against raw saved artifacts without external network requests. The audit explicitly ensures that traffic volume counts are never conflated with vehicular congestion delays, and that shortest-path graph calculations are strictly reported as free-flow resistance metrics.
            </p>
          </div>
        </div>

      </div>
    </section>
  );
};
