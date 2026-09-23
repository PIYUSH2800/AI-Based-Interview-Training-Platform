import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Mic,
  Square,
  Send,
  ChevronRight,
  Clock,
  AlertCircle,
  Volume2,
  VolumeX,
} from 'lucide-react';
import useSpeechRecognition from '../hooks/useSpeechRecognition';
import useTextToSpeech from '../hooks/useTextToSpeech';

const ActiveInterviewPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // ── Interview state ───────────────────────────────────────────────────────
  const [interview, setInterview] = useState(null);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [currentQuestionId, setCurrentQuestionId] = useState(null);
  const [questionText, setQuestionText] = useState('Loading your first question...');
  const [currentTopic, setCurrentTopic] = useState('');
  const [answer, setAnswer] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [timeLeft, setTimeLeft] = useState(120); // 2 mins per question
  const [startTime] = useState(Date.now());

  // ── Speech-to-text (Checkpoint 6A) ───────────────────────────────────────
  const handleFinalTranscript = useCallback((text) => {
    setAnswer((prev) => prev + (prev && !prev.endsWith(' ') ? ' ' : '') + text);
  }, []);

  const {
    isSupported: isSpeechInputSupported,
    isRecording,
    interimTranscript,
    error: speechError,
    startRecording,
    stopRecording,
  } = useSpeechRecognition(handleFinalTranscript);

  // ── Text-to-speech (Checkpoint 6B) ───────────────────────────────────────
  const {
    isSupported: isTTSSupported,
    isSpeaking,
    error: ttsError,
    speak,
    stop: stopSpeaking,
  } = useTextToSpeech();

  // ── Load interview on mount ───────────────────────────────────────────────
  useEffect(() => {
    const fetchInterview = async () => {
      try {
        const res = await api.get(`/interviews/${id}`);
        setInterview(res.data);
        await generateAndSaveNextQuestion(res.data, 0);
      } catch (err) {
        console.error('Failed to fetch interview', err);
        navigate('/dashboard');
      }
    };
    fetchInterview();
  }, [id, navigate]);

  // ── Per-question countdown timer ──────────────────────────────────────────
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          // Timer expired — stop all voice features and let existing logic handle it
          stopSpeaking();
          if (isRecording) stopRecording();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [currentQuestionIdx, stopSpeaking, isRecording, stopRecording]);

  // ── Stop TTS whenever the question changes ────────────────────────────────
  useEffect(() => {
    stopSpeaking();
  }, [currentQuestionIdx]);

  // ── Generate + persist next question ─────────────────────────────────────
  const generateAndSaveNextQuestion = async (intData, seqIdx) => {
    try {
      const res = await api.post('/ai/generate-question', {
        job_role: intData.job_role,
        interview_type: intData.interview_type,
        difficulty: intData.difficulty,
        skills: '',
        interview_id: Number(id),
      });
      const text = res.data.question;
      const qDifficulty = res.data.difficulty || intData.difficulty;
      const qTopic = res.data.topic || '';

      setQuestionText(text);
      setCurrentTopic(qTopic);
      setTimeLeft(120);

      // Save question to database
      const qRes = await api.post(`/interviews/${id}/questions`, {
        question_text: text,
        question_type: intData.interview_type,
        difficulty: qDifficulty,
        topic: qTopic,
        sequence_number: seqIdx + 1,
      });
      setCurrentQuestionId(qRes.data.id);
    } catch (err) {
      setQuestionText('Failed to generate question. Please try again.');
    }
  };

  // ── Submit answer ─────────────────────────────────────────────────────────
  const handleSubmitAnswer = async () => {
    if (!answer.trim()) return;
    setIsEvaluating(true);

    // Stop all voice features before submitting
    if (isRecording) stopRecording();
    stopSpeaking();

    try {
      // 1. Evaluate answer via AI (existing endpoint)
      const evalRes = await api.post('/ai/evaluate-answer', {
        question_text: questionText,
        answer_text: answer,
      });

      const evaluation = evalRes.data;

      // 2. Save answer and evaluation to database
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

      // 3. Clear answer field
      setAnswer('');

      // 4. Progress to next question or complete interview
      if (interview && currentQuestionIdx < interview.total_questions - 1) {
        const nextIdx = currentQuestionIdx + 1;
        setCurrentQuestionIdx(nextIdx);
        await generateAndSaveNextQuestion(interview, nextIdx);
      } else {
        const durationSecs = Math.round((Date.now() - startTime) / 1000);
        await api.post(`/interviews/${id}/complete`, { duration: durationSecs });
        navigate(`/interview/${id}/result`);
      }
    } catch (err) {
      console.error('Failed to evaluate/save answer', err);
    } finally {
      setIsEvaluating(false);
    }
  };

  // ── Toggle microphone recording ───────────────────────────────────────────
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // ── Toggle TTS speaking ───────────────────────────────────────────────────
  const handleReadQuestion = () => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      speak(questionText);
    }
  };

  // ── Loading guard ─────────────────────────────────────────────────────────
  if (!interview) {
    return <div className="p-8">Loading interview environment...</div>;
  }

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const isLastQuestion = currentQuestionIdx === interview.total_questions - 1;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 h-full flex flex-col">
      {/* ── Header: role name + question progress + timer ── */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-bold text-slate-900">{interview.job_role} Interview</h2>
            {currentTopic && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                Topic: {currentTopic}
              </span>
            )}
            {currentQuestionIdx > 0 && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
                Tailored Question
              </span>
            )}
          </div>
          <p className="text-sm text-slate-500">
            Question {currentQuestionIdx + 1} of {interview.total_questions}
          </p>
        </div>
        <div
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-bold ${
            timeLeft < 30 ? 'bg-red-50 text-red-600' : 'bg-slate-100 text-slate-700'
          }`}
        >
          <Clock size={20} />
          <span>{formatTime(timeLeft)}</span>
        </div>
      </div>

      {/* ── Main card ── */}
      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200 mb-6 flex-1 flex flex-col">

        {/* ── Question section ── */}
        <div className="flex-1 mb-6">
          {/* TTS control — shown only when TTS is supported */}
          {isTTSSupported && (
            <div className="mb-4 flex items-center space-x-3">
              <button
                id="read-question-btn"
                onClick={handleReadQuestion}
                aria-label={isSpeaking ? 'Stop reading the question aloud' : 'Read the question aloud'}
                title={isSpeaking ? 'Stop Speaking' : 'Read Question Aloud'}
                className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                  isSpeaking
                    ? 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200 focus:ring-indigo-500'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 focus:ring-slate-400'
                }`}
              >
                {isSpeaking ? (
                  <>
                    <VolumeX size={16} aria-hidden="true" />
                    <span>Stop Speaking</span>
                    {/* Animated speaking indicator */}
                    <span className="flex items-end space-x-0.5 h-4" aria-hidden="true">
                      <span className="w-0.5 bg-indigo-500 rounded-full animate-bounce" style={{ height: '8px', animationDelay: '0ms' }} />
                      <span className="w-0.5 bg-indigo-500 rounded-full animate-bounce" style={{ height: '12px', animationDelay: '150ms' }} />
                      <span className="w-0.5 bg-indigo-500 rounded-full animate-bounce" style={{ height: '8px', animationDelay: '300ms' }} />
                    </span>
                  </>
                ) : (
                  <>
                    <Volume2 size={16} aria-hidden="true" />
                    <span>Read Question</span>
                  </>
                )}
              </button>

              {/* Inline TTS error — dismissible */}
              {ttsError && (
                <div
                  role="alert"
                  className="flex items-center space-x-2 text-amber-600 text-sm bg-amber-50 px-3 py-1.5 rounded-lg border border-amber-200"
                >
                  <AlertCircle size={14} aria-hidden="true" />
                  <span>{ttsError}</span>
                </div>
              )}
            </div>
          )}

          {/* Question text — always visible regardless of TTS availability */}
          <h3 className="text-2xl font-semibold text-slate-900 leading-relaxed">
            {questionText}
          </h3>
        </div>

        {/* ── Answer section ── */}
        <div className="space-y-4">
          {/* Textarea with interim transcript overlay */}
          <div className="relative">
            <textarea
              id="answer-textarea"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here, or use the microphone to speak..."
              aria-label="Your answer"
              className="w-full h-48 p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-lg leading-relaxed"
            />
            {/* Interim transcript ghost overlay */}
            {interimTranscript && (
              <div className="absolute bottom-4 left-4 right-4 text-slate-400 italic text-lg leading-relaxed pointer-events-none">
                {interimTranscript}
              </div>
            )}
          </div>

          {/* Speech-to-text error */}
          {speechError && (
            <div
              role="alert"
              className="flex items-center space-x-2 text-red-500 text-sm bg-red-50 p-2 rounded-lg"
            >
              <AlertCircle size={16} aria-hidden="true" />
              <span>{speechError}</span>
            </div>
          )}

          {/* Controls row: microphone | submit */}
          <div className="flex justify-between items-center pt-2">
            {/* Microphone / voice input */}
            {!isSpeechInputSupported ? (
              <div className="text-slate-500 text-sm bg-slate-100 px-4 py-2 rounded-lg border border-slate-200">
                Voice input is not supported in this browser. Please type your answer.
              </div>
            ) : (
              <button
                id="toggle-recording-btn"
                onClick={toggleRecording}
                aria-label={isRecording ? 'Stop voice input' : 'Start voice input'}
                title={isRecording ? 'Stop Recording' : 'Start Voice Input'}
                className={`flex items-center space-x-2 px-6 py-3 rounded-full font-medium transition focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                  isRecording
                    ? 'bg-red-100 text-red-600 hover:bg-red-200 focus:ring-red-400'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 focus:ring-slate-400'
                }`}
              >
                {isRecording ? (
                  <Square size={18} fill="currentColor" aria-hidden="true" />
                ) : (
                  <Mic size={18} aria-hidden="true" />
                )}
                <span>{isRecording ? 'Stop Voice Input' : 'Start Voice Input'}</span>
                {isRecording && (
                  <span
                    className="w-2 h-2 bg-red-500 rounded-full animate-pulse"
                    aria-hidden="true"
                  />
                )}
              </button>
            )}

            {/* Submit / finish */}
            <button
              id="submit-answer-btn"
              onClick={handleSubmitAnswer}
              disabled={isEvaluating || !answer.trim()}
              aria-label={isLastQuestion ? 'Finish interview' : 'Submit answer and continue to next question'}
              className="flex items-center space-x-2 px-8 py-3 bg-blue-600 text-white rounded-full font-bold hover:bg-blue-700 transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <span>{isLastQuestion ? 'Finish Interview' : 'Submit & Next'}</span>
              {isLastQuestion ? (
                <Send size={18} aria-hidden="true" />
              ) : (
                <ChevronRight size={18} aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActiveInterviewPage;
