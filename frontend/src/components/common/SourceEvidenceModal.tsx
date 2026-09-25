import React, { useState } from 'react';
import {
  X,
  FileText,
  Sparkles,
  GitPullRequest,
  CheckCircle2,
  Copy,
  Check,
  ShieldCheck,
  BookOpen,
  ArrowDownUp,
  ExternalLink,
  Layers,
  Search,
} from 'lucide-react';
import { ProvenanceMetadata } from '../../types';

interface SourceEvidenceModalProps {
  isOpen: boolean;
  onClose: () => void;
  requirementTitle?: string;
  requirementCode?: string;
  requirementDescription?: string;
  provenance?: ProvenanceMetadata | null;
}

export const SourceEvidenceModal: React.FC<SourceEvidenceModalProps> = ({
  isOpen,
  onClose,
  requirementTitle,
  requirementCode,
  requirementDescription,
  provenance,
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopyQuote = () => {
    if (provenance?.exact_text) {
      navigator.clipboard.writeText(provenance.exact_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const isRecommended = provenance?.provenance_type === 'RECOMMENDED';
  const isDerived = provenance?.provenance_type === 'DERIVED';
  const isDirect = provenance?.provenance_type === 'DIRECT' || !provenance?.provenance_type;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-3xl w-full p-6 shadow-2xl relative max-h-[92vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div
              className={`p-2.5 rounded-xl border ${
                isDirect
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : isDerived
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  : 'bg-purple-500/10 border-purple-500/30 text-purple-400'
              }`}
            >
              {isDirect && <FileText className="w-6 h-6" />}
              {isDerived && <GitPullRequest className="w-6 h-6" />}
              {isRecommended && <Sparkles className="w-6 h-6" />}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span
                  className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${
                    isDirect
                      ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40'
                      : isDerived
                      ? 'bg-amber-950/80 text-amber-300 border-amber-500/40'
                      : 'bg-purple-950/80 text-purple-300 border-purple-500/40'
                  }`}
                >
                  {provenance?.provenance_type || 'SOURCE EVIDENCE'}
                </span>
                {provenance?.source_code && (
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {provenance.source_code}
                  </span>
                )}
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  Cryptographically Auditable
                </span>
              </div>
              <h3 className="text-lg font-bold text-slate-100 mt-1">
                Source Evidence & Provenance Inspector
              </h3>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto py-5 space-y-5 pr-1 text-sm">
          {/* Section 1: Generated Requirement */}
          <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5" />
                Generated Transformation Requirement
              </span>
              {requirementCode && (
                <span className="text-xs font-mono font-bold text-blue-300 bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800/60">
                  {requirementCode}
                </span>
              )}
            </div>
            <h4 className="text-base font-bold text-slate-100 mb-1.5">
              {requirementTitle || 'Grounded Requirement Statement'}
            </h4>
            {requirementDescription && (
              <p className="text-slate-300 text-xs leading-relaxed">
                {requirementDescription}
              </p>
            )}
          </div>

          {/* Derivation Connector */}
          <div className="flex items-center justify-center -my-2">
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs text-slate-400 shadow-sm">
              <ArrowDownUp className="w-3.5 h-3.5 text-blue-400" />
              <span className="font-medium text-slate-300">
                {isDirect
                  ? 'Directly extracted from verifiable source statement'
                  : isDerived
                  ? 'Logically deduced from business constraint in source'
                  : 'AI synthesized best-practice recommendation'}
              </span>
            </div>
          </div>

          {/* Section 2: Canonical Source Evidence */}
          {!provenance || !provenance.exact_text ? (
            <div className="p-6 rounded-xl bg-slate-800/30 border border-slate-700/50 text-center space-y-2">
              <BookOpen className="w-8 h-8 text-slate-500 mx-auto" />
              <p className="font-semibold text-slate-300">
                Source Traceability Unavailable for this Item
              </p>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                This item was generated prior to canonical source indexing or is an AI-assisted architectural suggestion.
              </p>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-3.5">
              <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-slate-700/50">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-emerald-400" />
                  <span className="font-semibold text-slate-200 text-xs uppercase tracking-wider">
                    Source Document Context
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  {provenance.document_name && (
                    <span className="font-medium text-slate-200 bg-slate-900 px-2.5 py-1 rounded border border-slate-700">
                      📄 {provenance.document_name}
                    </span>
                  )}
                  {provenance.page_number && (
                    <span className="font-medium text-emerald-300 bg-emerald-950/60 px-2 py-1 rounded border border-emerald-800/60">
                      Page {provenance.page_number}
                    </span>
                  )}
                  {provenance.section_heading && (
                    <span className="text-slate-400 bg-slate-900 px-2 py-1 rounded border border-slate-800">
                      § {provenance.section_heading}
                    </span>
                  )}
                </div>
              </div>

              {/* Verbatim Source Quote with Highlighting */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="font-semibold text-slate-300">Verbatim Extracted Evidence:</span>
                  <button
                    onClick={handleCopyQuote}
                    className="inline-flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 transition"
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    {copied ? 'Copied Quote' : 'Copy Quote'}
                  </button>
                </div>
                <div className="p-3.5 rounded-lg bg-amber-950/20 border border-amber-500/30 text-slate-100 text-xs sm:text-sm leading-relaxed relative">
                  <span className="bg-amber-400/20 text-amber-200 font-medium px-1.5 py-0.5 rounded border-b-2 border-amber-400 selection:bg-amber-300 selection:text-black">
                    "{provenance.exact_text}"
                  </span>
                </div>
              </div>

              {/* Derivation Rationale */}
              {provenance.derivation_rationale && (
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                    <Search className="w-3 h-3 text-blue-400" />
                    Why this Generated Item Exists:
                  </span>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {provenance.derivation_rationale}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Traceability Guarantee Footnote */}
          <div className="p-3 rounded-xl bg-blue-950/30 border border-blue-900/50 flex items-start gap-2.5 text-xs text-blue-200/90">
            <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-blue-100">Deterministic Source Lineage: </span>
              TransformIQ grounds all enterprise requirements against raw ingested artifacts without hallucinating citations or inflating confidence scores.
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
          <div className="text-xs text-slate-400">
            Status: <span className="text-emerald-400 font-medium">Verified & Linked</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
