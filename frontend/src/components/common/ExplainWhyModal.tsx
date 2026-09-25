import React from 'react';
import { X, Sparkles, ShieldCheck, Target, BookOpen, AlertTriangle } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

interface ExplainWhyModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: {
    recommendation_title: string;
    recommendation_category: string;
    confidence_score: string;
    contextual_rationale: string;
    business_problem_alignment: string;
    risk_of_inaction: string;
    expected_roi_contribution: string;
    citations?: string[];
  } | null;
}

export const ExplainWhyModal: React.FC<ExplainWhyModalProps> = ({ isOpen, onClose, data }) => {
  const { t } = useLanguage();
  if (!isOpen || !data) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800/60 hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2.5 mb-4">
          <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 uppercase">
                {t(data.recommendation_category, data.recommendation_category)}
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                {t('Confidence', 'Confidence')}: {data.confidence_score}
              </span>
            </div>
            <h3 className="text-lg font-bold text-slate-100 mt-1">{t('why_this_recommendation', 'Why this recommendation?')}</h3>
          </div>
        </div>

        <p className="text-sm font-semibold text-blue-200 bg-blue-950/40 border border-blue-900/60 p-3.5 rounded-xl mb-5">
          "{t(data.recommendation_title, data.recommendation_title)}"
        </p>

        <div className="space-y-4 text-sm">
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60">
            <h4 className="font-semibold text-slate-200 flex items-center mb-1.5 text-xs uppercase tracking-wider text-blue-400">
              <Target className="w-4 h-4 mr-1.5" /> {t('contextual_rationale', 'Contextual Rationale')}
            </h4>
            <p className="text-slate-300 leading-relaxed">{t(data.contextual_rationale, data.contextual_rationale)}</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60">
            <h4 className="font-semibold text-slate-200 flex items-center mb-1.5 text-xs uppercase tracking-wider text-emerald-400">
              <ShieldCheck className="w-4 h-4 mr-1.5" /> {t('alignment_with_business_problem', 'Alignment with Business Problem')}
            </h4>
            <p className="text-slate-300 leading-relaxed">{t(data.business_problem_alignment, data.business_problem_alignment)}</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60">
            <h4 className="font-semibold text-slate-200 flex items-center mb-1.5 text-xs uppercase tracking-wider text-amber-400">
              <AlertTriangle className="w-4 h-4 mr-1.5" /> {t('risk_of_inaction', 'Risk of Inaction')}
            </h4>
            <p className="text-slate-300 leading-relaxed">{t(data.risk_of_inaction, data.risk_of_inaction)}</p>
          </div>

          {data.citations && data.citations.length > 0 && (
            <div className="pt-2">
              <h4 className="font-semibold text-slate-400 text-xs uppercase tracking-wider flex items-center mb-2">
                <BookOpen className="w-3.5 h-3.5 mr-1.5" /> {t('grounded_source_citations', 'Grounded Source Citations')}
              </h4>
              <div className="flex flex-wrap gap-2">
                {data.citations.map((c, i) => (
                  <span key={i} className="text-xs px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition"
          >
            {t('close_explanation', 'Close Explanation')}
          </button>
        </div>
      </div>
    </div>
  );
};
