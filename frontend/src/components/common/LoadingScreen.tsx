import React from 'react';
import { Loader2, Sparkles } from 'lucide-react';

interface LoadingScreenProps {
  message?: string;
  steps?: string[];
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({
  message = "TransformIQ Intelligence Engine is synthesizing business context...",
  steps = [
    "Reading ingested enterprise documents & business problem",
    "Identifying core requirements and stakeholder bottlenecks",
    "Performing 8-dimension gap matrix analysis",
    "Generating AI & automation solution blueprint",
    "Calculating transformation readiness scorecard"
  ]
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center min-h-[400px]">
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-2xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center animate-pulse">
          <Sparkles className="w-8 h-8 text-blue-400 animate-spin" style={{ animationDuration: '6s' }} />
        </div>
        <div className="absolute -bottom-2 -right-2 bg-emerald-500 p-1.5 rounded-full text-white shadow-lg">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        </div>
      </div>

      <h3 className="text-lg font-bold text-slate-100 mb-2">{message}</h3>
      <p className="text-xs text-slate-400 max-w-md mb-6">
        Grounded in project context, document chunks, and domain rules.
      </p>

      <div className="w-full max-w-md bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-left space-y-2.5">
        {steps.map((step, idx) => (
          <div key={idx} className="flex items-center space-x-2.5 text-xs text-slate-300">
            <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-[10px]">
              0{idx + 1}
            </span>
            <span>{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
