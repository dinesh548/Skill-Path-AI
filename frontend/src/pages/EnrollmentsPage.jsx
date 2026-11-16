import React, { useState, useEffect } from 'react';
import {
  GraduationCap,
  Plus,
  CheckCircle,
  XCircle,
  Play,
  Award,
  Filter,
  Search,
  AlertCircle,
  Clock,
  Sparkles
} from 'lucide-react';
import { api } from '../api/client';
import { LoadingSpinner, Modal } from '../components/Modal';
import { StatusBadge } from '../components/SeverityBadge';

export function EnrollmentsPage() {
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [actionMsg, setActionMsg] = useState(null);

  // New Enrollment Modal
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);
  const [employees, setEmployees] = useState([]);
  const [courses, setCourses] = useState([]);
  const [newEmpId, setNewEmpId] = useState('');
  const [newCourseId, setNewCourseId] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Completion Modal
  const [isCompleteModalOpen, setIsCompleteModalOpen] = useState(false);
  const [selectedEnrId, setSelectedEnrId] = useState('');
  const [assessmentScore, setAssessmentScore] = useState(85.0);

  useEffect(() => {
    loadEnrollments();
  }, [statusFilter]);

  const loadEnrollments = async () => {
    try {
      setLoading(true);
      const params = { limit: 100 };
      if (statusFilter) params.status = statusFilter;
      const res = await api.getEnrollments(params);
      setEnrollments(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenNewEnrollment = async () => {
    try {
      const emps = await api.getEmployees({ limit: 100 });
      const crss = await api.getCourses({ limit: 100, status: 'AVAILABLE' });
      setEmployees(emps);
      setCourses(crss);
      if (emps.length > 0) setNewEmpId(emps[0].id);
      if (crss.length > 0) setNewCourseId(crss[0].id);
      setIsNewModalOpen(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmitEnrollment = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setActionMsg(null);
      const res = await api.createEnrollment({
        employee_id: newEmpId,
        course_id: newCourseId,
        auto_approve: false
      });
      setIsNewModalOpen(false);
      setActionMsg({ type: 'success', text: `Enrollment submitted! Status: ${res.status}` });
      loadEnrollments();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.message || 'Enrollment rejected' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleApprove = async (enrId) => {
    try {
      setActionMsg(null);
      await api.updateEnrollment(enrId, { status: 'APPROVED' });
      setActionMsg({ type: 'success', text: `Enrollment ${enrId} approved and departmental budget charged.` });
      loadEnrollments();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.message || 'Approval failed' });
    }
  };

  const handleStart = async (enrId) => {
    try {
      setActionMsg(null);
      await api.updateEnrollment(enrId, { status: 'IN_PROGRESS' });
      setActionMsg({ type: 'success', text: `Training started for enrollment ${enrId}.` });
      loadEnrollments();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.message || 'Failed to start course' });
    }
  };

  const handleCancel = async (enrId) => {
    try {
      setActionMsg(null);
      await api.updateEnrollment(enrId, { status: 'CANCELLED' });
      setActionMsg({ type: 'success', text: `Enrollment ${enrId} cancelled and seat/budget refunded.` });
      loadEnrollments();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.message || 'Failed to cancel enrollment' });
    }
  };

  const handleRecordCompletion = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setActionMsg(null);
      const res = await api.recordCompletion({
        enrollment_id: selectedEnrId,
        assessment_score: parseFloat(assessmentScore)
      });
      setIsCompleteModalOpen(false);
      setActionMsg({
        type: 'success',
        text: `Completion verified (Score: ${assessmentScore}%). Note: Skill proficiency will only update after formal reassessment examination.`
      });
      loadEnrollments();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.message || 'Completion recording failed' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleReassess = async (cmpId) => {
    try {
      setActionMsg(null);
      const res = await api.reassessCompletion(cmpId);
      setActionMsg({
        type: 'success',
        text: `Reassessment finalized! ${res.message}`
      });
      loadEnrollments();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.message || 'Reassessment failed' });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
        <div>
          <h2 className="text-lg font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-indigo-600" />
            Learning Lifecycle & Enrollment Management
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Operational governance: <span className="font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">Attendance ≠ Completion ≠ Skill Improvement</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs border border-slate-200 rounded-xl px-3 py-2.5 bg-slate-50/50 font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="PENDING">PENDING</option>
            <option value="APPROVED">APPROVED</option>
            <option value="IN_PROGRESS">IN_PROGRESS</option>
            <option value="COMPLETED">COMPLETED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>

          <button
            onClick={handleOpenNewEnrollment}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-600/20 transition-all hover:scale-102"
          >
            <Plus className="w-4 h-4" />
            <span>New Enrollment</span>
          </button>
        </div>
      </div>

      {actionMsg && (
        <div className={`p-4 rounded-xl border text-xs font-bold ${
          actionMsg.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'
        }`}>
          {actionMsg.text}
        </div>
      )}

      {/* Enrollments Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
        {loading ? (
          <LoadingSpinner message="Loading enrollment records..." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200/80 bg-slate-50/70 text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="py-3.5 px-5">Enrollment ID</th>
                  <th className="py-3.5 px-4">Learner</th>
                  <th className="py-3.5 px-4">Course</th>
                  <th className="py-3.5 px-4">Date</th>
                  <th className="py-3.5 px-4">Tuition Fee</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">Reassessment</th>
                  <th className="py-3.5 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {enrollments.map((enr) => (
                  <tr key={enr.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-5 font-mono text-slate-400 font-bold">{enr.id}</td>
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-900">{enr.employee_name}</div>
                      <span className="text-[11px] text-slate-500 font-medium">{enr.department}</span>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-900 max-w-xs truncate" title={enr.course_title}>
                      {enr.course_title}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 font-mono">{enr.enrollment_date}</td>
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900">${enr.cost_charged.toLocaleString()}</td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={enr.status} />
                    </td>
                    <td className="py-3.5 px-4">
                      {enr.status === 'COMPLETED' ? (
                        enr.reassessment_done ? (
                          <span className="inline-flex items-center gap-1.5 text-emerald-700 font-bold bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 glow-dot-emerald" /> Upgraded
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 text-amber-700 font-bold bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" /> Pending Exam
                          </span>
                        )
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-5 text-right space-x-1.5 whitespace-nowrap">
                      {enr.status === 'PENDING' && (
                        <>
                          <button
                            onClick={() => handleApprove(enr.id)}
                            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-[11px] shadow-sm transition-colors"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleCancel(enr.id)}
                            className="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold rounded-lg text-[11px] border border-rose-200 transition-colors"
                          >
                            Reject
                          </button>
                        </>
                      )}

                      {enr.status === 'APPROVED' && (
                        <button
                          onClick={() => handleStart(enr.id)}
                          className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg text-[11px] shadow-sm transition-colors"
                        >
                          Start Course
                        </button>
                      )}

                      {(enr.status === 'IN_PROGRESS' || enr.status === 'APPROVED') && (
                        <button
                          onClick={() => { setSelectedEnrId(enr.id); setIsCompleteModalOpen(true); }}
                          className="px-3 py-1.5 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-lg text-[11px] shadow-sm transition-colors"
                        >
                          Record Completion
                        </button>
                      )}

                      {enr.status === 'COMPLETED' && !enr.reassessment_done && enr.completion_id && (
                        <button
                          onClick={() => handleReassess(enr.completion_id)}
                          className="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-lg text-[11px] shadow-sm transition-colors"
                        >
                          Submit Reassessment
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal: New Enrollment Form */}
      <Modal
        isOpen={isNewModalOpen}
        onClose={() => setIsNewModalOpen(false)}
        title="Register Employee Course Enrollment"
        maxWidth="max-w-md"
      >
        <form onSubmit={handleSubmitEnrollment} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-slate-700 mb-1.5">Select Employee</label>
            <select
              value={newEmpId}
              onChange={(e) => setNewEmpId(e.target.value)}
              className="w-full border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50 font-semibold"
            >
              {employees.map((e) => (
                <option key={e.id} value={e.id}>{e.name} ({e.id}) - {e.department}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1.5">Select Course</label>
            <select
              value={newCourseId}
              onChange={(e) => setNewCourseId(e.target.value)}
              className="w-full border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50 font-semibold"
            >
              {courses.map((c) => (
                <option key={c.id} value={c.id}>{c.title} (${c.cost})</option>
              ))}
            </select>
          </div>

          <div className="pt-3 border-t border-slate-100 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsNewModalOpen(false)}
              className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold shadow-md shadow-indigo-600/20 disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit Enrollment'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Modal: Record Completion Form */}
      <Modal
        isOpen={isCompleteModalOpen}
        onClose={() => setIsCompleteModalOpen(false)}
        title="Verify Course Completion & Record Assessment Score"
        maxWidth="max-w-md"
      >
        <form onSubmit={handleRecordCompletion} className="space-y-4 text-xs">
          <div className="p-3.5 bg-amber-50 rounded-xl border border-amber-200 text-amber-900 font-medium">
            Enrollment ID: <strong className="font-mono">{selectedEnrId}</strong>
            <p className="mt-1 text-[11px] text-amber-800">
              Completion records are verified and logged. Duplicate completions will be detected and flagged without history loss.
            </p>
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1.5">
              Assessment Exam Score (0.00% to 100.00%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={assessmentScore}
              onChange={(e) => setAssessmentScore(e.target.value)}
              className="w-full border border-slate-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50 font-bold font-mono text-sm"
              required
            />
            <span className="text-[11px] text-slate-500 mt-1 block">Passing threshold for proficiency upgrade is 70.0%</span>
          </div>

          <div className="pt-3 border-t border-slate-100 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsCompleteModalOpen(false)}
              className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow-md shadow-emerald-600/20 disabled:opacity-50"
            >
              {submitting ? 'Recording...' : 'Record Verified Completion'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
