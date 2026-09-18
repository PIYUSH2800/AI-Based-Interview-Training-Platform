import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BrainCircuit, Target, Trophy, Clock, PlayCircle, ArrowRight, FileText, ChevronRight } from 'lucide-react';

const DashboardPage = () => {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get('/interviews');
        setInterviews(response.data);
      } catch (error) {
        console.error("Failed to fetch dashboard data");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) return <div className="p-8 text-center text-slate-500 font-medium">Loading dashboard overview...</div>;

  const totalInterviews = interviews.length;
  const completedInterviews = interviews.filter(i => i.overall_score !== null && i.overall_score !== undefined);
  
  const avgScore = completedInterviews.length > 0 
    ? Math.round(completedInterviews.reduce((acc, curr) => acc + curr.overall_score, 0) / completedInterviews.length)
    : 0;

  // Calculate real total practice time
  const totalSeconds = interviews.reduce((acc, curr) => acc + (curr.duration || 0), 0);
  const formatPracticeTime = (seconds) => {
    if (seconds === 0) return '0m';
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${(seconds / 3600).toFixed(1)}h`;
  };

  // Determine strongest area based on highest average score per job_role
  const strongestArea = (() => {
    if (completedInterviews.length === 0) return 'N/A';
    const roleScores = {};
    completedInterviews.forEach(i => {
      if (!roleScores[i.job_role]) roleScores[i.job_role] = [];
      roleScores[i.job_role].push(i.overall_score);
    });
    let bestRole = 'N/A';
    let bestAvg = -1;
    Object.entries(roleScores).forEach(([role, scores]) => {
      const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
      if (avg > bestAvg) {
        bestAvg = avg;
        bestRole = role;
      }
    });
    return bestRole;
  })();

  // Dynamic Chart Data (Chronological order)
  const chartData = interviews.length > 0 
    ? [...interviews].reverse().map((int, index) => {
        const dateLabel = int.created_at 
          ? new Date(int.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
          : `Session ${index + 1}`;
        return {
          name: dateLabel,
          score: Math.round(int.overall_score || 0),
          role: int.job_role
        };
      })
    : [
        { name: 'Session 1', score: 65 },
        { name: 'Session 2', score: 72 },
        { name: 'Session 3', score: 78 },
        { name: 'Session 4', score: 85 }
      ];

  const recentInterviews = interviews.slice(0, 3);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">Dashboard</h2>
          <p className="text-slate-500 mt-1">Welcome back! Here is your mock interview analytics overview.</p>
        </div>
        <Link 
          to="/setup" 
          className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-500/30 transition self-start md:self-auto"
        >
          <PlayCircle size={18} />
          <span>New Interview</span>
        </Link>
      </div>

      {/* Real Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center space-x-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-xl"><Trophy size={24} /></div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Average Score</p>
            <p className="text-2xl font-bold text-slate-900">{completedInterviews.length > 0 ? `${avgScore}%` : 'N/A'}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center space-x-4">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl"><BrainCircuit size={24} /></div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Interviews Completed</p>
            <p className="text-2xl font-bold text-slate-900">{totalInterviews}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center space-x-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl"><Target size={24} /></div>
          <div className="overflow-hidden">
            <p className="text-sm text-slate-500 font-medium">Top Performing Role</p>
            <p className="text-lg font-bold text-slate-900 truncate" title={strongestArea}>{strongestArea}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center space-x-4">
          <div className="p-3 bg-amber-50 text-amber-600 rounded-xl"><Clock size={24} /></div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Total Practice Time</p>
            <p className="text-2xl font-bold text-slate-900">{formatPracticeTime(totalSeconds)}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-bold text-slate-900">Performance Trend</h3>
            <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-600 rounded-full">
              {interviews.length > 0 ? `${interviews.length} Sessions` : 'Sample Trend'}
            </span>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} dx={-10} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px -2px rgb(0 0 0 / 0.12)'}}
                  formatter={(value, name, item) => [`${value}%`, `Score (${item.payload.role || 'Practice'})`]}
                />
                <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={3} dot={{r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff'}} activeDot={{r: 6}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Action / Practice Card */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col">
          <h3 className="text-lg font-bold text-slate-900 mb-2">Ready to Practice?</h3>
          <p className="text-slate-500 mb-6 flex-1 text-sm leading-relaxed">
            Start a dynamic AI mock interview session tailored to your target job role. Receive automated scoring and detailed recommendations.
          </p>
          <div className="space-y-3">
            <Link 
              to="/setup" 
              className="w-full flex justify-center items-center space-x-2 py-3 px-4 rounded-xl text-white bg-blue-600 hover:bg-blue-700 transition font-bold text-sm shadow-md shadow-blue-500/20"
            >
              <PlayCircle size={18} />
              <span>Start New Session</span>
            </Link>
            <Link 
              to="/history" 
              className="w-full flex justify-center items-center space-x-2 py-3 px-4 rounded-xl text-slate-700 bg-slate-100 hover:bg-slate-200 transition font-semibold text-sm"
            >
              <FileText size={18} />
              <span>View All History</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Interviews Preview Section */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-bold text-slate-900">Recent Interview Sessions</h3>
          {interviews.length > 0 && (
            <Link to="/history" className="text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center space-x-1">
              <span>View full history</span>
              <ChevronRight size={16} />
            </Link>
          )}
        </div>

        {recentInterviews.length === 0 ? (
          <div className="py-12 text-center text-slate-400 space-y-3">
            <p className="font-medium">No interview sessions recorded yet.</p>
            <Link to="/setup" className="inline-block px-5 py-2.5 bg-blue-50 text-blue-600 rounded-xl font-bold text-sm hover:bg-blue-100 transition">
              Start your first interview
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {recentInterviews.map((int) => (
              <div key={int.id} className="py-4 flex items-center justify-between gap-4">
                <div>
                  <p className="font-bold text-slate-900">{int.job_role}</p>
                  <div className="flex items-center space-x-3 text-xs text-slate-500 mt-1">
                    <span>{int.interview_type}</span>
                    <span>•</span>
                    <span>{int.difficulty}</span>
                    <span>•</span>
                    <span>{int.created_at ? new Date(int.created_at).toLocaleDateString() : 'Recent'}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <span className={`inline-block px-3 py-1 rounded-full font-bold text-xs ${
                      (int.overall_score || 0) >= 80 ? 'bg-emerald-50 text-emerald-700' :
                      (int.overall_score || 0) >= 60 ? 'bg-blue-50 text-blue-700' : 'bg-amber-50 text-amber-700'
                    }`}>
                      {int.overall_score !== null && int.overall_score !== undefined ? `${Math.round(int.overall_score)}%` : 'In Progress'}
                    </span>
                  </div>
                  <Link 
                    to={`/interview/${int.id}/result`} 
                    className="p-2 text-slate-400 hover:text-blue-600 transition hover:bg-slate-50 rounded-lg"
                    title="View Report"
                  >
                    <ArrowRight size={18} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
