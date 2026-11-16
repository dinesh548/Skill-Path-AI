import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Clock, XCircle, ShieldCheck } from 'lucide-react';

export function SeverityBadge({ severity }) {
  const configs = {
    Critical: {
      bg: 'bg-rose-50 text-rose-700 border-rose-200/80',
      dot: 'bg-rose-500 glow-dot-rose',
      icon: AlertCircle,
    },
    High: {
      bg: 'bg-amber-50 text-amber-700 border-amber-200/80',
      dot: 'bg-amber-500 glow-dot-amber',
      icon: AlertTriangle,
    },
    Medium: {
      bg: 'bg-indigo-50 text-indigo-700 border-indigo-200/80',
      dot: 'bg-indigo-500 glow-dot-brand',
      icon: Clock,
    },
    Low: {
      bg: 'bg-slate-100 text-slate-700 border-slate-200/80',
      dot: 'bg-slate-400',
      icon: Clock,
    },
    Met: {
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
      dot: 'bg-emerald-500 glow-dot-emerald',
      icon: CheckCircle2,
    }
  };

  const cfg = configs[severity] || configs.Low;
  const Icon = cfg.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${cfg.bg} shadow-xs`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      <span>{severity}</span>
    </span>
  );
}

export function StatusBadge({ status }) {
  const configs = {
    ACTIVE: { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200/80', dot: 'bg-emerald-500 glow-dot-emerald' },
    AVAILABLE: { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200/80', dot: 'bg-emerald-500 glow-dot-emerald' },
    COMPLETED: { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200/80', dot: 'bg-emerald-500 glow-dot-emerald' },
    APPROVED: { bg: 'bg-sky-50 text-sky-700 border-sky-200/80', dot: 'bg-sky-500' },
    IN_PROGRESS: { bg: 'bg-indigo-50 text-indigo-700 border-indigo-200/80', dot: 'bg-indigo-500 animate-pulse' },
    PENDING: { bg: 'bg-amber-50 text-amber-700 border-amber-200/80', dot: 'bg-amber-500' },
    CANCELLED: { bg: 'bg-slate-100 text-slate-600 border-slate-200/80', dot: 'bg-slate-400' },
    REJECTED: { bg: 'bg-rose-50 text-rose-700 border-rose-200/80', dot: 'bg-rose-500' },
    EXPIRED: { bg: 'bg-rose-50 text-rose-700 border-rose-200/80', dot: 'bg-rose-500' },
    OPEN: { bg: 'bg-rose-50 text-rose-700 border-rose-200/80', dot: 'bg-rose-500 glow-dot-rose' },
    RESOLVED: { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200/80', dot: 'bg-emerald-500 glow-dot-emerald' },
    ACKNOWLEDGED: { bg: 'bg-amber-50 text-amber-700 border-amber-200/80', dot: 'bg-amber-500' },
  };

  const cfg = configs[status] || { bg: 'bg-slate-100 text-slate-700 border-slate-200/80', dot: 'bg-slate-400' };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${cfg.bg} shadow-xs`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      <span>{status}</span>
    </span>
  );
}
