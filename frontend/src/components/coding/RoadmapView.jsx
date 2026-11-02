import React from 'react';
import {
  Cpu,
  Layers,
  GitCommit,
  Search,
  GitBranch,
  Zap,
  Lock,
  Unlock,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Trophy,
  BookOpen,
  Code2,
} from 'lucide-react';

const ICON_MAP = {
  Cpu: Cpu,
  Layers: Layers,
  GitCommit: GitCommit,
  Search: Search,
  GitBranch: GitBranch,
  Zap: Zap,
};

const MODULE_ACCENT_COLORS = {
  1: { bg: 'from-blue-500/10 to-indigo-500/10', border: 'border-blue-500/30', badge: 'bg-blue-500/15 text-blue-300 border-blue-500/30', icon: 'text-blue-400 bg-blue-950/60 border border-blue-800/40', bar: 'bg-blue-500' },
  2: { bg: 'from-emerald-500/10 to-teal-500/10', border: 'border-emerald-500/30', badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30', icon: 'text-emerald-400 bg-emerald-950/60 border border-emerald-800/40', bar: 'bg-emerald-500' },
  3: { bg: 'from-violet-500/10 to-purple-500/10', border: 'border-violet-500/30', badge: 'bg-violet-500/15 text-violet-300 border-violet-500/30', icon: 'text-violet-400 bg-violet-950/60 border border-violet-800/40', bar: 'bg-violet-500' },
  4: { bg: 'from-amber-500/10 to-orange-500/10', border: 'border-amber-500/30', badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30', icon: 'text-amber-400 bg-amber-950/60 border border-amber-800/40', bar: 'bg-amber-500' },
  5: { bg: 'from-cyan-500/10 to-sky-500/10', border: 'border-cyan-500/30', badge: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30', icon: 'text-cyan-400 bg-cyan-950/60 border border-cyan-800/40', bar: 'bg-cyan-500' },
  6: { bg: 'from-rose-500/10 to-pink-500/10', border: 'border-rose-500/30', badge: 'bg-rose-500/15 text-rose-300 border-rose-500/30', icon: 'text-rose-400 bg-rose-950/60 border border-rose-800/40', bar: 'bg-rose-500' },
};

export const RoadmapView = ({
  modules = [],
  progress = {},
  onSelectModule,
  onStartProblem,
  recommendedProblem,
  unlockedToast,
  onDismissToast,
}) => {
  const totalSolved = progress?.total_unique_solved ?? 0;
  const totalProblems = progress?.total_problems || 48;
  const overallPct = progress?.overall_progress_percent ?? 0;
  const unlockedCount = progress?.unlocked_modules_count ?? 2;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Newly Unlocked Module Celebration Toast */}
      {unlockedToast && (
        <div className="relative overflow-hidden p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 text-white shadow-xl shadow-emerald-500/20 border border-emerald-400/30 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-white/20 rounded-xl backdrop-blur-sm">
              <Sparkles size={24} className="text-yellow-200 animate-pulse" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-emerald-200">Achievement Unlocked!</p>
              <h4 className="text-base sm:text-lg font-bold">{unlockedToast.title}</h4>
              <p className="text-xs sm:text-sm text-emerald-100 mt-0.5">{unlockedToast.message}</p>
            </div>
          </div>
          <button
            onClick={onDismissToast}
            className="flex-shrink-0 px-3 py-1.5 bg-white/20 hover:bg-white/30 text-white rounded-lg text-xs font-semibold backdrop-blur-sm transition"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Hero Stats Card */}
      <div className="card p-6 sm:p-8 bg-gradient-to-br from-slate-900 via-indigo-950/20 to-slate-950 border border-slate-800 shadow-md relative overflow-hidden">
        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/60 border border-indigo-700/50 text-indigo-300 text-xs font-semibold">
              <Trophy size={14} />
              <span>Interactive Curriculum Roadmap</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Master Algorithmic Problem Solving
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              6 progressive modules designed to prepare you for technical interviews. Unlock advanced modules by mastering foundational concepts in Python, Java, or C++.
            </p>
          </div>

          {/* Quick Actions & Metrics */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full lg:w-auto">
            <div className="px-5 py-3 bg-slate-900/90 rounded-xl border border-slate-800 shadow-sm flex items-center gap-4">
              <div>
                <p className="text-[11px] font-semibold text-slate-400 uppercase">Solved</p>
                <p className="text-2xl font-bold text-white">{totalSolved} <span className="text-sm font-normal text-slate-400">/ {totalProblems}</span></p>
              </div>
              <div className="h-8 w-px bg-slate-800" />
              <div>
                <p className="text-[11px] font-semibold text-slate-400 uppercase">Unlocked</p>
                <p className="text-2xl font-bold text-indigo-400">{unlockedCount} <span className="text-sm font-normal text-slate-400">/ 6</span></p>
              </div>
            </div>

            {recommendedProblem && (
              <button
                onClick={() => onStartProblem(recommendedProblem)}
                className="btn-primary py-3 px-6 shadow-indigo-500/25 flex items-center justify-center gap-2"
              >
                <span>Continue Learning</span>
                <ArrowRight size={16} />
              </button>
            )}
          </div>
        </div>

        {/* Overall Progress Bar */}
        <div className="mt-6 pt-6 border-t border-slate-800">
          <div className="flex items-center justify-between text-xs font-semibold mb-2">
            <span className="text-slate-300">Curriculum Mastery</span>
            <span className="text-indigo-400 font-bold">{overallPct}% Completed</span>
          </div>
          <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-500 ease-out shadow-sm"
              style={{ width: `${Math.min(100, Math.max(0, overallPct))}%` }}
            />
          </div>
        </div>
      </div>

      {/* Module Roadmap Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modules.map((mod) => {
          const IconComponent = ICON_MAP[mod.icon_name] || Code2;
          const colors = MODULE_ACCENT_COLORS[mod.order_index] || MODULE_ACCENT_COLORS[1];
          const isUnlocked = mod.is_unlocked;
          const pct = mod.total_problems > 0 ? Math.round((mod.solved_problems / mod.total_problems) * 100) : 0;
          const isCompleted = mod.solved_problems === mod.total_problems && mod.total_problems > 0;

          return (
            <div
              key={mod.id}
              className={`card flex flex-col justify-between transition-all duration-200 relative overflow-hidden ${
                isUnlocked
                  ? 'hover:shadow-md hover:border-slate-700 bg-slate-900 border-slate-800'
                  : 'bg-slate-950/60 border-slate-800/60 opacity-80'
              }`}
            >
              {/* Header section */}
              <div className="p-6">
                <div className="flex items-start justify-between gap-3 mb-4">
                  <div className={`p-3 rounded-xl ${isUnlocked ? colors.icon : 'bg-slate-800 text-slate-400 border border-slate-700/60'}`}>
                    <IconComponent size={22} />
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-400">
                      Module {mod.order_index}
                    </span>
                    {isUnlocked ? (
                      <span className={`inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                        isCompleted
                          ? 'bg-emerald-950/60 text-emerald-300 border-emerald-700/50'
                          : 'bg-indigo-950/60 text-indigo-300 border-indigo-700/50'
                      }`}>
                        {isCompleted ? <CheckCircle2 size={12} /> : <Unlock size={12} />}
                        {isCompleted ? 'Completed' : 'Unlocked'}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                        <Lock size={12} />
                        Locked
                      </span>
                    )}
                  </div>
                </div>

                <h3 className="text-lg font-bold text-white tracking-tight mb-2">
                  {mod.title}
                </h3>
                <p className="text-xs sm:text-sm text-slate-400 line-clamp-3 leading-relaxed mb-4">
                  {mod.description}
                </p>

                {/* Status or Requirement */}
                {isUnlocked ? (
                  <div className="space-y-2 pt-2 border-t border-slate-800">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-medium text-slate-300">Module Progress</span>
                      <span className="font-bold text-white">
                        {mod.solved_problems} / {mod.total_problems} Solved
                      </span>
                    </div>
                    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-300 ${colors.bar}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                ) : (
                  <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-800/50 text-amber-300 text-xs">
                    <p className="font-semibold flex items-center gap-1.5 text-amber-200">
                      <Lock size={13} className="text-amber-400" />
                      Prerequisite Requirement:
                    </p>
                    <p className="mt-1 text-[11px] text-amber-300/90 leading-normal">
                      {mod.unlock_requirement}
                    </p>
                  </div>
                )}
              </div>

              {/* Card Footer Actions */}
              <div className="p-4 bg-slate-950/60 border-t border-slate-800 flex items-center justify-between gap-2">
                <button
                  onClick={() => onSelectModule(mod)}
                  className="btn-secondary text-xs py-2 px-3 flex-1 flex items-center justify-center gap-1.5"
                >
                  <BookOpen size={14} />
                  <span>{isUnlocked ? 'View Problems' : 'View Syllabus'}</span>
                </button>

                {isUnlocked && (
                  <button
                    onClick={() => onSelectModule(mod, true)}
                    className="btn-primary text-xs py-2 px-3 flex-1 flex items-center justify-center gap-1.5"
                  >
                    <span>Practice</span>
                    <ArrowRight size={14} />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
