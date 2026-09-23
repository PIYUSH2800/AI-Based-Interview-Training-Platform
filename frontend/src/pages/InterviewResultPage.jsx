import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  MessageSquare,
  Clock,
  AlignLeft,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  BarChart2,
} from 'lucide-react';

// ── Small reusable stat card ──────────────────────────────────────────────────
const StatCard = ({ label, value, sub }) => (
  <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-center">
    <p className="text-2xl font-bold text-slate-900">{value}</p>
    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mt-1">{label}</p>
    {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
  </div>
);

// ── Collapsible per-answer row ────────────────────────────────────────────────
const AnswerAccordion = ({ item, index }) => {
  const [open, setOpen] = useState(false);

  const hasFb = item.ai_feedback && (
    item.ai_feedback.directness ||
    item.ai_feedback.structure ||
    item.ai_feedback.conciseness ||
    item.ai_feedback.suggestion
  );

  return (
    <div className="border border-slate-200 rounded-2xl overflow-hidden">
      {/* Header row — always visible */}
      <button
        id={`answer-accordion-${index}`}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="w-full flex items-center justify-between px-5 py-4 bg-white hover:bg-slate-50 transition text-left"
      >
        <div className="flex items-center space-x-3 min-w-0">
          <span className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-100 text-blue-600 text-xs font-bold flex items-center justify-center">
            {item.sequence_number}
          </span>
          <p className="text-sm font-semibold text-slate-700 truncate">{item.question_text}</p>
        </div>
        <div className="flex items-center space-x-4 flex-shrink-0 ml-4">
          <span className="text-xs text-slate-500 hidden sm:inline">
            {item.word_count} words · {item.filler_word_count} fillers
          </span>
          {open ? (
            <ChevronUp size={16} className="text-slate-400" />
          ) : (
            <ChevronDown size={16} className="text-slate-400" />
          )}
        </div>
      </button>

      {/* Expanded body */}
      {open && (
        <div className="px-5 pb-5 bg-white border-t border-slate-100 space-y-5">
          {/* Mini stat row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4">
            <StatCard label="Words" value={item.word_count} />
            <StatCard label="Sentences" value={item.sentence_count} />
            <StatCard
              label="Est. speaking time"
              value={`${item.estimated_speaking_time_seconds}s`}
              sub="estimated"
            />
            <StatCard
              label="Filler words"
              value={item.filler_word_count}
              sub={item.filler_word_count > 0 ? `${item.filler_word_rate}% of words` : null}
            />
          </div>

          {/* Detected fillers badge list */}
          {item.filler_word_count > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                Detected fillers
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(item.detected_fillers).map(([word, count]) => (
                  <span
                    key={word}
                    className="px-2.5 py-1 bg-amber-50 border border-amber-200 text-amber-700 rounded-full text-xs font-medium"
                  >
                    "{word}" ×{count}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* AI qualitative feedback */}
          {hasFb && (
            <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 space-y-3">
              <p className="text-xs font-bold text-indigo-700 uppercase tracking-wide flex items-center space-x-1">
                <Lightbulb size={13} aria-hidden="true" />
                <span>Communication Insight</span>
              </p>
              {item.ai_feedback.directness && (
                <div>
                  <p className="text-xs font-semibold text-indigo-600 mb-0.5">Directness</p>
                  <p className="text-sm text-slate-700">{item.ai_feedback.directness}</p>
                </div>
              )}
              {item.ai_feedback.structure && (
                <div>
                  <p className="text-xs font-semibold text-indigo-600 mb-0.5">Structure</p>
                  <p className="text-sm text-slate-700">{item.ai_feedback.structure}</p>
                </div>
              )}
              {item.ai_feedback.conciseness && (
                <div>
                  <p className="text-xs font-semibold text-indigo-600 mb-0.5">Conciseness</p>
                  <p className="text-sm text-slate-700">{item.ai_feedback.conciseness}</p>
                </div>
              )}
              {item.ai_feedback.suggestion && (
                <div className="pt-2 border-t border-indigo-100">
                  <p className="text-xs font-semibold text-indigo-600 mb-0.5">Suggestion</p>
                  <p className="text-sm text-slate-700 font-medium">{item.ai_feedback.suggestion}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ── Main page ─────────────────────────────────────────────────────────────────
const InterviewResultPage = () => {
  const { id } = useParams();

  // Existing interview feedback state
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);

  // New communication analytics state
  const [analytics, setAnalytics] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);

  // Fetch existing AI feedback (unchanged)
  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        const res = await api.post(`/ai/generate-feedback/${id}`);
        setFeedback(res.data);
      } catch (err) {
        console.error('Failed to fetch feedback');
      } finally {
        setLoading(false);
      }
    };
    fetchFeedback();
  }, [id]);

  // Fetch communication analytics (new — runs independently)
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.get(`/interviews/${id}/communication-analytics`);
        setAnalytics(res.data);
      } catch (err) {
        console.error('Failed to fetch communication analytics', err);
      } finally {
        setAnalyticsLoading(false);
      }
    };
    fetchAnalytics();
  }, [id]);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-500">
        Generating comprehensive feedback...
      </div>
    );
  }
  if (!feedback) {
    return (
      <div className="p-8 text-center text-red-500">Failed to load results.</div>
    );
  }

  const chartData = feedback.category_breakdown || [
    { name: 'Technical', score: 75 },
    { name: 'Comm.', score: 75 },
    { name: 'Relevance', score: 75 },
    { name: 'Completeness', score: 75 },
  ];

  const overallScoreDisplay =
    feedback.overall_score !== undefined ? Math.round(feedback.overall_score) : 75;

  const hasAnalytics = analytics && analytics.per_question && analytics.per_question.length > 0;

  // Format speaking time to "Xm Ys" if >= 60 seconds
  const formatTime = (secs) => {
    if (!secs) return '0s';
    if (secs < 60) return `${secs}s`;
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return s > 0 ? `${m}m ${s}s` : `${m}m`;
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* ── Header ── */}
      <div className="text-center pb-8 border-b border-slate-200">
        <h2 className="text-4xl font-extrabold text-slate-900 mb-2">Interview Completed!</h2>
        <p className="text-lg text-slate-500">Here is your AI-generated performance evaluation.</p>
        <div className="mt-8 inline-block p-6 rounded-3xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-xl shadow-blue-500/30">
          <p className="text-sm font-medium opacity-80 uppercase tracking-wider mb-1">
            Overall Score
          </p>
          <p className="text-6xl font-black">
            {overallScoreDisplay}
            <span className="text-3xl opacity-70">%</span>
          </p>
        </div>
      </div>

      {/* ── Existing: Category breakdown + Strengths/Weaknesses ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Chart */}
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200">
          <h3 className="text-xl font-bold text-slate-900 mb-6">Category Breakdown</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 0, right: 30, left: 20, bottom: 0 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  horizontal={true}
                  vertical={false}
                  stroke="#e2e8f0"
                />
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis
                  dataKey="name"
                  type="category"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#475569', fontWeight: 500 }}
                  width={90}
                />
                <Tooltip
                  cursor={{ fill: 'transparent' }}
                  contentStyle={{
                    borderRadius: '8px',
                    border: 'none',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  }}
                />
                <Bar dataKey="score" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Strengths / Weaknesses */}
        <div className="space-y-6">
          <div className="bg-emerald-50 p-6 rounded-2xl border border-emerald-100">
            <h3 className="text-lg font-bold text-emerald-800 mb-4 flex items-center space-x-2">
              <CheckCircle size={20} />
              <span>Strengths</span>
            </h3>
            <ul className="space-y-3">
              {feedback.strengths?.map((item, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-emerald-700">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-amber-50 p-6 rounded-2xl border border-amber-100">
            <h3 className="text-lg font-bold text-amber-800 mb-4 flex items-center space-x-2">
              <AlertTriangle size={20} />
              <span>Areas for Improvement</span>
            </h3>
            <ul className="space-y-3">
              {feedback.weaknesses?.map((item, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-amber-700">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-amber-500 flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* ── Existing: Action Plan ── */}
      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200">
        <h3 className="text-xl font-bold text-slate-900 mb-6">Recommended Action Plan</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {feedback.recommendations?.map((item, idx) => (
            <div
              key={idx}
              className="flex items-center space-x-3 p-4 bg-slate-50 rounded-xl border border-slate-100"
            >
              <div className="bg-blue-100 text-blue-600 font-bold w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                {idx + 1}
              </div>
              <span className="text-slate-700 font-medium">{item}</span>
            </div>
          ))}
        </div>

        <div className="mt-8 pt-6 border-t border-slate-100 flex justify-end">
          <Link
            to="/dashboard"
            className="flex items-center space-x-2 px-6 py-3 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition font-medium"
          >
            <span>Return to Dashboard</span>
            <ArrowRight size={18} />
          </Link>
        </div>
      </div>

      {/* ════════════════════════════════════════════════════════════════════
          NEW: Communication Analytics section
          ═══════════════════════════════════════════════════════════════════ */}
      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-9 h-9 rounded-xl bg-indigo-100 flex items-center justify-center">
            <MessageSquare size={18} className="text-indigo-600" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-900">Communication Analytics</h3>
            <p className="text-sm text-slate-500">
              Based on your submitted answer text — speaking time is estimated at 130 wpm.
            </p>
          </div>
        </div>

        {analyticsLoading ? (
          <div className="text-center py-8 text-slate-400 text-sm">
            Analysing your answers...
          </div>
        ) : !analytics ? (
          <div className="text-center py-8 text-slate-400 text-sm">
            Communication analytics are not available for this interview.
          </div>
        ) : (
          <>
            {/* ── Overview stat cards ── */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
              <StatCard
                label="Total words"
                value={analytics.total_words}
              />
              <StatCard
                label="Est. speaking time"
                value={formatTime(
                  analytics.per_question.reduce(
                    (s, q) => s + q.estimated_speaking_time_seconds,
                    0
                  )
                )}
                sub="estimated"
              />
              <StatCard
                label="Avg. words/min"
                value={analytics.avg_wpm}
                sub="estimated"
              />
              <StatCard
                label="Total filler words"
                value={analytics.total_filler_words}
                sub={
                  analytics.total_filler_words > 0
                    ? `${analytics.avg_filler_rate}% avg rate`
                    : 'None detected'
                }
              />
            </div>

            {/* ── Overall suggestion ── */}
            {analytics.overall_suggestion && (
              <div className="flex items-start space-x-3 bg-indigo-50 border border-indigo-100 rounded-2xl p-4 mb-8">
                <Lightbulb size={18} className="text-indigo-500 flex-shrink-0 mt-0.5" aria-hidden="true" />
                <p className="text-sm text-indigo-800">{analytics.overall_suggestion}</p>
              </div>
            )}

            {/* ── Per-answer accordion ── */}
            {hasAnalytics ? (
              <div>
                <div className="flex items-center space-x-2 mb-4">
                  <BarChart2 size={15} className="text-slate-400" aria-hidden="true" />
                  <p className="text-sm font-semibold text-slate-600">
                    Per-Answer Breakdown
                  </p>
                  <span className="text-xs text-slate-400">(click to expand)</span>
                </div>
                <div className="space-y-3">
                  {analytics.per_question.map((item, idx) => (
                    <AnswerAccordion key={item.question_id} item={item} index={idx} />
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-400 text-center py-4">
                No answered questions found for this interview.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default InterviewResultPage;
