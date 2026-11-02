import React, { useState, useEffect, useContext } from 'react';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import {
  User, Mail, GraduationCap, Briefcase, Phone, CheckCircle,
  AlertCircle, Save, FileText, Upload, Trash2, Download,
  Sparkles, RefreshCw, FileCheck, Loader2,
} from 'lucide-react';
import { PageHeader, SectionCard, AlertBanner } from '../components/ui';

// ── Reusable field wrapper ────────────────────────────────────────────────────
const Field = ({ label, children, className = '' }) => (
  <div className={className}>
    <label className="form-label">{label}</label>
    {children}
  </div>
);

const ProfilePage = () => {
  const { user, updateUser, fetchUserProfile } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    name: '', email: '', education: '', experience_level: 'Entry Level',
    phone: '', college: '', degree: '', skills: '', target_role: '',
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
  const [applyCheckboxes, setApplyCheckboxes] = useState({ skills: true, education: true, target_role: true });

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
        target_role: user.target_role || '',
      });
    } else {
      fetchUserProfile().catch(console.error);
    }
    fetchResumeInfo();
  }, [user]);

  const fetchResumeInfo = async () => {
    try {
      const res = await api.get('/users/resume');
      setResumeInfo(res.data.has_resume ? res.data.resume : null);
    } catch {
      // silent
    }
  };

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSuccessMessage('');
    setErrorMessage('');
    if (!formData.name.trim()) { setErrorMessage('Full Name is required.'); setIsSaving(false); return; }
    if (!formData.email.trim()) { setErrorMessage('Email address is required.'); setIsSaving(false); return; }
    try {
      const response = await api.put('/users/profile', formData);
      updateUser(response.data);
      setSuccessMessage('Profile updated successfully!');
      setTimeout(() => setSuccessMessage(''), 4000);
    } catch (err) {
      setErrorMessage(err.response?.data?.detail || 'Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    setResumeError('');
    setResumeMessage('');
    if (!file) return;
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!['.pdf', '.docx'].includes(ext)) { setResumeError('Only PDF or Word (.docx) files are supported.'); return; }
    if (file.size > 5 * 1024 * 1024) { setResumeError('File size exceeds 5 MB limit.'); return; }
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
      await api.post('/users/resume', uploadData, { headers: { 'Content-Type': 'multipart/form-data' } });
      setResumeMessage('Resume uploaded successfully!');
      setSelectedFile(null);
      await fetchResumeInfo();
      await fetchUserProfile();
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to upload resume.');
    } finally {
      setIsUploading(false);
    }
  };

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
    } catch {
      setResumeError('Failed to download resume.');
    }
  };

  const handleDeleteResume = async () => {
    if (!window.confirm('Are you sure you want to delete your stored resume?')) return;
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

  const handleApplySuggestions = async () => {
    if (!analysisResult) return;
    const updated = { ...formData };
    if (applyCheckboxes.skills && analysisResult.skills?.length > 0) {
      const existing = formData.skills ? formData.skills.split(',').map(s => s.trim()) : [];
      updated.skills = Array.from(new Set([...existing, ...analysisResult.skills])).filter(Boolean).join(', ');
    }
    if (applyCheckboxes.education && analysisResult.education) updated.education = analysisResult.education;
    if (applyCheckboxes.target_role && analysisResult.target_role) updated.target_role = analysisResult.target_role;
    setFormData(updated);
    try {
      const res = await api.put('/users/profile', updated);
      updateUser(res.data);
      setSuccessMessage('Resume suggestions applied to your profile!');
      setAnalysisResult(null);
    } catch {
      setErrorMessage('Failed to update profile with suggestions.');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  };

  const initial = user?.name?.trim().charAt(0).toUpperCase() || user?.email?.trim().charAt(0).toUpperCase() || 'U';

  return (
    <div className="page-container max-w-4xl space-y-6 pb-12">

      <PageHeader
        title="Profile & Settings"
        subtitle="Manage your account information, education background, and resume documents."
      />

      {/* Global alerts */}
      {successMessage && (
        <AlertBanner type="success" message={successMessage} onDismiss={() => setSuccessMessage('')} />
      )}
      {errorMessage && (
        <AlertBanner type="error" message={errorMessage} onDismiss={() => setErrorMessage('')} />
      )}

      {/* ── Profile avatar banner ── */}
      <SectionCard>
        <div className="flex items-center gap-5">
          <div className="w-16 h-16 rounded-2xl bg-indigo-600 flex items-center justify-center text-2xl font-bold text-white flex-shrink-0 shadow-md shadow-indigo-500/30">
            {initial}
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">{user?.name || 'Your Name'}</h2>
            <p className="text-sm text-slate-400">{user?.email || ''}</p>
            {user?.experience_level && (
              <span className="inline-flex mt-1 items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-950/80 text-indigo-300 border border-indigo-700/50">
                {user.experience_level}
              </span>
            )}
          </div>
        </div>
      </SectionCard>

      {/* ── Resume Section ── */}
      <SectionCard title="Resume & Documents">
        {resumeMessage && <div className="mb-4"><AlertBanner type="success" message={resumeMessage} onDismiss={() => setResumeMessage('')} /></div>}
        {resumeError && <div className="mb-4"><AlertBanner type="error" message={resumeError} onDismiss={() => setResumeError('')} /></div>}

        {resumeInfo ? (
          <div className="space-y-5">
            {/* Uploaded file card */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 p-5 bg-slate-900 border border-slate-800 rounded-2xl">
              <div className="p-3 bg-indigo-950/80 text-indigo-400 border border-indigo-700/50 rounded-xl flex-shrink-0">
                <FileCheck size={24} aria-hidden="true" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-bold text-white truncate">{resumeInfo.filename}</p>
                  <span className="badge badge-success flex-shrink-0">Active</span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  {resumeInfo.file_type} · {formatFileSize(resumeInfo.size)}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button onClick={handleDownloadResume} className="btn-secondary text-xs py-1.5 px-3">
                  <Download size={13} /> Download
                </button>
                <button
                  onClick={handleAnalyzeResume}
                  disabled={isAnalyzing}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold transition disabled:opacity-50"
                >
                  {isAnalyzing ? <><Loader2 size={13} className="animate-spin" /> Analyzing…</> : <><Sparkles size={13} /> Analyze</>}
                </button>
                <button onClick={handleDeleteResume} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/60 rounded-lg text-xs font-semibold transition">
                  <Trash2 size={13} /> Delete
                </button>
              </div>
            </div>

            {/* Replace resume */}
            <div>
              <label className="form-label text-xs uppercase tracking-wider text-slate-400">Replace current resume:</label>
              <div className="flex items-center gap-3 mt-1">
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileSelect}
                  className="block text-xs text-slate-400 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 cursor-pointer"
                />
                {selectedFile && (
                  <button
                    type="button"
                    onClick={handleUploadResume}
                    disabled={isUploading}
                    className="btn-primary text-xs py-2 flex-shrink-0"
                  >
                    {isUploading ? <><Loader2 size={13} className="animate-spin" /> Uploading…</> : 'Upload'}
                  </button>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* Upload new resume */
          <div className="border-2 border-dashed border-slate-700 rounded-2xl p-8 text-center space-y-4 bg-slate-900/40">
            <div className="mx-auto w-12 h-12 bg-indigo-950/80 text-indigo-400 border border-indigo-700/50 rounded-2xl flex items-center justify-center">
              <Upload size={22} aria-hidden="true" />
            </div>
            <div>
              <p className="font-bold text-white">Upload Your Resume</p>
              <p className="text-xs text-slate-400 mt-1">PDF or Word (.docx) · Max 5 MB</p>
            </div>
            <div className="flex flex-col items-center gap-3">
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileSelect}
                className="block text-xs text-slate-400 file:mr-4 file:py-2 file:px-5 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700 cursor-pointer"
              />
              {selectedFile && (
                <button
                  type="button"
                  onClick={handleUploadResume}
                  disabled={isUploading}
                  className="btn-primary text-sm"
                >
                  {isUploading ? <><Loader2 size={15} className="animate-spin" /> Uploading…</> : 'Confirm Upload'}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Analysis result panel */}
        {analysisResult && (
          <div className="mt-5 p-5 bg-indigo-950/30 border border-indigo-800/50 rounded-2xl space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles size={18} className="text-indigo-400" />
              <h4 className="font-bold text-indigo-200">AI Resume Analysis</h4>
            </div>
            {analysisResult.extracted ? (
              <>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Review the extracted data below. Uncheck anything you don't want to apply.
                </p>
                <div className="space-y-3 bg-slate-900 p-4 rounded-xl border border-indigo-900/50 text-sm">
                  {analysisResult.skills?.length > 0 && (
                    <label className="flex items-start gap-3 cursor-pointer">
                      <input type="checkbox" checked={applyCheckboxes.skills} onChange={e => setApplyCheckboxes({ ...applyCheckboxes, skills: e.target.checked })} className="mt-1 accent-indigo-500 rounded" />
                      <div>
                        <span className="font-semibold text-white">Add Extracted Skills:</span>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {analysisResult.skills.map((s, i) => (
                            <span key={i} className="px-2 py-0.5 bg-indigo-950/80 text-indigo-300 border border-indigo-700/50 text-xs font-medium rounded-md">{s}</span>
                          ))}
                        </div>
                      </div>
                    </label>
                  )}
                  {analysisResult.education && (
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input type="checkbox" checked={applyCheckboxes.education} onChange={e => setApplyCheckboxes({ ...applyCheckboxes, education: e.target.checked })} className="accent-indigo-500 rounded" />
                      <span className="text-slate-300"><strong className="text-white">Education: </strong>{analysisResult.education}</span>
                    </label>
                  )}
                  {analysisResult.target_role && (
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input type="checkbox" checked={applyCheckboxes.target_role} onChange={e => setApplyCheckboxes({ ...applyCheckboxes, target_role: e.target.checked })} className="accent-indigo-500 rounded" />
                      <span className="text-slate-300"><strong className="text-white">Target Role: </strong>{analysisResult.target_role}</span>
                    </label>
                  )}
                </div>
                <div className="flex justify-end gap-3">
                  <button type="button" onClick={() => setAnalysisResult(null)} className="btn-secondary text-xs">Dismiss</button>
                  <button type="button" onClick={handleApplySuggestions} className="btn-primary text-xs">Apply Suggestions</button>
                </div>
              </>
            ) : (
              <p className="text-slate-300 text-xs">{analysisResult.message}</p>
            )}
          </div>
        )}
      </SectionCard>

      {/* ── Profile Form ── */}
      <form onSubmit={handleSubmit} noValidate>
        <div className="space-y-5">
          {/* Account Information */}
          <SectionCard title="Account Information">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <Field label="Full Name *">
                <input
                  type="text" name="name" required placeholder="Alex Johnson"
                  value={formData.name} onChange={handleChange} className="form-input"
                />
              </Field>
              <Field label="Email Address *">
                <input
                  type="email" name="email" required placeholder="you@example.com"
                  value={formData.email} onChange={handleChange} className="form-input"
                />
              </Field>
              <Field label="Phone Number">
                <input
                  type="text" name="phone" placeholder="+1 (555) 000-0000"
                  value={formData.phone} onChange={handleChange} className="form-input"
                />
              </Field>
            </div>
          </SectionCard>

          {/* Education & Background */}
          <SectionCard title="Education & Experience">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <Field label="Education Level">
                <input
                  type="text" name="education" placeholder="Bachelor's Degree"
                  value={formData.education} onChange={handleChange} className="form-input"
                />
              </Field>
              <Field label="Experience Level">
                <select name="experience_level" value={formData.experience_level} onChange={handleChange} className="form-select">
                  <option value="Entry Level">Entry Level</option>
                  <option value="Mid Level">Mid Level</option>
                  <option value="Senior Level">Senior Level</option>
                </select>
              </Field>
              <Field label="College / University">
                <input
                  type="text" name="college" placeholder="e.g. MIT, Stanford…"
                  value={formData.college} onChange={handleChange} className="form-input"
                />
              </Field>
              <Field label="Degree / Major">
                <input
                  type="text" name="degree" placeholder="B.S. Computer Science"
                  value={formData.degree} onChange={handleChange} className="form-input"
                />
              </Field>
            </div>
          </SectionCard>

          {/* Career & Skills */}
          <SectionCard title="Career & Technical Profile">
            <div className="grid grid-cols-1 gap-5">
              <Field label="Target Role">
                <input
                  type="text" name="target_role" placeholder="e.g. Software Developer, Data Scientist"
                  value={formData.target_role} onChange={handleChange} className="form-input"
                />
              </Field>
              <Field label="Skills (comma-separated)">
                <textarea
                  name="skills" rows={3}
                  placeholder="e.g. Python, React, SQL, FastAPI, Machine Learning"
                  value={formData.skills} onChange={handleChange}
                  className="form-input resize-none"
                />
              </Field>
            </div>

            {/* Save button */}
            <div className="flex justify-end pt-5 mt-2 border-t border-slate-100">
              <button
                type="submit"
                disabled={isSaving}
                className="btn-primary px-8 py-3"
              >
                {isSaving ? (
                  <><Loader2 size={17} className="animate-spin" /> Saving…</>
                ) : (
                  <><Save size={17} /> Save Profile</>
                )}
              </button>
            </div>
          </SectionCard>
        </div>
      </form>
    </div>
  );
};

export default ProfilePage;
