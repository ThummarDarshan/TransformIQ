import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  Layers,
  Cpu,
  FileCheck,
  Flame,
  Sliders
} from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

import { TransformIQLogo } from '../components/common/TransformIQLogo';

export const LandingPage: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-blue-600 selection:text-white relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-b from-blue-600/15 via-indigo-600/10 to-transparent blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 right-0 w-[500px] h-[500px] bg-emerald-500/10 blur-3xl pointer-events-none" />

      {/* HEADER */}
      <header className="max-w-7xl mx-auto px-4 sm:px-6 h-16 sm:h-20 flex items-center justify-between relative z-10 gap-2">
        <Link to="/" className="hover:opacity-95 transition-opacity shrink-0">
          <TransformIQLogo size="sm" showSubtitle={false} className="sm:hidden" />
          <TransformIQLogo size="md" showSubtitle className="hidden sm:flex" />
        </Link>

        <div className="flex items-center space-x-2 sm:space-x-4 shrink-0">
          <div className="hidden lg:flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-amber-400 font-medium">
            <Flame className="w-3.5 h-3.5" />
            <span>Chaos2Commit Hackathon 2026</span>
          </div>
          <Link
            to="/login"
            className="text-xs sm:text-sm font-semibold text-slate-300 hover:text-white px-2.5 sm:px-3 py-1.5 sm:py-2 transition"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="px-3 sm:px-5 py-1.5 sm:py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-emerald-500 hover:from-blue-500 hover:to-emerald-400 text-white font-bold text-xs sm:text-sm shadow-lg shadow-blue-600/25 transition transform hover:-translate-y-0.5"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="max-w-5xl mx-auto px-6 pt-16 pb-20 text-center relative z-10">
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs font-semibold mb-8 animate-fadeIn">
          <Sparkles className="w-4 h-4 text-blue-400" />
          <span>The AI Transformation Operating System for Enterprise</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-100 leading-[1.1] mb-6">
          Transform Business Chaos into{' '}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-300 to-emerald-400">
            Implementation-Ready Solutions
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto font-normal leading-relaxed mb-10">
          Upload enterprise documents (BRDs, SOPs, PDFs, Word) or describe your business challenge.
          Let specialized AI agents discover requirements, identify gaps, build React Flow architectures, design databases & APIs, run What-If simulations, and produce verifiable blueprints.
        </p>

        {/* CTA BUTTONS */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Link
            to="/register"
            className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-500 hover:from-blue-500 hover:to-emerald-400 text-white font-extrabold text-base shadow-xl shadow-blue-600/30 transition transform hover:-translate-y-0.5 flex items-center justify-center space-x-2.5"
          >
            <span>Create Enterprise Workspace</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/login"
            className="w-full sm:w-auto px-7 py-4 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-200 font-bold text-base transition flex items-center justify-center space-x-2"
          >
            <span>Sign In to Existing Workspace</span>
          </Link>
        </div>

        {/* CHAOS TO COMMIT STEPPER BAR */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md max-w-4xl mx-auto shadow-2xl">
          <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">
            Chaos2Commit Transformation Lifecycle
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 text-center">
            {[
              { label: "1. Business Chaos", color: "text-rose-400", bg: "bg-rose-500/10 border-rose-500/30" },
              { label: "2. Context & RAG", color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30" },
              { label: "3. Gap Detection", color: "text-purple-400", bg: "bg-purple-500/10 border-purple-500/30" },
              { label: "4. AI Solutions", color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/30" },
              { label: "5. Architecture", color: "text-indigo-400", bg: "bg-indigo-500/10 border-indigo-500/30" },
              { label: "6. Commit Blueprint", color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/30" },
            ].map((step, idx) => (
              <div key={idx} className={`p-2.5 rounded-xl border ${step.bg} flex flex-col items-center justify-center`}>
                <span className={`text-xs font-bold ${step.color}`}>{step.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CORE VALUE PILLARS */}
      <section className="max-w-7xl mx-auto px-6 py-20 border-t border-slate-900">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-100 tracking-tight">
            Not a Generic Chatbot. An Enterprise Solution Builder.
          </h2>
          <p className="text-slate-400 text-sm mt-3">
            TransformIQ acts as your AI Business Consultant, Business Analyst, Solution Architect, and Product Strategist in one unified workspace.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-blue-500/40 transition group">
            <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400 w-fit mb-4 group-hover:scale-110 transition">
              <FileCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-100 mb-2">Multi-Format RAG Ingestion</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Upload SOPs, BRDs, PDFs, Word, PPTX, or paste unstructured text. Extracted domain knowledge grounds every AI generation in real enterprise rules.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-emerald-500/40 transition group">
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 w-fit mb-4 group-hover:scale-110 transition">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-100 mb-2">Interactive React Flow HLD / BPMN</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Generate cloud architectures and BPMN workflows with drag-and-drop React Flow nodes, swimlanes, cycle time comparisons, and layout persistence.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-purple-500/40 transition group">
            <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 w-fit mb-4 group-hover:scale-110 transition">
              <Sliders className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-100 mb-2">Dynamic What-If Simulation</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Adjust automation percentage, team size, budget, and timeline sliders to recalculate projected ROI, effort hours, and delivery risk in real time.
            </p>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-slate-900 bg-slate-950 py-10 px-6 text-center text-xs text-slate-500">
        <p>© 2026 TransformIQ — Business Transformation AI. Built for Chaos2Commit Hackathon 2026.</p>
      </footer>
    </div>
  );
};
