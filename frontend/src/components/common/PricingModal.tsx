import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import {
  X,
  Sparkles,
  Check,
  Zap,
  Shield,
  Layers,
  Cpu,
  Calculator,
  CreditCard,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

interface PricingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PricingModal: React.FC<PricingModalProps> = ({ isOpen, onClose }) => {
  const { t } = useLanguage();
  const [activeBilling, setActiveBilling] = useState<'monthly' | 'yearly'>('monthly');
  const [blueprintCount, setBlueprintCount] = useState<number>(10);
  const [isSimulatingCheckout, setIsSimulatingCheckout] = useState(false);
  const [purchasedPlan, setPurchasedPlan] = useState<string | null>(null);

  // Close on Escape key press & prevent background scroll when open
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSimulatePurchase = (planName: string) => {
    setIsSimulatingCheckout(true);
    setTimeout(() => {
      setIsSimulatingCheckout(false);
      setPurchasedPlan(planName);
      setTimeout(() => {
        setPurchasedPlan(null);
        onClose();
      }, 1500);
    }, 1000);
  };

  // Cost breakdown calculation
  const promptTokensEst = blueprintCount * 12500;
  const outputTokensEst = blueprintCount * 28000;
  const rawLlmCost = (promptTokensEst / 1000000) * 0.075 + (outputTokensEst / 1000000) * 0.30;
  const infraCost = blueprintCount * 0.08;
  const totalCost = (rawLlmCost + infraCost).toFixed(2);
  const retailPrice = (blueprintCount * 0.49).toFixed(2);

  return createPortal(
    <div
      className="fixed inset-0 z-[999999] flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fadeIn"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-slate-700/90 rounded-3xl max-w-5xl w-full p-6 sm:p-8 shadow-2xl relative my-auto max-h-[90vh] overflow-y-auto ring-1 ring-slate-700 shadow-blue-500/10"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top Close Button */}
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-2 rounded-xl bg-slate-800 hover:bg-slate-700 transition border border-slate-700 z-10"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="text-center max-w-2xl mx-auto mb-8 pt-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span>Transparent & Justified Monetization</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Predictable Pricing & AI Token Economics
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-2">
            Every generation is powered by enterprise AI orchestrators with full cost transparency. Pay per blueprint or subscribe with generous monthly volume.
          </p>

          {/* Billing Switch */}
          <div className="flex items-center justify-center space-x-3 mt-6">
            <span className={`text-xs font-semibold ${activeBilling === 'monthly' ? 'text-white' : 'text-slate-400'}`}>
              Monthly Billing
            </span>
            <button
              onClick={() => setActiveBilling(prev => prev === 'monthly' ? 'yearly' : 'monthly')}
              className="w-12 h-6 rounded-full bg-slate-800 p-1 border border-slate-700 relative transition"
            >
              <div
                className={`w-4 h-4 rounded-full bg-blue-500 transition-transform ${
                  activeBilling === 'yearly' ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
            <span className={`text-xs font-semibold flex items-center space-x-1 ${activeBilling === 'yearly' ? 'text-white' : 'text-slate-400'}`}>
              <span>Annual Billing</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">20% OFF</span>
            </span>
          </div>
        </div>

        {/* SUCCESS ALERT */}
        {purchasedPlan && (
          <div className="mb-6 p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-sm flex items-center space-x-3 animate-fadeIn">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <span>Successfully activated <b>{purchasedPlan}</b>! Your credit allocation has been refreshed.</span>
          </div>
        )}

        {/* PRICING TIERS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* FREE TIER */}
          <div className="p-6 rounded-2xl bg-slate-950/60 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Community / Free</span>
              <h3 className="text-2xl font-bold text-white mt-1">$0 <span className="text-xs text-slate-500 font-normal">/ forever</span></h3>
              <p className="text-xs text-slate-400 mt-2">Essential business blueprinting for students and early explorers.</p>

              <div className="my-5 border-t border-slate-800/80 pt-4 space-y-2.5 text-xs text-slate-300">
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>3 Master Blueprints per month</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Standard AI (Deterministic Smart + Gemini Flash)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Interactive Wireframes & BPMN</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>PDF & JSON Exports</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSimulatePurchase('Free Community Plan')}
              disabled={isSimulatingCheckout}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition border border-slate-700"
            >
              Current Active Plan
            </button>
          </div>

          {/* PRO TIER */}
          <div className="p-6 rounded-2xl bg-gradient-to-b from-blue-950/40 to-slate-950/90 border-2 border-blue-500/60 shadow-xl shadow-blue-500/10 flex flex-col justify-between relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-[10px] font-black uppercase tracking-wider shadow">
              MOST POPULAR
            </div>

            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Professional Builder</span>
              <h3 className="text-2xl font-bold text-white mt-1">
                {activeBilling === 'monthly' ? '$39' : '$31'}{' '}
                <span className="text-xs text-slate-400 font-normal">/ month</span>
              </h3>
              <p className="text-xs text-slate-300 mt-2">Full end-to-end transformation suite for startups and product agencies.</p>

              <div className="my-5 border-t border-blue-900/40 pt-4 space-y-2.5 text-xs text-slate-200">
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span><b>100 Master Blueprints</b> / month ($0.39/gen)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Fast Gemini Flash Engine</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>1-Click Deploy to Vercel & Render</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Docker & Kubernetes Manifest Generator</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>DOCX, PDF, XLSX & PPTX 4-Format Exports</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Multilingual Voice Speech-to-Text Input</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSimulatePurchase('Professional Builder Plan')}
              disabled={isSimulatingCheckout}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold transition shadow-lg shadow-blue-500/20"
            >
              {isSimulatingCheckout ? 'Activating...' : 'Upgrade to Pro'}
            </button>
          </div>

          {/* ENTERPRISE TIER */}
          <div className="p-6 rounded-2xl bg-slate-950/60 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-purple-400">Enterprise Sovereign</span>
              <h3 className="text-2xl font-bold text-white mt-1">
                {activeBilling === 'monthly' ? '$199' : '$159'}{' '}
                <span className="text-xs text-slate-400 font-normal">/ month</span>
              </h3>
              <p className="text-xs text-slate-400 mt-2">Unlimited transformation generation for consulting firms & large enterprises.</p>

              <div className="my-5 border-t border-slate-800/80 pt-4 space-y-2.5 text-xs text-slate-300">
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span><b>Unlimited</b> Solution Blueprint Generations</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Custom LLM Fine-Tuning & Private VPC</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Granular 4-Role RBAC & Audit Trails</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>99.9% Uptime SLA + 24/7 Priority Support</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>White-label Client Export Branding</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSimulatePurchase('Enterprise Sovereign Plan')}
              disabled={isSimulatingCheckout}
              className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition shadow-lg shadow-purple-600/20"
            >
              {isSimulatingCheckout ? 'Activating...' : 'Contact Enterprise Sales'}
            </button>
          </div>
        </div>

        {/* TRANSPARENT UNIT ECONOMICS CALCULATOR */}
        <div className="p-6 rounded-2xl bg-slate-950/80 border border-slate-800">
          <div className="flex items-center justify-between flex-wrap gap-3 mb-4 pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <Calculator className="w-5 h-5 text-blue-400" />
              <h4 className="text-sm font-bold text-white">Justified Pay-Per-Generation Unit Economics</h4>
            </div>
            <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              Zero Markup AI Compute
            </span>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Simulate Volume (Master Blueprints Generated):</span>
              <span className="text-white font-bold">{blueprintCount} Blueprints</span>
            </div>
            <input
              type="range"
              min="1"
              max="100"
              value={blueprintCount}
              onChange={(e) => setBlueprintCount(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                <span className="text-[10px] uppercase font-bold text-slate-500">LLM Prompt Tokens</span>
                <p className="text-sm font-mono font-bold text-white mt-0.5">{promptTokensEst.toLocaleString()}</p>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                <span className="text-[10px] uppercase font-bold text-slate-500">Synthesis Tokens</span>
                <p className="text-sm font-mono font-bold text-white mt-0.5">{outputTokensEst.toLocaleString()}</p>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                <span className="text-[10px] uppercase font-bold text-slate-500">Actual Compute Cost</span>
                <p className="text-sm font-mono font-bold text-emerald-400 mt-0.5">${totalCost}</p>
              </div>
              <div className="p-3 rounded-xl bg-blue-950/30 border border-blue-500/30 text-center">
                <span className="text-[10px] uppercase font-bold text-blue-400">TransformIQ Price</span>
                <p className="text-sm font-mono font-bold text-blue-300 mt-0.5">${retailPrice}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};
