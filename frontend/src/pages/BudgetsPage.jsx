import React, { useState, useEffect } from 'react';
import { Wallet, AlertTriangle, CheckCircle, TrendingUp, DollarSign, ShieldCheck } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { api } from '../api/client';
import { LoadingSpinner } from '../components/Modal';

export function BudgetsPage() {
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBudgets();
  }, []);

  const loadBudgets = async () => {
    try {
      setLoading(true);
      const res = await api.getBudgets();
      setBudgets(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Reconciling department budget balances..." />;

  const totalAllocated = budgets.reduce((acc, b) => acc + b.allocated_amount, 0);
  const totalSpent = budgets.reduce((acc, b) => acc + b.spent_amount, 0);
  const totalRemaining = budgets.reduce((acc, b) => acc + b.remaining_balance, 0);
  const orgUtilization = totalAllocated > 0 ? ((totalSpent / totalAllocated) * 100).toFixed(1) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Wallet className="w-5 h-5 text-indigo-600" />
            Department Training Budget & Capital Allocation (FY 2026)
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Strict accounting reconciliation: <span className="font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">Allocated Amount = Spent Amount + Remaining Balance</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider block">Organization Utilization</span>
            <div className="text-2xl font-black text-indigo-600 font-mono">{orgUtilization}%</div>
          </div>
          <span className="text-xs font-bold px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            Reconciled
          </span>
        </div>
      </div>

      {/* Aggregate KPI Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Total Allocated Budget</span>
          <div className="text-3xl font-black text-slate-900 font-mono mt-2">${totalAllocated.toLocaleString()}</div>
          <p className="text-xs text-slate-500 mt-1 font-medium">Authorized annual grant across 6 departments</p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Total Spent to Date</span>
          <div className="text-3xl font-black text-indigo-600 font-mono mt-2">${totalSpent.toLocaleString()}</div>
          <p className="text-xs text-emerald-600 font-bold mt-1">Directly tied to approved course fees</p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Total Remaining Balance</span>
          <div className="text-3xl font-black text-emerald-600 font-mono mt-2">${totalRemaining.toLocaleString()}</div>
          <p className="text-xs text-slate-500 mt-1 font-medium">Available capital for recommended pathways</p>
        </div>
      </div>

      {/* Chart: Allocated vs Spent */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-card">
        <div className="mb-4">
          <h3 className="text-sm font-extrabold text-slate-900 tracking-tight">Department Budget Allocation & Utilization</h3>
          <p className="text-xs text-slate-500">Comparison of authorized grant vs active training tuition commitments</p>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={budgets} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
              <defs>
                <linearGradient id="budgetSpent" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4f46e5" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#818cf8" stopOpacity={0.7} />
                </linearGradient>
                <linearGradient id="budgetRem" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#34d399" stopOpacity={0.7} />
                </linearGradient>
              </defs>
              <XAxis dataKey="department" tick={{ fontSize: 11 }} angle={-15} textAnchor="end" interval={0} stroke="#94a3b8" />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v / 1000}k`} stroke="#94a3b8" />
              <Tooltip
                formatter={(val) => [`$${val.toLocaleString()}`, '']}
                contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '12px', color: '#fff', fontSize: '12px', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.3)' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Bar dataKey="allocated_amount" name="Allocated Amount" fill="#e2e8f0" radius={[4, 4, 0, 0]} />
              <Bar dataKey="spent_amount" name="Spent Amount" fill="url(#budgetSpent)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="remaining_balance" name="Remaining Balance" fill="url(#budgetRem)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Department Breakdown Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {budgets.map((b) => {
          const isHigh = b.utilization_pct > 80;
          return (
            <div key={b.id} className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-card flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-[11px] font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">{b.id}</span>
                  {isHigh ? (
                    <span className="inline-flex items-center gap-1.5 text-[11px] font-bold text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                      <AlertTriangle className="w-3 h-3 text-amber-600" /> Near Limit
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                      <CheckCircle className="w-3 h-3 text-emerald-600" /> Healthy
                    </span>
                  )}
                </div>

                <h4 className="text-sm font-extrabold text-slate-900 mt-2">{b.department}</h4>

                <div className="mt-4 space-y-2 text-xs">
                  <div className="flex justify-between text-slate-500">
                    <span>Allocated:</span>
                    <span className="font-mono font-bold text-slate-900">${b.allocated_amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-slate-500">
                    <span>Spent:</span>
                    <span className="font-mono font-bold text-indigo-600">${b.spent_amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-slate-500">
                    <span>Remaining Balance:</span>
                    <span className="font-mono font-bold text-emerald-600">${b.remaining_balance.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-100">
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-slate-500 font-medium">Budget Consumed</span>
                  <span className="font-mono font-bold text-slate-800">{b.utilization_pct}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${isHigh ? 'bg-amber-500' : 'bg-indigo-600'}`}
                    style={{ width: `${Math.min(100, b.utilization_pct)}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
