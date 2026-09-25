import React, { useState } from 'react';
import { Coins, Sparkles, ChevronRight } from 'lucide-react';
import { PricingModal } from './PricingModal';

export const CreditBalanceBadge: React.FC = () => {
  const [isPricingOpen, setIsPricingOpen] = useState(false);
  const [credits, setCredits] = useState<number>(240);

  return (
    <>
      <button
        onClick={() => setIsPricingOpen(true)}
        title="View AI Compute Credits & Pricing Engine"
        className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-3 py-1 sm:py-1.5 rounded-xl bg-gradient-to-r from-amber-500/10 via-amber-500/20 to-yellow-500/10 hover:from-amber-500/20 hover:to-yellow-500/20 border border-amber-500/30 text-amber-300 text-xs font-bold transition shadow-sm shrink-0"
      >
        <Coins className="w-3.5 h-3.5 text-amber-400 shrink-0" />
        <span className="sm:hidden">{credits}</span>
        <span className="hidden sm:inline">{credits} Credits</span>
        <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-400/20 text-amber-200 uppercase font-mono hidden md:inline">
          PRO
        </span>
      </button>

      <PricingModal isOpen={isPricingOpen} onClose={() => setIsPricingOpen(false)} />
    </>
  );
};
