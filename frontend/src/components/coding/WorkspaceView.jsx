import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import {
  Code,
  Play,
  Send,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  FileCode,
  Layers,
  Sparkles,
  ArrowRight,
  RotateCcw,
  Clock,
  Award,
  Terminal,
  XCircle,
  AlertTriangle,
  Lightbulb,
  BookOpen,
  Eye,
  EyeOff,
  ShieldAlert,
  Zap,
  Target,
} from 'lucide-react';
import api from '../../services/api';

const LANGUAGE_MAP = {
  python: { name: 'Python 3', monaco: 'python' },
  java: { name: 'Java', monaco: 'java' },
  cpp: { name: 'C++', monaco: 'cpp' },
};

export const WorkspaceView = ({
  problemDetail,
  allProblems = [],
  selectedProblemId,
  onSelectProblemId,
  selectedLanguage,
  onChangeLanguage,
  currentCode,
  onChangeCode,
  onResetCode,
  onRunCode,
  isRunning,
  onSubmitCode,
  isSubmitting,
  executionResult,
  executionError,
  submissionResult,
  submissions = [],
  onViewSubmission,
  onGetFeedback,
  isFetchingFeedback,
  onNextProblem,
  nextProblemAvailable,
  onBackToCatalog,
  onBackToRoadmap,
}) => {
  const [leftTab, setLeftTab] = useState('problem');
  const [activeTestTab, setActiveTestTab] = useState(0);

  // Progressive AI Hints State
  const [hints, setHints] = useState({ 1: null, 2: null, 3: null });
  const [loadingHintLevel, setLoadingHintLevel] = useState(null);
  const [hintError, setHintError] = useState(null);

  // Solution Explanation State
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [explanationError, setExplanationError] = useState(null);
  const [showSolutionCode, setShowSolutionCode] = useState(false);

  // Reset hint/explanation caches when active problem changes
  useEffect(() => {
    setHints({ 1: null, 2: null, 3: null });
    setLoadingHintLevel(null);
    setHintError(null);
    setExplanation(null);
    setLoadingExplanation(false);
    setExplanationError(null);
    setShowSolutionCode(false);
  }, [selectedProblemId]);

  // Automatically fetch explanation when Explanation tab is opened for the first time
  useEffect(() => {
    if (leftTab === 'explanation' && !explanation && !loadingExplanation && problemDetail?.id) {
      fetchExplanation();
    }
  }, [leftTab, problemDetail?.id]);

  // Fetch Progressive Hint
  const fetchHint = async (level) => {
    if (!problemDetail?.id) return;
    setLoadingHintLevel(level);
    setHintError(null);
    try {
      const res = await api.post(`/coding/problems/${problemDetail.id}/hints`, { level });
      setHints((prev) => ({ ...prev, [level]: res.data }));
    } catch (err) {
      console.error(`Failed to fetch Level ${level} hint:`, err);
      setHintError(err.response?.data?.detail || `Failed to fetch Level ${level} hint. Please try again.`);
    } finally {
      setLoadingHintLevel(null);
    }
  };

  // Fetch Solution Explanation
  const fetchExplanation = async () => {
    if (!problemDetail?.id) return;
    setLoadingExplanation(true);
    setExplanationError(null);
    try {
      const res = await api.get(`/coding/problems/${problemDetail.id}/explanation`);
      setExplanation(res.data);
    } catch (err) {
      console.error('Failed to fetch explanation:', err);
      setExplanationError(err.response?.data?.detail || 'Failed to generate solution explanation.');
    } finally {
      setLoadingExplanation(false);
    }
  };

  // Parse JSON helper
  const parseJsonField = (field, fallback) => {
    if (!field) return fallback;
    if (typeof field === 'object') return field;
    try {
      return JSON.parse(field);
    } catch {
      return fallback;
    }
  };

  const examples = parseJsonField(problemDetail?.examples, []);
  const constraints = parseJsonField(problemDetail?.constraints, []);
  const supportedLangs = parseJsonField(problemDetail?.supported_languages, ['python', 'java', 'cpp']);

  const currentIndex = allProblems.findIndex((p) => p.id === selectedProblemId);
  const handlePrev = () => {
    if (currentIndex > 0) onSelectProblemId(allProblems[currentIndex - 1].id);
  };
  const handleNext = () => {
    if (currentIndex < allProblems.length - 1) onSelectProblemId(allProblems[currentIndex + 1].id);
  };

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

  const revealedHintsCount = [hints[1], hints[2], hints[3]].filter(Boolean).length;

  return (
    <div className="flex flex-col h-[calc(100vh-6.5rem)] bg-slate-900 text-slate-100 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl animate-fadeIn">
      {/* Top Header / Control Bar */}
      <div className="bg-slate-950 border-b border-slate-800 px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3">
        {/* Left: Navigation and Problem Title */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex items-center gap-1.5">
            <button
              onClick={onBackToRoadmap}
              className="text-xs font-semibold text-slate-400 hover:text-white px-2 py-1 rounded-md hover:bg-slate-800 transition"
              title="Return to Roadmap"
            >
              Roadmap
            </button>
            <span className="text-slate-600">/</span>
            <button
              onClick={onBackToCatalog}
              className="text-xs font-semibold text-slate-400 hover:text-white px-2 py-1 rounded-md hover:bg-slate-800 transition"
              title="Return to Catalog"
            >
              Catalog
            </button>
          </div>

          <span className="text-slate-700">|</span>

          {/* Prev / Next Problem Navigation */}
          <div className="flex items-center gap-1">
            <button
              onClick={handlePrev}
              disabled={currentIndex <= 0}
              className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent transition"
              title="Previous Problem"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="text-xs text-slate-400 font-mono">
              {currentIndex >= 0 ? `${currentIndex + 1}/${allProblems.length}` : '—'}
            </span>
            <button
              onClick={handleNext}
              disabled={currentIndex < 0 || currentIndex >= allProblems.length - 1}
              className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent transition"
              title="Next Problem"
            >
              <ChevronRight size={16} />
            </button>
          </div>

          {/* Problem Name Badge */}
          <div className="hidden sm:flex items-center gap-2 truncate">
            <span className="text-xs font-bold text-white truncate max-w-xs md:max-w-md">
              {problemDetail?.title}
            </span>
            {problemDetail?.is_solved && (
              <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                <CheckCircle2 size={12} />
                Solved
              </span>
            )}
          </div>
        </div>

        {/* Right: Controls & Actions */}
        <div className="flex items-center gap-2.5">
          {/* Language Selector */}
          <select
            value={selectedLanguage}
            onChange={(e) => onChangeLanguage(e.target.value)}
            className="bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 text-xs font-medium focus:outline-none focus:border-indigo-500 transition cursor-pointer"
          >
            {supportedLangs.map((lang) => (
              <option key={lang} value={lang}>
                {LANGUAGE_MAP[lang]?.name || lang}
              </option>
            ))}
          </select>

          {/* Reset Code Button */}
          <button
            onClick={onResetCode}
            disabled={isRunning || isSubmitting}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition disabled:opacity-40"
            title="Reset to starter template"
          >
            <RotateCcw size={15} />
          </button>

          {/* Run Code Button */}
          <button
            onClick={onRunCode}
            disabled={isRunning || isSubmitting}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition disabled:opacity-40 shadow-xs"
          >
            {isRunning ? (
              <>
                <RefreshCw size={13} className="animate-spin text-indigo-400" />
                <span>Running...</span>
              </>
            ) : (
              <>
                <Play size={13} className="text-emerald-400" />
                <span>Run</span>
              </>
            )}
          </button>

          {/* Submit Solution Button */}
          <button
            onClick={onSubmitCode}
            disabled={isSubmitting || isRunning}
            className="btn-primary text-xs py-1.5 px-4 shadow-indigo-500/20 flex items-center gap-1.5"
          >
            {isSubmitting ? (
              <>
                <RefreshCw size={13} className="animate-spin" />
                <span>Submitting...</span>
              </>
            ) : (
              <>
                <Send size={13} />
                <span>Submit</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Workspace Body: Split Panels */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden min-h-0">
        {/* Left Panel: Tabs & Guidance */}
        <div className="w-full lg:w-1/2 flex flex-col border-b lg:border-b-0 lg:border-r border-slate-800 bg-slate-900/50 min-h-0 h-[45vh] lg:h-auto">
          {/* Left Panel Tab Headers */}
          <div className="flex items-center justify-between px-6 pt-3 border-b border-slate-800 bg-slate-950/40 overflow-x-auto no-scrollbar">
            <div className="flex items-center gap-5 sm:gap-6 shrink-0">
              {/* Problem Tab */}
              <button
                onClick={() => setLeftTab('problem')}
                className={`pb-2.5 text-xs font-semibold transition border-b-2 ${
                  leftTab === 'problem'
                    ? 'text-indigo-400 border-indigo-500'
                    : 'text-slate-400 border-transparent hover:text-slate-300'
                }`}
              >
                Problem Description
              </button>

              {/* Progressive AI Hints Tab */}
              <button
                onClick={() => setLeftTab('hints')}
                className={`pb-2.5 text-xs font-semibold transition border-b-2 flex items-center gap-1.5 ${
                  leftTab === 'hints'
                    ? 'text-amber-400 border-amber-500'
                    : 'text-slate-400 border-transparent hover:text-amber-300'
                }`}
              >
                <Lightbulb size={13} className={revealedHintsCount > 0 ? 'text-amber-400' : ''} />
                <span>AI Hints</span>
                {revealedHintsCount > 0 && (
                  <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    {revealedHintsCount}/3
                  </span>
                )}
              </button>

              {/* Educational Explanation Tab */}
              <button
                onClick={() => setLeftTab('explanation')}
                className={`pb-2.5 text-xs font-semibold transition border-b-2 flex items-center gap-1.5 ${
                  leftTab === 'explanation'
                    ? 'text-cyan-400 border-cyan-500'
                    : 'text-slate-400 border-transparent hover:text-cyan-300'
                }`}
              >
                <BookOpen size={13} />
                <span>Explanation</span>
              </button>

              {/* Submissions Tab */}
              <button
                onClick={() => setLeftTab('submissions')}
                className={`pb-2.5 text-xs font-semibold transition border-b-2 flex items-center gap-1.5 ${
                  leftTab === 'submissions'
                    ? 'text-indigo-400 border-indigo-500'
                    : 'text-slate-400 border-transparent hover:text-slate-300'
                }`}
              >
                <span>Submissions</span>
                {submissions.length > 0 && (
                  <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-800 text-slate-300">
                    {submissions.length}
                  </span>
                )}
              </button>

              {/* AI Feedback Tab */}
              {submissionResult?.feedback && (
                <button
                  onClick={() => setLeftTab('feedback')}
                  className={`pb-2.5 text-xs font-semibold transition border-b-2 flex items-center gap-1.5 ${
                    leftTab === 'feedback'
                      ? 'text-purple-400 border-purple-500'
                      : 'text-purple-400 border-transparent hover:text-purple-300'
                  }`}
                >
                  <Sparkles size={13} />
                  <span>AI Feedback</span>
                </button>
              )}
            </div>
          </div>

          {/* Left Panel Tab Contents */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 text-sm text-slate-300 leading-relaxed min-h-0">
            {/* TAB 1: Problem Description */}
            {leftTab === 'problem' && (
              <>
                {/* Title & Badges */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <h2 className="text-xl font-bold text-white tracking-tight">
                      {problemDetail?.title}
                    </h2>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getDifficultyBadge(problemDetail?.difficulty)}`}>
                      {problemDetail?.difficulty}
                    </span>
                    {problemDetail?.category && (
                      <span className="text-xs text-slate-400 font-medium px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700">
                        {problemDetail?.category}
                      </span>
                    )}
                  </div>
                </div>

                {/* Problem Statement */}
                <div className="prose prose-invert max-w-none text-slate-300 text-sm whitespace-pre-line leading-relaxed">
                  {problemDetail?.description}
                </div>

                {/* Examples */}
                {examples.length > 0 && (
                  <div className="space-y-4 pt-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Examples
                    </h4>
                    {examples.map((ex, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-2 text-xs font-mono"
                      >
                        <div className="font-bold text-slate-400 font-sans">Example {idx + 1}:</div>
                        <div>
                          <span className="text-slate-500">Input: </span>
                          <span className="text-slate-200">{ex.input}</span>
                        </div>
                        <div>
                          <span className="text-slate-500">Output: </span>
                          <span className="text-emerald-400">{ex.output}</span>
                        </div>
                        {ex.explanation && (
                          <div className="text-slate-400 font-sans text-xs pt-1 border-t border-slate-800/80">
                            <span className="font-semibold text-slate-300">Explanation: </span>
                            {ex.explanation}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Constraints */}
                {constraints.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Constraints
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-xs text-slate-400 font-mono">
                      {constraints.map((c, idx) => (
                        <li key={idx}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Quick Hint CTA */}
                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-between gap-4 mt-4">
                  <div className="flex items-center gap-3">
                    <Lightbulb size={20} className="text-amber-400 shrink-0" />
                    <div className="text-xs">
                      <p className="font-bold text-white">Stuck on the approach?</p>
                      <p className="text-slate-400">Get progressive conceptual hints without spoiling the solution.</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setLeftTab('hints')}
                    className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-semibold shrink-0 transition"
                  >
                    View AI Hints →
                  </button>
                </div>
              </>
            )}

            {/* TAB 2: Progressive AI Hints */}
            {leftTab === 'hints' && (
              <div className="space-y-6 animate-fadeIn">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Lightbulb size={18} className="text-amber-400" />
                    <h3 className="text-base font-bold text-white">Progressive AI Hints</h3>
                  </div>
                  <span className="text-xs text-slate-400">
                    Revealed: <strong className="text-amber-400 font-mono">{revealedHintsCount} / 3</strong>
                  </span>
                </div>

                {hintError && (
                  <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 flex items-center gap-2">
                    <AlertTriangle size={15} className="text-rose-400 shrink-0" />
                    <span>{hintError}</span>
                  </div>
                )}

                <div className="space-y-4">
                  {/* Hint Level 1: Conceptual */}
                  <div className="p-5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          Level 1
                        </span>
                        <h4 className="text-sm font-bold text-white">Conceptual Guidance</h4>
                      </div>
                      {hints[1] && (
                        <span className="text-[11px] text-emerald-400 flex items-center gap-1 font-semibold">
                          <CheckCircle2 size={13} />
                          Unlocked
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-slate-400">
                      Understand the underlying mental model and logical invariants before jumping into code.
                    </p>

                    {hints[1] ? (
                      <div className="pt-2 space-y-3 border-t border-slate-800/80">
                        <p className="text-xs text-slate-200 leading-relaxed bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                          {hints[1].hint}
                        </p>

                        {hints[1].key_takeaways?.length > 0 && (
                          <div className="space-y-1">
                            <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider">
                              Key Invariants
                            </span>
                            <ul className="space-y-1 text-xs text-slate-300">
                              {hints[1].key_takeaways.map((k, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <span className="text-indigo-400 font-bold">•</span>
                                  <span>{k}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ) : (
                      <button
                        onClick={() => fetchHint(1)}
                        disabled={loadingHintLevel === 1}
                        className="w-full mt-2 py-2 px-3 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50"
                      >
                        {loadingHintLevel === 1 ? (
                          <>
                            <RefreshCw size={13} className="animate-spin" />
                            <span>Generating Conceptual Hint...</span>
                          </>
                        ) : (
                          <>
                            <Sparkles size={13} />
                            <span>Reveal Conceptual Guidance</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  {/* Hint Level 2: Approach Guidance */}
                  <div className={`p-5 rounded-xl border transition space-y-3 ${
                    hints[1] ? 'bg-slate-950/70 border-slate-800' : 'bg-slate-950/40 border-slate-800/50 opacity-70'
                  }`}>
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          Level 2
                        </span>
                        <h4 className="text-sm font-bold text-white">Approach & Data Structures</h4>
                      </div>
                      {hints[2] && (
                        <span className="text-[11px] text-emerald-400 flex items-center gap-1 font-semibold">
                          <CheckCircle2 size={13} />
                          Unlocked
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-slate-400">
                      Specific algorithmic strategies, data structure choices, and critical edge cases.
                    </p>

                    {hints[2] ? (
                      <div className="pt-2 space-y-3 border-t border-slate-800/80">
                        <p className="text-xs text-slate-200 leading-relaxed bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                          {hints[2].hint}
                        </p>

                        {hints[2].edge_cases?.length > 0 && (
                          <div className="space-y-1">
                            <span className="text-[11px] font-bold text-amber-400 uppercase tracking-wider">
                              Boundary Cases to Watch
                            </span>
                            <ul className="space-y-1 text-xs text-slate-300">
                              {hints[2].edge_cases.map((e, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <span className="text-amber-400 font-bold">•</span>
                                  <span>{e}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ) : (
                      <button
                        onClick={() => fetchHint(2)}
                        disabled={!hints[1] || loadingHintLevel === 2}
                        className="w-full mt-2 py-2 px-3 rounded-lg bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 text-xs font-semibold flex items-center justify-center gap-2 transition disabled:opacity-40 disabled:cursor-not-allowed"
                        title={!hints[1] ? 'Unlock Level 1 first' : 'Reveal Approach Hint'}
                      >
                        {loadingHintLevel === 2 ? (
                          <>
                            <RefreshCw size={13} className="animate-spin" />
                            <span>Generating Approach Hint...</span>
                          </>
                        ) : (
                          <>
                            <Sparkles size={13} />
                            <span>{hints[1] ? 'Reveal Approach Hint' : 'Unlock Hint 1 First'}</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  {/* Hint Level 3: Detailed Guidance */}
                  <div className={`p-5 rounded-xl border transition space-y-3 ${
                    hints[2] ? 'bg-slate-950/70 border-slate-800' : 'bg-slate-950/40 border-slate-800/50 opacity-70'
                  }`}>
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                          Level 3
                        </span>
                        <h4 className="text-sm font-bold text-white">Detailed Implementation Outline</h4>
                      </div>
                      {hints[3] && (
                        <span className="text-[11px] text-emerald-400 flex items-center gap-1 font-semibold">
                          <CheckCircle2 size={13} />
                          Unlocked
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-slate-400">
                      Step-by-step algorithmic outline walking through loops, state transitions, and pseudocode.
                    </p>

                    {hints[3] ? (
                      <div className="pt-2 space-y-3 border-t border-slate-800/80">
                        <pre className="text-xs text-slate-200 leading-relaxed font-mono whitespace-pre-wrap bg-slate-900/80 p-3.5 rounded-lg border border-slate-800">
                          {hints[3].hint}
                        </pre>

                        {hints[3].key_takeaways?.length > 0 && (
                          <div className="space-y-1">
                            <span className="text-[11px] font-bold text-rose-400 uppercase tracking-wider">
                              Implementation Checklist
                            </span>
                            <ul className="space-y-1 text-xs text-slate-300">
                              {hints[3].key_takeaways.map((k, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <span className="text-rose-400 font-bold">•</span>
                                  <span>{k}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ) : (
                      <button
                        onClick={() => fetchHint(3)}
                        disabled={!hints[2] || loadingHintLevel === 3}
                        className="w-full mt-2 py-2 px-3 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 text-xs font-semibold flex items-center justify-center gap-2 transition disabled:opacity-40 disabled:cursor-not-allowed"
                        title={!hints[2] ? 'Unlock Level 2 first' : 'Reveal Detailed Guidance'}
                      >
                        {loadingHintLevel === 3 ? (
                          <>
                            <RefreshCw size={13} className="animate-spin" />
                            <span>Generating Detailed Outline...</span>
                          </>
                        ) : (
                          <>
                            <Sparkles size={13} />
                            <span>{hints[2] ? 'Reveal Detailed Guidance' : 'Unlock Hint 2 First'}</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: Educational Solution Explanation */}
            {leftTab === 'explanation' && (
              <div className="space-y-6 animate-fadeIn">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <BookOpen size={18} className="text-cyan-400" />
                    <h3 className="text-base font-bold text-white">Solution Explanation & Concepts</h3>
                  </div>
                  <button
                    onClick={fetchExplanation}
                    disabled={loadingExplanation}
                    className="p-1 rounded text-slate-400 hover:text-white transition"
                    title="Refresh explanation"
                  >
                    <RefreshCw size={14} className={loadingExplanation ? 'animate-spin' : ''} />
                  </button>
                </div>

                {loadingExplanation && (
                  <div className="flex flex-col items-center justify-center py-12 space-y-3 text-slate-400">
                    <RefreshCw size={24} className="animate-spin text-cyan-400" />
                    <p className="text-xs">Generating conceptual breakdown and complexity analysis...</p>
                  </div>
                )}

                {explanationError && (
                  <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 flex items-center gap-2">
                    <AlertTriangle size={15} className="text-rose-400 shrink-0" />
                    <span>{explanationError}</span>
                  </div>
                )}

                {explanation && !loadingExplanation && (
                  <div className="space-y-5">
                    {/* Intuition */}
                    <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                      <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Lightbulb size={14} />
                        Problem Intuition
                      </h4>
                      <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                        {explanation.intuition}
                      </p>
                    </div>

                    {/* Brute Force vs. Optimized Comparison */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1.5">
                        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                          Brute-Force Approach
                        </span>
                        <p className="text-xs text-slate-300 leading-relaxed">
                          {explanation.brute_force}
                        </p>
                      </div>

                      <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-500/30 space-y-1.5">
                        <span className="text-[11px] font-bold text-indigo-300 uppercase tracking-wider">
                          Optimized Approach
                        </span>
                        <p className="text-xs text-slate-200 leading-relaxed">
                          {explanation.optimized_approach}
                        </p>
                      </div>
                    </div>

                    {/* Step-by-Step Algorithm */}
                    {explanation.step_by_step?.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                          Step-by-Step Execution
                        </h4>
                        <div className="space-y-2">
                          {explanation.step_by_step.map((step, idx) => (
                            <div key={idx} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5">
                              <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold text-[11px] flex items-center justify-center shrink-0">
                                {idx + 1}
                              </span>
                              <span className="leading-relaxed mt-0.5">{step}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Complexity Badges */}
                    <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-slate-950/70 border border-slate-800">
                      <div>
                        <span className="text-[11px] text-slate-400">Time Complexity</span>
                        <p className="font-mono text-xs font-bold text-emerald-400 mt-0.5">
                          {explanation.time_complexity}
                        </p>
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400">Space Complexity</span>
                        <p className="font-mono text-xs font-bold text-emerald-400 mt-0.5">
                          {explanation.space_complexity}
                        </p>
                      </div>
                    </div>

                    {/* Common Traps & Edge Cases */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {explanation.common_mistakes?.length > 0 && (
                        <div className="space-y-2">
                          <h5 className="text-xs font-bold text-rose-400 flex items-center gap-1.5">
                            <AlertTriangle size={13} />
                            Common Pitfalls
                          </h5>
                          <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside">
                            {explanation.common_mistakes.map((m, i) => (
                              <li key={i}>{m}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {explanation.edge_cases?.length > 0 && (
                        <div className="space-y-2">
                          <h5 className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                            <Target size={13} />
                            Critical Edge Cases
                          </h5>
                          <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside">
                            {explanation.edge_cases.map((e, i) => (
                              <li key={i}>{e}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Interview Communication Tips */}
                    {explanation.interview_tips?.length > 0 && (
                      <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20 space-y-2">
                        <h5 className="text-xs font-bold text-indigo-300 flex items-center gap-1.5">
                          <Award size={14} />
                          Interview Tips
                        </h5>
                        <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside">
                          {explanation.interview_tips.map((t, i) => (
                            <li key={i}>{t}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Spoiler-Protected Code Solution */}
                    <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <ShieldAlert size={16} className="text-amber-400" />
                          <span className="text-xs font-bold text-white">Spoiler Warning: Reference Solution Code</span>
                        </div>
                        <button
                          onClick={() => setShowSolutionCode(!showSolutionCode)}
                          className="flex items-center gap-1.5 px-3 py-1 rounded text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                        >
                          {showSolutionCode ? <EyeOff size={13} /> : <Eye size={13} />}
                          <span>{showSolutionCode ? 'Hide Code' : 'Reveal Solution Code'}</span>
                        </button>
                      </div>

                      {showSolutionCode && (
                        <div className="pt-2 animate-fadeIn space-y-2 border-t border-slate-800">
                          <p className="text-[11px] text-slate-400">
                            Starter solution template for <strong className="text-indigo-400 capitalize">{selectedLanguage}</strong>:
                          </p>
                          <pre className="p-3 bg-slate-900 rounded-lg text-xs font-mono text-emerald-300 whitespace-pre-wrap overflow-x-auto border border-slate-800">
                            {explanation.solution_code?.[selectedLanguage] || '// No template available'}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 4: Submission History */}
            {leftTab === 'submissions' && (
              <div className="space-y-4 animate-fadeIn">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h3 className="text-base font-bold text-white">Submission History</h3>
                  <span className="text-xs text-slate-400">
                    {submissions.length} {submissions.length === 1 ? 'attempt' : 'attempts'}
                  </span>
                </div>

                {submissions.length === 0 ? (
                  <div className="text-center py-12 space-y-2 text-slate-500">
                    <FileCode size={32} className="mx-auto text-slate-600" />
                    <p className="text-xs">No submissions recorded for this problem yet.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {submissions.map((sub) => {
                      const isAccepted = sub.status === 'accepted';
                      return (
                        <div
                          key={sub.id}
                          className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 text-xs transition ${
                            isAccepted
                              ? 'bg-emerald-500/5 border-emerald-500/20'
                              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                          }`}
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className={`font-bold capitalize ${isAccepted ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {isAccepted ? 'Accepted' : sub.status.replace('_', ' ')}
                              </span>
                              <span className="text-slate-600">•</span>
                              <span className="text-slate-400 font-mono capitalize">{sub.language}</span>
                              <span className="text-slate-600">•</span>
                              <span className="font-semibold text-slate-300">Score: {sub.score}%</span>
                            </div>
                            <div className="text-[11px] text-slate-500 flex items-center gap-2">
                              <span>Passed {sub.passed_tests} of {sub.total_tests} test cases</span>
                              {sub.execution_time_ms && (
                                <span>• {Math.round(sub.execution_time_ms)}ms</span>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => onViewSubmission(sub.id)}
                              className="px-2.5 py-1 text-[11px] font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
                            >
                              Load Code
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* TAB 5: AI Feedback Tab */}
            {leftTab === 'feedback' && submissionResult?.feedback && (
              <div className="space-y-5 animate-fadeIn">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Sparkles size={18} className="text-purple-400" />
                    <h3 className="text-base font-bold text-white">AI Code Evaluation</h3>
                  </div>
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/30">
                    Provider: {submissionResult.feedback.provider}
                  </span>
                </div>

                {/* Grounded Execution Verdict */}
                <div className={`p-4 rounded-xl border flex items-center justify-between gap-3 ${
                  submissionResult.status === 'accepted'
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
                    : 'bg-rose-500/10 border-rose-500/30 text-rose-200'
                }`}>
                  <div className="flex items-center gap-2.5">
                    {submissionResult.status === 'accepted' ? (
                      <CheckCircle2 size={20} className="text-emerald-400" />
                    ) : (
                      <XCircle size={20} className="text-rose-400" />
                    )}
                    <div>
                      <span className="font-bold text-xs uppercase tracking-wider">
                        Execution Verdict (Docker Sandbox)
                      </span>
                      <p className="text-xs opacity-90 mt-0.5">
                        {submissionResult.status === 'accepted' ? 'Accepted (100% Score)' : submissionResult.status.replace('_', ' ')} • Passed {submissionResult.passed_tests}/{submissionResult.total_tests} test cases
                      </p>
                    </div>
                  </div>
                </div>

                {/* Summary & Complexity */}
                <div className="p-4 rounded-xl bg-slate-950/70 border border-purple-500/20 space-y-3">
                  <div>
                    <h5 className="text-xs font-bold uppercase text-purple-300">Approach Summary</h5>
                    <p className="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed">
                      {submissionResult.feedback.summary}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800">
                    <div>
                      <span className="text-[11px] text-slate-400">Time Complexity:</span>
                      <p className="font-mono text-xs font-semibold text-emerald-400 mt-0.5">
                        {submissionResult.feedback.time_complexity}
                      </p>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-400">Space Complexity:</span>
                      <p className="font-mono text-xs font-semibold text-emerald-400 mt-0.5">
                        {submissionResult.feedback.space_complexity}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Strengths */}
                {submissionResult.feedback.strengths?.length > 0 && (
                  <div className="space-y-2">
                    <h5 className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 size={14} />
                      Key Strengths
                    </h5>
                    <ul className="list-disc list-inside space-y-1 text-xs text-slate-300">
                      {submissionResult.feedback.strengths.map((s, idx) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Issues & Improvements */}
                {submissionResult.feedback.issues?.length > 0 && (
                  <div className="space-y-2">
                    <h5 className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                      <AlertTriangle size={14} />
                      Potential Issues / Pitfalls
                    </h5>
                    <ul className="list-disc list-inside space-y-1 text-xs text-slate-300">
                      {submissionResult.feedback.issues.map((iss, idx) => (
                        <li key={idx}>{iss}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Better Approach */}
                {submissionResult.feedback.better_approach && (
                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 space-y-1">
                    <span className="font-bold text-indigo-400">Recommended Optimization:</span>
                    <p className="leading-relaxed">{submissionResult.feedback.better_approach}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Monaco Editor & Output Console */}
        <div className="w-full lg:w-1/2 flex flex-col min-h-0 bg-slate-950">
          {/* Monaco Editor Container */}
          <div className="flex-1 min-h-[300px] relative overflow-hidden">
            <Editor
              height="100%"
              theme="vs-dark"
              language={LANGUAGE_MAP[selectedLanguage]?.monaco || 'python'}
              value={currentCode}
              onChange={onChangeCode}
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                scrollBeyondLastLine: false,
                automaticLayout: true,
                tabSize: 4,
                wordWrap: 'on',
                lineNumbers: 'on',
              }}
            />
          </div>

          {/* Console / Test Results Section */}
          <div className="h-64 border-t border-slate-800 bg-slate-900/90 flex flex-col overflow-hidden flex-shrink-0">
            {/* Console Header */}
            <div className="px-4 py-2 border-b border-slate-800 bg-slate-950/80 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 font-semibold text-slate-400">
                <Terminal size={14} />
                <span>Test Execution Results</span>
              </div>

              {/* Execution Status Badge */}
              {isRunning && (
                <span className="text-indigo-400 flex items-center gap-1.5 font-medium">
                  <RefreshCw size={12} className="animate-spin" />
                  Executing Docker sandbox...
                </span>
              )}
              {isSubmitting && (
                <span className="text-indigo-400 flex items-center gap-1.5 font-medium">
                  <RefreshCw size={12} className="animate-spin" />
                  Evaluating all test cases...
                </span>
              )}
            </div>

            {/* Console Body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs">
              {/* Errors (Server / Compile / Runtime) */}
              {executionError && (
                <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-rose-400">
                    <AlertCircle size={14} />
                    <span>Execution Error</span>
                  </div>
                  <pre className="whitespace-pre-wrap font-mono text-[11px]">{executionError}</pre>
                </div>
              )}

              {/* Submission Result Banner */}
              {submissionResult && (
                <div className={`p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 ${
                  submissionResult.status === 'accepted'
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
                    : 'bg-rose-500/10 border-rose-500/30 text-rose-200'
                }`}>
                  <div className="flex items-center gap-3">
                    {submissionResult.status === 'accepted' ? (
                      <CheckCircle2 size={24} className="text-emerald-400" />
                    ) : (
                      <XCircle size={24} className="text-rose-400" />
                    )}
                    <div>
                      <h4 className="text-sm font-bold capitalize">
                        {submissionResult.status === 'accepted' ? 'Accepted — All Tests Passed!' : submissionResult.status.replace('_', ' ')}
                      </h4>
                      <p className="text-xs opacity-90 mt-0.5">
                        Passed {submissionResult.passed_tests} of {submissionResult.total_tests} test cases • Score: {submissionResult.score}%
                      </p>
                    </div>
                  </div>

                  {/* Actions on Accepted */}
                  <div className="flex items-center gap-2 self-end sm:self-auto">
                    {submissionResult.status === 'accepted' && nextProblemAvailable && (
                      <button
                        onClick={onNextProblem}
                        className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm transition"
                      >
                        <span>Next Problem</span>
                        <ArrowRight size={14} />
                      </button>
                    )}

                    {!submissionResult.feedback && (
                      <button
                        onClick={onGetFeedback}
                        disabled={isFetchingFeedback}
                        className="px-3 py-1.5 bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition"
                      >
                        <Sparkles size={13} className={isFetchingFeedback ? 'animate-spin' : ''} />
                        <span>{isFetchingFeedback ? 'Reviewing...' : 'AI Feedback'}</span>
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Run Code Results (Sample Test Cases) */}
              {executionResult && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
                    <span className="font-sans font-semibold text-slate-400 text-xs">Results:</span>
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      executionResult.passed === executionResult.total
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-rose-500/20 text-rose-400'
                    }`}>
                      {executionResult.passed} / {executionResult.total} Passed
                    </span>
                    {executionResult.status !== 'completed' && (
                      <span className="text-rose-400 text-xs uppercase font-bold">
                        ({executionResult.status})
                      </span>
                    )}
                  </div>

                  {/* Test case tabs */}
                  {executionResult.results?.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-1.5">
                        {executionResult.results.map((r, idx) => (
                          <button
                            key={idx}
                            onClick={() => setActiveTestTab(idx)}
                            className={`px-2.5 py-1 rounded text-[11px] font-semibold transition flex items-center gap-1 ${
                              activeTestTab === idx
                                ? 'bg-slate-800 text-white border border-slate-700'
                                : 'text-slate-400 hover:text-slate-200'
                            }`}
                          >
                            <span className={r.passed ? 'text-emerald-400' : 'text-rose-400'}>
                              {r.passed ? '✓' : '✗'}
                            </span>
                            <span>Case {idx + 1}</span>
                          </button>
                        ))}
                      </div>

                      {/* Active Case Details */}
                      {executionResult.results[activeTestTab] && (
                        <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1.5 text-[11px]">
                          <div>
                            <span className="text-slate-500">Input: </span>
                            <span className="text-slate-300">
                              {executionResult.results[activeTestTab].input || '(hidden)'}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-500">Expected: </span>
                            <span className="text-emerald-400">
                              {executionResult.results[activeTestTab].expected_output || '(hidden)'}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-500">Your Output: </span>
                            <span className={executionResult.results[activeTestTab].passed ? 'text-emerald-400' : 'text-rose-400'}>
                              {executionResult.results[activeTestTab].output || '(no output)'}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {executionResult.error && (
                    <pre className="text-rose-400 text-[11px] whitespace-pre-wrap p-2 bg-slate-950 rounded">
                      {executionResult.error}
                    </pre>
                  )}
                </div>
              )}

              {!isRunning && !isSubmitting && !executionResult && !submissionResult && !executionError && (
                <div className="h-full flex items-center justify-center text-slate-500 text-xs font-sans">
                  Click <strong className="text-slate-400 mx-1">Run</strong> to test sample cases or <strong className="text-indigo-400 mx-1">Submit</strong> to validate your solution.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
