import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export function StatCard({ title, value, subtext, icon: Icon, color = 'indigo', trend, trendPositive = true }) {
  const colorMap = {
    indigo: {
      bg: 'from-indigo-500/10 to-indigo-500/5',
      border: 'hover:border-indigo-300/80',
      iconBg: 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25',
      badge: 'bg-indigo-50 text-indigo-700',
    },
    sky: {
      bg: 'from-sky-500/10 to-sky-500/5',
      border: 'hover:border-sky-300/80',
      iconBg: 'bg-sky-500 text-white shadow-md shadow-sky-500/25',
      badge: 'bg-sky-50 text-sky-700',
    },
    emerald: {
      bg: 'from-emerald-500/10 to-emerald-500/5',
      border: 'hover:border-emerald-300/80',
      iconBg: 'bg-emerald-600 text-white shadow-md shadow-emerald-500/25',
      badge: 'bg-emerald-50 text-emerald-700',
    },
    amber: {
      bg: 'from-amber-500/10 to-amber-500/5',
      border: 'hover:border-amber-300/80',
      iconBg: 'bg-amber-500 text-white shadow-md shadow-amber-500/25',
      badge: 'bg-amber-50 text-amber-700',
    },
    rose: {
      bg: 'from-rose-500/10 to-rose-500/5',
      border: 'hover:border-rose-300/80',
      iconBg: 'bg-rose-500 text-white shadow-md shadow-rose-500/25',
      badge: 'bg-rose-50 text-rose-700',
    },
    purple: {
      bg: 'from-purple-500/10 to-purple-500/5',
      border: 'hover:border-purple-300/80',
      iconBg: 'bg-purple-600 text-white shadow-md shadow-purple-500/25',
      badge: 'bg-purple-50 text-purple-700',
    },
  };

  const c = colorMap[color] || colorMap.indigo;

  return (
    <div className={`relative bg-white rounded-2xl border border-slate-200/80 p-5 shadow-card hover:shadow-card-hover transition-all duration-200 overflow-hidden group ${c.border}`}>
      {/* Background soft glow gradient */}
      <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${c.bg} rounded-bl-full pointer-events-none transition-opacity opacity-70 group-hover:opacity-100`} />

      <div className="relative flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</p>
        {Icon && (
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-105 duration-200 ${c.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="relative mt-3 flex items-baseline gap-2">
        <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight font-mono">{value}</h3>
        {trend && (
          <span className={`inline-flex items-center text-xs font-semibold px-1.5 py-0.5 rounded ${
            trendPositive ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
          }`}>
            {trendPositive ? <ArrowUpRight className="w-3 h-3 mr-0.5" /> : <ArrowDownRight className="w-3 h-3 mr-0.5" />}
            {trend}
          </span>
        )}
      </div>

      {subtext && (
        <p className="relative mt-1 text-xs text-slate-500 font-medium leading-relaxed">{subtext}</p>
      )}
    </div>
  );
}
