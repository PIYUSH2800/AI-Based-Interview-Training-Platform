import React, { useState, useEffect, useContext } from 'react';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { 
  User, Mail, GraduationCap, Briefcase, Phone, CheckCircle, 
  AlertCircle, Save, FileText, Upload, Trash2, Download, 
  Sparkles, RefreshCw, FileCheck
} from 'lucide-react';

const ProfilePage = () => {
  const { user, updateUser, fetchUserProfile } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    education: '',
    experience_level: 'Entry Level',
    phone: '',
    college: '',
    degree: '',
    skills: '',
    target_role: ''
  });

  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Resume states
  const [resumeInfo, setResumeInfo] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [resumeMessage, setResumeMessage] = useState('');
  const [resumeError, setResumeError] = useState('');

  // Analysis state
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [applyCheckboxes, setApplyCheckboxes] = useState({
    skills: true,
    education: true,
    target_role: true
  });

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        education: user.education || '',
        experience_level: user.experience_level || 'Entry Level',
        phone: user.phone || '',
        college: user.college || '',
        degree: user.degree || '',
        skills: user.skills || '',
        target_role: user.target_role || ''
      });
    } else {
      fetchUserProfile().catch(console.error);
    }
    fetchResumeInfo();
  }, [user]);

  const fetchResumeInfo = async () => {
    try {
      const res = await api.get('/users/resume');
      if (res.data.has_resume) {
        setResumeInfo(res.data.resume);
      } else {
        setResumeInfo(null);
      }
    } catch (err) {
      console.error("Failed to fetch resume info");
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSuccessMessage('');
    setErrorMessage('');

    if (!formData.name.trim()) {
      setErrorMessage('Full Name is required.');
      setIsSaving(false);
      return;
    }

    if (!formData.email.trim()) {
      setErrorMessage('Email address is required.');
      setIsSaving(false);
      return;
    }

    try {
      const response = await api.put('/users/profile', formData);
      updateUser(response.data);
      setSuccessMessage('Profile updated successfully!');
    } catch (err) {
      setErrorMessage(err.response?.data?.detail || 'Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  // Resume Upload Handler
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    setResumeError('');
    setResumeMessage('');
    if (!file) return;

    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!['.pdf', '.docx'].includes(ext)) {
      setResumeError('Only PDF (.pdf) and Word (.docx) files are supported.');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setResumeError('File size exceeds 5 MB limit.');
      return;
    }

    setSelectedFile(file);
  };

  const handleUploadResume = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setResumeError('');
    setResumeMessage('');

    const uploadData = new FormData();
    uploadData.append('file', selectedFile);

    try {
      const res = await api.post('/users/resume', uploadData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResumeMessage('Resume uploaded successfully!');
      setSelectedFile(null);
      await fetchResumeInfo();
      await fetchUserProfile(); // Refresh AuthContext
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to upload resume.');
    } finally {
      setIsUploading(false);
    }
  };

  // Resume Download Handler
  const handleDownloadResume = async () => {
    try {
      const res = await api.get('/users/resume/download', { responseType: 'blob' });
      const blob = new Blob([res.data], { type: res.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', resumeInfo?.filename || 'my_resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setResumeError('Failed to download resume.');
    }
  };

  // Resume Delete Handler
  const handleDeleteResume = async () => {
    if (!window.confirm("Are you sure you want to delete your stored resume?")) return;
    setResumeError('');
    setResumeMessage('');

    try {
      await api.delete('/users/resume');
      setResumeMessage('Resume deleted successfully.');
      setResumeInfo(null);
      setAnalysisResult(null);
      await fetchUserProfile();
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to delete resume.');
    }
  };

  // Resume Analysis Handler
  const handleAnalyzeResume = async () => {
    setIsAnalyzing(true);
    setResumeError('');
    setResumeMessage('');

    try {
      const res = await api.post('/api/users/resume/analyze');
      setAnalysisResult(res.data);
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to analyze resume.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Apply Selected Analysis Suggestions
  const handleApplySuggestions = async () => {
    if (!analysisResult) return;
    const updated = { ...formData };

    if (applyCheckboxes.skills && analysisResult.skills?.length > 0) {
      const existing = formData.skills ? formData.skills.split(',').map(s => s.trim()) : [];
      const merged = Array.from(new Set([...existing, ...analysisResult.skills])).filter(Boolean).join(', ');
      updated.skills = merged;
    }

    if (applyCheckboxes.education && analysisResult.education) {
      updated.education = analysisResult.education;
    }

    if (applyCheckboxes.target_role && analysisResult.target_role) {
      updated.target_role = analysisResult.target_role;
    }

    setFormData(updated);

    try {
      const res = await api.put('/users/profile', updated);
      updateUser(res.data);
      setSuccessMessage('Resume suggestions applied to your profile!');
      setAnalysisResult(null);
    } catch (err) {
      setErrorMessage('Failed to update profile with suggestions.');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div>
        <h2 className="text-3xl font-bold text-slate-900">User Profile</h2>
        <p className="text-slate-500 mt-1">Manage your account information, background, and resume documents.</p>
      </div>

      {successMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl flex items-center space-x-3 text-sm font-medium">
          <CheckCircle size={20} className="text-emerald-600 flex-shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-800 rounded-xl flex items-center space-x-3 text-sm font-medium">
          <AlertCircle size={20} className="text-red-600 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* SECTION: Resume & Document Management */}
      <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-4">
          <FileText size={20} className="text-blue-600" />
          <h3 className="text-lg font-bold text-slate-900">Resume & Documents</h3>
        </div>

        {resumeMessage && (
          <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-sm font-medium flex items-center space-x-2">
            <CheckCircle size={16} />
            <span>{resumeMessage}</span>
          </div>
        )}

        {resumeError && (
          <div className="p-3 bg-red-50 text-red-700 rounded-xl text-sm font-medium flex items-center space-x-2">
            <AlertCircle size={16} />
            <span>{resumeError}</span>
          </div>
        )}

        {resumeInfo ? (
          <div className="space-y-6">
            {/* Existing Resume Banner */}
            <div className="p-5 bg-slate-50 border border-slate-200 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-100 text-blue-600 rounded-xl">
                  <FileCheck size={28} />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <p className="font-bold text-slate-900">{resumeInfo.filename}</p>
                    <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 font-bold text-xs rounded-full">Active</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    {resumeInfo.file_type} • {formatFileSize(resumeInfo.size)}
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
                <button
                  type="button"
                  onClick={handleDownloadResume}
                  className="px-3.5 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
                >
                  <Download size={14} />
                  <span>Download</span>
                </button>
                <button
                  type="button"
                  onClick={handleAnalyzeResume}
                  disabled={isAnalyzing}
                  className="px-3.5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 transition shadow-sm disabled:opacity-50"
                >
                  <Sparkles size={14} />
                  <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Resume'}</span>
                </button>
                <button
                  type="button"
                  onClick={handleDeleteResume}
                  className="px-3.5 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
                >
                  <Trash2 size={14} />
                  <span>Delete</span>
                </button>
              </div>
            </div>

            {/* Replace Resume Accordion / Input */}
            <div className="pt-2">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Replace Current Resume:</label>
              <div className="flex items-center space-x-3">
                <input 
                  type="file" 
                  accept=".pdf,.docx" 
                  onChange={handleFileSelect}
                  className="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 cursor-pointer"
                />
                {selectedFile && (
                  <button
                    type="button"
                    onClick={handleUploadResume}
                    disabled={isUploading}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl flex-shrink-0 transition disabled:opacity-50"
                  >
                    {isUploading ? 'Uploading...' : 'Upload Replacement'}
                  </button>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* Upload New Resume Box */
          <div className="border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center space-y-4 bg-slate-50/50">
            <div className="mx-auto w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center">
              <Upload size={24} />
            </div>
            <div>
              <p className="font-bold text-slate-800 text-base">Upload Your Resume</p>
              <p className="text-xs text-slate-500 mt-1">Supported formats: PDF (.pdf), Word (.docx) | Maximum size: 5 MB</p>
            </div>
            <div className="flex flex-col items-center gap-3">
              <input 
                type="file" 
                accept=".pdf,.docx" 
                onChange={handleFileSelect}
                className="block text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"
              />
              {selectedFile && (
                <button
                  type="button"
                  onClick={handleUploadResume}
                  disabled={isUploading}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl transition shadow-md shadow-blue-500/20 disabled:opacity-50"
                >
                  {isUploading ? 'Uploading Resume...' : 'Confirm Resume Upload'}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Resume Analysis Review & Apply Suggestions Card */}
        {analysisResult && (
          <div className="p-6 bg-gradient-to-br from-indigo-50/80 to-blue-50/80 border border-indigo-200/80 rounded-2xl space-y-5">
            <div className="flex items-center space-x-2">
              <Sparkles size={20} className="text-indigo-600" />
              <h4 className="font-bold text-slate-900 text-base">Extracted Resume Analysis Suggestions</h4>
            </div>

            {analysisResult.extracted ? (
              <div className="space-y-4 text-sm">
                <p className="text-slate-600 text-xs leading-relaxed">
                  Review extracted data below. Uncheck any item you do not want to apply to your profile.
                </p>

                <div className="space-y-3 bg-white p-4 rounded-xl border border-indigo-100">
                  {analysisResult.skills?.length > 0 && (
                    <label className="flex items-start space-x-3 cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={applyCheckboxes.skills} 
                        onChange={(e) => setApplyCheckboxes({ ...applyCheckboxes, skills: e.target.checked })}
                        className="mt-1 text-blue-600 rounded"
                      />
                      <div>
                        <span className="font-semibold text-slate-900">Add Extracted Skills:</span>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {analysisResult.skills.map((s, idx) => (
                            <span key={idx} className="px-2 py-0.5 bg-blue-50 text-blue-700 font-medium text-xs rounded-md">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    </label>
                  )}

                  {analysisResult.education && (
                    <label className="flex items-center space-x-3 cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={applyCheckboxes.education} 
                        onChange={(e) => setApplyCheckboxes({ ...applyCheckboxes, education: e.target.checked })}
                        className="text-blue-600 rounded"
                      />
                      <div>
                        <span className="font-semibold text-slate-900">Education Level: </span>
                        <span className="text-slate-700">{analysisResult.education}</span>
                      </div>
                    </label>
                  )}

                  {analysisResult.target_role && (
                    <label className="flex items-center space-x-3 cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={applyCheckboxes.target_role} 
                        onChange={(e) => setApplyCheckboxes({ ...applyCheckboxes, target_role: e.target.checked })}
                        className="text-blue-600 rounded"
                      />
                      <div>
                        <span className="font-semibold text-slate-900">Suggested Target Role: </span>
                        <span className="text-slate-700">{analysisResult.target_role}</span>
                      </div>
                    </label>
                  )}
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setAnalysisResult(null)}
                    className="px-4 py-2 bg-white border border-slate-300 text-slate-600 rounded-xl font-semibold text-xs hover:bg-slate-50 transition"
                  >
                    Dismiss
                  </button>
                  <button
                    type="button"
                    onClick={handleApplySuggestions}
                    className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold text-xs shadow-md transition"
                  >
                    Apply Selected Suggestions
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-slate-600 text-xs">{analysisResult.message}</p>
            )}
          </div>
        )}
      </div>

      {/* FORM: User & Profile Details */}
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Section 1: Account Information */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-4">
            <User size={20} className="text-blue-600" />
            <h3 className="text-lg font-bold text-slate-900">Account Information</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700">Full Name *</label>
              <input 
                type="text" 
                name="name" 
                required
                value={formData.name} 
                onChange={handleChange} 
                className="mt-1 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" 
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Email Address *</label>
              <input 
                type="email" 
                name="email" 
                required
                value={formData.email} 
                onChange={handleChange} 
                className="mt-1 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" 
              />
            </div>
          </div>
        </div>

        {/* Section 2: Education & Background */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-4">
            <GraduationCap size={20} className="text-blue-600" />
            <h3 className="text-lg font-bold text-slate-900">Education & Experience</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700">Education Level</label>
              <input 
                type="text" 
                name="education" 
                placeholder="e.g. Bachelor's Degree" 
                value={formData.education} 
                onChange={handleChange} 
                className="mt-1 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" 
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Experience Level</label>
              <select 
                name="experience_level" 
                value={formData.experience_level} 
                onChange={handleChange} 
                className="mt-1 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              >
                <option value="Entry Level">Entry Level</option>
                <option value="Mid Level">Mid Level</option>
                <option value="Senior Level">Senior Level</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">College / University</label>
              <input 
                type="text" 
                name="college" 
                placeholder="e.g. Stanford University" 
                value={formData.college} 
                onChange={handleChange} 
                className="mt-1 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" 
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Degree / Major</label>
              <input 
                type="text" 
                name="degree" 
                placeholder="e.g. B.S. Computer Science" 
                value={formData.degree} 
                onChange={handleChange} 
                className="mt-1 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" 
              />
            </div>
          </div>
        </div>

        {/* Section 3: Professional & Career Goals */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 space-y-6">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-4">
            <Briefcase size={20} className="text-blue-600" />
            <h3 className="text-lg font-bold text-slate-900">Career & Technical Profile</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700">Phone Number</label>
              <input 
                type="text" 
                name="phone" 
                placeholder="e.g. +1 (555) 000-0000" 
                value={formData.phone} 
                onChange={handleChange} 
                className="mt-1 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" 
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Target Role</label>
              <input 
                type="text" 
                name="target_role" 
                placeholder="e.g. Software Developer" 
                value={formData.target_role} 
                onChange={handleChange} 
                className="mt-1 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" 
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700">Skills (comma-separated)</label>
              <textarea 
                name="skills" 
                rows="3" 
                placeholder="e.g. Python, React, SQL, Data Structures, FastAPI" 
                value={formData.skills} 
                onChange={handleChange} 
                className="mt-1 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition resize-none"
              ></textarea>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button 
              type="submit" 
              disabled={isSaving}
              className="flex items-center space-x-2 px-8 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition font-bold shadow-lg shadow-blue-500/30 disabled:opacity-50"
            >
              <Save size={18} />
              <span>{isSaving ? 'Saving Changes...' : 'Save Profile'}</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ProfilePage;
