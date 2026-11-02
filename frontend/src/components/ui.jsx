/**
 * Shared reusable UI components for the AI Interview Platform.
 * Import from: '../components/ui'
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, CheckCircle, Info, Loader2 } from 'lucide-react';

// ─── MetricCard ──────────────────────────────────────────────────────────────
export const MetricCard = ({ icon: Icon, label, value, sub, color = 'indigo', className = '' }) => {
  const colorMap = {
    indigo: 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30',
    emerald: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
    amber: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
    cyan: 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30',
    rose: 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
    slate: 'bg-slate-800 text-slate-300 border border-slate-700',
  };
  return (
    <div className={`card p-5 flex items-start gap-4 ${className}`}>
      {Icon && (
        <div className={`flex-shrink-0 p-2.5 rounded-xl ${colorMap[color] || colorMap.indigo}`}>
          <Icon size={20} />
        </div>
      )}
      <div className="min-w-0">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">{label}</p>
        <p className="text-2xl font-bold text-white mt-0.5 leading-none">{value}</p>
        {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
      </div>
    </div>
  );
};

// ─── SectionCard ─────────────────────────────────────────────────────────────
export const SectionCard = ({ title, action, children, className = '', noPad = false }) => (
  <div className={`card overflow-hidden ${className}`}>
    {title && (
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/80">
        <h3 className="section-title">{title}</h3>
        {action}
      </div>
    )}
    <div className={noPad ? '' : 'p-6'}>
      {children}
    </div>
  </div>
);

// ─── PageHeader ───────────────────────────────────────────────────────────────
export const PageHeader = ({ title, subtitle, action }) => (
  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
    <div>
      <h1 className="text-page">{title}</h1>
      {subtitle && <p className="text-muted mt-1">{subtitle}</p>}
    </div>
    {action && <div className="flex-shrink-0">{action}</div>}
  </div>
);

// ─── EmptyState ───────────────────────────────────────────────────────────────
export const EmptyState = ({ icon: Icon, title, description, action }) => (
  <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
    {Icon && (
      <div className="mb-4 p-4 bg-slate-800/80 border border-slate-700/60 rounded-2xl text-slate-400">
        <Icon size={32} />
      </div>
    )}
    <h4 className="text-base font-semibold text-white">{title}</h4>
    {description && <p className="text-sm text-slate-300 mt-1 max-w-sm">{description}</p>}
    {action && <div className="mt-5">{action}</div>}
  </div>
);

// ─── StatusBadge ─────────────────────────────────────────────────────────────
export const StatusBadge = ({ score, children }) => {
  if (children) {
    // Generic badge with children
    return <span className="badge badge-neutral">{children}</span>;
  }
  if (score === undefined || score === null) {
    return <span className="badge badge-neutral">In Progress</span>;
  }
  if (score >= 80) return <span className="badge badge-success">{Math.round(score)}%</span>;
  if (score >= 60) return <span className="badge badge-info">{Math.round(score)}%</span>;
  return <span className="badge badge-warning">{Math.round(score)}%</span>;
};

// ─── DifficultyBadge ─────────────────────────────────────────────────────────
export const DifficultyBadge = ({ difficulty }) => {
  const map = {
    Beginner: 'badge-success',
    Intermediate: 'badge-info',
    Advanced: 'badge-warning',
  };
  return <span className={`badge ${map[difficulty] || 'badge-neutral'}`}>{difficulty}</span>;
};

// ─── ProgressBar ─────────────────────────────────────────────────────────────
export const ProgressBar = ({ value, max = 100, color = 'indigo', className = '' }) => {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const colorFill = {
    indigo: 'bg-indigo-500',
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
    cyan: 'bg-cyan-500',
    red: 'bg-red-500',
  };
  return (
    <div className={`progress-bar ${className}`}>
      <div
        className={`progress-fill ${colorFill[color] || colorFill.indigo}`}
        style={{ width: `${pct}%` }}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      />
    </div>
  );
};

// ─── ScoreRing ────────────────────────────────────────────────────────────────
export const ScoreRing = ({ score, size = 120 }) => {
  const r = 40;
  const circumference = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, score));
  const strokeDash = (pct / 100) * circumference;
  const color = score >= 80 ? '#34d399' : score >= 60 ? '#818cf8' : '#fbbf24';

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" aria-label={`Score: ${score}%`}>
      <circle cx="50" cy="50" r={r} fill="none" stroke="#334155" strokeWidth="8" />
      <circle
        cx="50" cy="50" r={r}
        fill="none"
        stroke={color}
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={`${strokeDash} ${circumference - strokeDash}`}
        strokeDashoffset={circumference * 0.25}
        style={{ transition: 'stroke-dasharray 0.8s ease-out' }}
      />
      <text x="50" y="50" textAnchor="middle" dominantBaseline="central" className="font-bold" style={{ fontSize: 20, fill: color, fontFamily: 'Inter, sans-serif', fontWeight: 700 }}>
        {score}
      </text>
    </svg>
  );
};

// ─── LoadingSkeleton ──────────────────────────────────────────────────────────
export const LoadingSkeleton = ({ rows = 3 }) => (
  <div className="space-y-4 animate-pulse">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="card p-6 space-y-3 bg-slate-900 border-slate-800">
        <div className="h-4 bg-slate-800 rounded-full w-1/3" />
        <div className="h-3 bg-slate-800/60 rounded-full w-2/3" />
        <div className="h-3 bg-slate-800/60 rounded-full w-1/2" />
      </div>
    ))}
  </div>
);

// ─── LoadingSpinner ───────────────────────────────────────────────────────────
export const LoadingSpinner = ({ text = 'Loading...' }) => (
  <div className="flex flex-col items-center justify-center py-20 gap-4 text-slate-300">
    <Loader2 size={32} className="animate-spin text-indigo-400" />
    <span className="text-sm font-medium">{text}</span>
  </div>
);

// ─── AlertBanner ─────────────────────────────────────────────────────────────
export const AlertBanner = ({ type = 'info', message, onDismiss }) => {
  const map = {
    success: { cls: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300', Icon: CheckCircle, iconCls: 'text-emerald-400' },
    error:   { cls: 'bg-rose-500/15 border-rose-500/30 text-rose-300', Icon: AlertCircle, iconCls: 'text-rose-400' },
    warning: { cls: 'bg-amber-500/15 border-amber-500/30 text-amber-300', Icon: AlertCircle, iconCls: 'text-amber-400' },
    info:    { cls: 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300', Icon: Info, iconCls: 'text-indigo-400' },
  };
  const { cls, Icon, iconCls } = map[type] || map.info;
  return (
    <div className={`flex items-start gap-3 px-4 py-3 rounded-xl border text-sm ${cls}`} role="alert">
      <Icon size={16} className={`flex-shrink-0 mt-0.5 ${iconCls}`} aria-hidden="true" />
      <span className="flex-1 leading-relaxed">{message}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="flex-shrink-0 text-current opacity-70 hover:opacity-100" aria-label="Dismiss">×</button>
      )}
    </div>
  );
};

// ─── ScoreProgressRow ─────────────────────────────────────────────────────────
export const ScoreProgressRow = ({ label, score, max = 100 }) => {
  const color = score >= 80 ? 'emerald' : score >= 60 ? 'indigo' : 'amber';
  return (
    <div className="flex items-center gap-4">
      <span className="w-36 flex-shrink-0 text-sm font-medium text-slate-300">{label}</span>
      <ProgressBar value={score} max={max} color={color} className="flex-1" />
      <span className={`w-10 text-right text-sm font-bold ${
        score >= 80 ? 'text-emerald-400' : score >= 60 ? 'text-indigo-400' : 'text-amber-400'
      }`}>{score}</span>
    </div>
  );
};
