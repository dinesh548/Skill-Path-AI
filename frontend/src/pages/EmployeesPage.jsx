import React, { useState, useEffect } from 'react';
import { Search, Filter, User, ArrowRight, Target, Sparkles, TrendingUp, X, Mail, Building, Briefcase } from 'lucide-react';
import { api } from '../api/client';
import { LoadingSpinner, Modal } from '../components/Modal';
import { SeverityBadge, StatusBadge } from '../components/SeverityBadge';

const DEPT_COLORS = {
  Engineering: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  'Data Science': 'bg-sky-50 text-sky-700 border-sky-200',
  'Cloud Infrastructure': 'bg-cyan-50 text-cyan-700 border-cyan-200',
  Cybersecurity: 'bg-rose-50 text-rose-700 border-rose-200',
  'Product Management': 'bg-amber-50 text-amber-700 border-amber-200',
  'Quality Assurance': 'bg-emerald-50 text-emerald-700 border-emerald-200',
};

export function EmployeesPage({ onNavigateToRecommendations, onNavigateToCareer }) {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('');
  const [selectedEmp, setSelectedEmp] = useState(null);
  const [empGaps, setEmpGaps] = useState(null);
  const [gapsLoading, setGapsLoading] = useState(false);

  useEffect(() => {
    loadEmployees();
  }, [department]);

  const loadEmployees = async () => {
    try {
      setLoading(true);
      const params = { limit: 100 };
      if (department) params.department = department;
      if (search) params.search = search;
      const res = await api.getEmployees(params);
      setEmployees(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadEmployees();
  };

  const handleOpenProfile = async (emp) => {
    setSelectedEmp(emp);
    try {
      setGapsLoading(true);
      const gaps = await api.getEmployeeSkillGaps(emp.id);
      setEmpGaps(gaps);
    } catch (err) {
      console.error('Failed to load employee gaps', err);
    } finally {
      setGapsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
        <div>
          <h2 className="text-lg font-extrabold text-slate-900 tracking-tight">Workforce Directory</h2>
          <p className="text-xs text-slate-500 mt-0.5">Explore employee profiles, competency ratings, and personalized skill gap diagnostics</p>
        </div>

        <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[260px]">
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search name, EMP-ID, or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-3 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50 transition-all"
            />
          </div>

          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="text-xs border border-slate-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50 text-slate-700 font-semibold"
          >
            <option value="">All Departments</option>
            <option value="Engineering">Engineering</option>
            <option value="Data Science">Data Science</option>
            <option value="Cloud Infrastructure">Cloud Infrastructure</option>
            <option value="Cybersecurity">Cybersecurity</option>
            <option value="Product Management">Product Management</option>
            <option value="Quality Assurance">Quality Assurance</option>
          </select>

          <button
            type="submit"
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-600/20 transition-all hover:scale-102"
          >
            Filter
          </button>
        </form>
      </div>

      {/* Directory Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
        {loading ? (
          <LoadingSpinner message="Loading employee roster..." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200/80 bg-slate-50/70 text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="py-3.5 px-5">Employee</th>
                  <th className="py-3.5 px-4">Department</th>
                  <th className="py-3.5 px-4">Job Role & Tier</th>
                  <th className="py-3.5 px-4">Tenure Date</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {employees.map((emp) => (
                  <tr key={emp.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-5">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-indigo-700 text-white flex items-center justify-center font-bold text-xs shadow-sm">
                          {emp.name.charAt(0)}
                        </div>
                        <div>
                          <div className="font-bold text-slate-900 text-xs">{emp.name}</div>
                          <div className="text-[11px] font-mono text-slate-400">{emp.id} • {emp.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
                        DEPT_COLORS[emp.department] || 'bg-slate-100 text-slate-700 border-slate-200'
                      }`}>
                        {emp.department}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-900">{emp.role_title}</div>
                      <span className="text-[10px] text-slate-500 font-semibold px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 mt-0.5 inline-block">
                        {emp.role_level}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 font-mono">{emp.hire_date}</td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={emp.status} />
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <button
                        onClick={() => handleOpenProfile(emp)}
                        className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-bold rounded-lg text-xs transition-all"
                      >
                        Inspect Skills & Gaps
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Employee Profile & Skill Gap Modal */}
      <Modal
        isOpen={Boolean(selectedEmp)}
        onClose={() => { setSelectedEmp(null); setEmpGaps(null); }}
        title={`Employee Competency Profile: ${selectedEmp?.name} (${selectedEmp?.id})`}
        maxWidth="max-w-4xl"
      >
        {selectedEmp && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-5 rounded-2xl bg-gradient-to-r from-slate-50 to-indigo-50/30 border border-slate-200/80 text-xs">
              <div>
                <span className="text-slate-500 font-medium block">Department</span>
                <p className="font-bold text-slate-900 mt-0.5">{selectedEmp.department}</p>
              </div>
              <div>
                <span className="text-slate-500 font-medium block">Assigned Role</span>
                <p className="font-bold text-slate-900 mt-0.5">{selectedEmp.role_title}</p>
              </div>
              <div>
                <span className="text-slate-500 font-medium block">Hierarchy Tier</span>
                <p className="font-bold text-slate-900 mt-0.5">{selectedEmp.role_level}</p>
              </div>
              <div>
                <span className="text-slate-500 font-medium block">Role Readiness</span>
                <p className="font-extrabold text-indigo-600 text-base mt-0.5 font-mono">
                  {empGaps ? `${empGaps.overall_readiness_pct}%` : '...'}
                </p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  const empId = selectedEmp.id;
                  setSelectedEmp(null);
                  if (onNavigateToRecommendations) onNavigateToRecommendations(empId);
                }}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-600/20 transition-all"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Generate Recommendations</span>
              </button>
              <button
                onClick={() => {
                  const empId = selectedEmp.id;
                  setSelectedEmp(null);
                  if (onNavigateToCareer) onNavigateToCareer(empId);
                }}
                className="flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-all"
              >
                <TrendingUp className="w-3.5 h-3.5" />
                <span>View Career Pathway</span>
              </button>
            </div>

            {/* Detailed Skills & Gaps Table with Visual Level Meter */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Target className="w-4 h-4 text-indigo-600" />
                  Target Role Competencies & Gap Shortfalls
                </h4>
                <span className="text-xs font-mono text-slate-500">
                  Gap = MAX(0, Required - Current)
                </span>
              </div>

              {gapsLoading ? (
                <LoadingSpinner message="Calculating individual gaps..." />
              ) : empGaps?.skills ? (
                <div className="border border-slate-200/80 rounded-xl overflow-hidden shadow-xs">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200/80 bg-slate-50/70 text-slate-500 uppercase font-semibold">
                        <th className="py-2.5 px-4">Skill</th>
                        <th className="py-2.5 px-3">Category</th>
                        <th className="py-2.5 px-3">Proficiency Progress (0 - 5)</th>
                        <th className="py-2.5 px-3 text-center">Required</th>
                        <th className="py-2.5 px-3 text-center">Gap</th>
                        <th className="py-2.5 px-3 text-center">Severity</th>
                        <th className="py-2.5 px-4 text-right">Readiness %</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {empGaps.skills.map((s) => (
                        <tr key={s.skill_id} className="hover:bg-slate-50/60 transition-colors">
                          <td className="py-2.5 px-4 font-bold text-slate-900">{s.skill_name}</td>
                          <td className="py-2.5 px-3 text-slate-500">{s.category}</td>
                          <td className="py-2.5 px-3 w-48">
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-slate-100 h-2 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-indigo-600 rounded-full"
                                  style={{ width: `${(s.current_proficiency / 5) * 100}%` }}
                                />
                              </div>
                              <span className="font-mono font-bold text-[11px] text-slate-700">{s.current_proficiency}/5</span>
                            </div>
                          </td>
                          <td className="py-2.5 px-3 text-center font-bold text-indigo-700 font-mono">{s.required_proficiency}/5</td>
                          <td className="py-2.5 px-3 text-center font-extrabold font-mono">
                            <span className={s.gap > 0 ? 'text-rose-600' : 'text-emerald-600'}>
                              {s.gap}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-center">
                            <SeverityBadge severity={s.severity} />
                          </td>
                          <td className="py-2.5 px-4 text-right font-bold text-slate-800 font-mono">
                            {s.proficiency_pct}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
