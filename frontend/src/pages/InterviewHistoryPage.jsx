import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import {
  Calendar, Clock, Trophy, Eye, FileText, Search, X,
  CheckCircle, ArrowRight, PlayCircle, Filter,
} from 'lucide-react';
import {
  PageHeader, SectionCard, EmptyState, StatusBadge,
  DifficultyBadge, LoadingSpinner,
} from '../components/ui';

const InterviewHistoryPage = () => {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedInterviewDetails, setSelectedInterviewDetails] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);

  useEffect(() => { fetchInterviews(); }, []);

  const fetchInterviews = async () => {
    try {
      const res = await api.get('/interviews');
      setInterviews(res.data);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  const inspectInterviewDetails = async (interviewId) => {
    setModalLoading(true);
    try {
      const res = await api.get(`/interviews/${interviewId}/details`);
      setSelectedInterviewDetails(res.data);
    } catch {
      // silent
    } finally {
      setModalLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '—';
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s}s`;
  };

  const filteredInterviews = interviews.filter(i => {
    const matchesSearch = i.job_role.toLowerCase().includes(searchQuery.toLowerCase())
      || i.interview_type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDiff = selectedDifficulty === 'All' || i.difficulty === selectedDifficulty;
    return matchesSearch && matchesDiff;
  });

  if (loading) return <LoadingSpinner text="Loading interview history…" />;

  return (
    <div className="page-container space-y-6">
      <PageHeader
        title="Interview History"
        subtitle="Review past mock interview sessions, answers, and performance reports."
        action={
          <Link to="/setup" className="btn-primary text-sm">
            <PlayCircle size={16} />
            New Session
          </Link>
        }
      />

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
          {/* Search */}
          <div className="relative flex-1 min-w-0">
            <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" aria-hidden="true" />
            <input
              type="search"
              placeholder="Search by role or type…"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-400 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
              aria-label="Search interviews"
            />
          </div>

          {/* Difficulty filter */}
          <div className="flex items-center gap-2">
            <Filter size={14} className="text-slate-400" aria-hidden="true" />
            <select
              value={selectedDifficulty}
              onChange={e => setSelectedDifficulty(e.target.value)}
              className="px-3 py-2.5 bg-slate-900 border border-slate-700 text-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 transition cursor-pointer"
              aria-label="Filter by difficulty"
            >
              <option value="All">All Difficulties</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>

          {/* Count */}
          <span className="text-xs font-semibold text-slate-400 flex-shrink-0">
            {filteredInterviews.length} of {interviews.length}
          </span>
        </div>
      </div>

      {/* Table / List */}
      <SectionCard noPad>
        {filteredInterviews.length === 0 ? (
          <EmptyState
            icon={FileText}
            title={interviews.length === 0 ? 'No interview sessions yet' : 'No sessions match your filters'}
            description={interviews.length === 0
              ? 'Your completed practice sessions will appear here.'
              : 'Try clearing the search or changing the difficulty filter.'}
            action={
              interviews.length === 0 && (
                <Link to="/setup" className="btn-primary text-sm">
                  <PlayCircle size={16} />
                  Start First Interview
                </Link>
              )
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="bg-slate-900/90 border-b border-slate-800 text-xs font-bold uppercase tracking-wider text-slate-300">
                  <th className="px-6 py-3.5">Role & Type</th>
                  <th className="px-4 py-3.5">Difficulty</th>
                  <th className="px-4 py-3.5 hidden sm:table-cell">Date</th>
                  <th className="px-4 py-3.5 hidden md:table-cell">Duration</th>
                  <th className="px-4 py-3.5">Score</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {filteredInterviews.map((int) => (
                  <tr key={int.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4">
                      <p className="font-semibold text-white">{int.job_role}</p>
                      <p className="text-xs text-slate-400 mt-0.5">{int.interview_type} · {int.total_questions}Q</p>
                    </td>
                    <td className="px-4 py-4">
                      <DifficultyBadge difficulty={int.difficulty} />
                    </td>
                    <td className="px-4 py-4 hidden sm:table-cell">
                      <div className="flex items-center gap-1.5 text-xs text-slate-300">
                        <Calendar size={13} className="text-slate-400" aria-hidden="true" />
                        {int.created_at
                          ? new Date(int.created_at).toLocaleDateString(undefined, { dateStyle: 'medium' })
                          : '—'}
                      </div>
                    </td>
                    <td className="px-4 py-4 hidden md:table-cell">
                      <div className="flex items-center gap-1.5 text-xs text-slate-300">
                        <Clock size={13} className="text-slate-400" aria-hidden="true" />
                        {formatDuration(int.duration)}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <StatusBadge score={int.overall_score} />
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => inspectInterviewDetails(int.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition"
                          title="Inspect Q&A"
                          aria-label={`Inspect Q&A for ${int.job_role}`}
                        >
                          <Eye size={13} />
                          Q&amp;A
                        </button>
                        <Link
                          to={`/interview/${int.id}/result`}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-950/60 hover:bg-indigo-900/80 text-indigo-300 border border-indigo-700/50 rounded-lg text-xs font-semibold transition"
                          aria-label={`View report for ${int.job_role}`}
                        >
                          Report
                          <ArrowRight size={13} />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* Q&A Modal */}
      {(selectedInterviewDetails || modalLoading) && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          role="dialog"
          aria-modal="true"
          aria-label="Interview Q&A Details"
        >
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            onClick={() => setSelectedInterviewDetails(null)}
          />

          <div className="relative bg-slate-900 border border-slate-800 max-w-3xl w-full rounded-3xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col my-4 text-slate-100">
            {/* Header */}
            <div className="px-6 py-5 bg-slate-950 border-b border-slate-800 text-white flex items-start justify-between gap-4 flex-shrink-0">
              <div>
                <h2 className="text-lg font-bold">
                  {selectedInterviewDetails?.job_role} — Q&amp;A Review
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  {selectedInterviewDetails?.interview_type} · {selectedInterviewDetails?.difficulty} ·{' '}
                  Score: {selectedInterviewDetails?.overall_score || 0}%
                </p>
              </div>
              <button
                onClick={() => setSelectedInterviewDetails(null)}
                className="p-2 hover:bg-slate-800 rounded-xl transition flex-shrink-0 text-slate-400 hover:text-white"
                aria-label="Close modal"
              >
                <X size={18} />
              </button>
            </div>

            {/* Body */}
            <div className="overflow-y-auto flex-1 p-6 space-y-5">
              {modalLoading ? (
                <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-400">
                  <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm">Loading session details…</span>
                </div>
              ) : selectedInterviewDetails?.questions?.length === 0 ? (
                <p className="text-center text-slate-400 py-10">No questions recorded for this session.</p>
              ) : (
                selectedInterviewDetails?.questions?.map((q, idx) => (
                  <div key={q.id} className="rounded-2xl border border-slate-800 bg-slate-950/60 overflow-hidden">
                    {/* Question header */}
                    <div className="flex items-start gap-3 p-5 bg-slate-900/90 border-b border-slate-800">
                      <div className="w-7 h-7 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-700/50 font-bold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
                        {idx + 1}
                      </div>
                      <p className="font-semibold text-white text-sm leading-snug">{q.question_text}</p>
                    </div>

                    <div className="p-5 space-y-4">
                      {/* Answer */}
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Candidate Answer</p>
                        <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">
                          {q.answer?.answer_text || <span className="italic text-slate-500">No answer submitted.</span>}
                        </div>
                      </div>

                      {/* Scores */}
                      {q.answer && (
                        <div>
                          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">AI Evaluation</p>
                          <div className="flex flex-wrap gap-2">
                            {[
                              { label: 'Overall', value: q.answer.score, primary: true },
                              { label: 'Technical', value: q.answer.technical_score },
                              { label: 'Communication', value: q.answer.communication_score },
                              { label: 'Relevance', value: q.answer.relevance_score },
                            ].map(({ label, value, primary }) => (
                              <span
                                key={label}
                                className={`inline-flex items-center gap-1 px-3 py-1 rounded-lg text-xs font-bold border ${
                                  primary
                                    ? 'bg-indigo-950/70 text-indigo-300 border-indigo-700/50'
                                    : 'bg-slate-800 text-slate-200 border-slate-700'
                                }`}
                              >
                                {label}: {value}%
                              </span>
                            ))}
                          </div>
                          {q.answer.feedback && (
                            <p className="mt-3 text-xs text-amber-200 bg-amber-950/40 border border-amber-800/60 p-3 rounded-xl leading-relaxed">
                              <span className="font-bold text-amber-300">Feedback: </span>
                              {q.answer.feedback}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex justify-between items-center flex-shrink-0">
              <p className="text-xs text-slate-400">
                {selectedInterviewDetails?.questions?.length || 0} questions in this session
              </p>
              <button
                onClick={() => setSelectedInterviewDetails(null)}
                className="btn-secondary text-sm"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewHistoryPage;
