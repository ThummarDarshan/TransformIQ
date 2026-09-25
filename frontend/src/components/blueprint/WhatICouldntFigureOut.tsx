import React, { useState } from 'react';
import {
  AlertTriangle,
  HelpCircle,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronUp,
  FileText,
  ShieldAlert,
  Send,
  Sparkles,
  RefreshCw,
  ExternalLink,
  Info,
  Check,
  Edit3
} from 'lucide-react';
import { UncertaintyItem, UncertaintyStats } from '../../types';
import api from '../../services/api';

interface WhatICouldntFigureOutProps {
  projectId: string;
  projectName?: string;
  uncertainties: UncertaintyItem[];
  onClarificationConfirmed?: () => void;
  onOpenEvidenceModal?: (evidence: any) => void;
  onRegenerateBlueprint?: () => void;
}

export const WhatICouldntFigureOut: React.FC<WhatICouldntFigureOutProps> = ({
  projectId,
  projectName = 'Initiative',
  uncertainties = [],
  onClarificationConfirmed,
  onOpenEvidenceModal,
  onRegenerateBlueprint
}) => {
  const [items, setItems] = useState<UncertaintyItem[]>(uncertainties);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [expandedIds, setExpandedIds] = useState<Record<string, boolean>>({});
  
  // Modal state for user confirmation
  const [activeModalItem, setActiveModalItem] = useState<UncertaintyItem | null>(null);
  const [clarificationInput, setClarificationInput] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [actionType, setActionType] = useState<'CONFIRM' | 'EDIT_ASSUMPTION'>('CONFIRM');

  // Sync with prop updates
  React.useEffect(() => {
    setItems(uncertainties);
    // Auto-expand the first unconfirmed critical/high item
    const firstCritical = uncertainties.find(
      (u) => (u.status === 'UNCONFIRMED' || !u.status) && (u.severity === 'CRITICAL' || u.severity === 'HIGH')
    );
    if (firstCritical) {
      setExpandedIds((prev) => ({ ...prev, [firstCritical.id]: true }));
    }
  }, [uncertainties]);

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleOpenConfirmModal = (item: UncertaintyItem, type: 'CONFIRM' | 'EDIT_ASSUMPTION' = 'CONFIRM') => {
    setActiveModalItem(item);
    setActionType(type);
    if (type === 'EDIT_ASSUMPTION') {
      setClarificationInput(item.assumption || '');
    } else {
      setClarificationInput(item.user_clarification || '');
    }
  };

  const handleCloseModal = () => {
    setActiveModalItem(null);
    setClarificationInput('');
    setIsSubmitting(false);
  };

  const handleSubmitClarification = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeModalItem || !clarificationInput.trim()) return;

    setIsSubmitting(true);
    try {
      if (actionType === 'CONFIRM') {
        const res: any = await api.post(`/uncertainties/${activeModalItem.id}/confirm`, {
          user_clarification: clarificationInput.trim()
        });
        if (res.success) {
          setItems((prev) =>
            prev.map((it) =>
              it.id === activeModalItem.id
                ? {
                    ...it,
                    status: 'CONFIRMED',
                    user_clarification: clarificationInput.trim(),
                    confirmed_at: new Date().toISOString()
                  }
                : it
            )
          );
          if (onClarificationConfirmed) onClarificationConfirmed();
          handleCloseModal();
        }
      } else {
        const res: any = await api.post(`/uncertainties/${activeModalItem.id}/edit-assumption`, {
          assumption: clarificationInput.trim(),
          user_clarification: `Accepted custom assumption: ${clarificationInput.trim()}`
        });
        if (res.success) {
          setItems((prev) =>
            prev.map((it) =>
              it.id === activeModalItem.id
                ? {
                    ...it,
                    status: 'RESOLVED',
                    assumption: clarificationInput.trim(),
                    user_clarification: `Accepted custom assumption: ${clarificationInput.trim()}`,
                    confirmed_at: new Date().toISOString()
                  }
                : it
            )
          );
          if (onClarificationConfirmed) onClarificationConfirmed();
          handleCloseModal();
        }
      }
    } catch (err: any) {
      console.error('Failed to submit clarification:', err);
      alert(err?.detail || err?.message || 'Failed to submit clarification.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickAcceptAssumption = async (item: UncertaintyItem) => {
    try {
      const res: any = await api.post(`/uncertainties/${item.id}/edit-assumption`, {
        assumption: item.assumption,
        user_clarification: `Approved stated AI assumption: "${item.assumption}"`
      });
      if (res.success) {
        setItems((prev) =>
          prev.map((it) =>
            it.id === item.id
              ? {
                  ...it,
                  status: 'RESOLVED',
                  user_clarification: `Approved stated AI assumption: "${item.assumption}"`,
                  confirmed_at: new Date().toISOString()
                }
              : it
          )
        );
        if (onClarificationConfirmed) onClarificationConfirmed();
      }
    } catch (err) {
      console.error('Quick accept failed:', err);
    }
  };

  const handleReject = async (item: UncertaintyItem) => {
    if (!window.confirm(`Dismiss uncertainty "${item.title}"?`)) return;
    try {
      const res: any = await api.post(`/uncertainties/${item.id}/reject`, {
        reason: 'Marked as not applicable by operator'
      });
      if (res.success) {
        setItems((prev) =>
          prev.map((it) =>
            it.id === item.id ? { ...it, status: 'REJECTED' } : it
          )
        );
        if (onClarificationConfirmed) onClarificationConfirmed();
      }
    } catch (err) {
      console.error('Reject failed:', err);
    }
  };

  // Stats calculation
  const totalCount = items.length;
  const unconfirmedCount = items.filter((u) => u.status === 'UNCONFIRMED' || !u.status).length;
  const confirmedCount = items.filter((u) => u.status === 'CONFIRMED' || u.status === 'RESOLVED').length;
  const criticalHighCount = items.filter(
    (u) => (u.status === 'UNCONFIRMED' || !u.status) && (u.severity === 'CRITICAL' || u.severity === 'HIGH')
  ).length;

  const filteredItems = items.filter((item) => {
    if (filterStatus === 'UNCONFIRMED' && item.status !== 'UNCONFIRMED') return false;
    if (filterStatus === 'CONFIRMED' && (item.status !== 'CONFIRMED' && item.status !== 'RESOLVED')) return false;
    if (filterStatus === 'REJECTED' && item.status !== 'REJECTED') return false;

    if (filterSeverity !== 'ALL' && item.severity !== filterSeverity) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      {/* 1. HERO GOVERNANCE BANNER */}
      <div className="p-6 rounded-3xl bg-gradient-to-br from-amber-950/40 via-slate-900/90 to-rose-950/30 border border-amber-500/30 shadow-2xl backdrop-blur-xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center space-x-2">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
              </span>
              <span className="text-[11px] font-mono font-bold uppercase tracking-widest text-amber-400 bg-amber-950/60 px-2.5 py-0.5 rounded-full border border-amber-500/30 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                Core Requirement Quality & Trust Guard
              </span>
            </div>
            <h3 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
              <span>WHAT I COULDN'T FIGURE OUT</span>
              <span className="text-sm font-semibold text-slate-400 bg-slate-800/80 px-2.5 py-0.5 rounded-lg border border-slate-700">
                {unconfirmedCount} Uncertaint{unconfirmedCount === 1 ? 'y' : 'ies'} Found
              </span>
            </h3>
            <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
              TransformIQ strictly refuses to silently invent assumptions for missing, ambiguous, or contradictory requirements. Below are the key unknowns requiring human operator confirmation before production commitment.
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center space-x-3 bg-slate-950/80 p-3.5 rounded-2xl border border-slate-800 shrink-0">
            <div className="text-center px-2">
              <span className="text-[10px] uppercase font-bold text-rose-400 block">High Risk</span>
              <span className="text-lg font-black text-rose-300">{criticalHighCount}</span>
            </div>
            <div className="h-8 w-[1px] bg-slate-800" />
            <div className="text-center px-2">
              <span className="text-[10px] uppercase font-bold text-amber-400 block">Unconfirmed</span>
              <span className="text-lg font-black text-amber-300">{unconfirmedCount}</span>
            </div>
            <div className="h-8 w-[1px] bg-slate-800" />
            <div className="text-center px-2">
              <span className="text-[10px] uppercase font-bold text-emerald-400 block">Confirmed</span>
              <span className="text-lg font-black text-emerald-300">{confirmedCount}</span>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            {[
              { id: 'ALL', label: `All (${totalCount})` },
              { id: 'UNCONFIRMED', label: `Needs Confirmation (${unconfirmedCount})` },
              { id: 'CONFIRMED', label: `Confirmed Truths (${confirmedCount})` },
              { id: 'REJECTED', label: 'Dismissed' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setFilterStatus(tab.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  filterStatus === tab.id
                    ? 'bg-amber-600 text-white shadow-lg shadow-amber-600/20'
                    : 'bg-slate-800/60 hover:bg-slate-800 text-slate-400 border border-slate-700/60'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-[11px] text-slate-500 font-medium">Severity:</span>
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
              <button
                key={sev}
                onClick={() => setFilterSeverity(sev)}
                className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase transition ${
                  filterSeverity === sev
                    ? 'bg-slate-200 text-slate-900'
                    : 'bg-slate-800/40 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 2. UNCERTAINTY ITEMS LIST */}
      <div className="space-y-3">
        {filteredItems.length === 0 ? (
          <div className="p-8 rounded-2xl bg-slate-900/50 border border-slate-800 text-center space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto opacity-80" />
            <h4 className="text-sm font-bold text-white">No Uncertainties Match Filter</h4>
            <p className="text-xs text-slate-400">All filtered items have been addressed or none exist in this view.</p>
          </div>
        ) : (
          filteredItems.map((item) => {
            const isExpanded = !!expandedIds[item.id];
            const isConfirmed = item.status === 'CONFIRMED' || item.status === 'RESOLVED';
            const isRejected = item.status === 'REJECTED';
            const isCritical = item.severity === 'CRITICAL';
            const isHigh = item.severity === 'HIGH';

            return (
              <div
                key={item.id}
                className={`rounded-2xl border transition-all duration-200 ${
                  isConfirmed
                    ? 'bg-slate-900/60 border-emerald-500/30'
                    : isRejected
                    ? 'bg-slate-950/40 border-slate-800/50 opacity-60'
                    : isCritical
                    ? 'bg-slate-900/90 border-rose-500/40 shadow-lg shadow-rose-950/20'
                    : isHigh
                    ? 'bg-slate-900/90 border-amber-500/40 shadow-lg shadow-amber-950/20'
                    : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                }`}
              >
                {/* Header Bar */}
                <div
                  onClick={() => toggleExpand(item.id)}
                  className="p-4 cursor-pointer flex items-center justify-between gap-3 select-none"
                >
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <span
                      className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full border shrink-0 ${
                        isCritical
                          ? 'bg-rose-950/80 text-rose-300 border-rose-500/50'
                          : isHigh
                          ? 'bg-amber-950/80 text-amber-300 border-amber-500/50'
                          : item.severity === 'MEDIUM'
                          ? 'bg-blue-950/80 text-blue-300 border-blue-500/50'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      {item.severity}
                    </span>

                    <span className="text-[10px] font-mono font-bold text-slate-400 uppercase bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60 shrink-0">
                      {item.category.replace(/_/g, ' ')}
                    </span>

                    <h4 className="text-sm font-bold text-white truncate">{item.title}</h4>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                        isConfirmed
                          ? 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 flex items-center gap-1'
                          : isRejected
                          ? 'bg-slate-800 text-slate-400 border-slate-700'
                          : 'bg-amber-950/90 text-amber-300 border-amber-500/50 animate-pulse'
                      }`}
                    >
                      {isConfirmed ? <Check className="w-3 h-3 text-emerald-400" /> : null}
                      {item.status}
                    </span>

                    <div className="p-1 rounded-lg bg-slate-800/80 text-slate-400 hover:text-white">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-5 pb-5 pt-1 space-y-4 border-t border-slate-800/80 text-xs">
                    {/* 1. What is Unclear & Why */}
                    <div className="space-y-1">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                        1. What is Unclear & Why?
                      </span>
                      <p className="text-slate-200 leading-relaxed bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                        {item.what_is_unclear}
                        {item.why_unclear && (
                          <span className="block mt-1 text-slate-400 italic">Why: {item.why_unclear}</span>
                        )}
                      </p>
                    </div>

                    {/* 2. Source Evidence Citation */}
                    <div className="space-y-1">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                        2. Available Source Evidence
                      </span>
                      <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                        {item.source_code || item.document_name ? (
                          <div className="flex items-center justify-between text-[11px]">
                            <div className="flex items-center space-x-2 font-mono text-slate-300">
                              <FileText className="w-3.5 h-3.5 text-blue-400" />
                              <span className="font-bold text-blue-400">{item.source_code || 'SRC-DOC'}</span>
                              <span>•</span>
                              <span className="text-slate-200">{item.document_name}</span>
                              {item.page_number && <span className="text-emerald-400 font-semibold">(Page {item.page_number})</span>}
                            </div>
                            {item.section_heading && (
                              <span className="text-slate-400 text-[10px] bg-slate-800 px-2 py-0.5 rounded">
                                {item.section_heading}
                              </span>
                            )}
                          </div>
                        ) : null}

                        <p className="italic text-slate-300 text-[11px] bg-amber-950/10 p-2.5 rounded-lg border border-amber-500/20 leading-relaxed">
                          "{item.evidence_text || 'No source evidence was found for this requirement.'}"
                        </p>
                      </div>
                    </div>

                    {/* 3. Stated AI Assumption & Risk */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                          3. AI Assumption & Risk Disclosure
                        </span>
                        {item.is_high_risk_assumption ? (
                          <span className="text-[10px] font-bold text-rose-400 bg-rose-950/60 px-2 py-0.5 rounded border border-rose-500/30 flex items-center gap-1">
                            <ShieldAlert className="w-3 h-3" /> High-Risk Business Unknown — Confirmation Required
                          </span>
                        ) : (
                          <span className="text-[10px] font-medium text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                            Disclosed Baseline Assumption
                          </span>
                        )}
                      </div>
                      <p className="text-slate-300 bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                        {item.assumption}
                      </p>
                    </div>

                    {/* 4. What User Should Confirm & Potential Impact */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="p-3 rounded-xl bg-blue-950/20 border border-blue-500/20 space-y-1">
                        <span className="text-[10px] font-bold text-blue-300 uppercase block flex items-center gap-1">
                          <HelpCircle className="w-3 h-3 text-blue-400" /> 4. What to Confirm
                        </span>
                        <p className="text-slate-200 text-xs leading-relaxed">{item.what_to_confirm}</p>
                      </div>

                      <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-1">
                        <span className="text-[10px] font-bold text-amber-300 uppercase block flex items-center gap-1">
                          <Info className="w-3 h-3 text-amber-400" /> 5. Potential Downstream Impact
                        </span>
                        <p className="text-slate-200 text-xs leading-relaxed">{item.potential_impact}</p>
                      </div>
                    </div>

                    {/* 5. User Confirmed Truth Box (if confirmed) */}
                    {isConfirmed && item.user_clarification && (
                      <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/40 space-y-1">
                        <div className="flex items-center justify-between text-emerald-400 text-[11px] font-bold">
                          <span className="flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5" /> User-Confirmed Truth (Fed Back to Blueprint)
                          </span>
                          {item.confirmed_at && (
                            <span className="text-[10px] text-emerald-500 font-normal">
                              {new Date(item.confirmed_at).toLocaleString()}
                            </span>
                          )}
                        </div>
                        <p className="text-slate-100 font-medium text-xs bg-slate-950/60 p-2.5 rounded-lg border border-emerald-500/20">
                          {item.user_clarification}
                        </p>
                      </div>
                    )}

                    {/* 6. Interactive Action Bar */}
                    <div className="pt-2 flex flex-wrap items-center justify-between gap-2 border-t border-slate-800">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleOpenConfirmModal(item, 'CONFIRM')}
                          className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/20 transition flex items-center space-x-1.5"
                        >
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>{isConfirmed ? 'Edit Clarification' : 'Confirm & Clarify Rule'}</span>
                        </button>

                        {!isConfirmed && (
                          <button
                            onClick={() => handleQuickAcceptAssumption(item)}
                            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition flex items-center space-x-1"
                          >
                            <Check className="w-3 h-3 text-blue-400" />
                            <span>Accept AI Assumption</span>
                          </button>
                        )}
                      </div>

                      <div className="flex items-center space-x-2">
                        {item.source_code && onOpenEvidenceModal && (
                          <button
                            onClick={() =>
                              onOpenEvidenceModal({
                                requirementTitle: item.title,
                                requirementCode: item.source_code,
                                requirementDescription: item.what_is_unclear,
                                provenance: {
                                  provenance_type: 'DIRECT',
                                  source_code: item.source_code,
                                  document_name: item.document_name,
                                  page_number: item.page_number,
                                  section_heading: item.section_heading,
                                  exact_text: item.evidence_text,
                                  derivation_rationale: item.why_unclear || item.what_is_unclear,
                                  confidence_score: 0.95
                                }
                              })
                            }
                            className="px-2.5 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs border border-slate-700/60 transition flex items-center space-x-1"
                          >
                            <ExternalLink className="w-3 h-3" />
                            <span>Inspect Evidence</span>
                          </button>
                        )}

                        {!isRejected && (
                          <button
                            onClick={() => handleReject(item)}
                            className="px-2.5 py-1.5 rounded-xl bg-slate-900 hover:bg-rose-950/60 text-slate-500 hover:text-rose-300 text-xs border border-slate-800 transition"
                          >
                            Dismiss
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* 3. REGENERATION BANNER IF CLARIFICATIONS EXIST */}
      {confirmedCount > 0 && onRegenerateBlueprint && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/60 via-slate-900 to-blue-950/60 border border-emerald-500/40 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-xl">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h5 className="text-xs font-bold text-white">
                {confirmedCount} Confirmed Requirement Clarification{confirmedCount === 1 ? '' : 's'} Active
              </h5>
              <p className="text-[11px] text-slate-400">
                User clarifications are active and ready to be compiled into the updated solution blueprint.
              </p>
            </div>
          </div>

          <button
            onClick={onRegenerateBlueprint}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/25 transition flex items-center space-x-2 shrink-0"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Regenerate Blueprint with Confirmed Context</span>
          </button>
        </div>
      )}

      {/* 4. INTERACTIVE CONFIRMATION MODAL */}
      {activeModalItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5 relative">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
                  <Edit3 className="w-4 h-4" />
                </span>
                <h3 className="text-base font-bold text-white">
                  {actionType === 'CONFIRM' ? 'Provide Definitive Clarification' : 'Edit Stated AI Assumption'}
                </h3>
              </div>
              <button
                onClick={handleCloseModal}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="text-[10px] font-bold text-slate-500 uppercase block">Uncertainty Title</span>
                <p className="text-slate-200 font-semibold">{activeModalItem.title}</p>
                <p className="text-slate-400 text-[11px]">{activeModalItem.what_is_unclear}</p>
              </div>

              <div className="p-3 rounded-xl bg-blue-950/30 border border-blue-500/30 space-y-1">
                <span className="text-[10px] font-bold text-blue-300 uppercase block">Question for You</span>
                <p className="text-slate-200 font-medium">{activeModalItem.what_to_confirm}</p>
              </div>

              <form onSubmit={handleSubmitClarification} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1.5">
                    {actionType === 'CONFIRM' ? 'Your Business Rule / Clarification:' : 'Modified Stated Assumption:'}
                  </label>
                  <textarea
                    required
                    rows={4}
                    value={clarificationInput}
                    onChange={(e) => setClarificationInput(e.target.value)}
                    placeholder={
                      actionType === 'CONFIRM'
                        ? 'e.g. All claims under $1,000 are processed automatically; claims above $1,000 require Lead Claims Specialist approval.'
                        : 'e.g. Modern responsive React web app with OAuth2 JWT security.'
                    }
                    className="w-full p-3 rounded-xl bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                  <span className="text-[10px] text-slate-500 mt-1 block">
                    This confirmed rule will be treated as factual ground truth during blueprint generation.
                  </span>
                </div>

                <div className="flex items-center justify-end space-x-3 pt-2">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting || !clarificationInput.trim()}
                    className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs shadow-lg shadow-emerald-600/25 transition flex items-center space-x-1.5"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>{isSubmitting ? 'Saving...' : 'Save & Confirm Ground Truth'}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
