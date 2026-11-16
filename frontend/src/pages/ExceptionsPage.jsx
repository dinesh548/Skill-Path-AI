import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Filter,
  ShieldAlert,
  ArrowRight,
  Info,
  ShieldCheck,
  Zap
} from 'lucide-react';
import { api } from '../api/client';
import { LoadingSpinner, Modal } from '../components/Modal';
import { SeverityBadge } from '../components/SeverityBadge';

const ISSUE_DESCRIPTIONS = {
  PREREQUISITE_VIOLATION: 'CASE 1: Recommendation/enrollment blocked due to unsatisfied mandatory prerequisites.',
  BUDGET_EXCEEDED: 'CASE 2: Course cost exceeds available departmental remaining budget allocation.',
  DUPLICATE_COMPLETION: 'CASE 3: Duplicate completion detected without loss or overwriting of historical audit trail.',
  UNASSESSED_GAP: 'CASE 4: Course completed, but skill proficiency remains unchanged pending formal examination.',
  COURSE_UNAVAILABLE: 'CASE 5: Course status inactive or schedule outside active planning window.'
};

export function ExceptionsPage() {
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('');
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [newStatus, setNewStatus] = useState('RESOLVED');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [actionMsg, setActionMsg] = useState(null);

  useEffect(() => {
    loadExceptions();
  }, [filterType, filterSeverity]);

  const loadExceptions = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterType) params.issue_type = filterType;
      if (filterSeverity) params.severity = filterSeverity;
      const res = await api.getExceptions(params);
      setExceptions(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenResolve = (item) => {
    setSelectedIssue(item);
    setNewStatus('RESOLVED');
    setResolutionNotes(`Audit reviewed and verified on ${new Date().toISOString().slice(0, 10)}.`);
  };

  const handleResolveSubmit = async (e) => {
    e.preventDefault();
    if (!selectedIssue) return;
    try {
      setSubmitting(true);
      setActionMsg(null);
      await api.resolveException(selectedIssue.issue_id, {
        resolution_status: newStatus,
        notes: resolutionNotes
      });
      setActionMsg({ type: 'success', text: `Issue ${selectedIssue.issue_id} updated to ${newStatus}!` });
      setSelectedIssue(null);
      loadExceptions();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.message || 'Failed to update resolution' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-500" />
            Exception Monitoring & Security Audit Center
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Traceable oversight across 5 core scenario gates: prerequisite violations, budget breaches, duplicate certificates, unassessed gaps, and schedule conflicts
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="text-xs border border-slate-200 rounded-xl px-3 py-2.5 bg-slate-50/50 font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All 5 Exception Types</option>
            <option value="PREREQUISITE_VIOLATION">Case 1: Prerequisite Violation</option>
            <option value="BUDGET_EXCEEDED">Case 2: Budget Exceeded</option>
            <option value="DUPLICATE_COMPLETION">Case 3: Duplicate Completion</option>
            <option value="UNASSESSED_GAP">Case 4: Unassessed Gap</option>
            <option value="COURSE_UNAVAILABLE">Case 5: Course Unavailable</option>
          </select>

          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="text-xs border border-slate-200 rounded-xl px-3 py-2.5 bg-slate-50/50 font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {actionMsg && (
        <div className={`p-4 rounded-xl border text-xs font-bold ${
          actionMsg.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'
        }`}>
          {actionMsg.text}
        </div>
      )}

      {/* 5 Case Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3.5">
        {Object.entries(ISSUE_DESCRIPTIONS).map(([key, desc], idx) => (
          <div key={key} className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-card flex flex-col justify-between">
            <div>
              <span className="font-extrabold text-[10px] uppercase tracking-wider text-indigo-600 block">Case {idx + 1}</span>
              <div className="font-bold text-slate-900 mt-1 text-xs truncate" title={key}>{key}</div>
              <p className="text-[11px] text-slate-500 mt-1.5 leading-relaxed line-clamp-3">{desc}</p>
            </div>
            <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
              <span className="text-[10px] font-mono text-emerald-600 font-bold">Rule Tested</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 glow-dot-emerald" />
            </div>
          </div>
        ))}
      </div>

      {/* Exceptions Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
        {loading ? (
          <LoadingSpinner message="Scanning audit event records..." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200/80 bg-slate-50/70 text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="py-3.5 px-5">Issue ID</th>
                  <th className="py-3.5 px-4">Exception Type</th>
                  <th className="py-3.5 px-4">Severity</th>
                  <th className="py-3.5 px-4">Affected Learner & Course</th>
                  <th className="py-3.5 px-4">Expected vs Actual Decision</th>
                  <th className="py-3.5 px-4">Detection Time</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {exceptions.map((exc) => (
                  <tr key={exc.issue_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-5 font-mono font-extrabold text-slate-900">{exc.issue_id}</td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-slate-900 block">{exc.issue_type}</span>
                      <span className="text-[10px] text-slate-400 font-medium">{ISSUE_DESCRIPTIONS[exc.issue_type]?.split(':')[0]}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <SeverityBadge severity={exc.severity} />
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-900">{exc.employee_name || 'N/A'} ({exc.employee_id || 'N/A'})</div>
                      <span className="text-[11px] text-slate-500 block truncate max-w-xs">{exc.course_title || exc.course_id || 'N/A'}</span>
                    </td>
                    <td className="py-3.5 px-4 max-w-sm">
                      <div className="text-[11px] text-slate-600">
                        <span className="font-bold text-slate-700">Expected: </span>{exc.expected_result}
                      </div>
                      <div className="text-[11px] text-indigo-900 mt-1 font-semibold bg-indigo-50/70 p-1.5 rounded-lg border border-indigo-100">
                        <span className="font-bold text-indigo-950">Actual: </span>{exc.actual_result}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 whitespace-nowrap font-mono text-[11px]">
                      {new Date(exc.detection_date).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                        exc.resolution_status === 'RESOLVED'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : exc.resolution_status === 'ACKNOWLEDGED'
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-rose-50 text-rose-700 border border-rose-200'
                      }`}>
                        {exc.resolution_status}
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      {exc.resolution_status === 'OPEN' && (
                        <button
                          onClick={() => handleOpenResolve(exc)}
                          className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-lg text-xs transition-colors"
                        >
                          Resolve
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

      {/* Resolution Modal */}
      <Modal
        isOpen={Boolean(selectedIssue)}
        onClose={() => setSelectedIssue(null)}
        title={`Audit Resolution Action: ${selectedIssue?.issue_id}`}
        maxWidth="max-w-md"
      >
        {selectedIssue && (
          <form onSubmit={handleResolveSubmit} className="space-y-4 text-xs">
            <div>
              <span className="text-slate-500 font-medium block">Issue Classification</span>
              <p className="font-extrabold text-slate-900 text-sm mt-0.5">{selectedIssue.issue_type}</p>
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1.5">New Resolution Status</label>
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                className="w-full border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50 font-semibold"
              >
                <option value="RESOLVED">RESOLVED</option>
                <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
                <option value="SUPPRESSED">SUPPRESSED</option>
              </select>
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1.5">Resolution Audit Justification Note</label>
              <textarea
                rows={3}
                value={resolutionNotes}
                onChange={(e) => setResolutionNotes(e.target.value)}
                className="w-full border border-slate-200 rounded-xl p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50 font-medium"
                placeholder="Enter justification or corrective action note..."
              />
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setSelectedIssue(null)}
                className="px-4 py-2 border border-slate-200 rounded-xl text-slate-700 font-semibold hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold shadow-md shadow-indigo-600/20 disabled:opacity-50"
              >
                {submitting ? 'Updating...' : 'Confirm Resolution'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}
