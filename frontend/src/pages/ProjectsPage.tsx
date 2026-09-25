import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Plus,
  Layers,
  Upload,
  Globe,
  ArrowRight,
  Sparkles,
  Building2,
  Calendar,
  DollarSign,
  FileText,
  X,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import api from '../services/api';
import { Project } from '../types';
import { useLanguage } from '../contexts/LanguageContext';

export const ProjectsPage: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form fields
  const [name, setName] = useState('');
  const [industry, setIndustry] = useState('E-Commerce & Retail');
  const [orgSize, setOrgSize] = useState('Enterprise (1000+)');
  const [objective, setObjective] = useState('');
  const [problem, setProblem] = useState('');
  const [systems, setSystems] = useState('');
  const [constraints, setConstraints] = useState('');
  const [budget, setBudget] = useState(150000);
  const [timeline, setTimeline] = useState(4);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [referenceUrl, setReferenceUrl] = useState('');

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
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      // 1. Fetch workspaces to attach workspace_id
      const wsRes: any = await api.get('/workspaces');
      const workspaceId = wsRes?.data?.[0]?.id || 'default-ws';

      // 2. Create Project
      const createRes: any = await api.post('/projects', {
        name,
        workspace_id: workspaceId,
        industry,
        organization_size: orgSize,
        business_objective: objective,
        business_problem: problem,
        current_systems: systems,
        constraints,
        budget: Number(budget),
        timeline_months: Number(timeline)
      });

      if (createRes.success && createRes.data) {
        const newProjId = createRes.data.id;

        // 3. Upload file if provided
        if (uploadedFile) {
          const formData = new FormData();
          formData.append('file', uploadedFile);
          try {
            await api.post(`/documents/upload/${newProjId}`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            });
          } catch (uploadErr) {
            console.warn('Document upload warning:', uploadErr);
          }
        }

        // 4. Ingest URL reference if provided
        if (referenceUrl.trim()) {
          try {
            await api.post('/documents/ingest-url', {
              project_id: newProjId,
              url: referenceUrl.trim()
            });
          } catch (urlErr) {
            console.warn('URL ingestion warning:', urlErr);
          }
        }

        setIsModalOpen(false);
        navigate(`/projects/${newProjId}/discovery`);
      }
    } catch (err: any) {
      setError(err?.detail || err?.message || 'Failed to create project.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white">{t('transformation_portfolio', 'Transformation Portfolio')}</h1>
          <p className="text-xs text-slate-400 mt-0.5">{t('Manage and launch AI-driven enterprise transformation initiatives.', 'Manage and launch AI-driven enterprise transformation initiatives.')}</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl transition shadow-lg flex items-center space-x-2 w-fit"
        >
          <Plus className="w-4 h-4" />
          <span>{t('new_transformation_initiative', 'New Transformation Initiative')}</span>
        </button>
      </div>

      {/* PROJECTS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((p) => (
          <div key={p.id} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between group">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">
                  {t(p.industry, p.industry)}
                </span>
                <span className="text-xs font-bold text-emerald-400">
                  {t('Score', 'Score')}: {p.overall_score || 0}/100
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-100 group-hover:text-blue-400 transition mb-2">
                {p.name}
              </h3>
              <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed mb-4">
                {p.business_problem || p.description || 'Enterprise transformation initiative.'}
              </p>
            </div>

            <div className="pt-4 border-t border-slate-800/80">
              <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 mb-4">
                <div>
                  <span className="block text-slate-500">{t('Budget', 'Budget')}</span>
                  <span className="font-semibold text-slate-200">${p.budget ? p.budget.toLocaleString() : '150,000'}</span>
                </div>
                <div>
                  <span className="block text-slate-500">{t('Timeline', 'Timeline')}</span>
                  <span className="font-semibold text-slate-200">{p.timeline_months || 4} {t('Months', 'Months')}</span>
                </div>
              </div>

              <div className="flex items-center justify-between gap-2">
                <Link
                  to={`/projects/${p.id}/discovery`}
                  className="flex-1 py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold text-center transition"
                >
                  {t('AI Discovery', 'AI Discovery')}
                </Link>
                <Link
                  to={`/projects/${p.id}/blueprint`}
                  className="flex-1 py-1.5 px-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold text-center transition flex items-center justify-center space-x-1"
                >
                  <span>{t('final_blueprint', 'Blueprint')}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        ))}

        {projects.length === 0 && !isLoading && (
          <div className="col-span-full py-16 text-center text-slate-400 p-8 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3">
            <Layers className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-base font-bold text-white">{t('No Transformation Initiatives Yet', 'No Transformation Initiatives Yet')}</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              {t('Create your first enterprise transformation project by providing your business challenge or uploading BRD/SOP documents.', 'Create your first enterprise transformation project by providing your business challenge or uploading BRD/SOP documents.')}
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition shadow-lg mt-2"
            >
              <Plus className="w-4 h-4" />
              <span>{t('new_transformation_initiative', 'New Transformation Initiative')}</span>
            </button>
          </div>
        )}
      </div>

      {/* CREATE PROJECT MODAL */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800/60"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2.5 mb-5">
              <div className="p-2 rounded-lg bg-blue-600/20 text-blue-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">{t('create_transformation_initiative', 'Create Transformation Initiative')}</h3>
                <p className="text-xs text-slate-400">{t('Ingest business problem & documents into AI context engine', 'Ingest business problem & documents into AI context engine')}</p>
              </div>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleCreateProject} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">{t('project_name_star', 'Project Name *')}</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Healthcare Claims Automation & Triage"
                  className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">{t('Industry Vertical', 'Industry Vertical')}</label>
                  <select
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="E-Commerce & Retail">E-Commerce & Retail</option>
                    <option value="Healthcare & Insurance">Healthcare & Insurance</option>
                    <option value="Fintech & Banking">Fintech & Banking</option>
                    <option value="Supply Chain & Logistics">Supply Chain & Logistics</option>
                    <option value="Manufacturing & Operations">Manufacturing & Operations</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">{t('Organization Scale', 'Organization Size')}</label>
                  <select
                    value={orgSize}
                    onChange={(e) => setOrgSize(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Enterprise (1000+)">Enterprise (1000+)</option>
                    <option value="Mid-Market (250-1000)">Mid-Market (250-1000)</option>
                    <option value="Growth Startup (50-250)">Growth Startup (50-250)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">{t('business_problem_description', 'Business Problem / Chaos Description *')}</label>
                <textarea
                  rows={3}
                  required
                  value={problem}
                  onChange={(e) => setProblem(e.target.value)}
                  placeholder="Describe current operational bottlenecks, manual delays, systems in use, and pain points..."
                  className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">{t('Business Objective & Expected Outcome', 'Business Objective & Expected Outcome')}</label>
                <input
                  type="text"
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  placeholder="e.g. Automate 80% straight-through processing and reduce turnaround from 48h to 15m."
                  className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Upload BRD / SOP Document or Paste Web URL */}
              <div className="p-4 rounded-xl bg-slate-800/40 border border-dashed border-slate-700 space-y-3">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1 flex items-center">
                    <Upload className="w-4 h-4 text-blue-400 mr-1.5" />
                    {t('upload_enterprise_document', 'Upload Enterprise Document (PDF, Word, PPTX, TXT)')}
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.docx,.pptx,.txt"
                    onChange={(e) => setUploadedFile(e.target.files?.[0] || null)}
                    className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer"
                  />
                  {uploadedFile && (
                    <p className="text-[11px] text-emerald-400 mt-1">
                      ✓ Attached: {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
                    </p>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-800">
                  <label className="block font-semibold text-slate-300 mb-1 flex items-center">
                    <Globe className="w-4 h-4 text-emerald-400 mr-1.5" />
                    {t('reference_web_url', 'Reference Web / BRD URL (Website, Online Spec, Documentation)')}
                  </label>
                  <input
                    type="url"
                    value={referenceUrl}
                    onChange={(e) => setReferenceUrl(e.target.value)}
                    placeholder="e.g. https://enterprise.com/brd-doc or http://..."
                    className="w-full px-3 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-xs"
                  />
                  {referenceUrl && (
                    <p className="text-[11px] text-emerald-400 mt-1">
                      ✓ Web URL set for AI RAG Scraping: {referenceUrl}
                    </p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">{t('target_budget', 'Target Budget ($ USD)')}</label>
                  <input
                    type="number"
                    value={budget}
                    onChange={(e) => setBudget(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-white"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">{t('timeline_months', 'Timeline (Months)')}</label>
                  <input
                    type="number"
                    value={timeline}
                    onChange={(e) => setTimeline(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-white"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold"
                >
                  {t('cancel', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-emerald-500 hover:from-blue-500 hover:to-emerald-400 text-white font-bold shadow-lg transition disabled:opacity-50"
                >
                  {isSubmitting ? t('Synthesizing...', 'Synthesizing...') : t('initialize_ai_discovery', 'Initialize AI Discovery')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
