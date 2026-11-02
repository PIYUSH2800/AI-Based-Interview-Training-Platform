import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
  CheckCircle, AlertTriangle, ArrowRight, MessageSquare, Clock,
  ChevronDown, ChevronUp, Lightbulb, BarChart2, BookOpen,
  TrendingUp, Sparkles, Tag, LayoutDashboard, Trophy,
} from 'lucide-react';
import {
  SectionCard, MetricCard, ScoreProgressRow, EmptyState, LoadingSpinner,
  ProgressBar,
} from '../components/ui';

// ── Reusable stat card for analytics ─────────────────────────────────────────
const StatCard = ({ label, value, sub }) => (
  <div className="card p-4 text-center">
    <p className="text-2xl font-bold text-white">{value}</p>
    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mt-1">{label}</p>
    {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
  </div>
);

// ── Collapsible per-answer accordion ──────────────────────────────────────────
const AnswerAccordion = ({ item, index }) => {
  const [open, setOpen] = useState(false);
  const hasFb = item.ai_feedback && (
    item.ai_feedback.directness || item.ai_feedback.structure ||
    item.ai_feedback.conciseness || item.ai_feedback.suggestion
  );

  return (
    <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900">
      <button
        id={`answer-accordion-${index}`}
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
        className="w-full flex items-center justify-between px-5 py-3.5 bg-slate-900 hover:bg-slate-800/80 transition text-left"
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-700/50 text-xs font-bold flex items-center justify-center">
            {item.sequence_number}
          </span>
          <p className="text-sm font-semibold text-slate-200 truncate">{item.question_text}</p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0 ml-4">
          <span className="text-xs text-slate-400 hidden sm:inline">
            {item.word_count}w · {item.filler_word_count} fillers
          </span>
          {open ? <ChevronUp size={15} className="text-slate-400" /> : <ChevronDown size={15} className="text-slate-400" />}
        </div>
      </button>

      {open && (
        <div className="px-5 pb-5 bg-slate-900 border-t border-slate-800 space-y-4 pt-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <StatCard label="Words"            value={item.word_count} />
            <StatCard label="Sentences"        value={item.sentence_count} />
            <StatCard label="Est. speak time"  value={`${item.estimated_speaking_time_seconds}s`} sub="estimated" />
            <StatCard label="Filler words"     value={item.filler_word_count} sub={item.filler_word_count > 0 ? `${item.filler_word_rate}% of words` : null} />
          </div>

          {item.filler_word_count > 0 && (
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Detected fillers</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(item.detected_fillers).map(([word, count]) => (
                  <span key={word} className="px-2.5 py-1 bg-amber-950/40 border border-amber-800/60 text-amber-300 rounded-full text-xs font-medium">
                    "{word}" ×{count}
                  </span>
                ))}
              </div>
            </div>
          )}

          {hasFb && (
            <div className="bg-indigo-950/40 border border-indigo-800/50 rounded-xl p-4 space-y-3">
              <p className="text-xs font-bold text-indigo-300 uppercase tracking-wide flex items-center gap-1">
                <Lightbulb size={12} /> Communication Insight
              </p>
              {item.ai_feedback.directness && (
                <div>
                  <p className="text-xs font-semibold text-indigo-400">Directness</p>
                  <p className="text-sm text-slate-200">{item.ai_feedback.directness}</p>
                </div>
              )}
              {item.ai_feedback.structure && (
                <div>
                  <p className="text-xs font-semibold text-indigo-400">Structure</p>
                  <p className="text-sm text-slate-200">{item.ai_feedback.structure}</p>
                </div>
              )}
              {item.ai_feedback.conciseness && (
                <div>
                  <p className="text-xs font-semibold text-indigo-400">Conciseness</p>
                  <p className="text-sm text-slate-200">{item.ai_feedback.conciseness}</p>
                </div>
              )}
              {item.ai_feedback.suggestion && (
                <div className="pt-2 border-t border-indigo-800/60">
                  <p className="text-xs font-semibold text-indigo-400">Suggestion</p>
                  <p className="text-sm text-indigo-200 font-medium">{item.ai_feedback.suggestion}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ── Topic bar row ──────────────────────────────────────────────────────────────
const TopicBar = ({ topic, average_score, question_count, coverage_status }) => {
  const color = coverage_status === 'Strong' ? 'emerald' : coverage_status === 'Good' ? 'indigo' : 'amber';
  const badge = {
    Strong: 'badge-success',
    Good: 'badge-info',
    'Needs Practice': 'badge-warning',
  }[coverage_status] || 'badge-neutral';

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 min-w-0">
          <Tag size={12} className="text-slate-400 flex-shrink-0" />
          <span className="text-sm font-medium text-slate-200 truncate">{topic}</span>
          <span className="text-xs text-slate-400 flex-shrink-0">({question_count}Q)</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-sm font-bold text-white">{average_score}%</span>
          <span className={`badge ${badge}`}>{coverage_status}</span>
        </div>
      </div>
      <ProgressBar value={average_score} max={100} color={color} />
    </div>
  );
};

// ── Main Result Page ───────────────────────────────────────────────────────────
const InterviewResultPage = () => {
  const { id } = useParams();
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [intelligence, setIntelligence] = useState(null);
  const [intelligenceLoading, setIntelligenceLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);

  useEffect(() => {
    api.post(`/ai/generate-feedback/${id}`)
      .then(res => setFeedback(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    api.get(`/interviews/${id}/intelligence`)
      .then(res => setIntelligence(res.data))
      .catch(() => {})
      .finally(() => setIntelligenceLoading(false));
  }, [id]);

  useEffect(() => {
    api.get(`/interviews/${id}/communication-analytics`)
      .then(res => setAnalytics(res.data))
      .catch(() => {})
      .finally(() => setAnalyticsLoading(false));
  }, [id]);

  if (loading) return <LoadingSpinner text="Generating your comprehensive feedback report…" />;

  if (!feedback) {
    return (
      <div className="max-w-md mx-auto mt-16 text-center">
        <div className="card p-8">
          <AlertTriangle size={32} className="text-amber-500 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-900">Results Unavailable</h3>
          <p className="text-sm text-slate-500 mt-1">We couldn't load your interview results.</p>
          <Link to="/dashboard" className="btn-primary mt-5 text-sm">
            <LayoutDashboard size={16} /> Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const overallScore = intelligence
    ? Math.round(intelligence.overall_score)
    : (feedback.overall_score !== undefined ? Math.round(feedback.overall_score) : 75);

  const chartData = intelligence
    ? [
        { name: 'Technical',    score: intelligence.category_scores.technical },
        { name: 'Communication', score: intelligence.category_scores.communication },
        { name: 'Relevance',    score: intelligence.category_scores.relevance },
        { name: 'Completeness', score: intelligence.category_scores.completeness },
      ]
    : (feedback.category_breakdown || []);

  const strengths   = intelligence?.strengths             || feedback.strengths        || [];
  const weaknesses  = intelligence?.improvement_areas     || feedback.weaknesses       || [];
  const recs        = intelligence?.practice_recommendations || feedback.recommendations || [];
  const hasAnalytics = analytics?.per_question?.length > 0;

  const formatTime = (secs) => {
    if (!secs) return '0s';
    if (secs < 60) return `${secs}s`;
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return s > 0 ? `${m}m ${s}s` : `${m}m`;
  };

  const scoreColor = overallScore >= 80 ? 'from-emerald-500 to-emerald-600'
    : overallScore >= 60 ? 'from-indigo-500 to-indigo-600'
    : 'from-amber-500 to-amber-600';

  return (
    <div className="page-container space-y-8 animate-fade-in">

      {/* ── Hero ── */}
      <div className="card overflow-hidden">
        <div className={`bg-gradient-to-br ${scoreColor} px-8 py-10 text-white text-center relative`}>
          <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse at 70% 30%, rgba(255,255,255,0.12) 0%, transparent 60%)' }} />
          <div className="relative z-10">
            <p className="text-sm font-semibold uppercase tracking-widest text-white/70 mb-2">Interview Complete 🎉</p>
            <div className="text-8xl font-black leading-none mb-1">{overallScore}<span className="text-4xl font-bold opacity-70">%</span></div>
            <p className="text-white/70 font-medium text-sm">Overall Score</p>
            {intelligence && (
              <p className="text-white/50 text-xs mt-2">
                {intelligence.job_role} · {intelligence.interview_type} · {intelligence.difficulty}
              </p>
            )}
          </div>
        </div>
        {/* Category scores strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 divide-x divide-y sm:divide-y-0 divide-slate-800 bg-slate-900">
          {chartData.map(({ name, score }) => (
            <div key={name} className="p-4 text-center">
              <p className="text-xl font-bold text-white">{score}%</p>
              <p className="text-xs text-slate-400 mt-0.5">{name}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Performance breakdown chart + Strengths/Weaknesses ── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Category chart */}
        <SectionCard title="Performance Overview" className="lg:col-span-3">
          {chartData.length > 0 ? (
            <div className="space-y-3 pt-1">
              {chartData.map(({ name, score }) => (
                <ScoreProgressRow key={name} label={name} score={score} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400">No category breakdown available.</p>
          )}
        </SectionCard>

        {/* Strengths + Weaknesses */}
        <div className="lg:col-span-2 space-y-4">
          {/* Strengths */}
          <SectionCard title="Strengths" className="bg-emerald-950/20 border-emerald-800/40">
            {strengths.length === 0 ? (
              <p className="text-sm text-slate-400">No strengths data available.</p>
            ) : (
              <ul className="space-y-2">
                {strengths.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-emerald-200">
                    <CheckCircle size={14} className="text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}
          </SectionCard>

          {/* Improvement Areas */}
          <SectionCard title="Areas to Improve" className="bg-amber-950/20 border-amber-800/40">
            {weaknesses.length === 0 ? (
              <p className="text-sm text-slate-400">No improvement data available.</p>
            ) : (
              <ul className="space-y-2">
                {weaknesses.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-amber-200">
                    <AlertTriangle size={14} className="text-amber-400 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}
          </SectionCard>
        </div>
      </div>

      {/* ── Topic Performance ── */}
      {!intelligenceLoading && intelligence?.topic_performance?.length > 0 && (
        <SectionCard
          title="Topic Performance"
          action={<p className="text-xs text-slate-400">Strong ≥80 · Good ≥65</p>}
        >
          <div className="space-y-4">
            {intelligence.topic_performance.map(tp => (
              <TopicBar key={tp.topic} {...tp} />
            ))}
          </div>
        </SectionCard>
      )}

      {/* ── AI Interview Summary ── */}
      {!intelligenceLoading && intelligence?.ai_summary && (
        <div className="card p-6 bg-indigo-950/30 border border-indigo-800/50">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-950/80 text-indigo-400 border border-indigo-700/50 flex items-center justify-center">
              <Sparkles size={16} />
            </div>
            <h3 className="section-title text-indigo-200">AI Interview Summary</h3>
          </div>
          <p className="text-slate-200 leading-relaxed text-sm">{intelligence.ai_summary}</p>
        </div>
      )}

      {/* ── Recommended Practice ── */}
      {recs.length > 0 && (
        <SectionCard title="Recommended Practice">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {recs.map((item, i) => (
              <div key={i} className="flex items-start gap-3 p-3.5 bg-slate-800/60 rounded-xl border border-slate-700/60">
                <div className="w-6 h-6 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-700/50 font-bold flex items-center justify-center flex-shrink-0 text-xs">
                  {i + 1}
                </div>
                <span className="text-sm text-slate-200 leading-relaxed">{item}</span>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* ── Communication Analytics ── */}
      <SectionCard
        title="Communication Analytics"
        action={<p className="text-xs text-slate-400">Based on submitted answers · 130 WPM estimate</p>}
      >
        {analyticsLoading ? (
          <div className="flex items-center justify-center py-10 gap-3 text-slate-400">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm">Analysing your answers…</span>
          </div>
        ) : !analytics ? (
          <EmptyState
            icon={MessageSquare}
            title="Analytics Unavailable"
            description="Communication analytics are not available for this interview."
          />
        ) : (
          <>
            {/* Overview stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
              <StatCard label="Total Words"      value={analytics.total_words} />
              <StatCard label="Est. Speak Time"  value={formatTime(analytics.per_question?.reduce((s, q) => s + q.estimated_speaking_time_seconds, 0))} sub="estimated" />
              <StatCard label="Avg Words/Min"    value={analytics.avg_wpm} sub="estimated" />
              <StatCard label="Filler Words"     value={analytics.total_filler_words} sub={analytics.total_filler_words > 0 ? `${analytics.avg_filler_rate}% avg` : 'None detected'} />
            </div>

            {/* Overall suggestion */}
            {analytics.overall_suggestion && (
              <div className="flex items-start gap-3 bg-indigo-950/40 border border-indigo-800/60 rounded-xl p-4 mb-6">
                <Lightbulb size={16} className="text-indigo-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-indigo-200">{analytics.overall_suggestion}</p>
              </div>
            )}

            {/* Per-answer accordion */}
            {hasAnalytics ? (
              <div className="space-y-2">
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Per-Answer Breakdown</p>
                {analytics.per_question.map((item, idx) => (
                  <AnswerAccordion key={item.question_id} item={item} index={idx} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-400 text-center py-4">No answered questions found.</p>
            )}
          </>
        )}
      </SectionCard>

      {/* ── Footer Navigation ── */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-4">
        <Link to="/history" className="btn-secondary text-sm">
          View All History
        </Link>
        <div className="flex items-center gap-3">
          <Link to="/setup" className="btn-secondary text-sm">
            <ArrowRight size={15} />
            New Interview
          </Link>
          <Link to="/dashboard" className="btn-primary text-sm">
            <LayoutDashboard size={15} />
            Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default InterviewResultPage;
