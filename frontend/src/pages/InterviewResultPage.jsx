import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';

const InterviewResultPage = () => {
  const { id } = useParams();
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        const res = await api.post(`/ai/generate-feedback/${id}`);
        setFeedback(res.data);
      } catch (err) {
        console.error("Failed to fetch feedback");
      } finally {
        setLoading(false);
      }
    };
    fetchFeedback();
  }, [id]);

  if (loading) return <div className="p-8 text-center text-slate-500">Generating comprehensive feedback...</div>;
  if (!feedback) return <div className="p-8 text-center text-red-500">Failed to load results.</div>;

  const chartData = feedback.category_breakdown || [
    { name: 'Technical', score: 75 },
    { name: 'Comm.', score: 75 },
    { name: 'Relevance', score: 75 },
    { name: 'Completeness', score: 75 },
  ];

  const overallScoreDisplay = feedback.overall_score !== undefined ? Math.round(feedback.overall_score) : 75;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="text-center pb-8 border-b border-slate-200">
        <h2 className="text-4xl font-extrabold text-slate-900 mb-2">Interview Completed!</h2>
        <p className="text-lg text-slate-500">Here is your AI-generated performance evaluation.</p>
        <div className="mt-8 inline-block p-6 rounded-3xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-xl shadow-blue-500/30">
          <p className="text-sm font-medium opacity-80 uppercase tracking-wider mb-1">Overall Score</p>
          <p className="text-6xl font-black">{overallScoreDisplay}<span className="text-3xl opacity-70">%</span></p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Chart */}
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200">
          <h3 className="text-xl font-bold text-slate-900 mb-6">Category Breakdown</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 30, left: 20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#475569', fontWeight: 500}} width={90} />
                <Tooltip cursor={{fill: 'transparent'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}/>
                <Bar dataKey="score" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Feedback text */}
        <div className="space-y-6">
          <div className="bg-emerald-50 p-6 rounded-2xl border border-emerald-100">
            <h3 className="text-lg font-bold text-emerald-800 mb-4 flex items-center space-x-2">
              <CheckCircle size={20} />
              <span>Strengths</span>
            </h3>
            <ul className="space-y-3">
              {feedback.strengths?.map((item, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-emerald-700">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"></span>
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
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-amber-500 flex-shrink-0"></span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Action Plan */}
      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200">
        <h3 className="text-xl font-bold text-slate-900 mb-6">Recommended Action Plan</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {feedback.recommendations?.map((item, idx) => (
            <div key={idx} className="flex items-center space-x-3 p-4 bg-slate-50 rounded-xl border border-slate-100">
              <div className="bg-blue-100 text-blue-600 font-bold w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                {idx + 1}
              </div>
              <span className="text-slate-700 font-medium">{item}</span>
            </div>
          ))}
        </div>
        
        <div className="mt-8 pt-6 border-t border-slate-100 flex justify-end">
          <Link to="/dashboard" className="flex items-center space-x-2 px-6 py-3 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition font-medium">
            <span>Return to Dashboard</span>
            <ArrowRight size={18} />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default InterviewResultPage;
