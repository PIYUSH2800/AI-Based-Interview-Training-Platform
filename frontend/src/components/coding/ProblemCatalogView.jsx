import React, { useState, useMemo } from 'react';
import {
  Search,
  Filter,
  CheckCircle2,
  Lock,
  ArrowRight,
  BookOpen,
  Code2,
  Layers,
  RotateCcw,
  Sparkles,
} from 'lucide-react';

export const ProblemCatalogView = ({
  problems = [],
  modules = [],
  selectedModuleFilter,
  onSelectModuleFilter,
  onOpenProblem,
  onBackToRoadmap,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');

  // Extract unique categories
  const categories = useMemo(() => {
    const set = new Set();
    problems.forEach((p) => {
      if (p.category) set.add(p.category);
    });
    return ['All', ...Array.from(set).sort()];
  }, [problems]);

  // Build module map for quick lookup
  const moduleMap = useMemo(() => {
    const map = {};
    modules.forEach((m) => {
      map[m.id] = m;
    });
    return map;
  }, [modules]);

  // Filtered problems list
  const filteredProblems = useMemo(() => {
    return problems.filter((p) => {
      // 1. Search term
      if (searchTerm.trim()) {
        const term = searchTerm.toLowerCase();
        const matchTitle = p.title?.toLowerCase().includes(term);
        const matchSlug = p.slug?.toLowerCase().includes(term);
        const matchCat = p.category?.toLowerCase().includes(term);
        if (!matchTitle && !matchSlug && !matchCat) return false;
      }

      // 2. Module filter
      if (selectedModuleFilter !== 'All' && selectedModuleFilter !== null) {
        if (typeof selectedModuleFilter === 'number' && p.module_id !== selectedModuleFilter) {
          return false;
        }
        if (typeof selectedModuleFilter === 'string' && selectedModuleFilter !== 'All') {
          const mod = moduleMap[p.module_id];
          if (mod?.slug !== selectedModuleFilter) return false;
        }
      }

      // 3. Difficulty filter
      if (selectedDifficulty !== 'All') {
        if (p.difficulty?.toLowerCase() !== selectedDifficulty.toLowerCase()) {
          return false;
        }
      }

      // 4. Category filter
      if (selectedCategory !== 'All') {
        if (p.category !== selectedCategory) return false;
      }

      // 5. Status filter (Solved, Attempted, Not Started, Locked)
      if (selectedStatus === 'Solved' && !p.is_solved) return false;
      if (selectedStatus === 'Locked' && !p.is_locked) return false;
      if (selectedStatus === 'Not Started' && (p.is_solved || p.is_locked)) return false;

      return true;
    });
  }, [problems, searchTerm, selectedModuleFilter, selectedDifficulty, selectedCategory, selectedStatus, moduleMap]);

  const getDifficultyBadge = (diff) => {
    switch (diff?.toLowerCase()) {
      case 'easy':
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      case 'medium':
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      case 'hard':
        return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <button
              onClick={onBackToRoadmap}
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition flex items-center gap-1"
            >
              <span>← Learning Roadmap</span>
            </button>
          </div>
          <h2 className="text-2xl font-bold text-white mt-1">Problem Catalog</h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Browse through all {problems.length} curriculum challenges across 6 learning modules.
          </p>
        </div>

        {/* Count Pill */}
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 shadow-sm self-start sm:self-auto">
          <span>Showing:</span>
          <span className="font-bold text-white">{filteredProblems.length} of {problems.length}</span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="card p-4 bg-slate-900 border border-slate-800 shadow-sm space-y-3">
        {/* Search Input & Dropdowns */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Search by title */}
          <div className="relative sm:col-span-2 lg:col-span-2">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search problems by title or topic..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs sm:text-sm bg-slate-950 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition"
            />
          </div>

          {/* Module Filter */}
          <div>
            <select
              value={selectedModuleFilter || 'All'}
              onChange={(e) => onSelectModuleFilter(e.target.value === 'All' ? 'All' : Number(e.target.value))}
              className="w-full px-3 py-2 text-xs sm:text-sm bg-slate-950 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 transition font-medium"
            >
              <option value="All">All Modules (6)</option>
              {modules.map((m) => (
                <option key={m.id} value={m.id}>
                  Module {m.order_index}: {m.title} {m.is_unlocked ? '' : '🔒'}
                </option>
              ))}
            </select>
          </div>

          {/* Difficulty Filter */}
          <div>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full px-3 py-2 text-xs sm:text-sm bg-slate-950 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 transition font-medium"
            >
              <option value="All">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-3 py-2 text-xs sm:text-sm bg-slate-950 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 transition font-medium"
            >
              <option value="All">All Statuses</option>
              <option value="Solved">Solved</option>
              <option value="Not Started">Not Started</option>
              <option value="Locked">Locked</option>
            </select>
          </div>
        </div>

        {/* Quick Category Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 pt-1 text-xs text-slate-400">
          <span className="font-semibold text-slate-400 mr-1 flex-shrink-0">Topic:</span>
          {categories.slice(0, 8).map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              {cat}
            </button>
          ))}
          {categories.length > 8 && (
            <select
              value={categories.slice(0, 8).includes(selectedCategory) ? 'More' : selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-2 py-1 bg-slate-800 text-slate-300 border border-slate-700 rounded-md text-[11px] font-medium outline-none cursor-pointer"
            >
              <option value="More" disabled>More Topics...</option>
              {categories.slice(8).map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Problems List Table / Grid */}
      <div className="card overflow-hidden bg-slate-900 border border-slate-800 shadow-sm">
        {filteredProblems.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <Code2 size={36} className="mx-auto text-slate-500 mb-3" />
            <h4 className="text-base font-semibold text-slate-200">No Problems Found</h4>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Try adjusting your search terms, module filter, or difficulty settings.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {filteredProblems.map((prob) => {
              const mod = moduleMap[prob.module_id];
              const isLocked = prob.is_locked;
              const isSolved = prob.is_solved;

              return (
                <div
                  key={prob.id}
                  className={`p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition ${
                    isLocked ? 'bg-slate-950/40' : 'hover:bg-slate-800/50'
                  }`}
                >
                  {/* Left: Status Icon + Title + Tags */}
                  <div className="flex items-start gap-3.5 min-w-0">
                    <div className="mt-1 flex-shrink-0">
                      {isSolved ? (
                        <CheckCircle2 size={18} className="text-emerald-400" />
                      ) : isLocked ? (
                        <Lock size={18} className="text-slate-500" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border-2 border-slate-600" />
                      )}
                    </div>

                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h4 className={`text-sm sm:text-base font-semibold ${isLocked ? 'text-slate-400' : 'text-slate-100'}`}>
                          {prob.title}
                        </h4>
                        <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold border ${getDifficultyBadge(prob.difficulty)}`}>
                          {prob.difficulty}
                        </span>
                        {isSolved && (
                          <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                            Solved
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2 mt-1 text-xs text-slate-400 flex-wrap">
                        {mod && (
                          <span className="font-medium text-slate-300">
                            Module {mod.order_index}: {mod.title}
                          </span>
                        )}
                        {prob.category && (
                          <>
                            <span className="text-slate-600">•</span>
                            <span className="text-slate-400">{prob.category}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right: Action Button */}
                  <div className="flex items-center gap-3 self-end sm:self-auto flex-shrink-0">
                    {isLocked ? (
                      <div className="text-right">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
                          <Lock size={13} />
                          Locked
                        </span>
                        {mod && (
                          <p className="text-[10px] text-amber-400 mt-1 max-w-xs text-right">
                            {mod.unlock_requirement}
                          </p>
                        )}
                      </div>
                    ) : (
                      <button
                        onClick={() => onOpenProblem(prob)}
                        className={`text-xs font-semibold px-4 py-2 rounded-lg flex items-center gap-1.5 transition ${
                          isSolved
                            ? 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                            : 'btn-primary'
                        }`}
                      >
                        {isSolved ? (
                          <>
                            <RotateCcw size={13} />
                            <span>Reattempt</span>
                          </>
                        ) : (
                          <>
                            <span>Solve Problem</span>
                            <ArrowRight size={13} />
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
