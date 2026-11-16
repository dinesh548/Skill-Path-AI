import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Award,
  BookOpen,
  DollarSign,
  Clock,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Target,
  Sparkles,
  ChevronRight,
  Layers,
  GraduationCap,
  Briefcase,
  Zap,
  BarChart3,
  Calendar
} from 'lucide-react';
import { api } from '../api/client';
import { LoadingSpinner, EmptyState } from '../components/Modal';

export function CareerPathwaysPage({ initialEmployeeId, onNavigateToRecommendations }) {
  const [employees, setEmployees] = useState([]);
  const [selectedEmpId, setSelectedEmpId] = useState(initialEmployeeId || '');
  const [roles, setRoles] = useState([]);
  const [targetRoleId, setTargetRoleId] = useState('');
  const [careerData, setCareerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrollingCourseId, setEnrollingCourseId] = useState(null);
  const [enrollSuccessMsg, setEnrollSuccessMsg] = useState('');

  useEffect(() => {
    loadInitial();
  }, []);

  useEffect(() => {
    if (selectedEmpId) {
      loadPathway(selectedEmpId, targetRoleId);
    }
  }, [selectedEmpId, targetRoleId]);

  const loadInitial = async () => {
    try {
      const emps = await api.getEmployees({ limit: 100 });
      const rls = await api.getRoles();
      setEmployees(emps);
      setRoles(rls);
      if (!selectedEmpId && emps.length > 0) {
        setSelectedEmpId(emps[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadPathway = async (empId, tRoleId) => {
    try {
      setLoading(true);
      const res = await api.getCareerPathway(empId, tRoleId || null);
      setCareerData(res);
      if (!targetRoleId && res.target_role?.id) {
        setTargetRoleId(res.target_role.id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickEnroll = async (courseId) => {
    try {
      setEnrollingCourseId(courseId);
      setEnrollSuccessMsg('');
      await api.createEnrollment({
        employee_id: selectedEmpId,
        course_id: courseId
      });
      setEnrollSuccessMsg(`Successfully enrolled in ${courseId}!`);
      setTimeout(() => setEnrollSuccessMsg(''), 4000);
    } catch (err) {
      alert(`Enrollment Notice: ${err.message || 'Could not complete enrollment'}`);
    } finally {
      setEnrollingCourseId(null);
    }
  };

  const selectedEmployee = employees.find((e) => e.id === selectedEmpId);

  return (
    <div className="space-y-6">
      {/* Header & Controls Panel */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-soft">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-sm">
                <TrendingUp className="w-5 h-5" />
              </span>
              <div>
                <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                  Career Pathway & Succession Architecture
                </h2>
                <p className="text-xs text-slate-500 font-medium">
                  Dynamic competency-based mobility: calculate promotion readiness, missing skill matrices, and targeted upskilling roadmaps
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 bg-slate-50/80 p-2 rounded-xl border border-slate-200">
            <div>
              <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-0.5">
                Active Employee
              </label>
              <select
                value={selectedEmpId}
                onChange={(e) => {
                  setSelectedEmpId(e.target.value);
                  setTargetRoleId('');
                }}
                className="text-xs font-semibold border border-slate-200 rounded-lg py-1.5 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 shadow-xs cursor-pointer min-w-[200px]"
              >
                {employees.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.name} ({e.id}) - {e.role_title}
                  </option>
                ))}
              </select>
            </div>

            <div className="text-slate-300">/</div>

            <div>
              <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-0.5">
                Target Promotional Role
              </label>
              <select
                value={targetRoleId}
                onChange={(e) => setTargetRoleId(e.target.value)}
                className="text-xs font-semibold border border-slate-200 rounded-lg py-1.5 px-3 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 shadow-xs cursor-pointer min-w-[220px]"
              >
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.title} ({r.department} • {r.level})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {enrollSuccessMsg && (
          <div className="mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-semibold flex items-center gap-2 animate-fadeIn">
            <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>{enrollSuccessMsg}</span>
          </div>
        )}
      </div>

      {loading ? (
        <LoadingSpinner message="Calculating career competency transition and pathway roadmap..." />
      ) : careerData ? (
        <div className="space-y-6">
          {/* Executive Career Transition Hero Card */}
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 text-white p-7 shadow-lg border border-slate-800">
            {/* Background glowing ambient orbs */}
            <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute bottom-0 left-1/3 -mb-10 w-60 h-60 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />

            <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-8">
              {/* Transition Nodes */}
              <div className="space-y-4 max-w-2xl">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-indigo-200 text-[11px] font-semibold border border-white/10 backdrop-blur-sm">
                  <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                  <span>Succession & Growth Pathway Analysis</span>
                  <span className="text-white/40">•</span>
                  <span className="text-white font-mono">{careerData.department}</span>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-2xl font-black tracking-tight">
                  <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-4 py-2 rounded-xl">
                    <Briefcase className="w-5 h-5 text-slate-400" />
                    <span className="text-white">{careerData.current_role.title}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-bold uppercase ml-1">
                      {careerData.current_role.level}
                    </span>
                  </div>

                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-400/40 text-indigo-300">
                    <ArrowRight className="w-4 h-4" />
                  </div>

                  <div className="flex items-center gap-2 bg-gradient-to-r from-brand-600/30 to-purple-600/30 border border-brand-400/50 px-4 py-2 rounded-xl text-cyan-200 shadow-inner">
                    <Award className="w-5 h-5 text-amber-400" />
                    <span>{careerData.target_role.title}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-brand-500/40 text-brand-200 font-bold uppercase ml-1">
                      {careerData.target_role.level}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed max-w-xl">
                  {careerData.summary}
                </p>

                {/* Candidate Quick Stats */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
                  <div className="bg-white/5 border border-white/10 rounded-xl p-3">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">
                      Required Training
                    </span>
                    <span className="text-base font-bold text-white mt-0.5 block flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-cyan-400" />
                      {careerData.estimated_learning_hours} Hours
                    </span>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-xl p-3">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">
                      Upskilling Cost
                    </span>
                    <span className="text-base font-bold text-white mt-0.5 block flex items-center gap-1.5">
                      <DollarSign className="w-4 h-4 text-emerald-400" />
                      ${careerData.estimated_total_cost.toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-xl p-3 col-span-2 sm:col-span-1">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">
                      Competency Gaps
                    </span>
                    <span className="text-base font-bold text-white mt-0.5 block flex items-center gap-1.5">
                      <Target className="w-4 h-4 text-rose-400" />
                      {careerData.missing_competencies_count} Deficits
                    </span>
                  </div>
                </div>
              </div>

              {/* Circular Readiness Gauge Card */}
              <div className="flex flex-col items-center justify-center bg-white/10 backdrop-blur-md p-6 rounded-2xl border border-white/20 shadow-xl min-w-[220px]">
                <div className="relative w-32 h-32 flex items-center justify-center">
                  {/* SVG Circle Progress */}
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      className="text-white/10"
                      strokeWidth="10"
                      stroke="currentColor"
                      fill="transparent"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      className={
                        careerData.career_readiness_pct >= 80
                          ? 'text-emerald-400'
                          : careerData.career_readiness_pct >= 50
                          ? 'text-cyan-400'
                          : 'text-amber-400'
                      }
                      strokeWidth="10"
                      strokeDasharray={2 * Math.PI * 40}
                      strokeDashoffset={
                        2 * Math.PI * 40 * (1 - (careerData.career_readiness_pct || 0) / 100)
                      }
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="transparent"
                      style={{ transition: 'stroke-dashoffset 0.8s ease-in-out' }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                    <span className="text-3xl font-black tracking-tight text-white">
                      {careerData.career_readiness_pct}%
                    </span>
                    <span className="text-[9px] uppercase tracking-wider font-extrabold text-cyan-200">
                      Readiness
                    </span>
                  </div>
                </div>

                <div className="mt-3 text-center">
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-[11px] font-bold ${
                      careerData.career_readiness_pct >= 80
                        ? 'bg-emerald-400/20 text-emerald-300 border border-emerald-400/30'
                        : careerData.career_readiness_pct >= 50
                        ? 'bg-cyan-400/20 text-cyan-200 border border-cyan-400/30'
                        : 'bg-amber-400/20 text-amber-200 border border-amber-400/30'
                    }`}
                  >
                    {careerData.career_readiness_pct >= 80
                      ? 'Promotion Ready'
                      : careerData.career_readiness_pct >= 50
                      ? 'Developing Candidate'
                      : 'Early Progression'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Department Career Ladder Visualization */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-soft">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-brand-600" />
                  Succession Progression Track • {careerData.department}
                </h3>
                <p className="text-xs text-slate-500 font-medium">
                  Linear promotional sequence from entry-level to principal leadership
                </p>
              </div>
              <span className="text-[11px] font-bold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg">
                {careerData.career_ladder.length} Career Tiers
              </span>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch justify-between gap-3 overflow-x-auto py-5">
              {careerData.career_ladder.map((step, idx) => {
                const isSelectedAsTarget = targetRoleId === step.role_id;
                return (
                  <React.Fragment key={step.role_id}>
                    <div
                      onClick={() => !step.is_current && setTargetRoleId(step.role_id)}
                      className={`flex-1 min-w-[170px] p-4 rounded-xl border transition-all duration-200 cursor-pointer relative ${
                        step.is_current
                          ? 'bg-slate-900 text-white border-slate-900 shadow-md ring-2 ring-slate-800'
                          : isSelectedAsTarget
                          ? 'bg-gradient-to-b from-brand-50/80 to-indigo-50/80 border-brand-500 text-slate-900 shadow-md ring-2 ring-brand-500/30'
                          : 'bg-slate-50/60 hover:bg-white hover:border-slate-300 border-slate-200 text-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span
                          className={`text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded ${
                            step.is_current
                              ? 'bg-white/20 text-white'
                              : isSelectedAsTarget
                              ? 'bg-brand-100 text-brand-800'
                              : 'bg-slate-200/70 text-slate-600'
                          }`}
                        >
                          {step.level}
                        </span>
                        {step.is_current && (
                          <span className="flex h-2 w-2 relative">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                          </span>
                        )}
                        {isSelectedAsTarget && (
                          <Award className="w-4 h-4 text-amber-500" />
                        )}
                      </div>

                      <h4 className="text-xs font-bold line-clamp-1 mb-2">
                        {step.title}
                      </h4>

                      <div className="text-[10px] font-bold">
                        {step.is_current ? (
                          <span className="text-emerald-400">● Current Role</span>
                        ) : isSelectedAsTarget ? (
                          <span className="text-brand-700 font-extrabold">★ Target Candidate</span>
                        ) : (
                          <span className="text-slate-400 hover:text-brand-600">Click to Simulate →</span>
                        )}
                      </div>
                    </div>

                    {idx < careerData.career_ladder.length - 1 && (
                      <div className="flex items-center justify-center text-slate-300 hidden sm:flex">
                        <ChevronRight className="w-5 h-5 flex-shrink-0" />
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>

          {/* Target Role Competency Breakdown Matrix */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-soft overflow-hidden">
            <div className="p-5 border-b border-slate-100 bg-slate-50/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-brand-600" />
                  Target Role Competency Matrix: {careerData.target_role.title}
                </h3>
                <p className="text-xs text-slate-500 font-medium">
                  Detailed assessment of employee current proficiency vs target role benchmark expectations
                </p>
              </div>

              <div className="flex items-center gap-2 text-xs">
                <span className="px-2.5 py-1 bg-rose-50 text-rose-700 border border-rose-200 rounded-lg font-bold">
                  {careerData.missing_competencies_count} Deficit Skills
                </span>
                <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg font-bold">
                  {careerData.competency_breakdown.filter((c) => c.status === 'MET').length} Qualified Skills
                </span>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/40 text-[11px] text-slate-500 uppercase font-bold tracking-wider">
                    <th className="py-3 px-5">Competency Skill</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4 text-center">Current Prof</th>
                    <th className="py-3 px-4 text-center">Target Prof</th>
                    <th className="py-3 px-4 text-center">Proficiency Meter</th>
                    <th className="py-3 px-4 text-center">Gap</th>
                    <th className="py-3 px-4 text-center">Status</th>
                    <th className="py-3 px-4 text-center">Weight</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {careerData.competency_breakdown.map((c) => (
                    <tr key={c.skill_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-5">
                        <span className="font-bold text-slate-900 block">{c.skill_name}</span>
                        <span className="font-mono text-[10px] text-slate-400">{c.skill_id}</span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-slate-100 text-slate-700">
                          {c.category}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="font-mono font-bold text-slate-800 text-sm">
                          {c.current_proficiency}
                        </span>
                        <span className="text-slate-400 text-[10px]"> / 5</span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="font-mono font-bold text-brand-700 text-sm">
                          {c.target_proficiency}
                        </span>
                        <span className="text-slate-400 text-[10px]"> / 5</span>
                      </td>
                      {/* Step Progress Blocks */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center justify-center gap-1">
                          {[1, 2, 3, 4, 5].map((lvl) => {
                            const isCurrent = lvl <= c.current_proficiency;
                            const isTarget = lvl <= c.target_proficiency;
                            return (
                              <div
                                key={lvl}
                                title={`Level ${lvl}`}
                                className={`w-4 h-3 rounded-xs ${
                                  isCurrent
                                    ? 'bg-emerald-500 shadow-2xs'
                                    : isTarget
                                    ? 'bg-amber-300 border border-amber-400/50'
                                    : 'bg-slate-100'
                                }`}
                              />
                            );
                          })}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span
                          className={`font-mono font-bold text-sm ${
                            c.gap > 0 ? 'text-rose-600' : 'text-emerald-600'
                          }`}
                        >
                          {c.gap > 0 ? `-${c.gap}` : '0'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            c.status === 'MET'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : c.status === 'PARTIAL'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-rose-50 text-rose-700 border border-rose-200'
                          }`}
                        >
                          {c.status === 'MET' && <CheckCircle className="w-3 h-3 text-emerald-600" />}
                          {c.status === 'PARTIAL' && <Zap className="w-3 h-3 text-amber-600" />}
                          {c.status === 'UNMET' && <AlertCircle className="w-3 h-3 text-rose-600" />}
                          <span>{c.status}</span>
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center text-slate-600 font-mono font-medium">
                        {c.importance_weight}x
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recommended Bridge Courses for Career Progression */}
          {careerData.recommended_courses && careerData.recommended_courses.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-soft">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3 mb-5">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-brand-600" />
                    Recommended Career Upskilling Roadmap
                  </h3>
                  <p className="text-xs text-slate-500 font-medium">
                    Courses prioritized to bridge gaps for promotional transition to {careerData.target_role.title}
                  </p>
                </div>
                <button
                  onClick={() =>
                    onNavigateToRecommendations &&
                    onNavigateToRecommendations(careerData.employee_id)
                  }
                  className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white rounded-xl text-xs font-bold shadow-xs transition-all self-start sm:self-auto cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                  <span>Open Full AI Recommendation Engine</span>
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {careerData.recommended_courses.map((crs) => (
                  <div
                    key={crs.course_id}
                    className="p-5 rounded-xl border border-slate-200 bg-gradient-to-b from-white to-slate-50/50 hover:border-brand-300 hover:shadow-md transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                          {crs.course_id}
                        </span>
                        <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                          {crs.provider}
                        </span>
                      </div>

                      <h4 className="text-xs font-bold text-slate-900 line-clamp-2 leading-snug">
                        {crs.title}
                      </h4>

                      <div className="mt-3 p-2.5 rounded-lg bg-brand-50/60 border border-brand-100 text-[11px] text-slate-700">
                        <span className="text-[10px] font-bold uppercase text-brand-800 block">
                          Addressed Promotion Competency:
                        </span>
                        <strong className="text-brand-900">{crs.skill_addressed}</strong>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100">
                      <div className="flex items-center justify-between text-xs mb-3">
                        <span className="text-slate-500 font-medium flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          {crs.duration_hours} hrs
                        </span>
                        <span className="font-mono font-bold text-slate-900 text-sm">
                          ${crs.cost.toLocaleString()}
                        </span>
                      </div>

                      <button
                        onClick={() => handleQuickEnroll(crs.course_id)}
                        disabled={enrollingCourseId === crs.course_id}
                        className="w-full flex items-center justify-center gap-1.5 py-2 px-3 bg-brand-50 hover:bg-brand-100 text-brand-700 border border-brand-200 rounded-lg text-xs font-bold transition-colors cursor-pointer disabled:opacity-60"
                      >
                        <GraduationCap className="w-3.5 h-3.5" />
                        <span>
                          {enrollingCourseId === crs.course_id
                            ? 'Enrolling...'
                            : 'Quick Enroll in Pathway'}
                        </span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          title="No Career Pathway Data"
          description="Select an employee and target promotional role above to view the career trajectory analysis."
        />
      )}
    </div>
  );
}
