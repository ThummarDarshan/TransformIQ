import React from 'react';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showSubtitle?: boolean;
  className?: string;
}

export const TransformIQLogo: React.FC<LogoProps> = ({
  size = 'md',
  showSubtitle = false,
  className = ''
}) => {
  const iconSizes = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const textSizes = {
    sm: 'text-base',
    md: 'text-lg',
    lg: 'text-2xl',
    xl: 'text-3xl'
  };

  const badgeSizes = {
    sm: 'text-[9px] px-1.5 py-0.5 rounded-md',
    md: 'text-[11px] px-2 py-0.5 rounded-lg',
    lg: 'text-xs px-2.5 py-1 rounded-lg',
    xl: 'text-sm px-3 py-1 rounded-xl'
  };

  return (
    <div className={`flex items-center space-x-2.5 sm:space-x-3.5 ${className}`}>
      {/* High-Tech Vector Hexagonal Mark */}
      <div className={`relative ${iconSizes[size]} shrink-0 group select-none`}>
        {/* Ambient Glow */}
        <div className="absolute inset-0 bg-cyan-500/25 rounded-xl blur-[10px] opacity-80 group-hover:opacity-100 transition-opacity duration-300" />
        
        {/* SVG Emblem */}
        <svg
          viewBox="0 0 48 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="relative w-full h-full drop-shadow-[0_2px_10px_rgba(6,182,212,0.3)] transition-transform duration-300 group-hover:scale-105"
        >
          <defs>
            <linearGradient id="tqBorderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="50%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
            <radialGradient id="tqCoreGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#ffffff" />
              <stop offset="40%" stopColor="#38bdf8" />
              <stop offset="100%" stopColor="#0369a1" />
            </radialGradient>
          </defs>

          {/* Rounded Tech Container */}
          <rect x="1" y="1" width="46" height="46" rx="12" fill="#070c18" stroke="url(#tqBorderGrad)" strokeWidth="1.75" />
          
          {/* Subtle Background Matrix Dots */}
          <circle cx="18" cy="20" r="0.75" fill="#38bdf8" fillOpacity="0.3" />
          <circle cx="18" cy="28" r="0.75" fill="#38bdf8" fillOpacity="0.3" />
          <circle cx="30" cy="20" r="0.75" fill="#818cf8" fillOpacity="0.3" />
          <circle cx="30" cy="28" r="0.75" fill="#818cf8" fillOpacity="0.3" />

          {/* 4 Diagonal Connector Arms */}
          <line x1="14" y1="14" x2="24" y2="24" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round" />
          <line x1="34" y1="14" x2="24" y2="24" stroke="#818cf8" strokeWidth="2.5" strokeLinecap="round" />
          <line x1="14" y1="34" x2="24" y2="24" stroke="#34d399" strokeWidth="2.5" strokeLinecap="round" />
          <line x1="34" y1="34" x2="24" y2="24" stroke="#c084fc" strokeWidth="2.5" strokeLinecap="round" />

          {/* 4 Corner Data Nodes */}
          <circle cx="14" cy="14" r="3.75" fill="#38bdf8" />
          <circle cx="34" cy="14" r="3.75" fill="#818cf8" />
          <circle cx="14" cy="34" r="3.75" fill="#34d399" />
          <circle cx="34" cy="34" r="3.75" fill="#c084fc" />

          {/* Core Central Reactor */}
          <circle cx="24" cy="24" r="6" fill="#071224" stroke="#38bdf8" strokeWidth="1.75" />
          <circle cx="24" cy="24" r="3.2" fill="url(#tqCoreGlow)" />
        </svg>
      </div>

      {/* Typography & Brand Meta */}
      <div className="flex flex-col text-left">
        <div className="flex items-center space-x-2">
          <span className={`font-black ${textSizes[size]} tracking-tight text-white leading-none`}>
            Transform<span className="text-[#00e5ff]">I</span><span className="text-[#93c5fd]">Q</span>
          </span>
          <span className={`uppercase font-black tracking-wider bg-[#062033] text-[#00f0ff] border border-[#0284c7]/60 shadow-[0_0_10px_rgba(0,240,255,0.15)] ${badgeSizes[size]}`}>
            AI
          </span>
        </div>
        {showSubtitle && (
          <span className="text-[11px] text-slate-400 font-medium tracking-wide mt-1 hidden sm:block">
            Chaos → Context → Blueprint
          </span>
        )}
      </div>
    </div>
  );
};
