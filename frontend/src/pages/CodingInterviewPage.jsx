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
  Sparkles
} from 'lucide-react';
import api from '../services/api';

const LANGUAGE_MAP = {
  python: { name: 'Python 3', monaco: 'python' },
  java: { name: 'Java', monaco: 'java' },
  cpp: { name: 'C++', monaco: 'cpp' },
};

const CodingInterviewPage = () => {
  const [problems, setProblems] = useState([]);
  const [selectedProblemId, setSelectedProblemId] = useState(null);
  const [problemDetail, setProblemDetail] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  
  const [isRunning, setIsRunning] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [executionError, setExecutionError] = useState(null);
  const [notice, setNotice] = useState(null);
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [leftTab, setLeftTab] = useState('problem');

  // Fetch problem list on mount
  useEffect(() => {
    fetchProblems();
  }, []);

  const fetchProblems = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/coding/problems');
      setProblems(res.data || []);
      if (res.data && res.data.length > 0) {
        setSelectedProblemId(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch coding problems:', err);
      setError(err.response?.data?.detail || 'Failed to load coding problems');
    } finally {
      setLoading(false);
    }
  };

  // Fetch problem details when selectedProblemId changes
  useEffect(() => {
    if (selectedProblemId) {
      fetchProblemDetail(selectedProblemId);
      fetchSubmissions(selectedProblemId);
      setExecutionResult(null);
      setExecutionError(null);
      setSubmissionResult(null);
      setLeftTab('problem');
    }
  }, [selectedProblemId]);

  const fetchSubmissions = async (id) => {
    try {
      const res = await api.get(`/coding/submissions?problem_id=${id}`);
      setSubmissions(res.data || []);
    } catch (err) {
      console.error('Failed to fetch submissions:', err);
    }
  };

  // Reset execution state on language change
  useEffect(() => {
    setExecutionResult(null);
    setExecutionError(null);
  }, [selectedLanguage]);

  const fetchProblemDetail = async (id) => {
    setDetailLoading(true);
    setNotice(null);
    try {
      const res = await api.get(`/coding/problems/${id}`);
      setProblemDetail(res.data);
    } catch (err) {
      console.error('Failed to fetch problem detail:', err);
      setError(err.response?.data?.detail || 'Failed to load problem details');
    } finally {
      setDetailLoading(false);
    }
  };

  // Parse JSON helper with fallback
  const parseJsonField = (field, fallback) => {
    if (!field) return fallback;
    if (typeof field === 'object') return field;
    try {
      return JSON.parse(field);
    } catch {
      return fallback;
    }
  };

  // Current problem detail parsed fields
  const examples = parseJsonField(problemDetail?.examples, []);
  const constraints = parseJsonField(problemDetail?.constraints, []);
  const starterCode = parseJsonField(problemDetail?.starter_code, {});
  const supportedLangs = parseJsonField(problemDetail?.supported_languages, ['python', 'java', 'cpp']);

  // Get code for current problem + language
  const getCodeKey = (probId, lang) => `${probId}_${lang}`;
  const currentCodeKey = getCodeKey(selectedProblemId, selectedLanguage);
  
  const currentCode = codeMap[currentCodeKey] !== undefined 
    ? codeMap[currentCodeKey] 
    : (starterCode[selectedLanguage] || '# Write your code here');

  const handleCodeChange = (newCode) => {
    if (!selectedProblemId) return;
    setCodeMap(prev => ({
      ...prev,
      [currentCodeKey]: newCode || ''
    }));
  };

  const handleResetCode = () => {
    if (!selectedProblemId) return;
    const defaultCode = starterCode[selectedLanguage] || '';
    setCodeMap(prev => ({
      ...prev,
      [currentCodeKey]: defaultCode
    }));
    setExecutionResult(null);
    setExecutionError(null);
  };

  const handleRunCode = async () => {
    if (!selectedProblemId || isRunning || isSubmitting) return;
    setIsRunning(true);
    setExecutionResult(null);
    setSubmissionResult(null);
    setExecutionError(null);
    setNotice(null);

    try {
      const res = await api.post('/coding/run', {
        problem_id: selectedProblemId,
        language: selectedLanguage,
        code: currentCode
      });
      setExecutionResult(res.data);
    } catch (err) {
      console.error('Execution API error:', err);
      setExecutionError(err.response?.data?.detail || 'Execution service failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmitCode = async () => {
    if (!selectedProblemId || isSubmitting || isRunning) return;
    setIsSubmitting(true);
    setSubmissionResult(null);
    setExecutionResult(null);
    setExecutionError(null);
    setNotice(null);

    try {
      const res = await api.post('/coding/submit', {
        problem_id: selectedProblemId,
        language: selectedLanguage,
        code: currentCode
      });
      setSubmissionResult(res.data);
      fetchSubmissions(selectedProblemId);
    } catch (err) {
      console.error('Submit API error:', err);
      setExecutionError(err.response?.data?.detail || 'Submission service failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleViewSubmission = async (sub) => {
    try {
      const res = await api.get(`/coding/submissions/${sub.id}`);
      setSubmissionResult(res.data);
      setExecutionResult(null);
      if (res.data.source_code) {
        setSelectedLanguage(res.data.language);
        handleCodeChange(res.data.source_code);
      }
    } catch (err) {
      console.error('Failed to fetch submission details:', err);
    }
  };

  // Navigate next / previous problem
  const currentIndex = problems.findIndex(p => p.id === selectedProblemId);
  const handlePrevProblem = () => {
    if (currentIndex > 0) {
      setSelectedProblemId(problems[currentIndex - 1].id);
    }
  };
  const handleNextProblem = () => {
    if (currentIndex < problems.length - 1) {
      setSelectedProblemId(problems[currentIndex + 1].id);
    }
  };

  const getDifficultyBadge = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy':
        return 'bg-emerald-500/10 text-emerald-600 border-emerald-200';
      case 'medium':
        return 'bg-amber-500/10 text-amber-600 border-amber-200';
      case 'hard':
        return 'bg-rose-500/10 text-rose-600 border-rose-200';
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-slate-600 font-medium">Loading Coding Interview Module...</p>
        </div>
      </div>
    );
  }

  if (error && problems.length === 0) {
    return (
      <div className="p-8 max-w-lg mx-auto text-center bg-white rounded-xl shadow-sm border border-red-100 mt-12">
        <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-slate-900 mb-2">Failed to Load Problems</h2>
        <p className="text-slate-600 text-sm mb-6">{error}</p>
        <button 
          onClick={fetchProblems}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] bg-slate-900 text-slate-100 rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
      {/* Top Header / Navigation Bar */}
      <div className="bg-slate-950 border-b border-slate-800 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-blue-400 font-bold text-lg">
            <Code className="h-6 w-6" />
            <span>Coding Interview</span>
          </div>

          <div className="h-5 w-px bg-slate-800 hidden sm:block" />

          {/* Problem Selector Dropdown */}
          <div className="relative">
            <select
              value={selectedProblemId || ''}
              onChange={(e) => setSelectedProblemId(Number(e.target.value))}
              className="bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 text-sm font-medium focus:outline-none focus:border-blue-500 hover:border-slate-600 transition"
            >
              {problems.map((p, idx) => (
                <option key={p.id} value={p.id}>
                  {idx + 1}. {p.title} ({p.difficulty})
                </option>
              ))}
            </select>
          </div>

          {/* Next / Prev Problem controls */}
          <div className="flex items-center space-x-1">
            <button
              onClick={handlePrevProblem}
              disabled={currentIndex <= 0}
              className="p-1.5 rounded-lg border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent"
              title="Previous Problem"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={handleNextProblem}
              disabled={currentIndex >= problems.length - 1}
              className="p-1.5 rounded-lg border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent"
              title="Next Problem"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Current Problem Metadata Badges */}
        {problemDetail && (
          <div className="flex items-center space-x-3">
            <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getDifficultyBadge(problemDetail.difficulty)}`}>
              {problemDetail.difficulty}
            </span>
            <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
              {problemDetail.category}
            </span>
          </div>
        )}
      </div>

      {/* Main Content Area (Split Screen) */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
        
        {/* Left Panel: Problem Statement & Examples */}
        <div className="lg:col-span-5 bg-slate-900 border-r border-slate-800 flex flex-col h-full overflow-y-auto p-6 space-y-6">
          {detailLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
            </div>
          ) : problemDetail ? (
            <>
              <div className="flex space-x-1 border-b border-slate-800 pb-2">
                <button onClick={() => setLeftTab('problem')} className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${leftTab === 'problem' ? 'bg-slate-800 text-blue-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}>Description</button>
                <button onClick={() => setLeftTab('submissions')} className={`px-4 py-2 text-sm font-medium rounded-t-lg transition flex items-center space-x-2 ${leftTab === 'submissions' ? 'bg-slate-800 text-blue-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}>
                  <span>Submissions</span>
                  {submissions.length > 0 && <span className="bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded text-xs">{submissions.length}</span>}
                </button>
              </div>

              {leftTab === 'problem' ? (
              <div className="space-y-6">
                <div>
                  <h1 className="text-2xl font-bold text-white mb-2">{problemDetail.title}</h1>
                <div className="flex items-center space-x-2 text-xs text-slate-400 mb-4">
                  <Layers className="h-3.5 w-3.5" />
                  <span>Category: {problemDetail.category}</span>
                </div>
                <div className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed whitespace-pre-line">
                  {problemDetail.description}
                </div>
              </div>

              {/* Examples Section */}
              {examples && examples.length > 0 && (
                <div className="space-y-4 pt-2">
                  <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
                    <FileCode className="h-4 w-4 text-blue-400" />
                    <span>Examples</span>
                  </h3>
                  {examples.map((ex, idx) => (
                    <div key={idx} className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-2 text-xs">
                      <div className="font-semibold text-slate-300">Example {idx + 1}:</div>
                      <div className="font-mono text-slate-300">
                        <span className="text-slate-500 font-sans">Input: </span>
                        {ex.input}
                      </div>
                      <div className="font-mono text-slate-300">
                        <span className="text-slate-500 font-sans">Output: </span>
                        {ex.output}
                      </div>
                      {ex.explanation && (
                        <div className="text-slate-400 italic pt-1 border-t border-slate-900">
                          <span className="font-sans font-normal text-slate-500">Explanation: </span>
                          {ex.explanation}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Constraints Section */}
              {constraints && constraints.length > 0 && (
                <div className="space-y-3 pt-2">
                  <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
                    <HelpCircle className="h-4 w-4 text-amber-400" />
                    <span>Constraints</span>
                  </h3>
                  <ul className="list-disc list-inside space-y-1.5 text-xs text-slate-300 font-mono bg-slate-950 p-4 rounded-lg border border-slate-800">
                    {constraints.map((c, idx) => (
                      <li key={idx} className="leading-relaxed">{c}</li>
                    ))}
                  </ul>
                </div>
              )}
              </div>
              ) : (
                <div className="space-y-4">
                  <h2 className="text-lg font-bold text-white mb-4">Past Submissions</h2>
                  {submissions.length === 0 ? (
                    <div className="text-slate-500 text-sm text-center py-8">No submissions yet for this problem.</div>
                  ) : (
                    <div className="space-y-3">
                      {submissions.map(sub => (
                        <div key={sub.id} onClick={() => handleViewSubmission(sub)} className="cursor-pointer bg-slate-950 border border-slate-800 hover:border-slate-600 p-4 rounded-lg flex flex-col space-y-2 transition">
                          <div className="flex justify-between items-center">
                            <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${sub.status === 'accepted' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>{sub.status.replace('_', ' ')}</span>
                            <span className="text-slate-400 text-xs font-mono">{new Date(sub.created_at).toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between items-center text-sm font-medium">
                            <span className="text-slate-300">Score: {sub.score}/100</span>
                            <span className="text-slate-400 text-xs">{sub.language}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Right Panel: Code Editor & Execution Controls */}
        <div className="lg:col-span-7 bg-slate-950 flex flex-col h-full overflow-hidden">
          
          {/* Editor Header / Language Bar */}
          <div className="bg-slate-900 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Language:</span>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="bg-slate-950 text-blue-400 border border-slate-700 rounded-md px-3 py-1 text-xs font-semibold focus:outline-none focus:border-blue-500 cursor-pointer"
              >
                {supportedLangs.map((langKey) => (
                  <option key={langKey} value={langKey}>
                    {LANGUAGE_MAP[langKey]?.name || langKey}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={handleResetCode}
              className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-amber-400 transition px-2 py-1 rounded hover:bg-slate-800"
              title="Reset code to starter template"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Reset Template</span>
            </button>
          </div>

          {/* Monaco Editor Component */}
          <div className="flex-1 relative overflow-hidden min-h-[300px]">
            <Editor
              height="100%"
              language={LANGUAGE_MAP[selectedLanguage]?.monaco || 'plaintext'}
              theme="vs-dark"
              value={currentCode}
              onChange={handleCodeChange}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                tabSize: 4,
                padding: { top: 12, bottom: 12 },
              }}
            />
          </div>

          {/* Execution Results Panel */}
          {(isRunning || isSubmitting || executionResult || submissionResult || executionError) && (
            <div className="border-t border-slate-800 bg-slate-900 max-h-[40%] overflow-y-auto p-4 space-y-3">
              {(isRunning || isSubmitting) && (
                <div className="flex items-center space-x-3 text-blue-400 text-sm font-medium py-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400" />
                  <span>{isRunning ? 'Executing code in isolated environment...' : 'Evaluating submission...'}</span>
                </div>
              )}

              {executionError && (
                <div className="p-3 bg-red-950/60 border border-red-800/80 rounded-lg text-red-200 text-xs flex items-start space-x-2">
                  <AlertCircle className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-red-300">Execution Error</div>
                    <div className="mt-1">{executionError}</div>
                  </div>
                </div>
              )}

              {submissionResult && (
                <div className="space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-800">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Submission Result</span>
                      <span className={`px-2 py-0.5 text-xs rounded font-bold uppercase ${
                        submissionResult.status === 'accepted' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      }`}>
                        {submissionResult.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-center py-2">
                    <div className="bg-slate-950 border border-slate-800 rounded-lg p-3">
                      <div className="text-xs text-slate-500 uppercase font-bold mb-1">Score</div>
                      <div className={`text-xl font-mono font-bold ${submissionResult.score === 100 ? 'text-emerald-400' : 'text-amber-400'}`}>{submissionResult.score} / 100</div>
                    </div>
                    <div className="bg-slate-950 border border-slate-800 rounded-lg p-3">
                      <div className="text-xs text-slate-500 uppercase font-bold mb-1">Tests Passed</div>
                      <div className="text-xl font-mono font-bold text-slate-300">{submissionResult.passed_tests} / {submissionResult.total_tests}</div>
                    </div>
                    <div className="bg-slate-950 border border-slate-800 rounded-lg p-3">
                      <div className="text-xs text-slate-500 uppercase font-bold mb-1">Runtime</div>
                      <div className="text-xl font-mono font-bold text-blue-400">{submissionResult.execution_time_ms || 0} ms</div>
                    </div>
                  </div>
                  
                  {submissionResult.error_message && (
                    <div className="bg-slate-950 border border-rose-900/50 p-3 rounded-lg text-xs font-mono text-rose-300 whitespace-pre-wrap max-h-36 overflow-y-auto mt-3">
                      <div className="text-rose-400 font-bold font-sans mb-1 flex items-center space-x-1.5">
                        <AlertCircle className="h-3.5 w-3.5" />
                        <span>ERROR DETAILS:</span>
                      </div>
                      {submissionResult.error_message}
                    </div>
                  )}
                </div>
              )}

              {executionResult && (
                <div className="space-y-3">
                  {/* Results Header */}
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-800">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Test Results</span>
                      <span className={`px-2 py-0.5 text-xs rounded font-bold uppercase ${
                        executionResult.status === 'completed'
                          ? (executionResult.passed === executionResult.total ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30')
                          : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      }`}>
                        {executionResult.status === 'completed' 
                          ? (executionResult.passed === executionResult.total ? 'Passed All Tests' : 'Partial Pass')
                          : executionResult.status.replace('_', ' ')}
                      </span>
                    </div>

                    <div className="text-xs font-mono font-medium text-slate-400">
                      Passed: <span className="text-emerald-400 font-bold">{executionResult.passed}</span> / <span className="text-slate-200 font-bold">{executionResult.total}</span>
                    </div>
                  </div>

                  {/* Compile/Runtime Error banner if present */}
                  {executionResult.error && (
                    <div className="bg-slate-950 border border-rose-900/50 p-3 rounded-lg text-xs font-mono text-rose-300 whitespace-pre-wrap max-h-36 overflow-y-auto">
                      <div className="text-rose-400 font-bold font-sans mb-1 flex items-center space-x-1.5">
                        <AlertCircle className="h-3.5 w-3.5" />
                        <span>{executionResult.status.replace('_', ' ').toUpperCase()} DETAILS:</span>
                      </div>
                      {executionResult.error}
                    </div>
                  )}

                  {/* Test Cases Cards */}
                  {executionResult.results && executionResult.results.length > 0 && (
                    <div className="space-y-2">
                      {executionResult.results.map((res, idx) => (
                        <div key={idx} className={`p-3 rounded-lg border text-xs space-y-1.5 transition ${
                          res.passed 
                            ? 'bg-emerald-950/20 border-emerald-800/40 text-slate-200' 
                            : 'bg-rose-950/20 border-rose-800/40 text-slate-200'
                        }`}>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2 font-semibold">
                              {res.passed ? (
                                <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                              ) : (
                                <AlertCircle className="h-4 w-4 text-rose-400 flex-shrink-0" />
                              )}
                              <span>
                                {res.is_sample ? `Sample Test Case #${idx + 1}` : `Hidden Test Case #${idx + 1}`}
                              </span>
                            </div>

                            <div className="flex items-center space-x-3 text-[11px] text-slate-400 font-mono">
                              {res.execution_time_ms !== undefined && (
                                <span>{res.execution_time_ms} ms</span>
                              )}
                              <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                res.passed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                              }`}>
                                {res.passed ? 'PASSED' : 'FAILED'}
                              </span>
                            </div>
                          </div>

                          {/* Show sample test case input & output details */}
                          {res.is_sample && (
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 font-mono text-[11px] bg-slate-950/60 p-2 rounded border border-slate-800/80">
                              <div>
                                <span className="text-slate-500 font-sans block text-[10px]">Input:</span>
                                <span className="text-slate-300 whitespace-pre-wrap">{res.input}</span>
                              </div>
                              <div>
                                <span className="text-slate-500 font-sans block text-[10px]">Expected:</span>
                                <span className="text-emerald-400/90 whitespace-pre-wrap">{res.expected_output}</span>
                              </div>
                              <div>
                                <span className="text-slate-500 font-sans block text-[10px]">Actual Output:</span>
                                <span className={res.passed ? 'text-emerald-300' : 'text-rose-300'}>
                                  {res.output || '(empty)'}
                                </span>
                              </div>
                            </div>
                          )}

                          {/* Hidden test case note when failed */}
                          {!res.is_sample && !res.passed && (
                            <div className="text-[11px] text-slate-400 italic pt-0.5">
                              Hidden test case failed. Output and test data are hidden.
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Execution Notification Banner */}
          {notice && (
            <div className="bg-blue-950/80 border-t border-b border-blue-800/80 px-4 py-2.5 flex items-center space-x-2 text-xs text-blue-200">
              <Sparkles className="h-4 w-4 text-blue-400 flex-shrink-0" />
              <span>{notice.message}</span>
            </div>
          )}

          {/* Bottom Action Footer */}
          <div className="bg-slate-900 border-t border-slate-800 px-6 py-3.5 flex items-center justify-between">
            <div className="text-xs text-slate-500 font-medium hidden sm:block">
              Draft auto-saved locally
            </div>

            <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
              <button
                onClick={handleRunCode}
                disabled={isRunning}
                className="flex-1 sm:flex-initial flex items-center justify-center space-x-2 px-5 py-2 rounded-lg text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 disabled:opacity-50 transition"
              >
                <Play className="h-4 w-4 text-blue-400" />
                <span>{isRunning ? 'Running...' : 'Run Code'}</span>
              </button>

              <button
                onClick={handleSubmitCode}
                disabled={isSubmitting || isRunning}
                className="flex-1 sm:flex-initial flex items-center justify-center space-x-2 px-5 py-2 rounded-lg text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
                <span>{isSubmitting ? 'Submitting...' : 'Submit Code'}</span>
              </button>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default CodingInterviewPage;


