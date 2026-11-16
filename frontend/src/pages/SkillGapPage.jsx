import React, { useState, useEffect } from 'react';
import { Target, Filter, Users, TrendingDown, Layers, BarChart3, AlertCircle } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { api } from '../api/client';
import { LoadingSpinner } from '../components/Modal';
import { SeverityBadge } from '../components/SeverityBadge';

export function SkillGapPage() {
  const [employees, setEmployees] = useState([]);
  const [selectedEmpId, setSelectedEmpId] = useState('');
  const [gapData, setGapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [activeTab, setActiveTab] = useState('individual'); // 'individual' or 'comparison'
  const [deptComparisons, setDeptComparisons] = useState([]);

  useEffect(() => {
    loadInitial();
  }, []);

  const loadInitial = async () => {
    try {
      setLoading(true);
      const emps = await api.getEmployees({ limit: 50 });
      setEmployees(emps);
      if (emps.length > 0) {
        setSelectedEmpId(emps[0].id);
        const gaps = await api.getEmployeeSkillGaps(emps[0].id);
        setGapData(gaps);
      }
      const dash = await api.getDashboard();
      setDeptComparisons(dash.department_skill_gaps || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEmployeeChange = async (empId) => {
    setSelectedEmpId(empId);
    try {
      setLoading(true);
      const gaps = await api.getEmployeeSkillGaps(empId);
      setGapData(gaps);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !gapData) return <LoadingSpinner message="Calculating skill gap analytics..." />;

  const filteredSkills = gapData?.skills?.filter((s) => {
    if (filterSeverity === 'ALL') return true;
    if (filterSeverity === 'GAPS_ONLY') return s.gap > 0;
    return s.severity === filterSeverity;
  }) || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
        <div>
          <h2 className="text-lg font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Target className="w-5 h-5 text-indigo-600" />
            Skill Gap Calculation & Matrix Engine
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real calculation: <span className="font-mono font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">Skill Gap = MAX(0, Required - Current)</span>
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex items-center gap-1.5 bg-slate-100 p-1.5 rounded-xl border border-slate-200 text-xs font-bold">
          <button
            onClick={() => setActiveTab('individual')}
            className={`px-3.5 py-1.5 rounded-lg transition-all duration-150 ${
              activeTab === 'individual' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Individual Gap Matrix
          </button>
          <button
            onClick={() => setActiveTab('comparison')}
            className={`px-3.5 py-1.5 rounded-lg transition-all duration-150 ${
              activeTab === 'comparison' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Department Benchmarks
          </button>
        </div>
      </div>

      {activeTab === 'individual' ? (
        <>
          {/* Controls: Employee Picker & Severity Filter */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-card">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Select Employee</label>
              <select
                value={selectedEmpId}
                onChange={(e) => handleEmployeeChange(e.target.value)}
                className="w-full text-xs font-semibold border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50"
              >
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name} ({emp.id}) — {emp.role_title} [{emp.department}]
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Filter by Severity</label>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="w-full text-xs font-semibold border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50"
              >
                <option value="ALL">All Competencies</option>
                <option value="GAPS_ONLY">All Gaps (Gap &gt; 0)</option>
                <option value="Critical">Critical Gaps Only</option>
                <option value="High">High Gaps Only</option>
                <option value="Medium">Medium Gaps Only</option>
                <option value="Low">Low Gaps Only</option>
                <option value="Met">Met / No Gap</option>
              </select>
            </div>

            <div className="flex items-center gap-6 border-l border-slate-100 pl-6">
              <div>
                <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider block">Role Readiness</span>
                <span className="text-2xl font-black text-indigo-600 font-mono">{gapData?.overall_readiness_pct}%</span>
              </div>
              <div className="h-10 w-px bg-slate-200" />
              <div>
                <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider block">Total Gap Shortfall</span>
                <span className="text-2xl font-black text-rose-600 font-mono">{gapData?.total_gap_points} pts</span>
              </div>
            </div>
          </div>

          {/* Interactive Gap Comparison Bar Chart */}
          {gapData && (
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-card">
              <div className="mb-4">
                <h3 className="text-sm font-extrabold text-slate-900 tracking-tight">Required vs Current Skill Proficiency (Levels 0 - 5)</h3>
                <p className="text-xs text-slate-500">Benchmark requirement comparison for {gapData.employee_name} ({gapData.role_title})</p>
              </div>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={filteredSkills} margin={{ top: 10, right: 10, left: -10, bottom: 35 }}>
                    <defs>
                      <linearGradient id="barCur" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#4f46e5" stopOpacity={0.9} />
                        <stop offset="100%" stopColor="#818cf8" stopOpacity={0.7} />
                      </linearGradient>
                      <linearGradient id="barReq" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#cbd5e1" stopOpacity={0.9} />
                        <stop offset="100%" stopColor="#e2e8f0" stopOpacity={0.7} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="skill_name" tick={{ fontSize: 11 }} angle={-20} textAnchor="end" interval={0} stroke="#94a3b8" />
                    <YAxis domain={[0, 5]} tick={{ fontSize: 11 }} stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '12px', color: '#fff', fontSize: '12px', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.3)' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                    <Bar dataKey="current_proficiency" name="Current Proficiency" fill="url(#barCur)" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="required_proficiency" name="Required Target" fill="url(#barReq)" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Skill Gap Analysis Table */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-sm font-extrabold text-slate-900">
                Detailed Competency Inventory ({filteredSkills.length} Skills)
              </h3>
              <span className="text-xs text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full font-bold border border-indigo-200">
                Role-Target Weighted
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200/80 bg-slate-50/70 text-slate-500 uppercase tracking-wider font-semibold">
                    <th className="py-3 px-4">Skill ID</th>
                    <th className="py-3 px-4">Skill Name</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4 text-center">Current</th>
                    <th className="py-3 px-4 text-center">Required Target</th>
                    <th className="py-3 px-4 text-center">Gap</th>
                    <th className="py-3 px-4 text-center">Severity</th>
                    <th className="py-3 px-4 text-center">Importance</th>
                    <th className="py-3 px-4 text-right">Readiness %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredSkills.map((s) => (
                    <tr key={s.skill_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-mono text-slate-400">{s.skill_id}</td>
                      <td className="py-3 px-4 font-bold text-slate-900">{s.skill_name}</td>
                      <td className="py-3 px-4 text-slate-500">{s.category}</td>
                      <td className="py-3 px-4 text-center font-bold font-mono text-slate-800">{s.current_proficiency} / 5</td>
                      <td className="py-3 px-4 text-center font-bold font-mono text-indigo-700">{s.required_proficiency} / 5</td>
                      <td className="py-3 px-4 text-center font-extrabold font-mono">
                        <span className={s.gap > 0 ? 'text-rose-600 text-sm' : 'text-emerald-600 text-sm'}>
                          {s.gap}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <SeverityBadge severity={s.severity} />
                      </td>
                      <td className="py-3 px-4 text-center font-semibold text-slate-600 font-mono">
                        {s.importance_weight}x
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-slate-900 font-mono">
                        {s.proficiency_pct}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        /* Department & Organization Comparisons */
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-card">
            <h3 className="text-sm font-extrabold text-slate-900 mb-1">Department Skill Gap & Readiness Comparison</h3>
            <p className="text-xs text-slate-500 mb-4">Average readiness score and total gap magnitude across enterprise units</p>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deptComparisons} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                  <XAxis dataKey="department" tick={{ fontSize: 11 }} angle={-10} textAnchor="end" interval={0} stroke="#94a3b8" />
                  <YAxis yAxisId="left" orientation="left" stroke="#4f46e5" tick={{ fontSize: 11 }} />
                  <YAxis yAxisId="right" orientation="right" stroke="#10b981" domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '12px', color: '#fff', fontSize: '12px', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.3)' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  <Bar yAxisId="left" dataKey="total_gap_points" name="Total Gap Points" fill="#4f46e5" radius={[6, 6, 0, 0]} />
                  <Bar yAxisId="right" dataKey="avg_readiness_pct" name="Avg Readiness %" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
            <div className="p-5 border-b border-slate-100 font-extrabold text-sm text-slate-900">
              Department Benchmark Summary
            </div>
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200/80 bg-slate-50/70 text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-5">Department</th>
                  <th className="py-3 px-4 text-right">Headcount</th>
                  <th className="py-3 px-4 text-right">Total Gap Points</th>
                  <th className="py-3 px-4 text-right">Avg Gap / Employee</th>
                  <th className="py-3 px-4 text-right">Critical Gaps</th>
                  <th className="py-3 px-5 text-right">Avg Readiness</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {deptComparisons.map((d) => (
                  <tr key={d.department} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-5 font-bold text-slate-900">{d.department}</td>
                    <td className="py-3.5 px-4 text-right text-slate-700 font-medium">{d.employee_count}</td>
                    <td className="py-3.5 px-4 text-right font-extrabold text-indigo-600 font-mono">{d.total_gap_points}</td>
                    <td className="py-3.5 px-4 text-right text-slate-700 font-medium font-mono">{d.avg_gap_per_emp}</td>
                    <td className="py-3.5 px-4 text-right font-extrabold text-rose-600 font-mono">{d.critical_gaps_count}</td>
                    <td className="py-3.5 px-5 text-right font-extrabold text-emerald-600 font-mono">{d.avg_readiness_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
