import React from 'react';
import { Link } from 'react-router-dom';
import {
  BrainCircuit, Mic, BarChart2, Code2, Sparkles, ArrowRight,
  CheckCircle, Shield, Zap,
} from 'lucide-react';

const features = [
  {
    icon: BrainCircuit,
    title: 'Adaptive AI Interviews',
    description: 'Questions dynamically scale in difficulty based on your real-time performance, just like a genuine interview.',
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10',
  },
  {
    icon: Mic,
    title: 'Voice Input & TTS',
    description: 'Speak your answers naturally using browser-native speech recognition with real-time transcript editing.',
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
  },
  {
    icon: BarChart2,
    title: 'Deep Analytics',
    description: 'Track scores, filler words, speaking pace, topic performance, and overall communication trends.',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
  },
  {
    icon: Code2,
    title: 'Coding Challenges',
    description: 'Solve problems in Python, Java, or C++ inside a full Monaco editor with secure Docker execution.',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
  },
  {
    icon: Sparkles,
    title: 'AI Feedback',
    description: 'Gemini-powered evaluation of technical accuracy, communication quality, relevance and completeness.',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    description: 'JWT authentication, isolated code execution, and no data shared with external services without consent.',
    color: 'text-rose-400',
    bg: 'bg-rose-500/10',
  },
];

const LandingPage = () => (
  <div className="min-h-screen bg-slate-950 text-white flex flex-col">
    {/* ── Nav ── */}
    <nav className="sticky top-0 z-20 border-b border-slate-800/80 backdrop-blur-md bg-slate-950/80">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-500/30">
            <BrainCircuit size={18} className="text-white" />
          </div>
          <span className="font-bold text-white tracking-tight">AI Interviewer</span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white rounded-lg hover:bg-slate-800 transition-all"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-md shadow-indigo-500/20 transition-all"
          >
            Get Started Free
          </Link>
        </div>
      </div>
    </nav>

    {/* ── Hero ── */}
    <section className="flex-1 flex flex-col items-center justify-center text-center px-6 pt-24 pb-20 relative overflow-hidden">
      {/* Background glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
        style={{
          background: 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(99,102,241,0.12) 0%, transparent 70%)',
        }}
      />

      <div className="relative z-10 max-w-4xl mx-auto">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 mb-8 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-semibold">
          <Zap size={12} />
          Powered by Google Gemini
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-none">
          <span className="text-white">Ace Your Next</span>
          <br />
          <span
            className="bg-clip-text text-transparent"
            style={{
              backgroundImage: 'linear-gradient(135deg, #818cf8 0%, #6366f1 40%, #06b6d4 100%)',
            }}
          >
            Interview
          </span>
        </h1>

        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Practice with an AI that adapts to your skill level. Get detailed feedback on technical depth, communication, and problem-solving — all in one platform.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/register"
            className="inline-flex items-center gap-2 px-8 py-3.5 text-base font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-2xl shadow-xl shadow-indigo-500/30 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            Start Practicing Free
            <ArrowRight size={18} />
          </Link>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 px-8 py-3.5 text-base font-semibold text-slate-300 border border-slate-700 hover:border-slate-500 hover:text-white rounded-2xl transition-all"
          >
            I have an account
          </Link>
        </div>

        {/* Trust line */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-slate-500">
          {['No credit card required', 'Mock AI works offline', 'Docker-isolated code execution'].map((t) => (
            <span key={t} className="flex items-center gap-1.5">
              <CheckCircle size={13} className="text-emerald-500" />
              {t}
            </span>
          ))}
        </div>
      </div>
    </section>

    {/* ── Features ── */}
    <section className="py-24 px-6 bg-slate-900/60 border-t border-slate-800">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Everything you need to prepare
          </h2>
          <p className="text-slate-400 max-w-xl mx-auto text-base">
            A complete end-to-end interview preparation platform with AI at its core.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, description, color, bg }) => (
            <div
              key={title}
              className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-600 hover:bg-slate-800/60 transition-all duration-200 group"
            >
              <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
                <Icon size={20} className={color} />
              </div>
              <h3 className="text-base font-bold text-white mb-2">{title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* ── CTA ── */}
    <section className="py-20 px-6 text-center border-t border-slate-800">
      <h2 className="text-3xl font-bold text-white mb-4">Ready to level up?</h2>
      <p className="text-slate-400 mb-8 max-w-md mx-auto">
        Join now and start practicing with real-world interview scenarios powered by AI.
      </p>
      <Link
        to="/register"
        className="inline-flex items-center gap-2 px-8 py-3.5 text-base font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-2xl shadow-xl shadow-indigo-500/30 transition-all hover:scale-[1.02]"
      >
        Create Free Account
        <ArrowRight size={18} />
      </Link>
    </section>

    {/* ── Footer ── */}
    <footer className="py-8 text-center text-slate-600 border-t border-slate-800 text-sm">
      © {new Date().getFullYear()} AI Interview Training Platform. Built with FastAPI + React + Gemini.
    </footer>
  </div>
);

export default LandingPage;
