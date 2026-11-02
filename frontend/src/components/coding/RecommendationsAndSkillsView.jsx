import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Trophy,
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  BookOpen,
  ArrowRight,
  Code,
  Flame,
  Layers,
  Zap,
  RefreshCw,
  Award,
  HelpCircle,
  Clock,
  RotateCcw,
} from 'lucide-react';
import api from '../../services/api';

export const RecommendationsAndSkillsView = ({
  onSelectProblem,
  onNavigateToRoadmap,
  onNavigateToCatalog,
}) => {
  const [recommendations, setRecommendations] = useState([]);
  const [skills, setSkills] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [recsRes, skillsRes] = await Promise.all([
        api.get('/coding/recommendations'),
        api.get('/coding/skills'),
      ]);
      setRecommendations(recsRes.data?.recommendations || []);
      setSkills(skillsRes.data || null);
    } catch (err) {
      console.error('Failed to load mentor data:', err);
      setError(err.response?.data?.detail || 'Failed to load recommendations and skill insights.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getDifficultyBadge = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'medium':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'hard':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const getCategoryTheme = (category) => {
    switch (category) {
      case 'Continue Learning':
        return {
          icon: <BookOpen size={16} className="text-indigo-400" />,
          badge: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
          border: 'hover:border-indigo-500/40',
        };
      case 'Review Previous Mistakes':
        return {
          icon: <RotateCcw size={16} className="text-rose-400" />,
          badge: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
          border: 'hover:border-rose-500/40',
        };
      case 'Practice Weak Topics':
        return {
          icon: <Target size={16} className="text-amber-400" />,
          badge: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
          border: 'hover:border-amber-500/40',
        };
      case 'Increase Difficulty':
        return {
          icon: <Flame size={16} className="text-purple-400" />,
          badge: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
          border: 'hover:border-purple-500/40',
        };
      default:
        return {
          icon: <Sparkles size={16} className="text-cyan-400" />,
          badge: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
          border: 'hover:border-cyan-500/40',
        };
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4 text-slate-400">
        <RefreshCw size={32} className="animate-spin text-indigo-500" />
        <p className="text-sm font-medium">Analyzing submission history and tailoring practice recommendations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-xl mx-auto my-12 p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-center space-y-3">
        <AlertTriangle size={32} className="mx-auto text-rose-400" />
        <h3 className="text-lg font-bold text-white">Unable to Load Insights</h3>
        <p className="text-sm text-slate-300">{error}</p>
        <button
          onClick={fetchData}
          className="mt-2 px-4 py-2 text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white rounded-lg transition"
        >
          Try Again
        </button>
      </div>
    );
  }

  const topRec = recommendations[0];

  return (
    <div className="space-y-10 max-w-7xl mx-auto pb-16 animate-fadeIn">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center gap-1.5">
              <Sparkles size={12} />
              AI Coding Mentor
            </span>
            <span className="text-xs text-slate-500">•</span>
            <span className="text-xs text-slate-400">Adaptive Practice Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Personalized Recommendations & Skills
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Target your weakest algorithmic topics, learn from past mistakes, and accelerate mastery with data-driven practice suggestions.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition self-start md:self-center"
        >
          <RefreshCw size={13} />
          <span>Refresh Analysis</span>
        </button>
      </div>

      {/* Top Actionable Recommendation Hero */}
      {topRec && (
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-950/60 via-slate-900 to-slate-950 border border-indigo-500/30 p-6 sm:p-8 shadow-xl shadow-indigo-950/20">
          <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-3 max-w-3xl">
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`px-2.5 py-1 rounded-md text-xs font-bold border flex items-center gap-1.5 ${getCategoryTheme(topRec.category).badge}`}>
                  {getCategoryTheme(topRec.category).icon}
                  {topRec.category}
                </span>
                <span className={`px-2.5 py-1 rounded-md text-xs font-semibold border ${getDifficultyBadge(topRec.problem?.difficulty)}`}>
                  {topRec.problem?.difficulty}
                </span>
                <span className="text-xs text-slate-400 font-medium px-2 py-0.5 rounded-md bg-slate-800/80 border border-slate-700">
                  {topRec.problem?.category}
                </span>
              </div>

              <div>
                <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                  {topRec.problem?.title}
                </h3>
                <p className="text-sm text-slate-300 mt-2 leading-relaxed bg-slate-950/50 p-3.5 rounded-xl border border-slate-800/80">
                  {topRec.reason}
                </p>
              </div>
            </div>

            <button
              onClick={() => onSelectProblem(topRec.problem?.id)}
              className="btn-primary py-3 px-6 text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/20 shrink-0 self-start md:self-center"
            >
              <span>Solve Problem Now</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* All Ranked Recommendations Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Target size={18} className="text-indigo-400" />
            <span>Recommended Challenges for You</span>
          </h2>
          <span className="text-xs text-slate-400">
            {recommendations.length} actionable challenges
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec, index) => {
            const theme = getCategoryTheme(rec.category);
            return (
              <div
                key={rec.problem?.id || index}
                className={`group p-5 rounded-xl bg-slate-900/70 border border-slate-800 transition duration-200 flex flex-col justify-between gap-4 ${theme.border}`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <span className={`px-2.5 py-0.5 rounded-md text-[11px] font-bold border flex items-center gap-1.5 ${theme.badge}`}>
                      {theme.icon}
                      {rec.category}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${getDifficultyBadge(rec.problem?.difficulty)}`}>
                      {rec.problem?.difficulty}
                    </span>
                  </div>

                  <div>
                    <h4 className="text-base font-bold text-white group-hover:text-indigo-400 transition">
                      {rec.problem?.title}
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Topic: <span className="text-slate-300 font-medium">{rec.problem?.category}</span>
                    </p>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                    {rec.reason}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500 font-mono">
                    Priority #{rec.priority}
                  </span>
                  <button
                    onClick={() => onSelectProblem(rec.problem?.id)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
                  >
                    <span>{rec.problem?.is_solved ? 'Reattempt' : 'Solve Challenge'}</span>
                    <ArrowRight size={13} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Skill Insights & Performance Analytics */}
      {skills && (
        <div className="space-y-6 pt-4 border-t border-slate-800">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp size={18} className="text-emerald-400" />
              <span>Personalized Skill Analytics</span>
            </h2>
            <span className="text-xs text-slate-400">Grounded in actual execution submissions</span>
          </div>

          {/* Key Metrics Banner */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400 font-medium">Problems Solved</span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-extrabold text-white">{skills.total_unique_solved}</span>
                <span className="text-xs text-slate-500">/ {skills.total_problems}</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-2">
                <div
                  className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (skills.total_unique_solved / (skills.total_problems || 48)) * 100)}%` }}
                />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400 font-medium">Total Submissions</span>
              <div className="text-2xl font-extrabold text-white">{skills.total_submissions}</div>
              <span className="text-[11px] text-slate-500">All evaluation runs</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400 font-medium">Overall Acceptance</span>
              <div className="text-2xl font-extrabold text-emerald-400">{skills.overall_acceptance_rate}%</div>
              <span className="text-[11px] text-slate-500">Accepted test passes</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400 font-medium">Strongest Topics</span>
              <div className="text-2xl font-extrabold text-purple-400">
                {skills.stronger_topics?.length || 0}
              </div>
              <span className="text-[11px] text-slate-500">≥60% success rate</span>
            </div>
          </div>

          {/* Difficulty Mastery Breakdown */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Performance by Difficulty
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {skills.difficulty_breakdown?.map((diff) => {
                const badge = getDifficultyBadge(diff.difficulty);
                return (
                  <div key={diff.difficulty} className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${badge}`}>
                        {diff.difficulty}
                      </span>
                      <span className="text-xs text-slate-400 font-mono font-bold">
                        {diff.solved_problems} / {diff.total_problems}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                      <span>Attempts: {diff.attempts}</span>
                      <span className="font-semibold text-slate-300">Accuracy: {diff.success_rate}%</span>
                    </div>

                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          diff.difficulty === 'Easy'
                            ? 'bg-emerald-500'
                            : diff.difficulty === 'Medium'
                            ? 'bg-amber-500'
                            : 'bg-rose-500'
                        }`}
                        style={{ width: `${Math.min(100, (diff.solved_problems / (diff.total_problems || 1)) * 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Strengths & Growth Areas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Stronger Topics */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-emerald-400" />
                <h4 className="text-sm font-bold text-white">Demonstrated Strengths</h4>
              </div>
              {skills.stronger_topics?.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {skills.stronger_topics.map((top) => (
                    <span
                      key={top}
                      className="px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5"
                    >
                      <CheckCircle2 size={12} />
                      {top}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 leading-relaxed">
                  Solve your first set of challenges to unlock demonstrated strengths in specific algorithmic areas.
                </p>
              )}
            </div>

            {/* Topics Needing Practice */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div className="flex items-center gap-2">
                <Target size={16} className="text-amber-400" />
                <h4 className="text-sm font-bold text-white">Focus Areas Requiring Practice</h4>
              </div>
              {skills.topics_needing_practice?.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {skills.topics_needing_practice.map((top) => (
                    <span
                      key={top}
                      className="px-3 py-1 rounded-lg text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/30 flex items-center gap-1.5"
                    >
                      <Target size={12} />
                      {top}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 leading-relaxed">
                  No critical failure concentrations detected. Continue exploring new modules or increasing challenge difficulty!
                </p>
              )}
            </div>
          </div>

          {/* Actionable Next Steps */}
          {skills.suggested_next_steps?.length > 0 && (
            <div className="p-5 rounded-xl bg-indigo-950/30 border border-indigo-500/20 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-2">
                <Zap size={14} />
                <span>Suggested Actionable Next Steps</span>
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {skills.suggested_next_steps.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
