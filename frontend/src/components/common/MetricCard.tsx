import React from 'react';
import { LucideIcon } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: string;
  trendPositive?: boolean;
  icon: LucideIcon;
  variant?: 'blue' | 'emerald' | 'purple' | 'amber' | 'rose' | 'indigo';
}

const variantStyles = {
  blue: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
    text: 'text-blue-400',
    iconBg: 'bg-blue-500/20 text-blue-400',
  },
  emerald: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
    text: 'text-emerald-400',
    iconBg: 'bg-emerald-500/20 text-emerald-400',
  },
  purple: {
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/20',
    text: 'text-purple-400',
    iconBg: 'bg-purple-500/20 text-purple-400',
  },
  amber: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/20',
    text: 'text-amber-400',
    iconBg: 'bg-amber-500/20 text-amber-400',
  },
  rose: {
    bg: 'bg-rose-500/10',
    border: 'border-rose-500/20',
    text: 'text-rose-400',
    iconBg: 'bg-rose-500/20 text-rose-400',
  },
  indigo: {
    bg: 'bg-indigo-500/10',
    border: 'border-indigo-500/20',
    text: 'text-indigo-400',
    iconBg: 'bg-indigo-500/20 text-indigo-400',
  },
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  trendPositive = true,
  icon: Icon,
  variant = 'blue',
}) => {
  const { t } = useLanguage();
  const style = variantStyles[variant];

  return (
    <div className={`p-3.5 sm:p-5 rounded-xl border ${style.border} ${style.bg} backdrop-blur-md relative overflow-hidden transition-all duration-200 hover:border-slate-600`}>
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider text-slate-400 truncate">{t(title, title)}</p>
          <h3 className="text-lg sm:text-2xl font-bold text-slate-100 mt-1 truncate">{value}</h3>
          {subtitle && <p className="text-[10px] sm:text-xs text-slate-400 mt-0.5 truncate">{t(subtitle, subtitle)}</p>}
        </div>
        <div className={`p-2 sm:p-3 rounded-lg ${style.iconBg} shrink-0`}>
          <Icon className="w-4 h-4 sm:w-5 sm:h-5" />
        </div>
      </div>
      {trend && (
        <div className="mt-2.5 sm:mt-3.5 pt-2 sm:pt-3 border-t border-slate-800/80 flex items-center text-[10px] sm:text-xs truncate">
          <span className={`font-semibold shrink-0 ${trendPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {t(trend, trend)}
          </span>
          <span className="text-slate-500 ml-1.5 truncate hidden xs:inline">{t('vs benchmark', 'vs benchmark')}</span>
        </div>
      )}
    </div>
  );
};
