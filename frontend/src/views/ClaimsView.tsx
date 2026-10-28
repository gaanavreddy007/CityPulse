import React, { useState, useMemo } from 'react';
import claimsAuditRaw from '../data/claims_audit.json';
import { ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle2, Search, Filter, ChevronDown, ChevronUp } from 'lucide-react';

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

export const ClaimsView: React.FC = () => {
  const [expanded, setExpanded] = useState<string | null>(CLAIMS[0]?.claim_id || null);
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const claimsWithRisk = useMemo(() => {
    return CLAIMS.map(c => ({ ...c, risk: riskLevel(c) }));
  }, []);

  const filtered = useMemo(() => {
    return claimsWithRisk.filter(c => {
      const matchRisk = riskFilter === 'all' || c.risk === riskFilter;
      const matchSearch = searchQuery === '' ||
        c.proposed_headline_claim.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.scientifically_safe_portfolio_wording.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.claim_id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchRisk && matchSearch;
    });
  }, [claimsWithRisk, riskFilter, searchQuery]);

  return (
    <section id="claims" className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Heading */}
        <div className="max-w-3xl mb-8">
          <span className="text-xs font-mono uppercase tracking-wider text-[#C25E2E] font-semibold">
            Section 05 · Scientific Epistemics
          </span>
          <h2 className="font-serif text-2xl sm:text-3xl text-[#111827] mt-1 mb-2">
            Claims Integrity & Epistemic Audit Register
          </h2>
          <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed">
            A comprehensive line-by-line audit documenting each scientific finding, its overstatement risks, primary evidence artifacts, and the safe phrasing required for peer review and data-science portfolio evaluation.
          </p>
        </div>

        {/* Filter and Search Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 p-4 rounded border border-[#E5E0D8] bg-white mb-6 shadow-xs">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6B7280]" />
            <input
              type="text"
              placeholder="Filter claims by keyword, metric, or artifact..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded border border-[#D1C9BE] bg-white text-[#111827] placeholder-[#9CA3AF] focus:outline-none focus:border-[#C25E2E]"
            />
          </div>

          {/* Risk Level Segmented Control */}
          <div className="flex items-center gap-1.5 border border-[#D1C9BE] p-1 rounded bg-[#F4F1EA] text-xs">
            <span className="text-[11px] font-mono text-[#6B7280] px-1.5 flex items-center gap-1">
              <Filter size={11} /> Overstatement Risk:
            </span>
            {['all', 'low', 'medium', 'high'].map(r => (
              <button
                key={r}
                onClick={() => setRiskFilter(r)}
                className={`px-2.5 py-1 text-xs capitalize rounded transition-colors ${
                  riskFilter === r
                    ? 'bg-white text-[#111827] font-semibold shadow-xs'
                    : 'text-[#4B5563] hover:text-[#111827]'
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        {/* Claims Register List */}
        <div className="space-y-4 mb-8">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-xs text-[#6B7280] border border-[#E5E0D8] bg-white rounded">
              No claims matching the selected filters.
            </div>
          ) : (
            filtered.map(claim => {
              const isExpanded = expanded === claim.claim_id;
              return (
                <div
                  key={claim.claim_id}
                  className="border border-[#E5E0D8] bg-white rounded shadow-xs overflow-hidden transition-colors"
                >
                  {/* Claim Header Accordion Bar */}
                  <button
                    onClick={() => setExpanded(isExpanded ? null : claim.claim_id)}
                    className="w-full text-left p-5 flex items-start justify-between gap-4 hover:bg-[#F4F1EA]/40 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-2 text-xs">
                        <span className="font-mono text-[#6B7280] font-semibold">
                          {claim.claim_id}
                        </span>
                        
                        {/* Risk Badge */}
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium border ${
                          claim.risk === 'high'
                            ? 'bg-[#FBE8DE] text-[#C25E2E] border-[#E8B9A2]'
                            : claim.risk === 'medium'
                            ? 'bg-[#FEF3C7] text-[#B45309] border-[#FDE68A]'
                            : 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]'
                        }`}>
                          {claim.risk === 'high' && <AlertTriangle size={11} />}
                          {claim.risk === 'medium' && <ShieldAlert size={11} />}
                          {claim.risk === 'low' && <CheckCircle2 size={11} />}
                          <span>{claim.risk.toUpperCase()} OVERSTATEMENT RISK</span>
                        </span>

                        <span className="inline-flex items-center gap-1 font-mono text-[11px] text-[#065F46]">
                          <ShieldCheck size={12} />
                          <span>{claim.verification_status.replace(/_/g, ' ')}</span>
                        </span>
                      </div>

                      <h3 className="font-serif text-base sm:text-lg text-[#111827] leading-snug mb-1">
                        {claim.proposed_headline_claim}
                      </h3>

                      <p className="font-mono text-[11px] text-[#6B7280] truncate">
                        Artifact: {claim.supporting_evidence_artifact}
                      </p>
                    </div>

                    <div className="text-[#6B7280] shrink-0 pt-1">
                      {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </div>
                  </button>

                  {/* Expanded Audit Card Content */}
                  {isExpanded && (
                    <div className="px-5 pb-5 pt-3 border-t border-[#E5E0D8] bg-[#F4F1EA]/30 grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="border border-[#E5E0D8] bg-white p-4 rounded shadow-xs">
                        <div className="flex items-center gap-1.5 text-xs font-mono font-semibold text-[#C25E2E] mb-2 uppercase tracking-wider">
                          <AlertTriangle size={13} />
                          <span>Potential Overstatement Risk</span>
                        </div>
                        <p className="text-xs text-[#4B5563] leading-relaxed">
                          {claim.potential_overstatement_risk}
                        </p>
                      </div>

                      <div className="border border-[#A7F3D0] bg-[#ECFDF5]/50 p-4 rounded shadow-xs">
                        <div className="flex items-center gap-1.5 text-xs font-mono font-semibold text-[#065F46] mb-2 uppercase tracking-wider">
                          <ShieldCheck size={13} />
                          <span>Scientifically Safe Portfolio Wording</span>
                        </div>
                        <p className="text-xs text-[#065F46] leading-relaxed font-medium">
                          {claim.scientifically_safe_portfolio_wording}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Methodology Standards Note */}
        <div className="border border-[#D1C9BE] bg-white p-5 rounded shadow-xs text-xs text-[#4B5563] space-y-2">
          <div className="font-serif font-semibold text-[#111827] text-sm">
            Verification Protocol: REPRODUCED_OFFLINE Standard
          </div>
          <p className="leading-relaxed">
            All 6 primary research claims have been verified against raw saved artifacts without external network requests.
            The audit explicitly ensures that traffic volume counts are never conflated with vehicular congestion delays,
            and that shortest-path graph calculations are strictly reported as free-flow resistance metrics.
          </p>
        </div>

      </div>
    </section>
  );
};
