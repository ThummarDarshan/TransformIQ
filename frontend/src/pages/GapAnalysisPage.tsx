import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Split,
  AlertTriangle,
  ArrowRight,
  Filter,
  RefreshCw,
} from 'lucide-react';
import api from '../services/api';
import { GapAnalysisData, GapItem } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';
import { useLanguage } from '../contexts/LanguageContext';

export const GapAnalysisPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const { t } = useLanguage();
  const [data, setData] = useState<GapAnalysisData | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/gaps/project/${projectId}`);
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
      const res: any = await api.post(`/gaps/project/${projectId}/generate`);
      if (res.success && res.data) {
        setData(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsRegenerating(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  if (isLoading) {
    return <LoadingScreen message={t('Executing 8-dimension gap matrix and root-cause analysis...', 'Executing 8-dimension gap matrix and root-cause analysis...')} />;
  }

  const categories = ['ALL', 'Process', 'Technology', 'AI', 'Data', 'People', 'Security', 'Automation', 'Integration'];

  const filteredGaps = data?.gaps.filter((g) => {
    const matchCat = selectedCategory === 'ALL' || g.category.toLowerCase() === selectedCategory.toLowerCase();
    const matchSev = selectedSeverity === 'ALL' || g.severity.toUpperCase() === selectedSeverity.toUpperCase();
    return matchCat && matchSev;
  }) || [];

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">
              STEP 03
            </span>
            <h1 className="text-2xl font-extrabold text-white">{t('8_dimension_gap_matrix', '8-Dimension Gap Matrix')}</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {t('gap_matrix_desc', 'Current state vs desired future state across Process, Technology, AI, Data, Security, and Governance.')}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-3 sm:px-3.5 py-1.5 sm:py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-purple-400 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>{isRegenerating ? t('Analyzing...', 'Analyzing...') : t('Regenerate Gaps', 'Regenerate Gaps')}</span>
          </button>
          <Link
            to={`/projects/${projectId}/recommendations`}
            className="px-3.5 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>{t('Next: AI Solutions', 'Next: AI Solutions')}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* KPI METRICS ROW */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
          <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">{t('total_identified', 'Total Identified')}</span>
          <h3 className="text-2xl font-black text-white mt-1">{data?.total_gaps_count || 8}</h3>
        </div>
        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30 text-center">
          <span className="text-xs text-rose-400 uppercase font-bold tracking-wider">{t('critical_severity', 'Critical Severity')}</span>
          <h3 className="text-2xl font-black text-rose-400 mt-1">{data?.critical_count || 3}</h3>
        </div>
        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 text-center">
          <span className="text-xs text-amber-400 uppercase font-bold tracking-wider">{t('high_severity', 'High Severity')}</span>
          <h3 className="text-2xl font-black text-amber-400 mt-1">{data?.high_count || 3}</h3>
        </div>
        <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-500/30 text-center">
          <span className="text-xs text-blue-400 uppercase font-bold tracking-wider">{t('medium_low', 'Medium / Low')}</span>
          <h3 className="text-2xl font-black text-blue-400 mt-1">{data?.medium_count || 2}</h3>
        </div>
      </div>

      {/* FILTER BUTTONS */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-slate-400 mr-2 font-semibold flex items-center">
            <Filter className="w-3.5 h-3.5 mr-1" /> {t('Dimension:', 'Dimension:')}
          </span>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                selectedCategory.toLowerCase() === cat.toLowerCase()
                  ? 'bg-purple-600 text-white shadow'
                  : 'bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {t(cat, cat)}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 font-semibold">{t('Severity:', 'Severity:')}</span>
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none"
          >
            <option value="ALL">{t('All Severities', 'All Severities')}</option>
            <option value="CRITICAL">{t('Critical', 'Critical')}</option>
            <option value="HIGH">{t('High', 'High')}</option>
            <option value="MEDIUM">{t('Medium', 'Medium')}</option>
          </select>
        </div>
      </div>

      {/* GAP MATRIX GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredGaps.map((gap, idx) => {
          const isCritical = gap.severity === 'CRITICAL';
          return (
            <div
              key={idx}
              className={`p-6 rounded-2xl border backdrop-blur-md flex flex-col justify-between transition hover:border-slate-600 ${
                isCritical
                  ? 'bg-gradient-to-b from-rose-950/20 to-slate-900/60 border-rose-500/30'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">
                    {t(gap.category, gap.category)}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      isCritical
                        ? 'bg-rose-500/30 text-rose-300 border border-rose-500/40'
                        : 'bg-amber-500/30 text-amber-300 border border-amber-500/40'
                    }`}
                  >
                    {t(gap.severity, gap.severity)} {t('SEVERITY', 'SEVERITY')}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-100 mb-4">{t(gap.title, gap.title)}</h3>

                {/* CURRENT VS DESIRED */}
                <div className="space-y-3 mb-4 text-xs">
                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-rose-400 block mb-1">
                      {t('current_bottleneck_state', 'Current Bottleneck State')}
                    </span>
                    <p className="text-slate-300 leading-relaxed">{t(gap.current_state, gap.current_state)}</p>
                  </div>

                  <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block mb-1">
                      {t('desired_ai_target_state', 'Desired AI Target State')}
                    </span>
                    <p className="text-slate-200 leading-relaxed">{t(gap.desired_state, gap.desired_state)}</p>
                  </div>
                </div>

                {/* ROOT CAUSE & IMPACT */}
                <div className="space-y-1.5 text-xs text-slate-400 mb-4">
                  <p><b className="text-slate-300">{t('Impact:', 'Impact:')}</b> {t(gap.impact, gap.impact)}</p>
                  <p><b className="text-slate-300">{t('Root Cause:', 'Root Cause:')}</b> {t(gap.root_cause, gap.root_cause)}</p>
                </div>
              </div>

              {/* RECOMMENDED ACTION */}
              <div className="pt-3 border-t border-slate-800/80">
                <span className="text-[10px] uppercase font-bold tracking-wider text-blue-400 block mb-1">
                  {t('remediation_action', 'Remediation Action')}
                </span>
                <p className="text-xs font-semibold text-slate-200">{t(gap.recommended_action, gap.recommended_action)}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
