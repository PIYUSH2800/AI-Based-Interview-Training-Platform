import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Mic, Square, Send, ChevronRight, Clock } from 'lucide-react';

const ActiveInterviewPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [interview, setInterview] = useState(null);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [currentQuestionId, setCurrentQuestionId] = useState(null);
  const [questionText, setQuestionText] = useState('Loading your first question...');
  const [answer, setAnswer] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [timeLeft, setTimeLeft] = useState(120); // 2 mins per question
  const [startTime] = useState(Date.now());

  useEffect(() => {
    const fetchInterview = async () => {
      try {
        const res = await api.get(`/interviews/${id}`);
        setInterview(res.data);
        await generateAndSaveNextQuestion(res.data, 0);
      } catch (err) {
        console.error("Failed to fetch interview", err);
        navigate('/dashboard');
      }
    };
    fetchInterview();
  }, [id, navigate]);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => prev > 0 ? prev - 1 : 0);
    }, 1000);
    return () => clearInterval(timer);
  }, [currentQuestionIdx]);

  const generateAndSaveNextQuestion = async (intData, seqIdx) => {
    try {
      const res = await api.post('/ai/generate-question', {
        job_role: intData.job_role,
        interview_type: intData.interview_type,
        difficulty: intData.difficulty,
        skills: ''
      });
      const text = res.data.question;
      setQuestionText(text);
      setTimeLeft(120);

      // Save question to database
      const qRes = await api.post(`/interviews/${id}/questions`, {
        question_text: text,
        question_type: intData.interview_type,
        difficulty: intData.difficulty,
        sequence_number: seqIdx + 1
      });
      setCurrentQuestionId(qRes.data.id);
    } catch (err) {
      setQuestionText("Failed to generate question. Please try again.");
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) return;
    setIsEvaluating(true);
    
    try {
      // 1. Evaluate answer via AI
      const evalRes = await api.post('/ai/evaluate-answer', {
        question_text: questionText,
        answer_text: answer
      });

      const evaluation = evalRes.data;

      // 2. Save answer and evaluation to database if question was created
      if (currentQuestionId) {
        await api.post(`/interviews/${id}/questions/${currentQuestionId}/answers`, {
          answer_text: answer,
          score: evaluation.score,
          technical_score: evaluation.technical_score,
          communication_score: evaluation.communication_score,
          relevance_score: evaluation.relevance_score,
          completeness_score: evaluation.completeness_score,
          feedback: evaluation.feedback
        });
      }
      
      // Clear answer text
      setAnswer('');

      if (interview && currentQuestionIdx < interview.total_questions - 1) {
        const nextIdx = currentQuestionIdx + 1;
        setCurrentQuestionIdx(nextIdx);
        await generateAndSaveNextQuestion(interview, nextIdx);
      } else {
        // Complete interview session and calculate overall score
        const durationSecs = Math.round((Date.now() - startTime) / 1000);
        await api.post(`/interviews/${id}/complete`, { duration: durationSecs });
        navigate(`/interview/${id}/result`);
      }
    } catch (err) {
      console.error("Failed to evaluate/save answer", err);
    } finally {
      setIsEvaluating(false);
    }
  };


  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // In a real app, integrate SpeechRecognition API here
  };

  if (!interview) return <div className="p-8">Loading interview environment...</div>;

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 h-full flex flex-col">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-xl font-bold text-slate-900">{interview.job_role} Interview</h2>
          <p className="text-sm text-slate-500">Question {currentQuestionIdx + 1} of {interview.total_questions}</p>
        </div>
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-bold ${timeLeft < 30 ? 'bg-red-50 text-red-600' : 'bg-slate-100 text-slate-700'}`}>
          <Clock size={20} />
          <span>{formatTime(timeLeft)}</span>
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200 mb-6 flex-1 flex flex-col">
        <h3 className="text-2xl font-semibold text-slate-900 leading-relaxed mb-8 flex-1">
          {questionText}
        </h3>

        {/* Answer Input */}
        <div className="space-y-4">
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here, or use the microphone to speak..."
            className="w-full h-48 p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-lg leading-relaxed"
          ></textarea>
          
          <div className="flex justify-between items-center pt-2">
            <button 
              onClick={toggleRecording}
              className={`flex items-center space-x-2 px-6 py-3 rounded-full font-medium transition ${isRecording ? 'bg-red-100 text-red-600 hover:bg-red-200' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
            >
              {isRecording ? <Square size={18} fill="currentColor" /> : <Mic size={18} />}
              <span>{isRecording ? 'Stop Recording' : 'Voice Input'}</span>
            </button>

            <button 
              onClick={handleSubmitAnswer}
              disabled={isEvaluating || !answer.trim()}
              className="flex items-center space-x-2 px-8 py-3 bg-blue-600 text-white rounded-full font-bold hover:bg-blue-700 transition disabled:opacity-50"
            >
              <span>{currentQuestionIdx === interview.total_questions - 1 ? 'Finish Interview' : 'Submit & Next'}</span>
              {currentQuestionIdx === interview.total_questions - 1 ? <Send size={18} /> : <ChevronRight size={18} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActiveInterviewPage;
