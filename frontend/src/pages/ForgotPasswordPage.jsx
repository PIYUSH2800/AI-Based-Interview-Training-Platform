import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { BrainCircuit, Mail, Loader2, CheckCircle2, AlertCircle, ArrowLeft } from 'lucide-react';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!email || !email.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post('/auth/forgot-password', { email });
      setSuccessMessage(
        response.data?.message ||
          'If an account exists with this email, a password reset link has been sent.'
      );
    } catch (err) {
      if (err.response?.status === 429) {
        setError('Too many password reset requests. Please wait a few minutes before trying again.');
      } else {
        // Fallback generic error message that does not leak account details
        setError(err.response?.data?.detail || 'Unable to process your request. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4 py-12 relative overflow-hidden">
      {/* Background glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
        style={{
          background: 'radial-gradient(ellipse 60% 50% at 50% 0%, rgba(99,102,241,0.12) 0%, transparent 70%)',
        }}
      />

      <div className="relative z-10 w-full max-w-md">
        {/* Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl p-8 md:p-10">
          {/* Brand */}
          <div className="flex flex-col items-center mb-8">
            <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center mb-4 shadow-lg shadow-indigo-500/30">
              <BrainCircuit size={24} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Forgot password?</h1>
            <p className="text-sm text-slate-400 mt-1 text-center">
              Enter your account email and we'll send you a secure link to reset your password.
            </p>
          </div>

          {/* Success Banner */}
          {successMessage && (
            <div className="mb-6 p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm flex flex-col gap-2">
              <div className="flex items-center gap-2 font-semibold text-emerald-400">
                <CheckCircle2 size={18} className="flex-shrink-0" />
                <span>Reset link dispatched</span>
              </div>
              <p className="text-xs text-emerald-300/90 leading-relaxed">
                {successMessage}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                Please check your inbox (and spam folder). The link will expire in 20 minutes.
              </p>
            </div>
          )}

          {/* Error Banner */}
          {error && (
            <div className="flex items-center gap-2 mb-6 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm" role="alert">
              <AlertCircle size={15} className="flex-shrink-0" aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}

          {!successMessage ? (
            <form onSubmit={handleSubmit} className="space-y-5" noValidate>
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-slate-300 mb-1.5">
                  Registered Email Address
                </label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" aria-hidden="true" />
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    required
                    placeholder="student@example.com"
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={isSubmitting}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-semibold rounded-xl shadow-md shadow-indigo-500/20 transition-all disabled:opacity-60 disabled:cursor-not-allowed mt-2"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 size={18} className="animate-spin" aria-hidden="true" />
                    Sending reset link…
                  </>
                ) : (
                  'Send Reset Link'
                )}
              </button>
            </form>
          ) : (
            <div className="mt-4 flex flex-col gap-3">
              <Link
                to="/login"
                className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl border border-slate-700 transition"
              >
                <ArrowLeft size={16} />
                Return to Login
              </Link>
            </div>
          )}

          <div className="mt-6 pt-6 border-t border-slate-800/80 text-center">
            <Link
              to="/login"
              className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition font-medium"
            >
              <ArrowLeft size={14} />
              Back to Sign In
            </Link>
          </div>
        </div>

        <p className="text-center text-xs text-slate-600 mt-6">
          <Link to="/" className="hover:text-slate-400 transition">← Back to home</Link>
        </p>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
