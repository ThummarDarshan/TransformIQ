import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Layout,
  Users,
  Compass,
  ArrowRight,
  RefreshCw,
  Eye,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Monitor,
  Smartphone,
  Tablet,
  Code2,
  Copy,
  Check,
  Palette,
  Sliders,
  Maximize2
} from 'lucide-react';
import api from '../services/api';
import { UxData } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';
import { useLanguage } from '../contexts/LanguageContext';

export const UxPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const { t } = useLanguage();
  const [data, setData] = useState<UxData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [activeWireframeTab, setActiveWireframeTab] = useState(0);
  const [selectedDevice, setSelectedDevice] = useState<'desktop' | 'tablet' | 'ios' | 'android'>('desktop');
  const [activeTheme, setActiveTheme] = useState<'midnight' | 'emerald' | 'indigo' | 'slate'>('midnight');
  const [isCodeModalOpen, setIsCodeModalOpen] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/ux/project/${projectId}`);
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
      const res: any = await api.post(`/ux/project/${projectId}/generate`);
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
    return <LoadingScreen message={t('Designing user personas, journey stages, and multi-device wireframes...', 'Designing user personas, journey stages, and multi-device wireframes...')} />;
  }

  const activeWireframe = data?.wireframes?.[activeWireframeTab];

  // Theme styles
  const themeStyles = {
    midnight: {
      bg: 'bg-slate-950',
      cardBg: 'bg-slate-900',
      border: 'border-slate-800',
      accent: 'text-blue-400',
      badge: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      btn: 'bg-blue-600 hover:bg-blue-500 text-white'
    },
    emerald: {
      bg: 'bg-[#06140d]',
      cardBg: 'bg-[#0b2418]',
      border: 'border-emerald-900/60',
      accent: 'text-emerald-400',
      badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
      btn: 'bg-emerald-600 hover:bg-emerald-500 text-white'
    },
    indigo: {
      bg: 'bg-[#0a081e]',
      cardBg: 'bg-[#141138]',
      border: 'border-indigo-900/60',
      accent: 'text-indigo-400',
      badge: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
      btn: 'bg-indigo-600 hover:bg-indigo-500 text-white'
    },
    slate: {
      bg: 'bg-slate-900',
      cardBg: 'bg-slate-800/80',
      border: 'border-slate-700',
      accent: 'text-slate-200',
      badge: 'bg-slate-700 text-slate-200 border-slate-600',
      btn: 'bg-slate-700 hover:bg-slate-600 text-white'
    }
  }[activeTheme];

  const generatedComponentCode = activeWireframe ? `import React from 'react';

