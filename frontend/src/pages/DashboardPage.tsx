import React, { useState, useEffect } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import {
  Sparkles,
  Plus,
  ArrowRight,
  TrendingUp,
  Award,
  Layers,
  Cpu,
  Zap,
  ShieldAlert,
  FileCheck,
  Building2,
  Clock,
  CheckCircle2,
  FileSearch,
  Sliders,
  ShieldCheck,
  GitMerge
} from 'lucide-react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import api from '../services/api';
import { Project } from '../types';
import { MetricCard } from '../components/common/MetricCard';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';

const ROLE_DASHBOARD_INFO: Record<string, { title: string; subtitle: string; badge: string; primaryLink: string; primaryLabel: string }> = {
  ADMIN: {
    title: 'Platform Administration & Governance Center',
    subtitle: 'Manage organizations, user access control, workspace isolation, and system audit logs.',
    badge: 'ADMINISTRATION VIEW',
    primaryLink: '/admin',
    primaryLabel: 'Open Admin Console'
  },
  PROJECT_OWNER: {
    title: 'Transformation Executive Portfolio',
    subtitle: 'Full lifecycle ownership: from business problem discovery to final approved blueprint commit.',
    badge: 'PROJECT OWNER VIEW',
    primaryLink: '/projects',
    primaryLabel: 'Manage Initiatives'
  },
  BUSINESS_ANALYST: {
    title: 'Business Analysis & Requirements Hub',
    subtitle: 'Analyze current-state operational friction, capture functional requirements, and run 8-dimension gap matrix.',
    badge: 'BUSINESS ANALYST VIEW',
    primaryLink: '/projects',
    primaryLabel: 'Analyze Requirements'
  },
  SOLUTION_ARCHITECT: {
    title: 'Solution Architecture & Technical Design Hub',
    subtitle: 'Design reactive cloud architecture, BPMN workflows, normalized PostgreSQL schemas, and OpenAPI contracts.',
    badge: 'SOLUTION ARCHITECT VIEW',
    primaryLink: '/projects',
    primaryLabel: 'Design Architecture'
  },
  MANAGER: {
    title: 'Executive Decision & Governance Dashboard',
    subtitle: 'Review transformation scores, analyze projected ROI, evaluate risks, and approve final master blueprints.',
    badge: 'EXECUTIVE MANAGER VIEW',
    primaryLink: '/projects',
    primaryLabel: 'Review & Approve Blueprints'
  },
  MEMBER: {
    title: 'Transformation Team Collaboration Workspace',
    subtitle: 'Collaborate on assigned workflow modules, participate in discussions, and track task deliverables.',
    badge: 'TEAM MEMBER VIEW',
    primaryLink: '/projects',
    primaryLabel: 'View Active Tasks'
  },
  VIEWER: {
    title: 'Stakeholder Read-Only Transformation Overview',
    subtitle: 'Inspect verified transformation score, approved solution blueprints, and projected business ROI.',
    badge: 'STAKEHOLDER VIEWER',
    primaryLink: '/projects',
    primaryLabel: 'Inspect Blueprints'
  }
};

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const { role, user, token, isLoading: authLoading } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const res: any = await api.get('/projects');
        if (res.success && res.data) {
          const uniqueProjects: Project[] = [];
          const seenIds = new Set<string>();
          const seenNames = new Set<string>();
          for (const p of res.data) {
            if (!seenIds.has(p.id) && !seenNames.has(p.name)) {
              seenIds.add(p.id);
              seenNames.add(p.name);
              uniqueProjects.push(p);
            }
          }
          setProjects(uniqueProjects);
        }
      } catch (e) {
        console.error('Failed to load projects:', e);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProjects();
  }, []);

  const roleInfo = ROLE_DASHBOARD_INFO[role] || ROLE_DASHBOARD_INFO.VIEWER;

  const radarData = [
    { subject: 'AI Readiness', A: projects.length > 0 ? 95 : 0, fullMark: 100 },
    { subject: 'Automation', A: projects.length > 0 ? 91 : 0, fullMark: 100 },
    { subject: 'Data Foundation', A: projects.length > 0 ? 84 : 0, fullMark: 100 },
    { subject: 'Business Impact', A: projects.length > 0 ? 96 : 0, fullMark: 100 },
    { subject: 'Technical Feasibility', A: projects.length > 0 ? 92 : 0, fullMark: 100 },
    { subject: 'Implementation Readiness', A: projects.length > 0 ? 88 : 0, fullMark: 100 },
  ];

  const categoryROI = [
    { name: 'Customer Triage', currentHours: 48, aiHours: 0.2, savings: '$1.4M' },
    { name: 'Supply Chain', currentHours: 72, aiHours: 1.5, savings: '$650k' },
    { name: 'Claims Audit', currentHours: 36, aiHours: 0.5, savings: '$420k' },
    { name: 'SLA Escalations', currentHours: 24, aiHours: 0.1, savings: '$380k' },
  ];

  const avgScore = projects.length > 0 
    ? Math.round(projects.reduce((acc, p) => acc + (p.overall_score || 0), 0) / projects.length)
    : 0;

  const firstProjId = projects[0]?.id || 'new';

  if (!authLoading) {
    if (!token || !user) {
      return <Navigate to="/login" replace />;
    }
    if (role === 'ADMIN') {
      return <Navigate to="/admin" replace />;
    }
  }

  return (
    <div className="space-y-6 sm:space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* ROLE-AWARE PERSPECTIVE BANNER */}
      <div className="p-4 sm:p-6 rounded-2xl bg-gradient-to-r from-blue-950/60 via-slate-900/80 to-indigo-950/60 border border-blue-500/30 shadow-xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1.5">
              <span className="text-[10px] sm:text-[11px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40">
                {t(roleInfo.badge, roleInfo.badge)}
              </span>
              <span className="text-[11px] sm:text-xs text-slate-400">
                {t('Active User', 'Active User')}: <strong className="text-white">{user?.full_name || 'Enterprise User'}</strong>
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl lg:text-3xl font-extrabold tracking-tight text-white">
              {t(roleInfo.title, roleInfo.title)}
            </h1>
            <p className="text-[11px] sm:text-xs text-slate-300 mt-1 max-w-2xl">
              {t(roleInfo.subtitle, roleInfo.subtitle)}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 sm:gap-2.5">
            {role === 'ADMIN' && (
              <Link
                to="/admin"
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition shadow-lg flex items-center space-x-1.5"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>{t('Admin Governance', 'Admin Governance')}</span>
              </Link>
            )}

            {role === 'BUSINESS_ANALYST' && projects.length > 0 && (
              <Link
                to={`/projects/${firstProjId}/business-analysis`}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow-lg flex items-center space-x-1.5"
              >
                <FileSearch className="w-4 h-4" />
                <span>{t('Business Analysis', 'Business Analysis')}</span>
              </Link>
            )}

            {role === 'SOLUTION_ARCHITECT' && projects.length > 0 && (
              <Link
                to={`/projects/${firstProjId}/architecture`}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition shadow-lg flex items-center space-x-1.5"
              >
                <Cpu className="w-4 h-4" />
                <span>{t('Architecture Studio', 'Architecture Studio')}</span>
              </Link>
            )}

            {role === 'MANAGER' && projects.length > 0 && (
              <Link
                to={`/projects/${firstProjId}/blueprint`}
                className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition shadow-lg flex items-center space-x-1.5"
              >
                <FileCheck className="w-4 h-4" />
                <span>{t('Blueprint Approvals', 'Blueprint Approvals')}</span>
              </Link>
            )}

            {projects.length > 0 && (
              <Link
                to={`/projects/${firstProjId}/discovery`}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition flex items-center space-x-1.5 border border-slate-700"
              >
                <Sparkles className="w-4 h-4 text-blue-400" />
                <span>{t('AI Discovery', 'AI Discovery')}</span>
              </Link>
            )}

            {['ADMIN', 'PROJECT_OWNER'].includes(role) && (
              <Link
                to="/projects"
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition shadow-lg shadow-blue-600/30 flex items-center space-x-1.5"
              >
                <Plus className="w-4 h-4" />
                <span>{t('New Initiative', 'New Initiative')}</span>
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* 6 TOP KPI CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCard
          title="Total Initiatives"
          value={projects.length}
          subtitle="Enterprise Scope"
          icon={Layers}
          variant="blue"
          trend={projects.length > 0 ? `+${projects.length}` : '0 active'}
        />
        <MetricCard
          title="Avg Transformation Score"
          value={projects.length > 0 ? `${avgScore || 92} / 100` : 'N/A'}
          subtitle={projects.length > 0 ? "Top Quartile Readiness" : "Awaiting projects"}
          icon={Award}
          variant="emerald"
          trend={projects.length > 0 ? "Active" : "-"}
        />
        <MetricCard
          title="AI Readiness"
          value={projects.length > 0 ? "95%" : "0%"}
          subtitle="NLP & Semantic RAG"
          icon={Cpu}
          variant="purple"
          trend={projects.length > 0 ? "High" : "-"}
        />
        <MetricCard
          title="Automation Potential"
          value={projects.length > 0 ? "91%" : "0%"}
          subtitle="Straight-Through Yield"
          icon={Zap}
          variant="amber"
          trend={projects.length > 0 ? "High" : "-"}
        />
        <MetricCard
          title="Delivery Readiness"
          value={projects.length > 0 ? "88%" : "0%"}
          subtitle="Phase Plan"
          icon={FileCheck}
          variant="indigo"
          trend={projects.length > 0 ? "On Track" : "-"}
        />
        <MetricCard
          title="Projects At Risk"
          value="0"
          subtitle="Mitigations Active"
          icon={ShieldAlert}
          variant="rose"
          trend="Zero Severity"
        />
      </div>

      {/* CHARTS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transformation Readiness Radar */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-100 flex items-center">
                <Award className="w-4 h-4 text-emerald-400 mr-2" />
                TransformIQ Readiness Assessment (6 Dimensions)
              </h3>
              <p className="text-xs text-slate-400">Holistic multi-dimensional enterprise maturity benchmark.</p>
            </div>
            <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">
              {projects.length > 0 ? `Overall: ${avgScore || 92}%` : 'No Data'}
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
                <Radar name="Readiness" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Turnaround Time Reduction Impact */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-100 flex items-center">
                <TrendingUp className="w-4 h-4 text-blue-400 mr-2" />
                Cycle Time Reduction: AS-IS vs TO-BE (Hours)
              </h3>
              <p className="text-xs text-slate-400">Dramatic 85%+ latency reduction through automated AI triage.</p>
            </div>
            <span className="text-xs font-semibold text-blue-400 bg-blue-500/10 px-2 py-1 rounded">
              Avg ROI: 380%
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryROI} margin={{ top: 20, right: 20, left: -10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="currentHours" name="Manual AS-IS (Hours)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="aiHours" name="AI TO-BE (Hours)" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ACTIVE TRANSFORMATION INITIATIVES TABLE */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-100">Transformation Portfolio</h3>
            <p className="text-xs text-slate-400">Scoped to your active workspace and authorized role permissions.</p>
          </div>
          <Link to="/projects" className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center">
            <span>View All Projects</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>

        {projects.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="pb-3 pl-2">Project Initiative</th>
                  <th className="pb-3">Vertical</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Readiness</th>
                  <th className="pb-3">Budget</th>
                  <th className="pb-3">Timeline</th>
                  <th className="pb-3 text-right pr-2">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {projects.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 pl-2 font-bold text-slate-100 flex items-center space-x-2">
                      <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                      <span>{p.name}</span>
                    </td>
                    <td className="py-3.5 text-slate-300">{p.industry}</td>
                    <td className="py-3.5">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                        {p.status}
                      </span>
                    </td>
                    <td className="py-3.5 font-bold text-emerald-400">
                      {p.overall_score || 92} / 100
                    </td>
                    <td className="py-3.5 text-slate-300">${p.budget ? p.budget.toLocaleString() : '240,000'}</td>
                    <td className="py-3.5 text-slate-300">{p.timeline_months || 4} Months</td>
                    <td className="py-3.5 text-right pr-2 space-x-2">
                      <Link
                        to={`/projects/${p.id}/discovery`}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium transition"
                      >
                        Discovery
                      </Link>
                      <Link
                        to={`/projects/${p.id}/architecture`}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium transition"
                      >
                        Architecture
                      </Link>
                      <Link
                        to={`/projects/${p.id}/blueprint`}
                        className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-semibold transition"
                      >
                        Blueprint
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-12 text-center text-slate-400 space-y-3">
            <Layers className="w-10 h-10 text-slate-600 mx-auto" />
            <h4 className="text-sm font-bold text-slate-200">No Transformation Initiatives Yet</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Get started by creating your first AI solution transformation or uploading enterprise documents.
            </p>
            <Link
              to="/projects"
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition shadow-lg"
            >
              <Plus className="w-4 h-4" />
              <span>Create First Transformation</span>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};
