import React, { useState, useEffect } from 'react';
import { BookOpen, Search, Filter, Clock, DollarSign, Users, Award, ShieldAlert, Check } from 'lucide-react';
import { api } from '../api/client';
import { LoadingSpinner } from '../components/Modal';
import { StatusBadge } from '../components/SeverityBadge';

export function CoursesPage() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [provider, setProvider] = useState('');
  const [status, setStatus] = useState('');

  useEffect(() => {
    loadCourses();
  }, [provider, status]);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const params = { limit: 100 };
      if (provider) params.provider = provider;
      if (status) params.status = status;
      if (search) params.search = search;
      const res = await api.getCourses(params);
      setCourses(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadCourses();
  };

  return (
    <div className="space-y-6">
      {/* Search & Filter Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
        <div>
          <h2 className="text-lg font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-600" />
            Accredited Course Catalogue
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">Explore certified training curricula, mandatory prerequisite dependencies, and capacity limits</p>
        </div>

        <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search course title or code..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-3 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50 font-medium"
            />
          </div>

          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="text-xs border border-slate-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50 text-slate-700 font-semibold"
          >
            <option value="">All Providers</option>
            <option value="SkillPath Academy">SkillPath Academy</option>
            <option value="Coursera Enterprise">Coursera Enterprise</option>
            <option value="O'Reilly Learning">O'Reilly Learning</option>
            <option value="Pluralsight">Pluralsight</option>
            <option value="AWS Training">AWS Training</option>
            <option value="Google Cloud Skills Boost">Google Cloud Skills Boost</option>
            <option value="Linux Foundation">Linux Foundation</option>
          </select>

          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="text-xs border border-slate-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50 text-slate-700 font-semibold"
          >
            <option value="">All Statuses</option>
            <option value="AVAILABLE">AVAILABLE</option>
            <option value="IN_PROGRESS">IN_PROGRESS</option>
            <option value="EXPIRED">EXPIRED</option>
          </select>

          <button
            type="submit"
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-600/20 transition-all hover:scale-102"
          >
            Filter
          </button>
        </form>
      </div>

      {/* Course Cards Grid */}
      {loading ? (
        <LoadingSpinner message="Loading course catalogue..." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {courses.map((course) => {
            const seatsRemaining = course.capacity - course.enrolled_count;
            const occupancyPct = Math.round((course.enrolled_count / course.capacity) * 100);
            return (
              <div key={course.id} className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-card hover:shadow-card-hover transition-all duration-200 flex flex-col justify-between group">
                <div>
                  <div className="flex items-center justify-between text-xs mb-3">
                    <span className="font-mono font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">{course.id}</span>
                    <StatusBadge status={course.status} />
                  </div>
                  <h3 className="text-sm font-extrabold text-slate-900 leading-snug line-clamp-2 group-hover:text-indigo-600 transition-colors">
                    {course.title}
                  </h3>
                  <p className="text-xs text-indigo-600 font-bold mt-1">{course.provider}</p>

                  <p className="text-xs text-slate-500 mt-2.5 line-clamp-2 leading-relaxed">{course.description}</p>

                  {/* Skills Taught */}
                  <div className="mt-4 pt-3 border-t border-slate-100">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
                      Curriculum Competencies:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {course.skills_taught?.map((s) => (
                        <span key={s.skill_id} className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] bg-indigo-50 text-indigo-700 font-semibold border border-indigo-200/80">
                          <Award className="w-3 h-3 text-indigo-500" />
                          {s.skill_name} (+{s.proficiency_gain} lvl)
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Prerequisites */}
                  {course.prerequisites && course.prerequisites.length > 0 && (
                    <div className="mt-3.5 pt-3 border-t border-slate-100">
                      <span className="text-[10px] font-bold text-amber-700 uppercase tracking-wider flex items-center gap-1 mb-1.5">
                        <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                        Mandatory Prerequisite:
                      </span>
                      <div className="space-y-1">
                        {course.prerequisites.map((p) => (
                          <div key={p.prerequisite_course_id} className="text-[11px] text-slate-700 font-medium flex items-center justify-between bg-amber-50/60 p-2 rounded-lg border border-amber-200/60">
                            <span className="line-clamp-1 font-semibold">{p.title}</span>
                            <span className="text-[9px] font-bold text-amber-800 bg-amber-100 px-1.5 py-0.5 rounded">Gated</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Seat Progress Meter */}
                  <div className="mt-4 pt-3 border-t border-slate-100">
                    <div className="flex items-center justify-between text-[11px] mb-1">
                      <span className="text-slate-500 font-medium">Seat Capacity</span>
                      <span className={`font-mono font-bold ${seatsRemaining <= 3 ? 'text-rose-600' : 'text-slate-800'}`}>
                        {course.enrolled_count} / {course.capacity} filled ({seatsRemaining} left)
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${occupancyPct > 80 ? 'bg-amber-500' : 'bg-indigo-600'}`}
                        style={{ width: `${occupancyPct}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Footer Metrics */}
                <div className="mt-5 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-center text-xs">
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-400 block font-medium">Tuition</span>
                    <span className="font-extrabold text-slate-900 font-mono text-sm">${course.cost.toLocaleString()}</span>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-400 block font-medium">Duration</span>
                    <span className="font-extrabold text-slate-900 font-mono text-sm">{course.duration_hours} hrs</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
