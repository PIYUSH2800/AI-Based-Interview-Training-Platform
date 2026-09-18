import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Briefcase, Activity, Target, Hash } from 'lucide-react';

const InterviewSetupPage = () => {
  const [formData, setFormData] = useState({
    job_role: 'Software Developer',
    interview_type: 'Technical Interview',
    difficulty: 'Intermediate',
    mode: 'Text',
    total_questions: 5
  });
  const [isStarting, setIsStarting] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsStarting(true);
    try {
      const response = await api.post('/interviews', formData);
      // Navigate to the active interview session passing the ID
      navigate(`/interview/${response.data.id}`);
    } catch (err) {
      console.error("Failed to start interview", err);
      setIsStarting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-slate-900">Configure Interview</h2>
        <p className="text-slate-500 mt-1">Set up your mock interview environment to match your goals.</p>
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
        <form onSubmit={handleSubmit} className="space-y-8">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-2">
              <label className="flex items-center space-x-2 text-sm font-semibold text-slate-700">
                <Briefcase size={16} className="text-blue-500" />
                <span>Job Role</span>
              </label>
              <select name="job_role" value={formData.job_role} onChange={handleChange} className="block w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                <option>Software Developer</option>
                <option>Data Scientist</option>
                <option>Data Analyst</option>
                <option>AI/ML Engineer</option>
                <option>Product Manager</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="flex items-center space-x-2 text-sm font-semibold text-slate-700">
                <Target size={16} className="text-blue-500" />
                <span>Interview Type</span>
              </label>
              <select name="interview_type" value={formData.interview_type} onChange={handleChange} className="block w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                <option>Technical Interview</option>
                <option>HR Interview</option>
                <option>Behavioral Interview</option>
                <option>System Design Interview</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="flex items-center space-x-2 text-sm font-semibold text-slate-700">
                <Activity size={16} className="text-blue-500" />
                <span>Difficulty</span>
              </label>
              <select name="difficulty" value={formData.difficulty} onChange={handleChange} className="block w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                <option>Beginner</option>
                <option>Intermediate</option>
                <option>Advanced</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="flex items-center space-x-2 text-sm font-semibold text-slate-700">
                <Hash size={16} className="text-blue-500" />
                <span>Number of Questions</span>
              </label>
              <select name="total_questions" value={formData.total_questions} onChange={handleChange} className="block w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                <option value={3}>3 Questions (Quick Practice)</option>
                <option value={5}>5 Questions (Standard)</option>
                <option value={10}>10 Questions (Full Session)</option>
              </select>
            </div>
          </div>

          <div className="pt-6 border-t border-slate-100 flex justify-end">
            <button 
              type="submit" 
              disabled={isStarting}
              className="px-8 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition font-bold shadow-lg shadow-blue-500/30 disabled:opacity-50 disabled:shadow-none flex items-center space-x-2"
            >
              {isStarting ? (
                <span>Preparing Environment...</span>
              ) : (
                <span>Start Mock Interview</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InterviewSetupPage;
