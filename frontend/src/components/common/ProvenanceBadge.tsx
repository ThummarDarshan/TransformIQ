import React from 'react';
import { FileText, Sparkles, GitPullRequest, HelpCircle } from 'lucide-react';
import { ProvenanceMetadata } from '../../types';

interface ProvenanceBadgeProps {
  provenance?: ProvenanceMetadata;
  onClick?: () => void;
  className?: string;
  showDetails?: boolean;
}

export const ProvenanceBadge: React.FC<ProvenanceBadgeProps> = ({
  provenance,
  onClick,
  className = '',
  showDetails = true,
}) => {
  if (!provenance) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-800 text-slate-400 border border-slate-700/60 ${className}`}
        title="Source traceability unavailable for this item"
      >
        <HelpCircle className="w-3 h-3 text-slate-500" />
        <span>No Citation</span>
      </span>
    );
  }

  const type = provenance.provenance_type || 'DIRECT';

  const badgeConfig = {
    DIRECT: {
      bg: 'bg-emerald-950/60 hover:bg-emerald-900/80 border-emerald-500/40 text-emerald-300',
      icon: <FileText className="w-3 h-3 text-emerald-400" />,
      label: 'Direct Source',
      tag: 'DIRECT',
    },
    DERIVED: {
      bg: 'bg-amber-950/60 hover:bg-amber-900/80 border-amber-500/40 text-amber-300',
      icon: <GitPullRequest className="w-3 h-3 text-amber-400" />,
      label: 'Derived Logic',
      tag: 'DERIVED',
    },
    RECOMMENDED: {
      bg: 'bg-purple-950/60 hover:bg-purple-900/80 border-purple-500/40 text-purple-300',
      icon: <Sparkles className="w-3 h-3 text-purple-400" />,
      label: 'AI Recommendation',
      tag: 'RECOMMENDED',
    },
  };

  const config = badgeConfig[type] || badgeConfig.DIRECT;
  const pageText = provenance.page_number ? ` • P.${provenance.page_number}` : '';
  const docShort = provenance.document_name
    ? provenance.document_name.length > 22
      ? provenance.document_name.slice(0, 19) + '...'
      : provenance.document_name
    : provenance.source_code;

  return (
    <button
      type="button"
      onClick={onClick}
      title={`Click to inspect exact source evidence & provenance (${config.tag})`}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium border transition-all duration-150 cursor-pointer shadow-sm hover:scale-[1.02] active:scale-[0.98] ${config.bg} ${className}`}
    >
      {config.icon}
      <span className="font-semibold">{provenance.source_code || config.tag}</span>
      {showDetails && (
        <span className="text-slate-300/90 font-normal">
          {type === 'RECOMMENDED' ? 'Best Practice' : `[${docShort}${pageText}]`}
        </span>
      )}
    </button>
  );
};
