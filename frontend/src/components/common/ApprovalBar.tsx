import React from 'react';
import { CheckCircle2, XCircle, Clock } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

interface ApprovalBarProps {
  status: string; // APPROVED, UNDER_REVIEW, REJECTED, DRAFT
  reviewedBy?: string;
  decisionDate?: string;
  onApprove?: () => void;
  onReject?: () => void;
  isSubmitting?: boolean;
}

export const ApprovalBar: React.FC<ApprovalBarProps> = ({
  status,
  reviewedBy,
  decisionDate,
  onApprove,
  onReject,
  isSubmitting = false,
}) => {
  const { t } = useLanguage();
  const isApproved = status === 'APPROVED';
  const isRejected = status === 'REJECTED';

  return (
    <div className={`p-4 rounded-xl border flex flex-col md:flex-row items-center justify-between gap-4 ${
      isApproved 
        ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-200' 
        : isRejected 
          ? 'bg-rose-950/40 border-rose-500/30 text-rose-200'
          : 'bg-amber-950/40 border-amber-500/30 text-amber-200'
    }`}>
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${
          isApproved ? 'bg-emerald-500/20 text-emerald-400' : isRejected ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
        }`}>
          {isApproved ? <CheckCircle2 className="w-5 h-5" /> : isRejected ? <XCircle className="w-5 h-5" /> : <Clock className="w-5 h-5" />}
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-sm tracking-wide">{t('human_in_the_loop_governance', 'Human-in-the-Loop Governance:')}</span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              isApproved ? 'bg-emerald-500/30 text-emerald-300' : isRejected ? 'bg-rose-500/30 text-rose-300' : 'bg-amber-500/30 text-amber-300'
            }`}>
              {t(status, status)}
            </span>
          </div>
          <p className="text-xs text-slate-300 mt-0.5">
            {isApproved 
              ? `${t('Approved by', 'Approved by')} ${reviewedBy || t('Lead Architect', 'Lead Architect')}. ${t('Ready for implementation blueprint export.', 'Ready for implementation blueprint export.')}`
              : isRejected 
                ? t('Rejected during review. Please revise requirements or architecture before resubmitting.', 'Rejected during review. Please revise requirements or architecture before resubmitting.')
                : t('AI recommendations are advisory and require human validation before production commit.', 'AI recommendations are advisory and require human validation before production commit.')}
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        {onApprove && !isApproved && (
          <button
            onClick={onApprove}
            disabled={isSubmitting}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-md transition disabled:opacity-50"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>{t('approve_blueprint', 'Approve Blueprint')}</span>
          </button>
        )}
        {onReject && !isRejected && (
          <button
            onClick={onReject}
            disabled={isSubmitting}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-rose-900/50 text-rose-300 border border-slate-700 transition disabled:opacity-50"
          >
            <XCircle className="w-4 h-4" />
            <span>{t('request_revision', 'Request Revision')}</span>
          </button>
        )}
      </div>
    </div>
  );
};
