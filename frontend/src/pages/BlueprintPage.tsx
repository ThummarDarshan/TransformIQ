import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FileCheck,
  Download,
  CheckCircle2,
  XCircle,
  FileText,
  Layers,
  Cpu,
  GitMerge,
  Database,
  Code2,
  Layout,
  CalendarDays,
  DollarSign,
  ShieldAlert,
  Award,
  Sparkles,
  Share2,
  Printer,
  ChevronRight,
  Flame
} from 'lucide-react';
import api from '../services/api';
import { MasterBlueprintData } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';
import { ApprovalBar } from '../components/common/ApprovalBar';
import { LiveDeploymentHub } from '../components/blueprint/LiveDeploymentHub';
import { useLanguage } from '../contexts/LanguageContext';

export const BlueprintPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const { t } = useLanguage();
  const [data, setData] = useState<MasterBlueprintData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isApproving, setIsApproving] = useState(false);
  const [downloadingFormat, setDownloadingFormat] = useState<string | null>(null);

  const fetchBlueprint = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/blueprints/project/${projectId}`);
      if (res.success && res.data) {
        setData(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (action: 'APPROVE' | 'REJECT') => {
    if (!projectId) return;
    setIsApproving(true);
    try {
      const res: any = await api.post(`/blueprints/project/${projectId}/approve`, {
        action,
        comments: action === 'APPROVE' ? 'Approved for Phase 1 Sprint Implementation.' : 'Revision requested.'
      });
      if (res.success) {
        fetchBlueprint();
      }
    } catch (e: any) {
      console.error('Approve blueprint error:', e);
      alert(e?.detail || e?.message || 'Failed to update approval status.');
    } finally {
      setIsApproving(false);
    }
  };

  const handleDownload = async (format: 'pdf' | 'docx' | 'xlsx' | 'pptx') => {
    if (!projectId) return;
    setDownloadingFormat(format);
    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const cleanBase = baseUrl.endsWith('/api/v1') ? baseUrl : `${baseUrl.replace(/\/+$/, '')}/api/v1`;
      const token = localStorage.getItem('transformiq_token');
      
      const downloadUrl = `${cleanBase}/exports/project/${projectId}/download?format=${format}${token ? `&token=${encodeURIComponent(token)}` : ''}`;

      const res = await fetch(downloadUrl, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Export download failed (${res.status}): ${errText}`);
      }

      const blob = await res.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      const safeName = data?.project_name ? data.project_name.replace(/[^a-zA-Z0-9_-]/g, '_') : 'Blueprint';
      link.setAttribute('download', `${safeName}_Blueprint.${format}`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(objectUrl);
    } catch (e: any) {
      console.error('Download blueprint error:', e);
      alert(e?.message || 'Failed to download blueprint.');
    } finally {
      setTimeout(() => setDownloadingFormat(null), 1000);
    }
  };

  useEffect(() => {
    fetchBlueprint();
  }, [projectId]);

  if (isLoading) {
    return <LoadingScreen message="Assembling unified 24-dimension Implementation-Ready Master Blueprint..." />;
  }

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto pb-16">
      {/* EXPORT ACTION TOOLBAR */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 backdrop-blur-xl shadow-xl relative z-10">
        <div className="space-y-1">
          <div className="flex items-center space-x-2 flex-wrap gap-y-1">
            <span className="text-[10px] font-mono font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wider">
              {t('final_blueprint', 'STEP 13 • FINAL BLUEPRINT')}
            </span>
            <h1 className="text-lg font-bold text-white tracking-tight">{t('Implementation-Ready Solution Blueprint', 'Implementation-Ready Solution Blueprint')}</h1>
          </div>
          <p className="text-xs text-slate-400">
            {data?.project_name} • {data?.industry} • {t('Generated', 'Generated')}: {data?.generated_at}
          </p>
        </div>

        {/* Real Export Buttons */}
        <div className="grid grid-cols-2 sm:flex sm:items-center gap-2 shrink-0">
          <button
            onClick={() => handleDownload('pdf')}
            disabled={!!downloadingFormat}
            className="px-3.5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition shadow-lg shadow-rose-600/20 flex items-center justify-center space-x-1.5 disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{downloadingFormat === 'pdf' ? t('Generating...', 'Generating...') : t('export_pdf', 'Export PDF')}</span>
          </button>
          <button
            onClick={() => handleDownload('docx')}
            disabled={!!downloadingFormat}
            className="px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition shadow-lg shadow-blue-600/20 flex items-center justify-center space-x-1.5 disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{downloadingFormat === 'docx' ? t('Generating...', 'Generating...') : t('Export DOCX', 'Export DOCX')}</span>
          </button>
          <button
            onClick={() => handleDownload('xlsx')}
            disabled={!!downloadingFormat}
            className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow-lg shadow-emerald-600/20 flex items-center justify-center space-x-1.5 disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{downloadingFormat === 'xlsx' ? t('Generating...', 'Generating...') : t('Export XLSX', 'Export XLSX')}</span>
          </button>
          <button
            onClick={() => handleDownload('pptx')}
            disabled={!!downloadingFormat}
            className="px-3.5 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold transition shadow-lg shadow-amber-600/20 flex items-center justify-center space-x-1.5 disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{downloadingFormat === 'pptx' ? t('Generating...', 'Generating...') : t('Export PPTX', 'Export PPTX')}</span>
          </button>
        </div>
      </div>

      {/* HUMAN IN THE LOOP APPROVAL BAR */}
      <ApprovalBar
        status={data?.approval_status || 'UNDER_REVIEW'}
        reviewedBy={data?.reviewed_by}
        decisionDate={data?.decision_date}
        onApprove={() => handleApprove('APPROVE')}
        onReject={() => handleApprove('REJECT')}
        isSubmitting={isApproving}
      />

      {/* SECTION 1: EXECUTIVE COVER CARD */}
      <div className="p-8 rounded-3xl bg-gradient-to-br from-blue-950/60 via-slate-900/90 to-emerald-950/50 border border-blue-500/30 backdrop-blur-xl shadow-2xl relative overflow-hidden">
        <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-widest text-blue-400 mb-2">
          <Flame className="w-4 h-4 text-amber-400" />
          <span>TransformIQ Enterprise Blueprint • Chaos2Commit Edition</span>
        </div>

        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-2">
          {data?.project_name}
        </h2>
        <p className="text-sm font-semibold text-emerald-400 mb-6">{data?.recommended_solution.tagline}</p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-xs mb-6">
          <div>
            <span className="text-slate-500 block">Readiness Score</span>
            <span className="text-lg font-black text-emerald-400">{data?.transformation_score.overall_score}/100</span>
          </div>
          <div>
            <span className="text-slate-500 block">Estimated 12M ROI</span>
            <span className="text-lg font-black text-white">{data?.recommended_solution.expected_roi}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Delivery Duration</span>
            <span className="text-lg font-black text-blue-400">{data?.roadmap_summary.total_duration_weeks} Weeks</span>
          </div>
          <div>
            <span className="text-slate-500 block">Estimated Budget</span>
            <span className="text-lg font-black text-white">${data?.estimate_summary.total_cost.toLocaleString()}</span>
          </div>
        </div>

        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          {data?.executive_summary}
        </p>
      </div>

      {/* SECTION 2: TRANSFORMATION SCORECARD */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
        <h3 className="text-base font-bold text-white mb-4 flex items-center">
          <Award className="w-4 h-4 text-emerald-400 mr-2" />
          1. Digital Transformation Scorecard
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { label: 'AI Readiness', val: data?.transformation_score.ai_readiness },
            { label: 'Automation', val: data?.transformation_score.automation_potential },
            { label: 'Data Readiness', val: data?.transformation_score.data_readiness },
            { label: 'Business Impact', val: data?.transformation_score.business_impact },
            { label: 'Tech Feasibility', val: data?.transformation_score.technical_feasibility },
            { label: 'Implementation', val: data?.transformation_score.implementation_readiness },
          ].map((sc, i) => (
            <div key={i} className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 text-center">
              <span className="text-[10px] uppercase font-bold text-slate-400">{sc.label}</span>
              <h4 className="text-xl font-black text-emerald-400 mt-1">{sc.val}%</h4>
            </div>
          ))}
        </div>
      </div>

      {/* SECTION 3: GAP MATRIX HIGHLIGHTS */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
        <h3 className="text-base font-bold text-white mb-4 flex items-center">
          <Layers className="w-4 h-4 text-purple-400 mr-2" />
          2. Identified Gaps & Remediation Actions
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data?.key_gaps.map((g, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-purple-300 uppercase text-[10px]">{g.category}</span>
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300">{g.severity}</span>
              </div>
              <h4 className="font-bold text-white">{g.title}</h4>
              <p className="text-slate-400 text-[11px]"><b className="text-slate-300">Remedy:</b> {g.recommended_action}</p>
            </div>
          ))}
        </div>
      </div>

      {/* SECTION 4: ARCHITECTURE & BPMN WORKFLOW SUMMARY */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center">
            <Cpu className="w-4 h-4 text-blue-400 mr-2" />
            3. Solution Architecture Spec
          </h3>
          <p className="text-xs text-slate-300 mb-3">
            {data?.architecture_summary.components_count} microservice components across{' '}
            {data?.architecture_summary.layers.length} tiers.
          </p>
          <div className="flex flex-wrap gap-1.5">
            {data?.architecture_summary.layers.map((l, i) => (
              <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {l}
              </span>
            ))}
          </div>
          <Link
            to={`/projects/${projectId}/architecture`}
            className="text-xs text-blue-400 font-semibold hover:underline mt-4 inline-flex items-center"
          >
            <span>Open React Flow Canvas</span>
            <ChevronRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center">
            <GitMerge className="w-4 h-4 text-purple-400 mr-2" />
            4. BPMN Workflow Optimization
          </h3>
          <div className="space-y-1.5 text-xs text-slate-300 mb-3">
            <p>Cycle Time: <span className="text-rose-400">{data?.process_summary.cycle_time_current}</span> → <span className="text-emerald-400 font-bold">{data?.process_summary.cycle_time_projected}</span></p>
            <p>Efficiency Gain: <span className="text-emerald-400 font-bold">{data?.process_summary.efficiency_gain}</span></p>
          </div>
          <Link
            to={`/projects/${projectId}/process`}
            className="text-xs text-purple-400 font-semibold hover:underline mt-2 inline-flex items-center"
          >
            <span>Open BPMN Workflow Canvas</span>
            <ChevronRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>
      </div>

      {/* SECTION 5: IMPLEMENTATION ROADMAP & BUDGET */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
        <h3 className="text-base font-bold text-white mb-4 flex items-center">
          <CalendarDays className="w-4 h-4 text-emerald-400 mr-2" />
          5. 16-Week Phase Plan & Estimated Investment
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60">
            <span className="text-slate-500 block mb-1">Duration</span>
            <h4 className="text-lg font-bold text-white">{data?.roadmap_summary.total_duration_weeks} Weeks (4 Phases)</h4>
            <span className="text-[11px] text-slate-400">Discovery, Core AI, UI, Hardening</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60">
            <span className="text-slate-500 block mb-1">Engineering Effort</span>
            <h4 className="text-lg font-bold text-white">{data?.estimate_summary.total_hours} Hours</h4>
            <span className="text-[11px] text-slate-400">6 Specialized Engineering Roles</span>
          </div>

          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30">
            <span className="text-emerald-400 font-semibold block mb-1">Total Estimated Cost</span>
            <h4 className="text-lg font-black text-emerald-400">${data?.estimate_summary.total_cost.toLocaleString()} USD</h4>
            <span className="text-[11px] text-emerald-400/80">Labor + Cloud Infra + AI APIs</span>
          </div>
        </div>
      </div>

      {/* SECTION 6: ONE-CLICK CLOUD DEPLOYMENT & LIVE SYSTEM SANDBOX */}
      {projectId && (
        <LiveDeploymentHub
          projectId={projectId}
          data={data}
          onRegenerateRequest={fetchBlueprint}
        />
      )}
    </div>
  );
};
