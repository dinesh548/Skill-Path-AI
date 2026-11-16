import React from 'react';
import {
  LayoutDashboard,
  Users,
  Target,
  BookOpen,
  Sparkles,
  GraduationCap,
  Wallet,
  AlertTriangle,
  TrendingUp,
  FileText,
  ShieldCheck,
  ChevronRight,
  Database,
  Cpu,
  Compass,
  Layers,
  Search,
  Bell
} from 'lucide-react';

const NAV_GROUPS = [
  {
    group: 'INTELLIGENCE & WORKFORCE',
    items: [
      { id: 'overview', name: 'Overview', icon: LayoutDashboard },
      { id: 'employees', name: 'Employees Directory', icon: Users },
      { id: 'skill-gaps', name: 'Skill Gap Matrix', icon: Target },
    ]
  },
  {
    group: 'LEARNING & AI ENGINE',
    items: [
      { id: 'recommendations', name: 'Recommendations', icon: Sparkles, badge: 'AI Engine' },
      { id: 'courses', name: 'Course Catalogue', icon: BookOpen },
      { id: 'enrollments', name: 'Enrollments & Lifecycle', icon: GraduationCap },
    ]
  },
  {
    group: 'GOVERNANCE & CAREER',
    items: [
      { id: 'career-pathways', name: 'Career Pathways', icon: TrendingUp },
      { id: 'budgets', name: 'Budget Management', icon: Wallet },
      { id: 'exceptions', name: 'Exception Monitoring', icon: AlertTriangle, alert: true },
      { id: 'reports', name: 'Reports & Export', icon: FileText },
    ]
  }
];

export function Layout({ activePage, setActivePage, children }) {
  const allItems = NAV_GROUPS.flatMap((g) => g.items);
  const activeItem = allItems.find((n) => n.id === activePage) || allItems[0];

  return (
    <div className="min-h-screen flex bg-[#f8fafc]">
      {/* Sleek Enterprise Sidebar */}
      <aside className="w-68 bg-slate-950 text-slate-300 flex flex-col flex-shrink-0 border-r border-slate-900 selection:bg-indigo-500 selection:text-white">
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-900/90 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25 ring-1 ring-white/20">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h1 className="font-extrabold text-white text-base tracking-tight">SkillPath</h1>
                <span className="px-1.5 py-0.2 rounded text-[10px] font-extrabold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">AI</span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Enterprise Skill Engine</p>
            </div>
          </div>
        </div>

        {/* Navigation Categories */}
        <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
          {NAV_GROUPS.map((group) => (
            <div key={group.group} className="space-y-1">
              <span className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                {group.group}
              </span>
              <div className="mt-1 space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activePage === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActivePage(item.id)}
                      className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 ${
                        isActive
                          ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md shadow-indigo-600/30'
                          : 'text-slate-400 hover:text-white hover:bg-slate-900/70'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                        <span>{item.name}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        {item.badge && (
                          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-indigo-400/20 text-indigo-200 border border-indigo-400/30">
                            {item.badge}
                          </span>
                        )}
                        {isActive && <ChevronRight className="w-3.5 h-3.5 opacity-80" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer Profile & Status Pill */}
        <div className="p-4 border-t border-slate-900 bg-slate-950/80">
          <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/70 border border-slate-800/80 mb-2">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-sky-400 flex items-center justify-center text-white text-xs font-bold">
                HR
              </div>
              <div>
                <p className="text-xs font-bold text-white leading-none">Enterprise Admin</p>
                <p className="text-[10px] text-slate-400 mt-0.5 font-mono">admin@skillpath.ai</p>
              </div>
            </div>
            <span className="w-2 h-2 rounded-full bg-emerald-400 glow-dot-emerald animate-pulse" />
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
            <span className="flex items-center gap-1 font-mono">
              <Database className="w-3 h-3 text-slate-400" />
              Seed: 20261022
            </span>
            <span className="text-emerald-400 font-semibold text-[10px] bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
              Deterministic
            </span>
          </div>
        </div>
      </aside>

      {/* Main App Container */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-8 flex items-center justify-between flex-shrink-0 z-10 sticky top-0">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-400">Platform</span>
              <span className="text-slate-300">/</span>
              <h2 className="text-sm font-bold text-slate-900">
                {activeItem.name}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-lg border border-slate-200 text-xs text-slate-500 font-medium">
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <span>Quick Search</span>
              <kbd className="px-1.5 py-0.5 bg-white border border-slate-300 rounded text-[10px] font-mono text-slate-600 shadow-2xs">⌘K</kbd>
            </div>

            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200/80">
              <Cpu className="w-3.5 h-3.5 text-indigo-600" />
              <span>Deterministic Rule Engine</span>
            </div>

            <div className="text-xs font-semibold text-slate-700 bg-slate-50 px-3 py-1 rounded-lg border border-slate-200 font-mono">
              FY 2026
            </div>
          </div>
        </header>

        {/* Viewport Content */}
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto space-y-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
