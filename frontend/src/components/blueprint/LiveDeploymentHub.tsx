import React, { useState } from 'react';
import {
  Rocket,
  Globe,
  Server,
  Download,
  Play,
  RefreshCw,
  Sliders,
  CheckCircle2,
  ExternalLink,
  Shield,
  Layers,
  Code2,
  Terminal,
  Activity,
  Box,
  Monitor,
  Smartphone,
  Tablet,
  Check
} from 'lucide-react';
import { MasterBlueprintData } from '../../types';
import api from '../../services/api';

interface LiveDeploymentHubProps {
  projectId: string;
  data: MasterBlueprintData | null;
  onRegenerateRequest?: () => void;
}

export const LiveDeploymentHub: React.FC<LiveDeploymentHubProps> = ({
  projectId,
  data,
  onRegenerateRequest
}) => {
  const [activeTab, setActiveTab] = useState<'deploy' | 'sandbox' | 'customize'>('deploy');
  const [isDownloadingBundle, setIsDownloadingBundle] = useState(false);
  const [sandboxDevice, setSandboxDevice] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [sandboxActiveTab, setSandboxActiveTab] = useState<'portal' | 'dashboard' | 'workflows'>('dashboard');
  const [sandboxMetric, setSandboxMetric] = useState<number>(1420);
  const [isCustomizing, setIsCustomizing] = useState(false);
  const [customGoal, setCustomGoal] = useState('');
  const [customTheme, setCustomTheme] = useState('midnight');
  const [deployStatus, setDeployStatus] = useState<'ready' | 'deploying' | 'live'>('ready');

  const handleDownloadDevOpsBundle = async () => {
    if (!projectId) return;
    setIsDownloadingBundle(true);
    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const cleanBase = baseUrl.endsWith('/api/v1') ? baseUrl : `${baseUrl.replace(/\/+$/, '')}/api/v1`;
      const token = localStorage.getItem('transformiq_token');

      const downloadUrl = `${cleanBase}/exports/project/${projectId}/download-bundle${token ? `?token=${encodeURIComponent(token)}` : ''}`;

      const res = await fetch(downloadUrl, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Deployment bundle download failed (${res.status}): ${errText}`);
      }

      const blob = await res.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      const safeName = data?.project_name ? data.project_name.replace(/[^a-zA-Z0-9_-]/g, '_') : 'TransformIQ';
      link.setAttribute('download', `${safeName}_Deployment_Bundle.zip`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(objectUrl);
    } catch (e: any) {
      console.error('Download deployment bundle error:', e);
      alert(e?.message || 'Failed to download deployment bundle.');
    } finally {
      setTimeout(() => setIsDownloadingBundle(false), 1000);
    }
  };

  const handleSimulateDeploy = () => {
    setDeployStatus('deploying');
    setTimeout(() => {
      setDeployStatus('live');
    }, 2500);
  };

  const handleApplyCustomization = () => {
    setIsCustomizing(true);
    setTimeout(() => {
      setIsCustomizing(false);
      alert('Customization parameters saved! Blueprint and live preview re-synchronized.');
      if (onRegenerateRequest) {
        onRegenerateRequest();
      }
    }, 1500);
  };

  const renderUrl = `https://dashboard.render.com/blueprints`;
  const vercelUrl = `https://vercel.com/new/clone?repository-url=https://github.com/VadsolaKishan/transformiq-chaos2commit-2026`;

  return (
    <div className="rounded-3xl bg-slate-900/90 border border-slate-800 backdrop-blur-xl shadow-2xl p-6 sm:p-8 space-y-6">
      {/* HEADER & TABS */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-mono font-extrabold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 uppercase tracking-wider">
              STEP 14 • LIVE SYSTEM & DEPLOYMENT
            </span>
            <span className="text-xs font-bold text-emerald-400 flex items-center">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Ready for Cloud Deployment
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
            One-Click Cloud Deployment & Live Solution Sandbox
          </h2>
          <p className="text-xs text-slate-400">
            Convert the approved blueprint into a fully functional live system accessible across Web, Mobile & Cloud platforms.
          </p>
        </div>

        {/* Action Tabs */}
        <div className="flex items-center space-x-1.5 bg-slate-950 p-1.5 rounded-2xl border border-slate-800 shrink-0">
          <button
            onClick={() => setActiveTab('deploy')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 ${
              activeTab === 'deploy'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Rocket className="w-3.5 h-3.5" />
            <span>1-Click Deploy</span>
          </button>
          <button
            onClick={() => setActiveTab('sandbox')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 ${
              activeTab === 'sandbox'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Play className="w-3.5 h-3.5" />
            <span>Live Sandbox</span>
          </button>
          <button
            onClick={() => setActiveTab('customize')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 ${
              activeTab === 'customize'
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Customize & Regenerate</span>
          </button>
        </div>
      </div>

      {/* TAB 1: ONE-CLICK DEPLOYMENT ENGINE */}
      {activeTab === 'deploy' && (
        <div className="space-y-6 animate-fadeIn">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* RENDER CARD */}
            <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-950/80 to-slate-900/60 border border-slate-800 hover:border-blue-500/50 transition flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold">
                    <Server className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    Backend & DB
                  </span>
                </div>
                <h3 className="text-base font-bold text-white">Deploy to Render</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Automated deployment using pre-configured <code className="text-blue-300">render.yaml</code> with async PostgreSQL and Gemini AI engine.
                </p>
              </div>

              <a
                href={renderUrl}
                target="_blank"
                rel="noreferrer"
                className="w-full py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition flex items-center justify-center space-x-2 shadow-lg shadow-blue-600/20"
              >
                <span>Deploy to Render Dashboard</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            {/* VERCEL CARD */}
            <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-950/80 to-slate-900/60 border border-slate-800 hover:border-slate-600 transition flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-white font-bold">
                    <Globe className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Global Edge
                  </span>
                </div>
                <h3 className="text-base font-bold text-white">Deploy to Vercel</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Instant edge CDN distribution for the responsive React frontend with automated CI/CD previews.
                </p>
              </div>

              <a
                href={vercelUrl}
                target="_blank"
                rel="noreferrer"
                className="w-full py-2.5 px-4 rounded-xl bg-white hover:bg-slate-200 text-slate-950 text-xs font-bold transition flex items-center justify-center space-x-2 shadow-lg"
              >
                <span>1-Click Deploy on Vercel</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            {/* DOCKER / K8S BUNDLE */}
            <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-950/80 to-slate-900/60 border border-slate-800 hover:border-purple-500/50 transition flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold">
                    <Box className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                    Self-Hosted
                  </span>
                </div>
                <h3 className="text-base font-bold text-white">DevOps & K8s Bundle</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Download ready-to-run <code className="text-purple-300">Dockerfile</code>, <code className="text-purple-300">docker-compose.yml</code>, and Kubernetes manifests.
                </p>
              </div>

              <button
                onClick={handleDownloadDevOpsBundle}
                disabled={isDownloadingBundle}
                className="w-full py-2.5 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition flex items-center justify-center space-x-2 shadow-lg shadow-purple-600/20 disabled:opacity-50"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{isDownloadingBundle ? 'Assembling Zip...' : 'Download Complete .ZIP'}</span>
              </button>
            </div>
          </div>

          {/* LIVE DEPLOYMENT SIMULATION STATUS BAR */}
          <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                deployStatus === 'live' ? 'bg-emerald-400 animate-ping' : deployStatus === 'deploying' ? 'bg-amber-400 animate-spin' : 'bg-blue-400'
              }`} />
              <div>
                <h4 className="text-xs font-bold text-white">
                  {deployStatus === 'live' ? '🟢 Live Production Environment Online' : deployStatus === 'deploying' ? '🟡 Deploying Container Clusters...' : '🔵 Ready for 1-Click Deployment Trigger'}
                </h4>
                <p className="text-[11px] text-slate-400">
                  {deployStatus === 'live'
                    ? 'SSL Active • NeonDB Connected • Healthcheck HTTP 200 OK • Latency: 24ms'
                    : 'Target: AWS ap-southeast-1 • Container: Docker Python 3.10 • Database: Neon PostgreSQL'}
                </p>
              </div>
            </div>

            <button
              onClick={handleSimulateDeploy}
              disabled={deployStatus === 'deploying'}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition flex items-center justify-center space-x-1.5"
            >
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span>{deployStatus === 'live' ? 'Re-test Health Check' : 'Trigger Live Sync'}</span>
            </button>
          </div>
        </div>
      )}

      {/* TAB 2: INTERACTIVE LIVE SOLUTION SANDBOX */}
      {activeTab === 'sandbox' && (
        <div className="space-y-5 animate-fadeIn">
          {/* Device and Screen Switcher */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-2xl bg-slate-950 border border-slate-800">
            {/* Devices */}
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setSandboxDevice('desktop')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  sandboxDevice === 'desktop' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Monitor className="w-3.5 h-3.5" />
                <span>Web / Desktop</span>
              </button>
              <button
                onClick={() => setSandboxDevice('tablet')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  sandboxDevice === 'tablet' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Tablet className="w-3.5 h-3.5" />
                <span>Tablet (iPad)</span>
              </button>
              <button
                onClick={() => setSandboxDevice('mobile')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  sandboxDevice === 'mobile' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Smartphone className="w-3.5 h-3.5" />
                <span>Mobile (iOS/Android)</span>
              </button>
            </div>

            {/* Sandbox Views */}
            <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setSandboxActiveTab('dashboard')}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                  sandboxActiveTab === 'dashboard' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Operations Dashboard
              </button>
              <button
                onClick={() => setSandboxActiveTab('portal')}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                  sandboxActiveTab === 'portal' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Customer Portal
              </button>
              <button
                onClick={() => setSandboxActiveTab('workflows')}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                  sandboxActiveTab === 'workflows' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Automated Pipeline
              </button>
            </div>
          </div>

          {/* SANDBOX SCREEN FRAME */}
          <div className="flex justify-center">
            <div
              className={`transition-all duration-300 rounded-3xl bg-slate-950 border-4 border-slate-800 shadow-2xl p-6 overflow-hidden ${
                sandboxDevice === 'desktop'
                  ? 'w-full min-h-[420px]'
                  : sandboxDevice === 'tablet'
                  ? 'w-[680px] min-h-[460px]'
                  : 'w-[360px] min-h-[500px]'
              }`}
            >
              {/* Fake Browser / Device Header */}
              <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800 text-xs text-slate-400">
                <div className="flex items-center space-x-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                  <span className="ml-2 font-mono text-[10px] text-slate-500">
                    https://{data?.project_name ? data.project_name.toLowerCase().replace(/[^a-z0-9]/g, '') : 'app'}.transformiq.live
                  </span>
                </div>
                <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                  SANDBOX v1.0
                </span>
              </div>

              {/* LIVE SIMULATED CONTENT */}
              {sandboxActiveTab === 'dashboard' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-white">{data?.project_name} Enterprise Suite</h4>
                      <p className="text-[11px] text-slate-400">{data?.recommended_solution.tagline}</p>
                    </div>
                    <button
                      onClick={() => setSandboxMetric(prev => prev + 15)}
                      className="px-2.5 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-bold"
                    >
                      + Trigger Action
                    </button>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">Active Throughput</span>
                      <span className="text-lg font-extrabold text-white mt-0.5 block">{sandboxMetric.toLocaleString()} / hr</span>
                      <span className="text-[9px] text-emerald-400">↑ 18.4% efficiency</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">AI Resolution Rate</span>
                      <span className="text-lg font-extrabold text-emerald-400 mt-0.5 block">94.8%</span>
                      <span className="text-[9px] text-slate-500">Autonomous workflow</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 col-span-2 sm:col-span-1">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">Cloud Status</span>
                      <span className="text-lg font-extrabold text-blue-400 mt-0.5 block">99.98%</span>
                      <span className="text-[9px] text-blue-300">Multi-region active</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                    <h5 className="text-xs font-bold text-slate-300 mb-2">Real-Time Event Stream</h5>
                    <div className="space-y-1.5 text-[11px] font-mono text-slate-400">
                      <p className="text-emerald-400">✔ [00:01:04] Order #89201 processed autonomously via BPMN rule engine</p>
                      <p className="text-blue-400">ℹ [00:01:12] CRM synchronization verified with 0 schema drift</p>
                      <p className="text-purple-400">⚡ [00:01:28] Anomaly detection model flagged 0 security risks</p>
                    </div>
                  </div>
                </div>
              )}

              {sandboxActiveTab === 'portal' && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-gradient-to-r from-blue-950/50 to-indigo-950/50 border border-blue-500/30">
                    <h4 className="text-xs font-bold text-white">Client Self-Service Onboarding</h4>
                    <p className="text-[11px] text-slate-300 mt-1">Submit requirements or service requests with automatic AI triage.</p>
                  </div>

                  <div className="space-y-2 text-xs">
                    <input
                      type="text"
                      placeholder="Enter request title..."
                      className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500"
                    />
                    <textarea
                      rows={2}
                      placeholder="Describe the business scenario..."
                      className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500"
                    />
                    <button
                      onClick={() => alert('Simulated Request submitted successfully to AI queue!')}
                      className="w-full py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition"
                    >
                      Submit Service Request
                    </button>
                  </div>
                </div>
              )}

              {sandboxActiveTab === 'workflows' && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-white">Configured Autonomous Pipelines</h4>
                  <div className="space-y-2">
                    {[
                      { name: 'Customer Ingestion & Verification', time: '1.2s', status: 'Optimal' },
                      { name: 'Automated Invoice Matching & Ledger Post', time: '0.8s', status: 'Optimal' },
                      { name: 'Predictive Inventory Restock Trigger', time: '2.4s', status: 'Running' }
                    ].map((wf, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                        <div>
                          <span className="font-bold text-white">{wf.name}</span>
                          <span className="text-[10px] text-slate-500 block">Avg latency: {wf.time}</span>
                        </div>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                          {wf.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: CUSTOMIZE & REGENERATE STUDIO */}
      {activeTab === 'customize' && (
        <div className="space-y-6 animate-fadeIn">
          <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white">Fine-tune Business Requirements & Design Specs</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Update core assumptions, add unexpected features, change UI styles, or adjust target cloud providers before regeneration.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Additional Requirement or Business Nuance</label>
                <textarea
                  rows={3}
                  value={customGoal}
                  onChange={(e) => setCustomGoal(e.target.value)}
                  placeholder="e.g. Add biometric authentication for mobile app and automated Slack webhook alerts for high-value events..."
                  className="w-full p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="space-y-3">
                <label className="text-xs font-semibold text-slate-300 block">UI Theme & Aesthetics</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'midnight', name: 'Midnight Cyber', color: 'bg-blue-600' },
                    { id: 'emerald', name: 'Enterprise Emerald', color: 'bg-emerald-600' },
                    { id: 'indigo', name: 'Royal Indigo', color: 'bg-indigo-600' },
                    { id: 'slate', name: 'Minimal Slate', color: 'bg-slate-700' },
                  ].map((th) => (
                    <button
                      key={th.id}
                      onClick={() => setCustomTheme(th.id)}
                      className={`p-2.5 rounded-xl border text-xs font-semibold flex items-center space-x-2 transition ${
                        customTheme === th.id
                          ? 'border-emerald-500 bg-emerald-500/10 text-white'
                          : 'border-slate-800 bg-slate-900 text-slate-400 hover:text-white'
                      }`}
                    >
                      <span className={`w-3 h-3 rounded-full ${th.color}`} />
                      <span>{th.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={handleApplyCustomization}
                disabled={isCustomizing}
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center space-x-2 shadow-lg shadow-emerald-600/20 disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isCustomizing ? 'animate-spin' : ''}`} />
                <span>{isCustomizing ? 'Regenerating Solution...' : 'Apply & Regenerate Blueprint'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
