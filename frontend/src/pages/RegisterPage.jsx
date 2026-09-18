import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    education: '',
    experience_level: 'Entry Level'
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords don't match");
      return;
    }

    setIsSubmitting(true);
    try {
      const { confirmPassword, ...registerData } = formData;
      await register(registerData);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-2xl shadow-xl border border-slate-100">
        <div>
          <h2 className="mt-2 text-center text-3xl font-extrabold text-slate-900 tracking-tight">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-slate-500">
            Start your interview preparation journey today
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{error}</div>}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700">Full Name</label>
              <input 
                name="name" type="text" required 
                className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" 
                value={formData.name} onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Email address</label>
              <input 
                name="email" type="email" required 
                className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" 
                value={formData.email} onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Password</label>
              <input 
                name="password" type="password" required 
                className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" 
                value={formData.password} onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Confirm Password</label>
              <input 
                name="confirmPassword" type="password" required 
                className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" 
                value={formData.confirmPassword} onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Experience Level</label>
              <select 
                name="experience_level" 
                className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                value={formData.experience_level} onChange={handleChange}
              >
                <option value="Entry Level">Entry Level</option>
                <option value="Mid Level">Mid Level</option>
                <option value="Senior Level">Senior Level</option>
              </select>
            </div>
          </div>
          <div>
            <button 
              type="submit" 
              disabled={isSubmitting}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400 transition"
            >
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </button>
          </div>
          <div className="text-center text-sm">
            <span className="text-slate-500">Already have an account? </span>
            <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">Log in</Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterPage;