export const ${activeWireframe.screen_name.replace(/[^a-zA-Z0-9]/g, '')}Screen: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-white p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <span className="text-xs uppercase font-bold text-blue-400">${activeWireframe.layout_type}</span>
          <h1 className="text-xl font-bold mt-1">${activeWireframe.screen_name}</h1>
          <p className="text-xs text-slate-400">${activeWireframe.purpose}</p>
        </div>
        <div className="flex items-center space-x-2">
          ${activeWireframe.user_actions.map(act => `<button className="px-3 py-1.5 rounded-lg bg-blue-600 text-xs font-semibold hover:bg-blue-500">${act}</button>`).join('\n          ')}
        </div>
      </div>

      {/* Dynamic Wireframe Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        ${activeWireframe.components.map(c => `
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 block">${c.label}</span>
          <span className="text-lg font-bold text-white mt-1 block">${c.props?.value || 'Value'}</span>
        </div>`).join('')}
      </div>
    </div>
  );
};
` : '';

  const handleCopyCode = () => {
    navigator.clipboard.writeText(generatedComponentCode);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto pb-16">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
              STEP 09
            </span>
            <h1 className="text-2xl font-extrabold text-white">AI UX Designer & Multi-Platform Wireframes</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Enterprise user personas, responsive device previews (Web + iOS + Android + Tablet), and exportable UI components.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>{isRegenerating ? 'Designing...' : 'Regenerate UX'}</span>
          </button>
          <Link
            to={`/projects/${projectId}/planning`}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>Next: Roadmap & Costs</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* USER PERSONAS */}
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center">
          <Users className="w-4 h-4 text-indigo-400 mr-2" /> Target User Personas & Journey Drivers
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {data?.personas.map((p, idx) => (
            <div key={idx} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center font-bold text-sm text-indigo-300">
                  {p.name.charAt(0)}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">{p.name}</h4>
                  <p className="text-xs text-indigo-400 font-medium">{p.role}</p>
                </div>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="font-bold text-slate-300 block mb-1 text-[11px] uppercase text-emerald-400">Goals</span>
                  <ul className="list-disc list-inside text-slate-400 space-y-0.5">
                    {p.goals.map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <span className="font-bold text-slate-300 block mb-1 text-[11px] uppercase text-rose-400">Pain Points</span>
                  <ul className="list-disc list-inside text-slate-400 space-y-0.5">
                    {p.pain_points.map((pt, i) => (
                      <li key={i}>{pt}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* MULTI-PLATFORM WIREFRAME STUDIO */}
      <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 backdrop-blur-md space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white flex items-center">
              <Layout className="w-4 h-4 text-blue-400 mr-2" /> Multi-Platform Responsive Wireframes
            </h3>
            <p className="text-xs text-slate-400">Simulate UX layout across Web, iOS, Android, and Tablet interfaces.</p>
          </div>

          {/* Controls: Device & Theme */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Device Frame Switcher */}
            <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setSelectedDevice('desktop')}
                title="Desktop / Web View"
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
                  selectedDevice === 'desktop' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Monitor className="w-4 h-4" />
                <span className="hidden sm:inline">Web</span>
              </button>
              <button
                onClick={() => setSelectedDevice('tablet')}
                title="Tablet / iPad View"
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
                  selectedDevice === 'tablet' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Tablet className="w-4 h-4" />
                <span className="hidden sm:inline">Tablet</span>
              </button>
              <button
                onClick={() => setSelectedDevice('ios')}
                title="Apple iPhone iOS View"
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
                  selectedDevice === 'ios' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Smartphone className="w-4 h-4" />
                <span className="hidden sm:inline">iOS</span>
              </button>
              <button
                onClick={() => setSelectedDevice('android')}
                title="Google Android Material View"
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
                  selectedDevice === 'android' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Smartphone className="w-4 h-4" />
                <span className="hidden sm:inline">Android</span>
              </button>
            </div>

            {/* Theme Selector */}
            <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
              {(['midnight', 'emerald', 'indigo', 'slate'] as const).map((tId) => (
                <button
                  key={tId}
                  onClick={() => setActiveTheme(tId)}
                  title={`Apply ${tId} theme`}
                  className={`px-2 py-1 rounded-lg text-[11px] font-bold capitalize transition ${
                    activeTheme === tId ? 'bg-slate-800 text-white shadow' : 'text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {tId}
                </button>
              ))}
            </div>

            {/* Export Code Button */}
            <button
              onClick={() => setIsCodeModalOpen(true)}
              className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition flex items-center space-x-1.5"
            >
              <Code2 className="w-3.5 h-3.5 text-blue-400" />
              <span>Export Code</span>
            </button>
          </div>
        </div>

        {/* Wireframe Screen Selector Tabs */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1">
          {data?.wireframes.map((wf, idx) => (
            <button
              key={idx}
              onClick={() => setActiveWireframeTab(idx)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap ${
                activeWireframeTab === idx
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                  : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {wf.screen_name}
            </button>
          ))}
        </div>

        {/* DEVICE FRAME CONTAINER */}
        {activeWireframe && (
          <div className="flex justify-center py-2 sm:py-4 overflow-x-auto max-w-full">
            <div
              className={`transition-all duration-300 shadow-2xl rounded-2xl sm:rounded-3xl overflow-hidden border-2 sm:border-4 ${themeStyles.border} ${themeStyles.bg} ${
                selectedDevice === 'desktop'
                  ? 'w-full min-h-[420px]'
                  : selectedDevice === 'tablet'
                  ? 'w-full max-w-[720px] min-h-[440px]'
                  : selectedDevice === 'ios'
                  ? 'w-full max-w-[375px] min-h-[560px] rounded-[32px] sm:rounded-[48px] border-4 sm:border-8 border-slate-800 relative ring-1 ring-slate-700'
                  : 'w-full max-w-[380px] min-h-[560px] rounded-[28px] sm:rounded-[36px] border-4 sm:border-8 border-slate-800 relative ring-1 ring-slate-700'
              }`}
            >
              {/* iPhone Dynamic Island / Android Camera cutout */}
              {selectedDevice === 'ios' && (
                <div className="pt-2 pb-1 flex justify-center items-center bg-black">
                  <div className="w-24 h-4 bg-slate-900 rounded-full flex items-center justify-between px-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500/80" />
                    <div className="w-2 h-2 rounded-full bg-slate-800" />
                  </div>
                </div>
              )}

              {/* Top Navigation Bar of simulated device */}
              <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
                <div>
                  <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${themeStyles.badge}`}>
                    {activeWireframe.layout_type} • {selectedDevice.toUpperCase()}
                  </span>
                  <h4 className="text-sm font-bold text-white mt-1">{activeWireframe.screen_name}</h4>
                  <p className="text-xs text-slate-400">{activeWireframe.purpose}</p>
                </div>
                <div className="flex items-center space-x-1.5 flex-wrap gap-1">
                  {activeWireframe.user_actions.map((act, idx) => (
                    <button
                      key={idx}
                      className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition ${themeStyles.btn}`}
                    >
                      {act}
                    </button>
                  ))}
                </div>
              </div>

              {/* Rendered Mockup Components */}
              <div className="p-4 sm:p-6 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {activeWireframe.components.map((comp, idx) => {
                    if (comp.type === 'stat_card') {
                      return (
                        <div key={idx} className={`p-4 rounded-2xl border ${themeStyles.cardBg} ${themeStyles.border}`}>
                          <span className="text-[11px] font-semibold text-slate-400 block">{comp.label}</span>
                          <span className={`text-xl font-black mt-1 block ${themeStyles.accent}`}>
                            {comp.props?.value || '94.6%'}
                          </span>
                          <span className="text-[10px] text-emerald-400 font-bold">{comp.props?.trend || '+12% vs baseline'}</span>
                        </div>
                      );
                    }
                    if (comp.type === 'alert') {
                      return (
                        <div key={idx} className="sm:col-span-3 p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/40 text-amber-200 text-xs flex items-center space-x-2">
                          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                          <span>{comp.label}</span>
                        </div>
                      );
                    }
                    return (
                      <div key={idx} className={`p-4 rounded-xl border text-xs text-slate-300 ${themeStyles.cardBg} ${themeStyles.border}`}>
                        <span className="font-bold text-white block mb-1">{comp.label}</span>
                        <span className="text-[10px] text-slate-500">Component Type: {comp.type}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* REACT CODE EXPORT MODAL */}
      {isCodeModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full p-6 shadow-2xl relative max-h-[88vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <Code2 className="w-5 h-5 text-blue-400" />
                <h3 className="text-base font-bold text-white">Generated React & Tailwind Component Code</h3>
              </div>
              <button
                onClick={() => setIsCodeModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="my-4 flex-1 overflow-auto rounded-xl bg-slate-950 p-4 border border-slate-800 font-mono text-xs text-blue-200">
              <pre>{generatedComponentCode}</pre>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={handleCopyCode}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition flex items-center space-x-1.5"
              >
                {copiedCode ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
                <span>{copiedCode ? 'Copied Code!' : 'Copy React Component'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
