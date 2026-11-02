import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Code,
  Map,
  BookOpen,
  Trophy,
  Sparkles,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
  Lock,
} from 'lucide-react';
import api from '../services/api';
import { RoadmapView } from '../components/coding/RoadmapView';
import { ProblemCatalogView } from '../components/coding/ProblemCatalogView';
import { WorkspaceView } from '../components/coding/WorkspaceView';
import { RecommendationsAndSkillsView } from '../components/coding/RecommendationsAndSkillsView';

const CodingInterviewPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Primary data states
  const [modules, setModules] = useState([]);
  const [progress, setProgress] = useState(null);
  const [problems, setProblems] = useState([]);
  const [selectedProblemId, setSelectedProblemId] = useState(null);
  const [problemDetail, setProblemDetail] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('python');

  // Navigation & View state: 'roadmap' | 'catalog' | 'workspace'
  const initialMode = searchParams.get('view') || 'roadmap';
  const [currentMode, setCurrentMode] = useState(initialMode);
  const [selectedModuleFilter, setSelectedModuleFilter] = useState('All');

  // Loading & Error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFetchingFeedback, setIsFetchingFeedback] = useState(false);

  // Execution & Submissions
  const [executionResult, setExecutionResult] = useState(null);
  const [executionError, setExecutionError] = useState(null);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [submissions, setSubmissions] = useState([]);

  // Draft Code state Map: `${problemId}_${language}` -> code string
  const [codeMap, setCodeMap] = useState({});

  // Unlock Toast Alert
  const [unlockedToast, setUnlockedToast] = useState(null);

  // 1. Initial Data Fetch: Modules, Progress, and Problem Catalog
  const fetchInitialData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [modulesRes, progressRes, problemsRes] = await Promise.all([
        api.get('/coding/modules'),
        api.get('/coding/progress').catch(() => ({ data: null })),
        api.get('/coding/problems'),
      ]);

      const fetchedModules = modulesRes.data || [];
      const fetchedProblems = problemsRes.data || [];
      const fetchedProgress = progressRes.data || null;

      setModules(fetchedModules);
      setProgress(fetchedProgress);
      setProblems(fetchedProblems);

      // Check if a problem is requested via query param e.g. ?problem=two-sum or ?problem=1
      const queryProb = searchParams.get('problem');
      if (queryProb) {
        const found = fetchedProblems.find(
          (p) => String(p.id) === queryProb || p.slug === queryProb
        );
        if (found) {
          setSelectedProblemId(found.id);
          setCurrentMode('workspace');
          return;
        }
      }

      // Default problem selection if none selected yet
      if (fetchedProblems.length > 0 && !selectedProblemId) {
        // Pick first unlocked problem
        const firstUnlocked = fetchedProblems.find((p) => !p.is_locked) || fetchedProblems[0];
        setSelectedProblemId(firstUnlocked.id);
      }
    } catch (err) {
      console.error('Failed to initialize coding data:', err);
      setError(err.response?.data?.detail || 'Failed to load coding curriculum.');
    } finally {
      setLoading(false);
    }
  }, [searchParams, selectedProblemId]);

  useEffect(() => {
    fetchInitialData();
  }, []);

  // 2. Fetch Problem Details & Submissions whenever selectedProblemId changes
  useEffect(() => {
    if (selectedProblemId) {
      fetchProblemDetail(selectedProblemId);
      fetchSubmissions(selectedProblemId);
      setExecutionResult(null);
      setExecutionError(null);
      setSubmissionResult(null);
    }
  }, [selectedProblemId]);

  const fetchProblemDetail = async (id) => {
    try {
      const res = await api.get(`/coding/problems/${id}`);
      setProblemDetail(res.data);
    } catch (err) {
      console.error('Failed to load problem detail:', err);
      setExecutionError(err.response?.data?.detail || 'Failed to load problem specifications.');
    }
  };

  const fetchSubmissions = async (id) => {
    try {
      const res = await api.get(`/coding/submissions?problem_id=${id}`);
      setSubmissions(res.data || []);
    } catch (err) {
      console.error('Failed to load submissions:', err);
    }
  };

  // 3. Draft Code Helpers
  const parseJsonField = (field, fallback) => {
    if (!field) return fallback;
    if (typeof field === 'object') return field;
    try {
      return JSON.parse(field);
    } catch {
      return fallback;
    }
  };

  const starterCode = useMemo(() => {
    return parseJsonField(problemDetail?.starter_code, {});
  }, [problemDetail]);

  const currentCodeKey = `${selectedProblemId}_${selectedLanguage}`;
  const currentCode =
    codeMap[currentCodeKey] !== undefined
      ? codeMap[currentCodeKey]
      : starterCode[selectedLanguage] || '# Write your solution here\n';

  const handleCodeChange = (newCode) => {
    if (!selectedProblemId) return;
    setCodeMap((prev) => ({
      ...prev,
      [currentCodeKey]: newCode || '',
    }));
  };

  const handleResetCode = () => {
    if (!selectedProblemId) return;
    const defaultCode = starterCode[selectedLanguage] || '';
    setCodeMap((prev) => ({
      ...prev,
      [currentCodeKey]: defaultCode,
    }));
    setExecutionResult(null);
    setExecutionError(null);
  };

  // 4. Run Code (Sample Test Cases)
  const handleRunCode = async () => {
    if (!selectedProblemId || isRunning || isSubmitting) return;
    setIsRunning(true);
    setExecutionResult(null);
    setExecutionError(null);

    try {
      const res = await api.post('/coding/run', {
        problem_id: selectedProblemId,
        language: selectedLanguage,
        code: currentCode,
      });
      setExecutionResult(res.data);
    } catch (err) {
      console.error('Run code error:', err);
      setExecutionError(err.response?.data?.detail || 'Code execution failed. Please verify syntax.');
    } finally {
      setIsRunning(false);
    }
  };

  // 5. Submit Code (All Test Cases + Progress Update)
  const handleSubmitCode = async () => {
    if (!selectedProblemId || isSubmitting || isRunning) return;
    setIsSubmitting(true);
    setSubmissionResult(null);
    setExecutionResult(null);
    setExecutionError(null);

    try {
      const res = await api.post('/coding/submit', {
        problem_id: selectedProblemId,
        language: selectedLanguage,
        code: currentCode,
      });
      const sub = res.data;
      setSubmissionResult(sub);

      // Refresh submissions list for this problem
      fetchSubmissions(selectedProblemId);

      // If submission is accepted, refresh modules and progress to detect unlocks
      if (sub.status === 'accepted') {
        const [newModsRes, newProgRes, newProbsRes] = await Promise.all([
          api.get('/coding/modules'),
          api.get('/coding/progress').catch(() => ({ data: null })),
          api.get('/coding/problems'),
        ]);

        const prevUnlockedCount = modules.filter((m) => m.is_unlocked).length;
        const newMods = newModsRes.data || [];
        const newUnlockedCount = newMods.filter((m) => m.is_unlocked).length;

        // Check if a new module unlocked!
        if (newUnlockedCount > prevUnlockedCount) {
          const newlyUnlocked = newMods.find(
            (nm) => nm.is_unlocked && !modules.find((om) => om.id === nm.id && om.is_unlocked)
          );
          if (newlyUnlocked) {
            setUnlockedToast({
              title: `Module ${newlyUnlocked.order_index}: ${newlyUnlocked.title}`,
              message: `Congratulations! You met the prerequisite requirements and unlocked ${newlyUnlocked.title}!`,
            });
          }
        }

        setModules(newMods);
        if (newProgRes.data) setProgress(newProgRes.data);
        if (newProbsRes.data) setProblems(newProbsRes.data);
      }
    } catch (err) {
      console.error('Submit code error:', err);
      setExecutionError(err.response?.data?.detail || 'Submission failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 6. AI Feedback Request
  const handleGetFeedback = async () => {
    if (!submissionResult || isFetchingFeedback) return;
    setIsFetchingFeedback(true);
    try {
      const res = await api.post(`/coding/submissions/${submissionResult.id}/feedback`);
      setSubmissionResult((prev) => ({ ...prev, feedback: res.data }));
    } catch (err) {
      console.error('Failed to get feedback:', err);
      setExecutionError(err.response?.data?.detail || 'Failed to generate AI feedback.');
    } finally {
      setIsFetchingFeedback(false);
    }
  };

  // 7. Load previous submission code
  const handleViewSubmission = async (sub) => {
    try {
      const res = await api.get(`/coding/submissions/${sub.id}`);
      setSubmissionResult(res.data);
      if (res.data.source_code) {
        setSelectedLanguage(res.data.language);
        handleCodeChange(res.data.source_code);
      }
    } catch (err) {
      console.error('Failed to fetch submission detail:', err);
    }
  };

  // 8. Next Recommended Problem Calculation
  const recommendedNextProblem = useMemo(() => {
    if (!problems || problems.length === 0) return null;
    const current = problems.find((p) => p.id === selectedProblemId);

    // 1. Next unsolved in current module
    if (current) {
      const modProbs = problems.filter((p) => p.module_id === current.module_id);
      const nextInMod = modProbs.find((p) => !p.is_solved && p.id !== current.id && !p.is_locked);
      if (nextInMod) return nextInMod;
    }

    // 2. Unsolved in any unlocked module (in order of module order_index)
    const unlockedModIds = new Set(modules.filter((m) => m.is_unlocked).map((m) => m.id));
    const nextUnlocked = problems.find(
      (p) => unlockedModIds.has(p.module_id) && !p.is_solved && p.id !== selectedProblemId
    );
    if (nextUnlocked) return nextUnlocked;

    // 3. Any unsolved accessible problem
    const anyUnsolved = problems.find((p) => !p.is_locked && !p.is_solved);
    if (anyUnsolved) return anyUnsolved;

    // 4. Fallback to first accessible problem
    return problems.find((p) => !p.is_locked) || null;
  }, [problems, modules, selectedProblemId]);

  const handleNextProblem = () => {
    if (recommendedNextProblem) {
      setSelectedProblemId(recommendedNextProblem.id);
      setExecutionResult(null);
      setSubmissionResult(null);
      setExecutionError(null);
    }
  };

  // 9. Navigation Mode Switcher handlers
  const handleSwitchMode = (mode) => {
    setCurrentMode(mode);
    setSearchParams({ view: mode });
  };

  const handleSelectModuleFromRoadmap = (moduleObj, startPractice = false) => {
    if (startPractice) {
      // Find first unsolved problem in this module
      const modProbs = problems.filter((p) => p.module_id === moduleObj.id);
      const target = modProbs.find((p) => !p.is_solved && !p.is_locked) || modProbs[0];
      if (target) {
        setSelectedProblemId(target.id);
        setCurrentMode('workspace');
        setSearchParams({ view: 'workspace', problem: target.slug });
        return;
      }
    }
    // Filter problem catalog by this module
    setSelectedModuleFilter(moduleObj.id);
    setCurrentMode('catalog');
    setSearchParams({ view: 'catalog', module: moduleObj.slug });
  };

  const handleOpenProblem = (prob) => {
    setSelectedProblemId(prob.id);
    setCurrentMode('workspace');
    setSearchParams({ view: 'workspace', problem: prob.slug });
  };

  // Loading Screen
  if (loading) {
    return (
      <div className="flex h-[75vh] items-center justify-center">
        <div className="flex flex-col items-center space-y-3">
          <RefreshCw className="animate-spin h-10 w-10 text-indigo-400" />
          <p className="text-sm font-semibold text-slate-300">Loading Algorithmic Learning Curriculum...</p>
        </div>
      </div>
    );
  }

  // Error Screen
  if (error && problems.length === 0) {
    return (
      <div className="p-8 max-w-md mx-auto text-center bg-slate-900 rounded-2xl shadow-sm border border-rose-500/30 mt-16">
        <AlertCircle className="mx-auto h-12 w-12 text-rose-400 mb-3" />
        <h3 className="text-lg font-bold text-white mb-1">Failed to Load Curriculum</h3>
        <p className="text-xs sm:text-sm text-slate-300 mb-5">{error}</p>
        <button
          onClick={fetchInitialData}
          className="btn-primary text-xs py-2 px-5 shadow-sm"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Experience Navigation Bar */}
      <div className="card p-3 sm:p-4 bg-slate-900 border border-slate-800 shadow-md flex flex-wrap items-center justify-between gap-3">
        {/* View Mode Buttons */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-950/80 border border-slate-800/80 rounded-xl">
          <button
            onClick={() => handleSwitchMode('roadmap')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              currentMode === 'roadmap'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Map size={15} />
            <span>Learning Roadmap</span>
          </button>

          <button
            onClick={() => handleSwitchMode('catalog')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              currentMode === 'catalog'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <BookOpen size={15} />
            <span>Problem Catalog</span>
          </button>

          <button
            onClick={() => handleSwitchMode('recommendations')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              currentMode === 'recommendations'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Sparkles size={15} className={currentMode === 'recommendations' ? 'text-white' : 'text-amber-400'} />
            <span>Mentor & Skills</span>
          </button>

          <button
            onClick={() => handleSwitchMode('workspace')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              currentMode === 'workspace'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Code size={15} />
            <span>Workspace</span>
          </button>
        </div>

        {/* Compact Progress Badge */}
        {progress && (
          <div className="flex items-center gap-3 text-xs">
            <div className="hidden md:flex items-center gap-1.5 font-semibold text-slate-400">
              <CheckCircle2 size={15} className="text-emerald-400" />
              <span>Solved:</span>
              <span className="font-bold text-white">
                {progress.total_unique_solved} / {progress.total_problems}
              </span>
            </div>

            <div className="w-24 sm:w-32 h-2 bg-slate-800 rounded-full overflow-hidden hidden sm:block">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-300"
                style={{ width: `${progress.overall_progress_percent}%` }}
              />
            </div>

            <span className="text-[11px] font-bold px-2.5 py-1 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-700/50">
              {progress.overall_progress_percent}% Complete
            </span>
          </div>
        )}
      </div>

      {/* Render Active View */}
      {currentMode === 'roadmap' && (
        <RoadmapView
          modules={modules}
          progress={progress}
          onSelectModule={handleSelectModuleFromRoadmap}
          onStartProblem={(prob) => handleOpenProblem(prob)}
          recommendedProblem={recommendedNextProblem}
          unlockedToast={unlockedToast}
          onDismissToast={() => setUnlockedToast(null)}
        />
      )}

      {currentMode === 'catalog' && (
        <ProblemCatalogView
          problems={problems}
          modules={modules}
          selectedModuleFilter={selectedModuleFilter}
          onSelectModuleFilter={setSelectedModuleFilter}
          onOpenProblem={handleOpenProblem}
          onBackToRoadmap={() => handleSwitchMode('roadmap')}
        />
      )}

      {currentMode === 'recommendations' && (
        <RecommendationsAndSkillsView
          onSelectProblem={(id) => {
            const prob = problems.find((p) => p.id === id);
            if (prob) {
              handleOpenProblem(prob);
            } else {
              setSelectedProblemId(id);
              setCurrentMode('workspace');
              setSearchParams({ view: 'workspace', problem: String(id) });
            }
          }}
          onNavigateToRoadmap={() => handleSwitchMode('roadmap')}
          onNavigateToCatalog={() => handleSwitchMode('catalog')}
        />
      )}

      {currentMode === 'workspace' && (
        <WorkspaceView
          problemDetail={problemDetail}
          allProblems={problems}
          selectedProblemId={selectedProblemId}
          onSelectProblemId={setSelectedProblemId}
          selectedLanguage={selectedLanguage}
          onChangeLanguage={setSelectedLanguage}
          currentCode={currentCode}
          onChangeCode={handleCodeChange}
          onResetCode={handleResetCode}
          onRunCode={handleRunCode}
          isRunning={isRunning}
          onSubmitCode={handleSubmitCode}
          isSubmitting={isSubmitting}
          executionResult={executionResult}
          executionError={executionError}
          submissionResult={submissionResult}
          submissions={submissions}
          onViewSubmission={handleViewSubmission}
          onGetFeedback={handleGetFeedback}
          isFetchingFeedback={isFetchingFeedback}
          onNextProblem={handleNextProblem}
          nextProblemAvailable={!!recommendedNextProblem}
          onBackToCatalog={() => handleSwitchMode('catalog')}
          onBackToRoadmap={() => handleSwitchMode('roadmap')}
        />
      )}
    </div>
  );
};

export default CodingInterviewPage;
