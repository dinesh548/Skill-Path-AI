import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  CheckCircle2,
  XCircle,
  Clock,
  DollarSign,
  Users,
  ArrowRight,
  ShieldAlert,
  GraduationCap,
  ListOrdered,
  Bot,
  Zap,
  Target
} from 'lucide-react';
import { api } from '../api/client';
import { LoadingSpinner } from '../components/Modal';
import { SeverityBadge } from '../components/SeverityBadge';

export function RecommendationsPage({ initialEmployeeId, onNavigateToEnrollments }) {
  const [employees, setEmployees] = useState([]);
  const [selectedEmpId, setSelectedEmpId] = useState(initialEmployeeId || '');
  const [recommendationData, setRecommendationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrollingCourseId, setEnrollingCourseId] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);

  useEffect(() => {
    loadEmployees();
  }, []);

  useEffect(() => {
    if (selectedEmpId) {
      loadRecommendations(selectedEmpId);
    }
  }, [selectedEmpId]);

  const loadEmployees = async () => {
    try {
      const emps = await api.getEmployees({ limit: 100 });
      setEmployees(emps);
      if (!selectedEmpId && emps.length > 0) {
        setSelectedEmpId(emps[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadRecommendations = async (empId) => {
    try {
      setLoading(true);
      setActionMessage(null);
      const res = await api.getRecommendations(empId);
      setRecommendationData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (courseId) => {
    try {
      setEnrollingCourseId(courseId);
      setActionMessage(null);
      const res = await api.createEnrollment({
        employee_id: selectedEmpId,
        course_id: courseId,
        auto_approve: true
      });
      setActionMessage({ type: 'success', text: `Successfully enrolled in ${courseId}! Enrollment ID: ${res.enrollment_id}` });
      loadRecommendations(selectedEmpId);
    } catch (err) {
      setActionMessage({ type: 'error', text: err.message || 'Enrollment failed' });
    } finally {
      setEnrollingCourseId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Controls Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
        <div>
          <h2 className="text-lg font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            Intelligent Recommendation Engine (12-Step Architecture)
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Multi-constraint optimization: <span className="font-semibold text-indigo-700">Severity × Role Benchmarks × Prerequisite Gating × Department Budget</span>
          </p>
        </div>

        {/* Employee Picker */}
        <div className="min-w-[300px]">
          <label className="block text-xs font-bold text-slate-700 mb-1">Target Employee</label>
          <select
            value={selectedEmpId}
            onChange={(e) => setSelectedEmpId(e.target.value)}
            className="w-full text-xs font-semibold border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50"
          >
            {employees.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.name} ({emp.id}) — {emp.role_title} [{emp.department}]
              </option>
            ))}
          </select>
        </div>
      </div>

      {actionMessage && (
        <div className={`p-4 rounded-xl border text-xs font-bold ${
          actionMessage.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'
        }`}>
          {actionMessage.text}
        </div>
      )}

      {loading ? (
        <LoadingSpinner message="Evaluating 12-step recommendation constraints..." />
      ) : recommendationData ? (
        <div className="space-y-6">
          {/* Summary Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-5 rounded-2xl bg-white border border-slate-200/80 shadow-card text-xs">
            <div>
              <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px] block">Department / Role</span>
              <span className="font-bold text-slate-900 mt-0.5 block">{recommendationData.department}</span>
              <span className="text-slate-500 font-medium">{recommendationData.role_title}</span>
            </div>
            <div>
              <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px] block">Identified Skill Shortfalls</span>
              <span className="font-extrabold text-rose-600 font-mono text-base mt-0.5 block">{recommendationData.total_missing_skills} Skills</span>
              <span className="text-slate-500 font-medium">Require remediation</span>
            </div>
            <div>
              <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px] block">Feasible Courses Approved</span>
              <span className="font-extrabold text-emerald-600 font-mono text-base mt-0.5 block">{recommendationData.feasible_count} Courses</span>
              <span className="text-slate-500 font-medium">Prerequisites & budget verified</span>
            </div>
            <div>
              <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px] block">Gated Candidates Filtered</span>
              <span className="font-extrabold text-amber-600 font-mono text-base mt-0.5 block">{recommendationData.rejected_count} Filtered</span>
              <span className="text-slate-500 font-medium">Violations intercepted</span>
            </div>
          </div>

          {/* Ordered Learning Pathway Sequence */}
          {recommendationData.learning_pathway && recommendationData.learning_pathway.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-card">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-100">
                <div>
                  <h3 className="text-sm font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
                    <ListOrdered className="w-5 h-5 text-indigo-600" />
                    Recommended Sequential Learning Pathway
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">Chronological milestones structured to master foundational prerequisites before advanced topics</p>
                </div>
                <div className="text-right text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                  <span className="text-slate-500 font-medium">Total Pathway Investment: </span>
                  <span className="font-extrabold text-indigo-700 font-mono text-sm">${recommendationData.total_pathway_cost.toLocaleString()}</span>
                  <span className="text-slate-400 font-medium"> ({recommendationData.total_pathway_hours} training hrs)</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {recommendationData.learning_pathway.map((step) => (
                  <div key={step.sequence_step} className="p-5 rounded-2xl border border-indigo-100 bg-gradient-to-b from-indigo-50/40 to-white flex flex-col justify-between shadow-xs">
                    <div>
                      <div className="flex items-center justify-between text-xs mb-3">
                        <span className="w-7 h-7 rounded-xl bg-indigo-600 text-white font-extrabold flex items-center justify-center text-xs shadow-md shadow-indigo-500/25">
                          {step.sequence_step}
                        </span>
                        <span className="font-mono text-slate-400 font-bold text-[11px] bg-white px-2 py-0.5 rounded border border-slate-200">{step.course_id}</span>
                      </div>
                      <h4 className="text-xs font-extrabold text-slate-900 line-clamp-2 leading-snug">{step.course_title}</h4>
                      <p className="text-[11px] text-slate-600 mt-2 font-medium leading-relaxed">{step.rationale}</p>
                    </div>
                    <div className="mt-5 pt-3 border-t border-indigo-100/80 flex items-center justify-between text-xs font-mono">
                      <span className="text-slate-500 font-medium">{step.estimated_hours} hrs</span>
                      <span className="font-extrabold text-indigo-700">${step.cost.toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section: Feasible Recommendations with Explanations */}
          <div className="space-y-4">
            <h3 className="text-sm font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Feasible Course Recommendations ({recommendationData.feasible_count})
            </h3>

            {recommendationData.recommendations?.length === 0 ? (
              <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-slate-500 text-xs">
                No active training recommendations required or candidate courses exceed budget restrictions.
              </div>
            ) : (
              <div className="space-y-4">
                {recommendationData.recommendations.map((rec) => (
                  <div key={rec.course_id} className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-card hover:shadow-card-hover hover:border-indigo-200 transition-all duration-200">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-5">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap text-xs mb-1.5">
                          <span className="font-mono font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">{rec.course_id}</span>
                          <span className="font-extrabold text-slate-900 text-sm tracking-tight">{rec.course_title}</span>
                          <SeverityBadge severity={rec.gap_severity} />
                          <span className="px-2.5 py-0.5 rounded-full text-[11px] bg-indigo-50 text-indigo-700 font-bold border border-indigo-200">
                            Priority Score: {rec.priority_score}
                          </span>
                        </div>

                        {/* Explicit Positive Explanation Callout */}
                        <div className="mt-3 p-4 rounded-xl bg-gradient-to-r from-emerald-50/90 to-teal-50/50 border border-emerald-200/80 text-xs text-emerald-950 leading-relaxed font-medium shadow-2xs">
                          <div className="flex items-center gap-1.5 text-emerald-800 font-bold mb-1">
                            <Bot className="w-4 h-4 text-emerald-600" />
                            <span>Recommendation Explanation:</span>
                          </div>
                          {rec.explanation}
                        </div>

                        <div className="mt-3.5 flex flex-wrap items-center gap-4 text-xs text-slate-600">
                          <span className="flex items-center gap-1 font-medium">
                            <DollarSign className="w-3.5 h-3.5 text-slate-400" />
                            Cost: <strong className="text-slate-900 font-mono">${rec.cost.toLocaleString()}</strong>
                          </span>
                          <span className="flex items-center gap-1 font-medium">
                            <Clock className="w-3.5 h-3.5 text-slate-400" />
                            Duration: <strong className="text-slate-900 font-mono">{rec.duration_hours} hrs</strong>
                          </span>
                          <span className="flex items-center gap-1 font-medium">
                            <Users className="w-3.5 h-3.5 text-slate-400" />
                            Seats: <strong className="text-slate-900 font-mono">{rec.available_seats} remaining</strong>
                          </span>
                          <span className="text-slate-300">|</span>
                          <span className="text-[11px] text-slate-500 font-medium">
                            Target Competency: <strong className="text-indigo-700">{rec.primary_skill}</strong> (Gap: {rec.skill_gap})
                          </span>
                        </div>
                      </div>

                      <div className="flex-shrink-0 self-end md:self-center">
                        <button
                          onClick={() => handleEnroll(rec.course_id)}
                          disabled={enrollingCourseId === rec.course_id}
                          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-600/25 transition-all hover:scale-102 disabled:opacity-50"
                        >
                          <GraduationCap className="w-4 h-4" />
                          <span>{enrollingCourseId === rec.course_id ? 'Enrolling...' : 'Enroll Learner'}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section: Rejected Recommendations with Explicit Rejection Reasons */}
          <div className="space-y-4">
            <h3 className="text-sm font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <XCircle className="w-4 h-4 text-rose-600" />
              Rejected Candidate Courses ({recommendationData.rejected_count})
            </h3>
            <p className="text-xs text-slate-500">
              System enforces non-negotiable gates: prerequisite compliance, budget ceilings, capacity limits, and schedule windows.
            </p>

            <div className="space-y-3">
              {recommendationData.rejected_recommendations?.map((rej, idx) => (
                <div key={idx} className="bg-white rounded-2xl border border-slate-200/80 p-5 border-l-4 border-l-rose-500 text-xs shadow-xs">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-extrabold text-slate-900">{rej.course_title} ({rej.course_id})</span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-rose-50 text-rose-700 border border-rose-200">
                      {rej.rejection_category}
                    </span>
                  </div>
                  {/* Explicit Rejection Explanation */}
                  <div className="text-rose-950 font-medium bg-rose-50/70 p-3 rounded-xl border border-rose-100 leading-relaxed">
                    <span className="font-bold text-rose-800">Rejection Reason: </span>
                    {rej.reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
