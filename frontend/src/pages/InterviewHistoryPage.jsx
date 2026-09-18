import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Calendar, Clock, Trophy, Eye, FileText, Search, X, CheckCircle, HelpCircle, ArrowRight } from 'lucide-react';

const InterviewHistoryPage = () => {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  
  // State for detailed Q&A inspection modal
  const [selectedInterviewDetails, setSelectedInterviewDetails] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);

  useEffect(() => {
    fetchInterviews();
  }, []);

  const fetchInterviews = async () => {
    try {
      const res = await api.get('/interviews');
      setInterviews(res.data);
    } catch (err) {
      console.error("Failed to load interview history", err);
    } finally {
      setLoading(false);
    }
  };

  const inspectInterviewDetails = async (id) => {
    setModalLoading(true);
    try {
      const res = await api.get(`/interviews/${id}/details`);
      setSelectedInterviewDetails(res.data);
    } catch (err) {
      console.error("Failed to fetch interview details", err);
    } finally {
      setModalLoading(false);
    }
  };

  const closeModal = () => {
    setSelectedInterviewDetails(null);
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s}s`;
  };

  // Filtered interviews
  const filteredInterviews = interviews.filter(int => {
    const matchesSearch = int.job_role.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          int.interview_type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDifficulty = selectedDifficulty === 'All' || int.difficulty === selectedDifficulty;
    return matchesSearch && matchesDifficulty;
  });

  if (loading) return <div className="p-8 text-center text-slate-500 font-medium">Loading interview history...</div>;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">Interview History</h2>
          <p className="text-slate-500 mt-1">Review past mock interview sessions, answers, and AI performance reports.</p>
        </div>
        <Link 
          to="/setup" 
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-500/30 transition self-start md:self-auto"
        >
          New Practice Session
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 flex flex-col md:flex-row gap-4 justify-between items-center">
        <div className="relative w-full md:w-80">
          <Search size={18} className="absolute left-3.5 top-3 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search by role or type..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <span className="text-sm font-semibold text-slate-600 flex-shrink-0">Difficulty:</span>
          <select 
            value={selectedDifficulty} 
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          >
            <option value="All">All Difficulties</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        {filteredInterviews.length === 0 ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <FileText size={40} className="mx-auto text-slate-300" />
            <p className="font-semibold text-slate-600">No interview sessions found.</p>
            <p className="text-sm">Try clearing search filters or start a new mock interview session.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-xs tracking-wider">
                  <th className="p-4 pl-6">Job Role & Type</th>
                  <th className="p-4">Difficulty</th>
                  <th className="p-4">Date & Time</th>
                  <th className="p-4">Duration</th>
                  <th className="p-4">Overall Score</th>
                  <th className="p-4 pr-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredInterviews.map((int) => (
                  <tr key={int.id} className="hover:bg-slate-50/80 transition">
                    <td className="p-4 pl-6">
                      <p className="font-bold text-slate-900">{int.job_role}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{int.interview_type} • {int.total_questions} Questions</p>
                    </td>
                    <td className="p-4">
                      <span className={`inline-block px-2.5 py-1 rounded-md text-xs font-semibold ${
                        int.difficulty === 'Beginner' ? 'bg-emerald-50 text-emerald-700' :
                        int.difficulty === 'Intermediate' ? 'bg-blue-50 text-blue-700' : 'bg-purple-50 text-purple-700'
                      }`}>
                        {int.difficulty}
                      </span>
                    </td>
                    <td className="p-4 text-slate-600">
                      <div className="flex items-center space-x-1.5 text-xs">
                        <Calendar size={14} className="text-slate-400" />
                        <span>{int.created_at ? new Date(int.created_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : 'N/A'}</span>
                      </div>
                    </td>
                    <td className="p-4 text-slate-600">
                      <div className="flex items-center space-x-1 text-xs">
                        <Clock size={14} className="text-slate-400" />
                        <span>{formatDuration(int.duration)}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      {int.overall_score !== null && int.overall_score !== undefined ? (
                        <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full font-bold text-xs ${
                          int.overall_score >= 80 ? 'bg-emerald-100 text-emerald-800' :
                          int.overall_score >= 60 ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'
                        }`}>
                          <Trophy size={12} />
                          <span>{Math.round(int.overall_score)}%</span>
                        </span>
                      ) : (
                        <span className="text-xs font-semibold text-slate-400 bg-slate-100 px-2.5 py-1 rounded-full">
                          In Progress
                        </span>
                      )}
                    </td>
                    <td className="p-4 pr-6 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => inspectInterviewDetails(int.id)}
                          className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-1 transition"
                          title="Inspect Q&A Details"
                        >
                          <Eye size={14} />
                          <span>Q&A</span>
                        </button>
                        <Link
                          to={`/interview/${int.id}/result`}
                          className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-xs font-semibold flex items-center space-x-1 transition"
                        >
                          <span>Report</span>
                          <ArrowRight size={14} />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Inspect Q&A Modal */}
      {selectedInterviewDetails && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white max-w-3xl w-full rounded-3xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col my-8">
            {/* Modal Header */}
            <div className="p-6 bg-slate-900 text-white flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold">{selectedInterviewDetails.job_role} Session Q&A</h3>
                <p className="text-xs text-slate-400 mt-1">
                  {selectedInterviewDetails.interview_type} • {selectedInterviewDetails.difficulty} • Score: {selectedInterviewDetails.overall_score || 0}%
                </p>
              </div>
              <button onClick={closeModal} className="p-2 hover:bg-slate-800 rounded-full transition">
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              {selectedInterviewDetails.questions?.length === 0 ? (
                <div className="py-8 text-center text-slate-400">No questions recorded for this session.</div>
              ) : (
                selectedInterviewDetails.questions?.map((q, idx) => (
                  <div key={q.id} className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
                    <div className="flex items-start space-x-3">
                      <div className="w-7 h-7 rounded-full bg-blue-100 text-blue-600 font-bold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
                        Q{idx + 1}
                      </div>
                      <h4 className="font-bold text-slate-900 text-base leading-snug">
                        {q.question_text}
                      </h4>
                    </div>

                    {/* Candidate Answer */}
                    <div className="pl-10 space-y-2">
                      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Candidate Answer:</p>
                      <div className="p-4 bg-white rounded-xl border border-slate-200 text-sm text-slate-800 whitespace-pre-wrap leading-relaxed">
                        {q.answer?.answer_text || <span className="italic text-slate-400">No answer submitted.</span>}
                      </div>
                    </div>

                    {/* AI Evaluation */}
                    {q.answer && (
                      <div className="pl-10 space-y-2">
                        <div className="flex flex-wrap items-center gap-3 pt-1">
                          <span className="text-xs font-bold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md">
                            Overall: {q.answer.score}%
                          </span>
                          <span className="text-xs text-slate-600">Technical: {q.answer.technical_score}%</span>
                          <span className="text-xs text-slate-600">Communication: {q.answer.communication_score}%</span>
                          <span className="text-xs text-slate-600">Relevance: {q.answer.relevance_score}%</span>
                        </div>
                        {q.answer.feedback && (
                          <p className="text-xs text-slate-600 bg-amber-50 border border-amber-200/60 p-3 rounded-lg">
                            <span className="font-semibold text-amber-900">Feedback: </span>
                            {q.answer.feedback}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button onClick={closeModal} className="px-6 py-2.5 bg-slate-900 text-white rounded-xl font-medium text-sm hover:bg-slate-800 transition">
                Close Inspection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewHistoryPage;
