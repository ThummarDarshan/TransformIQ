import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  CalendarDays,
  DollarSign,
  Users,
  Clock,
  ArrowRight,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import api from '../services/api';
import { PlanningData } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';

export const PlanningPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<PlanningData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const normalizeData = (resData: any): PlanningData => {
    const rawRoadmap = resData?.roadmap;
    const roadmap = {
      name: rawRoadmap?.name || `Roadmap for Project`,
      total_duration_weeks: rawRoadmap?.total_duration_weeks || resData?.total_duration_weeks || 16,
      phases: rawRoadmap?.phases || resData?.roadmap_phases || []
    };

    const rawEst = resData?.estimate || {};
    const roles = rawEst.roles_breakdown || rawEst.role_breakdown || resData?.role_breakdown || [];
    const estimate = {
      total_estimated_hours: rawEst.total_estimated_hours ?? 1120,
      total_estimated_cost: rawEst.total_estimated_cost ?? 138500,
      currency: rawEst.currency || 'USD',
      duration_months: rawEst.duration_months ?? 4,
      roles_breakdown: roles,
      infrastructure_cost_monthly: rawEst.infrastructure_cost_monthly ?? rawEst.infrastructure_cost ?? 650,
      ai_api_cost_monthly: rawEst.ai_api_cost_monthly ?? 420,
      assumptions: rawEst.assumptions || [],
      confidence_level: rawEst.confidence_level || 'HIGH',
      disclaimer: rawEst.disclaimer || 'AI-generated preliminary estimate. Validated estimates require detailed technical discovery.'
    };

    return { roadmap, estimate };
  };

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res: any = await api.get(`/planning/project/${projectId}`);
      if (res.success && res.data) {
        setData(normalizeData(res.data));
      }
    } catch (e: any) {
      console.error(e);
      setError(e?.response?.data?.detail || 'Failed to load implementation planning data.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async () => {
    if (!projectId) return;
    setIsRegenerating(true);
    setError(null);
    try {
      const res: any = await api.post(`/planning/project/${projectId}/generate`);
      if (res.success && res.data) {
        setData(normalizeData(res.data));
      }
    } catch (e: any) {
      console.error(e);
      setError(e?.response?.data?.detail || 'Failed to regenerate implementation planning data.');
    } finally {
      setIsRegenerating(false);
    }
  };

  useEffect(() => {
    if (projectId === 'default') {
      api.get('/projects').then((res: any) => {
        if (res.success && res.data?.length > 0) {
          navigate(`/projects/${res.data[0].id}/planning`, { replace: true });
        }
      }).catch(console.error);
    }
  }, [projectId, navigate]);

  useEffect(() => {
    fetchData();
  }, [projectId]);

  if (isLoading) {
    return <LoadingScreen message="Calculating phase timelines, sprint tasks, and staffing budget..." />;
  }

  const phases = data?.roadmap?.phases || [];
  const roles = data?.estimate?.roles_breakdown || [];

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
              STEP 10
            </span>
            <h1 className="text-2xl font-extrabold text-white">Transformation Roadmap & Cost Estimation</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            4-Phase implementation roadmap, sprint milestones, resource allocation, and preliminary cost breakdown.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>{isRegenerating ? 'Planning...' : 'Regenerate'}</span>
          </button>
          <Link
            to={`/projects/${projectId}/simulation`}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-500 hover:to-blue-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>Next: What-If Simulator</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 flex items-center justify-between text-xs text-red-200">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchData}
            className="px-3 py-1 rounded bg-red-900/60 hover:bg-red-800 text-white font-semibold transition"
          >
            Retry
          </button>
        </div>
      )}

      {/* TOP COST & TIMELINE CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center">
            <Clock className="w-4 h-4 text-blue-400 mr-1.5" /> Total Delivery Timeline
          </span>
          <h3 className="text-2xl font-black text-white mt-2">
            {data?.roadmap?.total_duration_weeks ?? 16} Weeks
          </h3>
          <p className="text-xs text-slate-400 mt-1">4 Sprints across 4 Delivery Phases</p>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center">
            <Users className="w-4 h-4 text-purple-400 mr-1.5" /> Engineering Effort
          </span>
          <h3 className="text-2xl font-black text-white mt-2">
            {data?.estimate?.total_estimated_hours ?? 1120} Hours
          </h3>
          <p className="text-xs text-slate-400 mt-1">Cross-functional team of 6 engineers</p>
        </div>

        <div className="p-6 rounded-2xl bg-emerald-950/20 border border-emerald-500/30">
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center">
            <DollarSign className="w-4 h-4 text-emerald-400 mr-1.5" /> Preliminary Estimated Cost
          </span>
          <h3 className="text-2xl font-black text-emerald-400 mt-2">
            ${(data?.estimate?.total_estimated_cost ?? 138500).toLocaleString()}
          </h3>
          <p className="text-xs text-slate-400 mt-1">Includes labor, cloud infra, & AI inference</p>
        </div>
      </div>

      {/* ROADMAP PHASES & TASKS */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-white flex items-center">
          <CalendarDays className="w-4 h-4 text-blue-400 mr-2" />
          Implementation Phases & WBS Tasks
        </h3>

        {phases.length === 0 ? (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 text-center">
            <CalendarDays className="w-8 h-8 text-slate-500 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-300">No implementation phases available</p>
            <p className="text-xs text-slate-500 mt-1 mb-4">Generate an AI-driven transformation roadmap and resource estimation.</p>
            <button
              onClick={handleRegenerate}
              disabled={isRegenerating}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow-lg inline-flex items-center space-x-2"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating ? 'animate-spin' : ''}`} />
              <span>{isRegenerating ? 'Generating...' : 'Generate Roadmap'}</span>
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {phases.map((phase, idx) => (
              <div key={idx} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-blue-600/30 text-blue-400 font-bold text-xs flex items-center justify-center">
                      0{idx + 1}
                    </span>
                    <h4 className="text-sm font-bold text-white">{phase.phase_name}</h4>
                  </div>
                  <span className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded bg-slate-800 text-slate-300">
                    Duration: {phase.duration_weeks} Weeks
                  </span>
                </div>

                <p className="text-xs text-slate-300 mb-4">{phase.objective}</p>

                {/* Tasks List */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {(phase.tasks || []).map((task, tIdx) => (
                    <div key={tIdx} className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs">
                      <div className="flex items-center justify-between font-semibold text-slate-200 mb-1">
                        <span>{typeof task === 'string' ? task : task.title}</span>
                        <span className="text-[10px] text-blue-400 font-mono">
                          {typeof task === 'object' ? task.duration : ''}
                        </span>
                      </div>
                      {typeof task === 'object' && (
                        <>
                          <p className="text-[11px] text-slate-400">Owner: <span className="text-slate-300 font-medium">{task.owner}</span></p>
                          <p className="text-[11px] text-emerald-400 mt-1">Deliverable: {task.deliverable}</p>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* STAFFING & HOURLY BREAKDOWN */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
        <h3 className="text-sm font-bold text-white mb-4 flex items-center">
          <Users className="w-4 h-4 text-purple-400 mr-2" />
          Role-Based Effort & Cost Breakdown
        </h3>

        {roles.length === 0 ? (
          <p className="text-xs text-slate-500 py-4 text-center">No role estimates available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                  <th className="pb-2">Role</th>
                  <th className="pb-2">Headcount</th>
                  <th className="pb-2">Estimated Hours</th>
                  <th className="pb-2">Blended Rate ($/hr)</th>
                  <th className="pb-2 text-right">Subtotal ($)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {roles.map((r, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-sans font-semibold text-slate-200">{r.role}</td>
                    <td className="py-2.5 text-slate-400">{r.headcount}</td>
                    <td className="py-2.5 text-blue-400">{r.hours} hrs</td>
                    <td className="py-2.5 text-slate-400">${r.rate_hourly}/hr</td>
                    <td className="py-2.5 text-right font-bold text-emerald-400">
                      ${(r.cost ?? (r.hours * r.rate_hourly)).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Disclaimer */}
        {data?.estimate?.disclaimer && (
          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 italic">
            ℹ️ {data.estimate.disclaimer}
          </div>
        )}
      </div>
    </div>
  );
};
export default PlanningPage;
