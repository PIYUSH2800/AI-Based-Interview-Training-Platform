import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="flex flex-col min-h-screen bg-slate-900 text-white">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 border-b border-slate-800">
        <div className="text-2xl font-bold text-blue-500 tracking-tight">AI Interviewer</div>
        <div className="space-x-4">
          <Link to="/login" className="px-4 py-2 text-slate-300 hover:text-white transition">Login</Link>
          <Link to="/register" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md font-medium transition shadow-lg shadow-blue-500/30">Get Started</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 pt-20 pb-32">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          Ace Your Next Interview
        </h1>
        <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mb-10">
          Practice with our advanced AI. Get real-time feedback on your technical answers, communication skills, and problem-solving abilities.
        </p>
        <div className="flex space-x-4">
          <Link to="/register" className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-full font-bold text-lg transition shadow-xl shadow-blue-600/40">
            Start Practicing Now
          </Link>
        </div>
      </main>

      {/* Features Section */}
      <section className="bg-slate-950 py-24 px-6 border-t border-slate-800">
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-12">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 transition">
            <h3 className="text-xl font-bold mb-3 text-blue-400">Adaptive AI</h3>
            <p className="text-slate-400">Questions scale in difficulty based on your performance, just like a real interview.</p>
          </div>
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 transition">
            <h3 className="text-xl font-bold mb-3 text-blue-400">Detailed Feedback</h3>
            <p className="text-slate-400">Receive comprehensive scoring on technical accuracy, completeness, and clarity.</p>
          </div>
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 transition">
            <h3 className="text-xl font-bold mb-3 text-blue-400">Role Specific</h3>
            <p className="text-slate-400">Tailor your practice sessions to specific roles like Software Developer, Data Scientist, and more.</p>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="p-8 text-center text-slate-500 border-t border-slate-800">
        &copy; 2026 AI Interview Platform. All rights reserved.
      </footer>
    </div>
  );
};

export default LandingPage;
