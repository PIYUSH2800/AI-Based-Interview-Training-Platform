import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Briefcase, Activity, Target, Hash, ArrowRight, Loader2,
  CheckCircle, Zap,
} from 'lucide-react';
import { PageHeader, SectionCard, AlertBanner } from '../components/ui';

// Option selector card
const OptionGroup = ({ label, icon: Icon, name, options, value, onChange, descriptions = {} }) => (
  <div>
    {label && (
      <label className="flex items-center gap-2 form-label">
        <Icon size={15} className="text-indigo-400" aria-hidden="true" />
        {label}
      </label>
    )}
    <div className="space-y-2 mt-1">
      {options.map((opt) => {
        const optValue = typeof opt === 'object' ? opt.value : opt;
        const optLabel = typeof opt === 'object' ? opt.label : opt;
        const desc = descriptions[optValue] || '';
        const isSelected = String(value) === String(optValue);
        return (
          <label
            key={optValue}
            className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all duration-150 ${
              isSelected
                ? 'border-indigo-500 bg-indigo-950/50 shadow-sm'
                : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-800/80'
            }`}
          >
            <input
              type="radio"
              name={name}
              value={optValue}
              checked={isSelected}
              onChange={onChange}
              className="mt-0.5 accent-indigo-500 flex-shrink-0"
            />
            <div className="min-w-0">
              <span className={`text-sm font-semibold leading-none ${isSelected ? 'text-indigo-300' : 'text-slate-200'}`}>
                {optLabel}
              </span>
              {desc && <p className={`text-xs mt-0.5 ${isSelected ? 'text-indigo-400' : 'text-slate-400'}`}>{desc}</p>}
            </div>
            {isSelected && (
              <CheckCircle size={16} className="flex-shrink-0 ml-auto text-indigo-400 mt-0.5" aria-hidden="true" />
            )}
          </label>
        );
      })}
    </div>
  </div>
);

const InterviewSetupPage = () => {
  const [formData, setFormData] = useState({
    job_role: 'Software Developer',
    interview_type: 'Technical Interview',
    difficulty: 'Intermediate',
    mode: 'Text',
    total_questions: 5,
  });
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    const val = e.target.type === 'number' ? Number(e.target.value) : e.target.value;
    setFormData({ ...formData, [e.target.name]: val });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsStarting(true);
    setError('');
    try {
      const res = await api.post('/interviews', formData);
      navigate(`/interview/${res.data.id}`);
    } catch (err) {
      setError('Failed to start interview. Please try again.');
      setIsStarting(false);
    }
  };

  return (
    <div className="page-container max-w-3xl">
      <PageHeader
        title="Configure Interview"
        subtitle="Customise your mock interview session to match your target role and goals."
      />

      <form onSubmit={handleSubmit} className="space-y-6" noValidate>
        {error && <AlertBanner type="error" message={error} onDismiss={() => setError('')} />}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Job Role */}
          <SectionCard title="Target Role" className="md:col-span-2">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {['Software Developer', 'Data Scientist', 'Data Analyst', 'AI/ML Engineer', 'Product Manager'].map(role => {
                const sel = formData.job_role === role;
                return (
                  <label
                    key={role}
                    className={`flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all text-sm font-medium ${
                      sel
                        ? 'border-indigo-500 bg-indigo-950/50 text-indigo-200 shadow-sm'
                        : 'border-slate-800 bg-slate-900/60 text-slate-200 hover:border-slate-700 hover:bg-slate-800/80'
                    }`}
                  >
                    <input
                      type="radio"
                      name="job_role"
                      value={role}
                      checked={sel}
                      onChange={handleChange}
                      className="accent-indigo-500 flex-shrink-0"
                    />
                    <Briefcase size={13} className={sel ? 'text-indigo-400' : 'text-slate-400'} aria-hidden="true" />
                    <span>{role}</span>
                  </label>
                );
              })}
            </div>
          </SectionCard>

          {/* Interview Type */}
          <SectionCard title="Interview Type">
            <OptionGroup
              name="interview_type"
              icon={Target}
              label=""
              value={formData.interview_type}
              onChange={handleChange}
              options={['Technical Interview', 'HR Interview', 'Behavioral Interview', 'System Design Interview']}
              descriptions={{
                'Technical Interview': 'Algorithms, data structures, coding problems',
                'HR Interview': 'Fit, culture, motivation questions',
                'Behavioral Interview': 'Situation-based STAR method questions',
                'System Design Interview': 'Architecture and scalability design',
              }}
            />
          </SectionCard>

          {/* Difficulty */}
          <SectionCard title="Difficulty Level">
            <OptionGroup
              name="difficulty"
              icon={Activity}
              label=""
              value={formData.difficulty}
              onChange={handleChange}
              options={['Beginner', 'Intermediate', 'Advanced']}
              descriptions={{
                Beginner: 'Foundational concepts, great for first sessions',
                Intermediate: 'Real interview level — recommended',
                Advanced: 'Challenging deep-dives and edge cases',
              }}
            />
          </SectionCard>

          {/* Number of Questions */}
          <SectionCard title="Number of Questions">
            <OptionGroup
              name="total_questions"
              icon={Hash}
              label=""
              value={formData.total_questions}
              onChange={handleChange}
              options={[
                { value: 3,  label: '3 Questions'  },
                { value: 5,  label: '5 Questions'  },
                { value: 10, label: '10 Questions' },
                { value: 15, label: '15 Questions' },
                { value: 20, label: '20 Questions' },
              ]}
              descriptions={{
                3: 'Quick 6–10 min warm-up practice',
                5: 'Standard 10–15 min focused practice',
                10: 'Full 20–25 min comprehensive interview',
                15: 'In-depth 30–35 min extended session',
                20: 'Thorough 40–45 min marathon assessment',
              }}
            />
          </SectionCard>

          {/* AI Mode info */}
          <SectionCard title="AI Mode" className="">
            <div className="flex items-start gap-3 p-3.5 rounded-xl bg-indigo-950/40 border border-indigo-700/50">
              <Zap size={18} className="text-indigo-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
              <div>
                <p className="text-sm font-semibold text-indigo-200">Adaptive AI</p>
                <p className="text-xs text-indigo-300/90 mt-0.5 leading-relaxed">
                  Questions adapt dynamically based on your answers. Topics and difficulty shift to target your weak areas.
                </p>
              </div>
            </div>
          </SectionCard>
        </div>

        {/* Submit */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={isStarting}
            className="btn-primary px-8 py-3.5 text-base"
          >
            {isStarting ? (
              <>
                <Loader2 size={18} className="animate-spin" aria-hidden="true" />
                Preparing environment…
              </>
            ) : (
              <>
                Start Interview
                <ArrowRight size={18} aria-hidden="true" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default InterviewSetupPage;
