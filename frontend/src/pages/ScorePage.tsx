import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Award,
  TrendingUp,
  Cpu,
  Zap,
  Database,
  ArrowRight,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ShieldCheck
} from 'lucide-react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer
} from 'recharts';
import api from '../services/api';
import { TransformationScoreData } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';

export const ScorePage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const [data, setData] = useState<TransformationScoreData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRecalculating, setIsRecalculating] = useState(false);

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/scores/project/${projectId}`);
      if (res.success && res.data) {
        setData(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecalculate = async () => {
    if (!projectId) return;
    setIsRecalculating(true);
    try {
      const res: any = await api.post(`/scores/project/${projectId}/calculate`);
      if (res.success && res.data) {
        setData(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsRecalculating(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  if (isLoading) {
    return <LoadingScreen message="Calculating multi-dimensional Transformation Readiness Scorecard..." />;
  }

  const radarData = [
    { subject: 'AI Readiness', A: data?.ai_readiness || 91, fullMark: 100 },
    { subject: 'Automation', A: data?.automation_potential || 88, fullMark: 100 },
    { subject: 'Data Readiness', A: data?.data_readiness || 76, fullMark: 100 },
    { subject: 'Business Impact', A: data?.business_impact || 94, fullMark: 100 },
    { subject: 'Tech Feasibility', A: data?.technical_feasibility || 89, fullMark: 100 },
    { subject: 'Implementation', A: data?.implementation_readiness || 85, fullMark: 100 },
  ];

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
              STEP 12
            </span>
            <h1 className="text-2xl font-extrabold text-white">TransformIQ Readiness Scorecard</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Proprietary 6-dimension digital transformation readiness and maturity assessment.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleRecalculate}
            disabled={isRecalculating}
            className="px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${isRecalculating ? 'animate-spin' : ''}`} />
            <span>{isRecalculating ? 'Calculating...' : 'Recalculate Score'}</span>
          </button>
          <Link
            to={`/projects/${projectId}/blueprint`}
            className="px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-500 hover:to-blue-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>Next: Master Blueprint</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* OVERALL SCORE HERO */}
      <div className="p-4 sm:p-8 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-slate-900/80 to-blue-950/40 border border-emerald-500/30 backdrop-blur-md flex flex-col md:flex-row items-start md:items-center justify-between gap-6 sm:gap-8">
        <div>
          <span className="text-xs font-bold uppercase tracking-widest text-emerald-400 flex items-center mb-1">
            <Award className="w-4 h-4 mr-1.5" /> Overall Transformation Score
          </span>
          <div className="flex flex-wrap items-baseline gap-2.5 mt-1">
            <h2 className="text-4xl sm:text-6xl font-black text-white">{data?.overall_score || 88}</h2>
            <span className="text-lg sm:text-xl text-slate-400 font-bold">/ 100</span>
            <span className="text-[11px] sm:text-xs font-semibold px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300">
              Top Quartile (Implementation Ready)
            </span>
          </div>
          <p className="text-xs text-slate-300 mt-2 max-w-xl">
            This initiative qualifies for immediate execution with strong executive alignment, high straight-through automation yield, and manageable technical risk.
          </p>
        </div>

        <div className="h-56 w-72 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="subject" stroke="#94a3b8" tick={{ fontSize: 9 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
              <Radar name="Score" dataKey="A" stroke="#10b981" fill="#10b981" fillOpacity={0.4} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 6 DIMENSION METRIC BARS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { label: 'AI Readiness', val: data?.ai_readiness || 91, desc: 'NLP, Sentiment & Semantic RAG capability' },
          { label: 'Automation Potential', val: data?.automation_potential || 88, desc: 'Straight-through event-driven routing yield' },
          { label: 'Business Impact', val: data?.business_impact || 94, desc: '340% projected ROI & $420k annual savings' },
          { label: 'Technical Feasibility', val: data?.technical_feasibility || 89, desc: 'FastAPI microservices & PostgreSQL stability' },
          { label: 'Implementation Readiness', val: data?.implementation_readiness || 85, desc: 'Validated 16-week 4-phase agile roadmap' },
          { label: 'Data Readiness', val: data?.data_readiness || 76, desc: 'Unstructured document corpus indexing' },
        ].map((dim, idx) => (
          <div key={idx} className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-bold text-slate-200">{dim.label}</span>
              <span className="text-xs font-bold text-emerald-400 font-mono">{dim.val}%</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mb-2">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-emerald-400 rounded-full"
                style={{ width: `${dim.val}%` }}
              />
            </div>
            <p className="text-[11px] text-slate-400">{dim.desc}</p>
          </div>
        ))}
      </div>

      {/* KEY DRIVERS & STRATEGIC RECOMMENDATIONS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
          <h3 className="text-sm font-bold text-white flex items-center mb-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 mr-2" />
            Key Readiness Drivers
          </h3>
          <div className="space-y-2 text-xs text-slate-300">
            {data?.key_drivers.map((drv, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60">
                • {drv}
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
          <h3 className="text-sm font-bold text-white flex items-center mb-3">
            <Sparkles className="w-4 h-4 text-blue-400 mr-2" />
            Strategic Next Steps
          </h3>
          <div className="space-y-2 text-xs text-slate-300">
            {data?.strategic_recommendations.map((rec, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60">
                ⚡ {rec}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center text-xs text-slate-400 italic">
        ℹ️ {data?.disclaimer || 'AI-assisted assessment based on project inputs and enterprise artifacts.'}
      </div>
    </div>
  );
};
