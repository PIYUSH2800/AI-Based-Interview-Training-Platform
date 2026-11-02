import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Mic, Square, Send, ChevronRight, Clock,
  AlertCircle, Volume2, VolumeX, Tag, Zap, Loader2, RefreshCw,
} from 'lucide-react';
import useSpeechRecognition from '../hooks/useSpeechRecognition';
import useTextToSpeech from '../hooks/useTextToSpeech';

const ActiveInterviewPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [interview, setInterview] = useState(null);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [currentQuestionId, setCurrentQuestionId] = useState(null);
  const [questionText, setQuestionText] = useState('');
  const [currentTopic, setCurrentTopic] = useState('');
  const [currentDifficulty, setCurrentDifficulty] = useState('');
  const [answer, setAnswer] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(true);
  const [generationError, setGenerationError] = useState(null);
  const [timeLeft, setTimeLeft] = useState(120);
  const [startTime] = useState(Date.now());
  const initialLoadDone = useRef(false);

  // Speech recognition
  const handleFinalTranscript = useCallback((text) => {
    setAnswer(prev => prev + (prev && !prev.endsWith(' ') ? ' ' : '') + text);
  }, []);
  const {
    isSupported: isSpeechInputSupported, isRecording,
    interimTranscript, error: speechError,
    startRecording, stopRecording,
  } = useSpeechRecognition(handleFinalTranscript);

  // TTS
  const {
    isSupported: isTTSSupported, isSpeaking,
    error: ttsError, speak, stop: stopSpeaking,
  } = useTextToSpeech();

  // Load interview on mount — resumes existing questions if present
  useEffect(() => {
    if (initialLoadDone.current) return;
    initialLoadDone.current = true;

    const fetchInterviewAndQuestions = async () => {
      try {
        const res = await api.get(`/interviews/${id}/details`);
        const intData = res.data;
        setInterview(intData);

        const existingQuestions = intData.questions || [];
        if (existingQuestions.length > 0) {
          // Check for pending unanswered question
          const unansweredIdx = existingQuestions.findIndex(q => !q.answer);
          if (unansweredIdx !== -1) {
            const pendingQ = existingQuestions[unansweredIdx];
            setCurrentQuestionIdx(unansweredIdx);
            setCurrentQuestionId(pendingQ.id);
            setQuestionText(pendingQ.question_text);
            setCurrentTopic(pendingQ.topic || '');
            setCurrentDifficulty(pendingQ.difficulty || intData.difficulty);
            setIsLoadingQuestion(false);
            setGenerationError(null);
            return;
          } else if (existingQuestions.length < intData.total_questions) {
            // All prior answered, generate next
            const nextIdx = existingQuestions.length;
            setCurrentQuestionIdx(nextIdx);
            await generateAndSaveNextQuestion(intData, nextIdx);
            return;
          } else {
            // All completed
            navigate(`/interview/${id}/result`);
            return;
          }
        }

        // Fresh interview with no questions yet
        await generateAndSaveNextQuestion(intData, 0);
      } catch (err) {
        console.error('Failed to load interview session:', err);
        navigate('/dashboard');
      }
    };
    fetchInterviewAndQuestions();
  }, [id, navigate]);

  // Countdown timer — only runs when a valid question exists and is not loading
  useEffect(() => {
    if (isLoadingQuestion || generationError || !questionText) {
      return;
    }
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          stopSpeaking();
          if (isRecording) stopRecording();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [currentQuestionIdx, isLoadingQuestion, generationError, questionText, stopSpeaking, isRecording, stopRecording]);

  useEffect(() => { stopSpeaking(); }, [currentQuestionIdx]);

  const generateAndSaveNextQuestion = async (intData, seqIdx) => {
    setIsLoadingQuestion(true);
    setGenerationError(null);
    setQuestionText('');
    try {
      const res = await api.post('/ai/generate-question', {
        job_role: intData.job_role,
        interview_type: intData.interview_type,
        difficulty: intData.difficulty,
        skills: '',
        interview_id: Number(id),
      });

      const qText = res.data.question;
      const qTopic = res.data.topic || '';
      const qDiff = res.data.difficulty || intData.difficulty;

      const qRes = await api.post(`/interviews/${id}/questions`, {
        question_text: qText,
        question_type: intData.interview_type,
        difficulty: qDiff,
        topic: qTopic,
        sequence_number: seqIdx + 1,
      });

      setQuestionText(qText);
      setCurrentTopic(qTopic);
      setCurrentDifficulty(qDiff);
      setCurrentQuestionId(qRes.data.id);
      setTimeLeft(120);
      setGenerationError(null);
    } catch (err) {
      console.error('Error generating question:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to generate question. Please try clicking retry.';
      setGenerationError(errorMsg);
      setQuestionText('');
    } finally {
      setIsLoadingQuestion(false);
    }
  };

  const handleRetryQuestion = () => {
    if (interview) {
      generateAndSaveNextQuestion(interview, currentQuestionIdx);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim() || !questionText || isLoadingQuestion || generationError) return;
    setIsEvaluating(true);
    if (isRecording) stopRecording();
    stopSpeaking();
    try {
      const evalRes = await api.post('/ai/evaluate-answer', {
        question_text: questionText,
        answer_text: answer,
      });
      const evaluation = evalRes.data;
      if (currentQuestionId) {
        await api.post(`/interviews/${id}/questions/${currentQuestionId}/answers`, {
          answer_text: answer,
          score: evaluation.score,
          technical_score: evaluation.technical_score,
          communication_score: evaluation.communication_score,
          relevance_score: evaluation.relevance_score,
          completeness_score: evaluation.completeness_score,
          feedback: evaluation.feedback,
        });
      }
      setAnswer('');
      if (interview && currentQuestionIdx < interview.total_questions - 1) {
        const nextIdx = currentQuestionIdx + 1;
        setCurrentQuestionIdx(nextIdx);
        await generateAndSaveNextQuestion(interview, nextIdx);
      } else {
        const durationSecs = Math.round((Date.now() - startTime) / 1000);
        await api.post(`/interviews/${id}/complete`, { duration: durationSecs });
        navigate(`/interview/${id}/result`);
      }
    } catch {
      // keep user's answer, show nothing extra
    } finally {
      setIsEvaluating(false);
    }
  };

  const toggleRecording = () => isRecording ? stopRecording() : startRecording();
  const handleReadQuestion = () => isSpeaking ? stopSpeaking() : speak(questionText);

  if (!interview) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-500">
        <Loader2 size={32} className="animate-spin text-indigo-500" />
        <span className="text-sm font-medium">Loading interview environment…</span>
      </div>
    );
  }

  const formatTime = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  const isLast = currentQuestionIdx === interview.total_questions - 1;
  const progress = ((currentQuestionIdx + (isLoadingQuestion || !answer.trim() ? 0 : 0)) / interview.total_questions) * 100;
  const difficultyColor = {
    Beginner: 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30',
    Intermediate: 'bg-indigo-500/15 text-indigo-300 border border-indigo-500/30',
    Advanced: 'bg-amber-500/15 text-amber-300 border border-amber-500/30',
  }[currentDifficulty] || 'bg-slate-800 text-slate-300 border border-slate-700';

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6 animate-fade-in">
      {/* ── Header ── */}
      <div className="card px-5 py-4">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-sm font-bold text-white">{interview.job_role}</span>
            {currentTopic && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700/60">
                <Tag size={11} /> {currentTopic}
              </span>
            )}
            {currentDifficulty && (
              <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${difficultyColor}`}>
                <Zap size={11} /> {currentDifficulty}
              </span>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold text-sm transition-colors ${
                timeLeft < 30 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-slate-800 text-slate-200 border border-slate-700/60'
              }`}
              aria-live="polite"
              aria-label={`Time remaining: ${formatTime(timeLeft)}`}
            >
              <Clock size={16} aria-hidden="true" />
              {formatTime(timeLeft)}
            </div>
            <span className="text-xs font-semibold text-slate-400">
              {currentQuestionIdx + 1} / {interview.total_questions}
            </span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-3 h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full transition-all duration-500"
            style={{ width: `${((currentQuestionIdx) / interview.total_questions) * 100}%` }}
            role="progressbar"
            aria-valuenow={currentQuestionIdx}
            aria-valuemax={interview.total_questions}
          />
        </div>
      </div>

      {/* ── Main Question Card ── */}
      <div className="card p-6 md:p-8 flex flex-col gap-6">
        {/* Question area */}
        <div>
          {/* TTS control */}
          {isTTSSupported && !isLoadingQuestion && questionText && (
            <div className="flex items-center gap-3 mb-4">
              <button
                id="read-question-btn"
                onClick={handleReadQuestion}
                aria-label={isSpeaking ? 'Stop reading aloud' : 'Read question aloud'}
                className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                  isSpeaking
                    ? 'bg-indigo-950/70 text-indigo-300 hover:bg-indigo-900 border border-indigo-700/50'
                    : 'bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700'
                }`}
              >
                {isSpeaking ? (
                  <>
                    <VolumeX size={14} aria-hidden="true" />
                    Stop Speaking
                    {/* Wave bars */}
                    <span className="flex items-end gap-0.5 h-3.5" aria-hidden="true">
                      <span className="w-0.5 bg-indigo-400 rounded-full animate-bar-1" style={{ height: '6px' }} />
                      <span className="w-0.5 bg-indigo-400 rounded-full animate-bar-2" style={{ height: '10px' }} />
                      <span className="w-0.5 bg-indigo-400 rounded-full animate-bar-3" style={{ height: '6px' }} />
                    </span>
                  </>
                ) : (
                  <>
                    <Volume2 size={14} aria-hidden="true" />
                    Read Question
                  </>
                )}
              </button>
              {ttsError && (
                <span className="flex items-center gap-1 text-xs text-amber-300 bg-amber-950/40 px-2.5 py-1 rounded-full border border-amber-800/60" role="alert">
                  <AlertCircle size={12} />
                  {ttsError}
                </span>
              )}
            </div>
          )}

          {/* Question text */}
          <div className="min-h-[80px]">
            {isLoadingQuestion ? (
              <div className="space-y-3 animate-pulse">
                <div className="h-5 bg-slate-800 rounded-full w-full" />
                <div className="h-5 bg-slate-800 rounded-full w-5/6" />
                <div className="h-5 bg-slate-800/60 rounded-full w-3/4" />
              </div>
            ) : generationError ? (
              <div className="p-6 rounded-xl bg-amber-950/40 border border-amber-800/60 flex flex-col items-center text-center gap-3" role="alert">
                <AlertCircle size={32} className="text-amber-400" />
                <div>
                  <h3 className="text-base font-semibold text-white">Unable to generate question</h3>
                  <p className="text-sm text-slate-300 mt-1">{generationError}</p>
                </div>
                <button
                  id="retry-question-btn"
                  onClick={handleRetryQuestion}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg shadow-sm transition"
                >
                  <RefreshCw size={15} />
                  Retry Question
                </button>
              </div>
            ) : (
              <h2 className="text-xl md:text-2xl font-semibold text-white leading-relaxed">
                {questionText}
              </h2>
            )}
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-slate-800" />

        {/* Answer section */}
        <div className="space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Your Answer</p>

          {/* Textarea */}
          <div className="relative">
            <textarea
              id="answer-textarea"
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              disabled={isLoadingQuestion || !!generationError || !questionText}
              placeholder={
                generationError
                  ? "Question generation failed. Click Retry Question above to generate."
                  : isLoadingQuestion
                  ? "Generating question…"
                  : "Type your answer here, or use the microphone to speak…"
              }
              aria-label="Your answer"
              rows={6}
              className="w-full p-4 bg-slate-900 border border-slate-700 rounded-xl text-slate-100 placeholder-slate-400 leading-relaxed text-base resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
            />
            {/* Interim transcript ghost */}
            {interimTranscript && (
              <div className="absolute bottom-4 left-4 right-4 text-slate-400 italic text-sm pointer-events-none leading-relaxed">
                {interimTranscript}
              </div>
            )}
            {/* Recording indicator */}
            {isRecording && (
              <div className="absolute top-3 right-3 flex items-center gap-1.5 px-2.5 py-1 bg-red-500/20 text-red-300 border border-red-500/30 rounded-full text-xs font-semibold" aria-live="polite">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-mic-pulse" aria-hidden="true" />
                Listening…
              </div>
            )}
          </div>

          {/* Speech error */}
          {speechError && (
            <div className="flex items-center gap-2 text-sm text-red-300 bg-red-500/20 px-3 py-2 rounded-lg border border-red-500/30" role="alert">
              <AlertCircle size={14} aria-hidden="true" />
              {speechError}
            </div>
          )}

          {/* Controls */}
          <div className="flex items-center justify-between gap-4 flex-wrap">
            {/* Mic button */}
            {!isSpeechInputSupported ? (
              <p className="text-xs text-slate-400 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
                Voice input not supported in this browser.
              </p>
            ) : (
              <button
                id="toggle-recording-btn"
                onClick={toggleRecording}
                disabled={isLoadingQuestion || !!generationError || !questionText}
                aria-label={isRecording ? 'Stop voice input' : 'Start voice input'}
                className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                  isRecording
                    ? 'bg-rose-600 text-white hover:bg-rose-700 focus-visible:ring-rose-400'
                    : 'bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700 focus-visible:ring-slate-400'
                }`}
              >
                {isRecording
                  ? <Square size={16} fill="currentColor" aria-hidden="true" />
                  : <Mic size={16} aria-hidden="true" />
                }
                {isRecording ? 'Stop Voice' : 'Voice Input'}
              </button>
            )}

            {/* Submit button */}
            <button
              id="submit-answer-btn"
              onClick={handleSubmitAnswer}
              disabled={isEvaluating || !answer.trim() || isLoadingQuestion || !!generationError || !questionText}
              aria-label={isLast ? 'Finish interview' : 'Submit answer and go to next question'}
              className="inline-flex items-center gap-2 px-7 py-2.5 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-bold rounded-xl shadow-md shadow-indigo-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2"
            >
              {isEvaluating ? (
                <>
                  <Loader2 size={16} className="animate-spin" aria-hidden="true" />
                  Evaluating…
                </>
              ) : isLast ? (
                <>Finish Interview <Send size={16} aria-hidden="true" /></>
              ) : (
                <>Submit &amp; Next <ChevronRight size={16} aria-hidden="true" /></>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActiveInterviewPage;
