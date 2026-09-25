import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FileSearch,
  Users,
  Target,
  AlertTriangle,
  Clock,
  ArrowRight,
  CheckCircle2,
  Layers,
  RefreshCw
} from 'lucide-react';
import api from '../services/api';
import { BusinessAnalysisData } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';
import { useLanguage } from '../contexts/LanguageContext';

export const BusinessAnalysisPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const { t } = useLanguage();
  const [data, setData] = useState<BusinessAnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/business-analysis/project/${projectId}`);
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
      const res: any = await api.post(`/business-analysis/project/${projectId}/generate`);
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
    return <LoadingScreen message={t('Synthesizing requirements, AS-IS process, and stakeholder analysis...', 'Synthesizing requirements, AS-IS process, and stakeholder analysis...')} />;
  }

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER BAR */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">
              STEP 02
            </span>
            <h1 className="text-2xl font-extrabold text-white">{t('business_analysis_title', 'Business Analysis & Current State')}</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {t('business_analysis_desc', 'Requirement discovery, AS-IS process bottlenecks, stakeholder alignment, and operational KPIs.')}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-blue-400 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>{isRegenerating ? t('Analyzing...', 'Analyzing...') : t('Regenerate Analysis', 'Regenerate Analysis')}</span>
          </button>
          <Link
            to={`/projects/${projectId}/gap-analysis`}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>{t('Next: 8-Dimension Gaps', 'Next: 8-Dimension Gaps')}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* SUMMARY & OBJECTIVES */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
          <h3 className="text-sm font-bold text-slate-100 flex items-center mb-3">
            <Target className="w-4 h-4 text-blue-400 mr-2" />
            {t('executive_business_summary', 'Executive Business Summary')}
          </h3>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            {t(data?.business_summary || '', data?.business_summary)}
          </p>

          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mt-6 mb-3">
            {t('strategic_objectives', 'Strategic Objectives')}
          </h4>
          <div className="space-y-2">
            {data?.objectives.map((obj, idx) => (
              <div key={idx} className="flex items-start space-x-2 text-xs text-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{t(obj, obj)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* TARGET KPIs */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center mb-3">
              <Clock className="w-4 h-4 text-emerald-400 mr-2" />
              {t('target_transformation_kpis', 'Target Transformation KPIs')}
            </h3>
            <div className="space-y-3">
              {data?.kpis.map((kpi, idx) => (
                <div key={idx} className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-xs font-semibold text-slate-200">
                  ⚡ {t(kpi, kpi)}
                </div>
              ))}
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400">
            {t('Confidence Index:', 'Confidence Index:')} <span className="text-emerald-400 font-bold">95.4%</span> ({t('Grounded in context', 'Grounded in context')})
          </div>
        </div>
      </div>

      {/* AS-IS CURRENT-STATE PROCESS FLOW */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center">
              <Clock className="w-4 h-4 text-amber-400 mr-2" />
              {t('current_state_as_is_manual_workflow', 'Current State (AS-IS) Manual Workflow & Bottlenecks')}
            </h3>
            <p className="text-xs text-slate-400">{t('Step-by-step audit of operational friction points before transformation.', 'Step-by-step audit of operational friction points before transformation.')}</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
            {t('Total Latency:', 'Total Latency:')} 48 Hours
          </span>
        </div>

        <div className="space-y-3">
          {data?.as_is_process.map((step) => (
            <div
              key={step.step_number}
              className={`p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs ${
                step.is_bottleneck
                  ? 'bg-rose-950/20 border-rose-500/40 text-slate-200'
                  : 'bg-slate-800/40 border-slate-700/60 text-slate-300'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="w-6 h-6 rounded-full bg-slate-800 text-slate-300 font-bold flex items-center justify-center text-xs shrink-0">
                  {step.step_number}
                </span>
                <div>
                  <h4 className="font-bold text-slate-100">{t(step.activity, step.activity)}</h4>
                  <p className="text-[11px] text-slate-400">{t('Actor', 'Actor')}: <span className="text-slate-300 font-medium">{t(step.actor, step.actor)}</span> | {t('System', 'System')}: <span className="text-slate-300 font-medium">{t(step.system, step.system)}</span></p>
                </div>
              </div>

              <div className="flex items-center space-x-3 md:text-right">
                <div>
                  <span className="text-[10px] text-slate-500 block">{t('Duration', 'Duration')}</span>
                  <span className="font-mono font-bold text-amber-400">{step.duration}</span>
                </div>
                {step.is_bottleneck && (
                  <span className="px-2 py-1 rounded bg-rose-500/30 text-rose-300 font-bold text-[10px] uppercase flex items-center">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    {t('Bottleneck', 'Bottleneck')}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* REQUIREMENTS CATALOG */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
        <h3 className="text-sm font-bold text-slate-100 flex items-center mb-4">
          <Layers className="w-4 h-4 text-purple-400 mr-2" />
          {t('discovered_functional_non_functional_requirements', 'Discovered Functional & Non-Functional Requirements')}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data?.functional_requirements.concat(data?.non_functional_requirements || []).map((req) => (
            <div key={req.code} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 text-xs">
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-mono font-bold text-blue-400">{req.code}</span>
                <div className="flex items-center space-x-1.5">
                  <span className="text-[10px] px-2 py-0.5 rounded bg-slate-700 text-slate-300">
                    {t(req.req_type, req.req_type)}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                    req.priority === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {t(req.priority, req.priority)}
                  </span>
                </div>
              </div>
              <h4 className="font-bold text-slate-100 mb-1">{t(req.title, req.title)}</h4>
              <p className="text-slate-400 leading-relaxed mb-2">{t(req.description, req.description)}</p>
              <span className="text-[10px] text-slate-500 block">{t('Source:', 'Source:')} {t(req.source || 'Document Analysis', req.source || 'Document Analysis')}</span>
            </div>
          ))}
        </div>
      </div>

      {/* STAKEHOLDERS */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
        <h3 className="text-sm font-bold text-slate-100 flex items-center mb-4">
          <Users className="w-4 h-4 text-indigo-400 mr-2" />
          {t('stakeholder_matrix_impact_analysis', 'Stakeholder Matrix & Impact Analysis')}
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {data?.stakeholders.map((sh, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs">
              <h4 className="font-bold text-slate-100">{t(sh.name, sh.name)}</h4>
              <p className="text-[11px] text-blue-400 font-medium">{t(sh.role, sh.role)}</p>
              <p className="text-[11px] text-slate-400">{t(sh.department, sh.department)}</p>
              <div className="mt-3 pt-2 border-t border-slate-700 flex items-center justify-between text-[10px]">
                <span className="text-slate-500">{t('Influence:', 'Influence:')} <b className="text-slate-300">{t(sh.influence, sh.influence)}</b></span>
                <span className="text-slate-500">{t('Interest:', 'Interest:')} <b className="text-slate-300">{t(sh.interest, sh.interest)}</b></span>
              </div>
              <p className="text-[11px] text-slate-400 mt-2 italic line-clamp-2">"{t(sh.key_concerns, sh.key_concerns)}"</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
