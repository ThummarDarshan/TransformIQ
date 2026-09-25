import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Sparkles,
  Zap,
  HelpCircle,
  CheckCircle2,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import api from '../services/api';
import { SolutionData, RecommendationItem } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';
import { ExplainWhyModal } from '../components/common/ExplainWhyModal';
import { useLanguage } from '../contexts/LanguageContext';

export const RecommendationsPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const { t } = useLanguage();
  const [data, setData] = useState<SolutionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [selectedWhyData, setSelectedWhyData] = useState<any | null>(null);
  const [isWhyModalOpen, setIsWhyModalOpen] = useState(false);

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/recommendations/project/${projectId}`);
      if (res.success && res.data) {
        setData(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async () => {
    if (!projectId) return;
    setIsRegenerating(true);
    try {
      const res: any = await api.post(`/recommendations/project/${projectId}/generate`);
      if (res.success && res.data) {
        setData(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleOpenWhy = async (recId: string) => {
    try {
      const res: any = await api.get(`/recommendations/why/${recId}`);
      if (res.success && res.data) {
        setSelectedWhyData(res.data);
        setIsWhyModalOpen(true);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleStatusUpdate = async (recId: string, newStatus: string) => {
    try {
      await api.post(`/recommendations/${recId}/status?status_value=${newStatus}`);
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          recommendations: prev.recommendations.map((r) =>
            r.id === recId ? { ...r, status: newStatus } : r
          ),
        };
      });
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  if (isLoading) {
    return <LoadingScreen message={t('Synthesizing AI & automation recommendations with explainability rationale...', 'Synthesizing AI & automation recommendations with explainability rationale...')} />;
  }

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">
              STEP 04
            </span>
            <h1 className="text-2xl font-extrabold text-white">{t('ai_recommendations_engine', 'AI & Automation Solution Recommendation')}</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {t('recommendations_desc', 'Grounded solution design, explainable rationale, and prioritization matrix.')}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-3 sm:px-3.5 py-1.5 sm:py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-blue-400 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>{isRegenerating ? t('Synthesizing...', 'Synthesizing...') : t('Regenerate', 'Regenerate')}</span>
          </button>
          <Link
            to={`/projects/${projectId}/architecture`}
            className="px-3.5 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>{t('Next: React Flow Architecture', 'Next: React Flow Architecture')}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* RECOMMENDED SOLUTION BANNER */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/50 via-slate-900/80 to-emerald-950/40 border border-blue-500/30 backdrop-blur-md relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center mb-1">
              <Sparkles className="w-4 h-4 mr-1.5" /> {t('target_transformation_solution', 'Target Transformation Solution')}
            </span>
            <h2 className="text-xl sm:text-2xl font-extrabold text-white">{t(data?.recommended_solution_name || '', data?.recommended_solution_name)}</h2>
            <p className="text-xs text-slate-300 italic mt-0.5">{t(data?.tagline || '', data?.tagline)}</p>
          </div>
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-right shrink-0">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">{t('projected_12m_return', 'Projected 12M Return')}</span>
            <span className="text-lg font-black text-emerald-400">{t(data?.expected_roi || '340% ROI', data?.expected_roi || '340% ROI')}</span>
          </div>
        </div>

        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed mb-4">
          {t(data?.executive_summary || '', data?.executive_summary)}
        </p>

        {/* Technology Stack Pills */}
        <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-400 mr-2">{t('Architecture Stack:', 'Architecture Stack:')}</span>
          {data?.technology_stack &&
            Object.entries(data.technology_stack).flatMap(([layer, techs]) =>
              techs.map((tech, idx) => (
                <span
                  key={`${layer}-${idx}`}
                  className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-800 text-slate-200 border border-slate-700"
                >
                  {t(tech, tech)}
                </span>
              ))
            )}
        </div>
      </div>

      {/* RECOMMENDATIONS CARDS WITH WHY BUTTON */}
      <div>
        <h3 className="text-base font-bold text-white mb-4 flex items-center">
          <Zap className="w-4 h-4 text-amber-400 mr-2" />
          {t('prioritized_ai_automation_initiatives', 'Prioritized AI & Automation Initiatives')} ({data?.recommendations.length})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {data?.recommendations.map((rec) => {
            const isApproved = rec.status === 'APPROVED';
            return (
              <div
                key={rec.id}
                className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">
                      {t(rec.category, rec.category)}
                    </span>
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                        {Math.round(rec.confidence_score * 100)}% {t('Confidence', 'Confidence')}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                          rec.priority === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                        }`}
                      >
                        {t(rec.priority, rec.priority)}
                      </span>
                    </div>
                  </div>

                  <h4 className="text-base font-bold text-slate-100 mb-2">{t(rec.title, rec.title)}</h4>
                  <p className="text-xs text-slate-300 leading-relaxed mb-3">{t(rec.description, rec.description)}</p>

                  <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800 text-xs text-slate-400 mb-4">
                    <b className="text-slate-200">{t('Business Rationale:', 'Business Rationale:')}</b> {t(rec.reason, rec.reason)}
                  </div>
                </div>

                {/* BOTTOM ACTIONS: WHY BUTTON & HUMAN APPROVAL */}
                <div className="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
                  <button
                    onClick={() => handleOpenWhy(rec.id)}
                    className="px-3 py-1.5 rounded-lg bg-blue-950/60 hover:bg-blue-900/80 text-blue-300 border border-blue-800/60 text-xs font-semibold flex items-center space-x-1.5 transition"
                  >
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span>{t('why_this_recommendation', 'Why this recommendation?')}</span>
                  </button>

                  <div className="flex items-center space-x-1.5">
                    <button
                      onClick={() => handleStatusUpdate(rec.id, isApproved ? 'UNDER_REVIEW' : 'APPROVED')}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
                        isApproved
                          ? 'bg-emerald-600 text-white shadow'
                          : 'bg-slate-800 text-slate-400 hover:text-emerald-300'
                      }`}
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{isApproved ? t('Approved', 'Approved') : t('Approve', 'Approve')}</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* EXPLAINABILITY MODAL */}
      <ExplainWhyModal
        isOpen={isWhyModalOpen}
        onClose={() => setIsWhyModalOpen(false)}
        data={selectedWhyData}
      />
    </div>
  );
};
