import React, { useEffect, useState, useContext } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import {
  BrainCircuit, Target, Trophy, Clock, PlayCircle,
  ArrowRight, FileText, Code2, ChevronRight, Mic,
} from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import {
  MetricCard, SectionCard, PageHeader, EmptyState, StatusBadge,
  DifficultyBadge, LoadingSpinner,
} from '../components/ui';

const DashboardPage = () => {
  const { user } = useContext(AuthContext);
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/interviews')
      .then(res => setInterviews(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner text="Loading your dashboard…" />;

  const completedInterviews = interviews.filter(i => i.overall_score !== null && i.overall_score !== undefined);
  const avgScore = completedInterviews.length > 0
    ? Math.round(completedInterviews.reduce((a, c) => a + c.overall_score, 0) / completedInterviews.length)
    : null;

  const totalSeconds = interviews.reduce((a, c) => a + (c.duration || 0), 0);
  const formatTime = (s) => {
    if (!s) return '0m';
    if (s < 60) return `${s}s`;
    if (s < 3600) return `${Math.round(s / 60)}m`;
    return `${(s / 3600).toFixed(1)}h`;
  };

  const strongestArea = (() => {
    if (!completedInterviews.length) return null;
    const roleScores = {};
    completedInterviews.forEach(i => {
      if (!roleScores[i.job_role]) roleScores[i.job_role] = [];
      roleScores[i.job_role].push(i.overall_score);
    });
    let bestRole = null, bestAvg = -1;
    Object.entries(roleScores).forEach(([role, scores]) => {
      const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
      if (avg > bestAvg) { bestAvg = avg; bestRole = role; }
    });
    return bestRole;
  })();

  const chartData = interviews.length > 0
    ? [...interviews].reverse().map((int, i) => ({
        name: int.created_at
          ? new Date(int.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
          : `S${i + 1}`,
        score: Math.round(int.overall_score || 0),
        role: int.job_role,
      }))
    : [65, 72, 78, 85].map((score, i) => ({ name: `Demo ${i + 1}`, score, role: 'Practice' }));

  const recentInterviews = interviews.slice(0, 4);
  const greeting = (() => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  })();
  const firstName = user?.name?.split(' ')[0] || 'there';

  const quickActions = [
    { label: 'Start Interview',   sub: 'AI mock session',        to: '/setup',   icon: PlayCircle, color: 'bg-indigo-600 hover:bg-indigo-700 text-white', shadow: 'shadow-indigo-500/20' },
    { label: 'Coding Practice',   sub: 'Python · Java · C++',    to: '/coding',  icon: Code2,      color: 'bg-slate-800 hover:bg-slate-700 text-white',   shadow: '' },
    { label: 'Voice Interview',   sub: 'Speech-to-text mode',    to: '/setup',   icon: Mic,        color: 'bg-slate-800 hover:bg-slate-700 text-white',   shadow: '' },
    { label: 'View History',      sub: 'All past sessions',       to: '/history', icon: FileText,   color: 'bg-slate-800 hover:bg-slate-700 text-white',   shadow: '' },
  ];

  return (
    <div className="page-container space-y-8">

      {/* ── Hero Welcome ── */}
      <div className="rounded-2xl bg-indigo-600 px-6 py-7 text-white relative overflow-hidden">
        <div
          className="absolute inset-0 pointer-events-none"
          aria-hidden="true"
          style={{ background: 'radial-gradient(ellipse at 80% 50%, rgba(255,255,255,0.08) 0%, transparent 60%)' }}
        />
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <p className="text-indigo-200 text-sm font-medium mb-1">{greeting} 👋</p>
            <h1 className="text-2xl font-bold text-white">{firstName}</h1>
            <p className="text-indigo-200 text-sm mt-1">
              {interviews.length === 0
                ? 'Start your first practice session to track your progress.'
                : `You've completed ${interviews.length} practice session${interviews.length !== 1 ? 's' : ''}. Keep going!`}
            </p>
          </div>
          <Link
            to="/setup"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-indigo-700 font-bold rounded-xl shadow-md hover:bg-indigo-50 transition-all flex-shrink-0 text-sm"
          >
            <PlayCircle size={16} />
            Start Interview
          </Link>
        </div>
      </div>

      {/* ── Metric Cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={Trophy}      label="Average Score"     value={avgScore !== null ? `${avgScore}%` : 'N/A'} sub={completedInterviews.length > 0 ? `${completedInterviews.length} scored` : 'Complete an interview'} color="indigo" />
        <MetricCard icon={BrainCircuit} label="Total Sessions"    value={interviews.length}                          sub="All time"                 color="cyan"    />
        <MetricCard icon={Clock}        label="Practice Time"     value={formatTime(totalSeconds)}                    sub="Total invested"           color="amber"   />
        <MetricCard icon={Target}       label="Top Performing Role" value={strongestArea || '—'}                    sub={strongestArea ? 'Highest avg score' : 'Complete sessions'} color="emerald" />
      </div>

      {/* ── Chart + Quick Actions ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Trend */}
        <SectionCard
          title="Score Trend"
          className="lg:col-span-2"
          action={
            <span className="text-xs font-semibold px-2.5 py-1 bg-slate-800 text-slate-300 border border-slate-700/60 rounded-full">
              {interviews.length > 0 ? `${interviews.length} Sessions` : 'Sample Data'}
            </span>
          }
        >
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} dy={8} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ borderRadius: '12px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', boxShadow: '0 4px 20px -2px rgb(0 0 0 / 0.5)', fontSize: 12 }}
                  formatter={(v, _, item) => [`${v}%`, item.payload.role || 'Score']}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#6366f1"
                  strokeWidth={2.5}
                  dot={{ r: 3.5, fill: '#6366f1', strokeWidth: 2, stroke: '#0f172a' }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </SectionCard>

        {/* Quick Actions */}
        <SectionCard title="Quick Actions">
          <div className="space-y-2">
            {quickActions.map(({ label, sub, to, icon: Icon, color, shadow }) => (
              <Link
                key={label}
                to={to}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-150 ${color} shadow-sm ${shadow}`}
              >
                <Icon size={18} aria-hidden="true" />
                <div className="min-w-0">
                  <p className="text-sm font-semibold leading-none">{label}</p>
                  <p className="text-xs opacity-70 mt-0.5">{sub}</p>
                </div>
                <ChevronRight size={14} className="ml-auto opacity-50" aria-hidden="true" />
              </Link>
            ))}
          </div>
        </SectionCard>
      </div>

      {/* ── Recent Sessions ── */}
      <SectionCard
        title="Recent Sessions"
        noPad
        action={
          interviews.length > 0 && (
            <Link to="/history" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
              View all <ChevronRight size={14} />
            </Link>
          )
        }
      >
        {recentInterviews.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No interview sessions yet"
            description="Your first practice session will appear here once you complete it."
            action={
              <Link to="/setup" className="btn-primary text-sm">
                <PlayCircle size={16} />
                Start Your First Interview
              </Link>
            }
          />
        ) : (
          <div className="divide-y divide-slate-800/80">
            {recentInterviews.map((int) => (
              <div key={int.id} className="flex items-center justify-between gap-4 px-6 py-4 hover:bg-slate-800/50 transition">
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-white text-sm truncate">{int.job_role}</p>
                  <div className="flex flex-wrap items-center gap-2 mt-1">
                    <span className="text-xs text-slate-400">{int.interview_type}</span>
                    <span className="text-slate-600 text-xs">·</span>
                    <DifficultyBadge difficulty={int.difficulty} />
                    <span className="text-slate-600 text-xs hidden sm:inline">·</span>
                    <span className="text-xs text-slate-400 hidden sm:inline">
                      {int.created_at ? new Date(int.created_at).toLocaleDateString() : 'Recent'}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  <StatusBadge score={int.overall_score} />
                  <Link
                    to={`/interview/${int.id}/result`}
                    className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-lg transition"
                    title="View result"
                    aria-label={`View result for ${int.job_role}`}
                  >
                    <ArrowRight size={16} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </SectionCard>
    </div>
  );
};

export default DashboardPage;
