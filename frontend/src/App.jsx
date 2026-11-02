import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from './context/AuthContext';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import DashboardPage from './pages/DashboardPage';
import ProfilePage from './pages/ProfilePage';
import InterviewSetupPage from './pages/InterviewSetupPage';
import ActiveInterviewPage from './pages/ActiveInterviewPage';
import InterviewResultPage from './pages/InterviewResultPage';
import InterviewHistoryPage from './pages/InterviewHistoryPage';
import CodingInterviewPage from './pages/CodingInterviewPage';
import DashboardLayout from './layouts/DashboardLayout';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div className="flex h-screen items-center justify-center">Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  return children;
};

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardLayout>
                <DashboardPage />
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/coding" element={
            <ProtectedRoute>
              <DashboardLayout>
                <CodingInterviewPage />
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/history" element={
            <ProtectedRoute>
              <DashboardLayout>
                <InterviewHistoryPage />
              </DashboardLayout>
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <DashboardLayout>
                <ProfilePage />
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/setup" element={
            <ProtectedRoute>
              <DashboardLayout>
                <InterviewSetupPage />
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/interview/:id" element={
            <ProtectedRoute>
              <DashboardLayout>
                <ActiveInterviewPage />
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/interview/:id/result" element={
            <ProtectedRoute>
              <DashboardLayout>
                <InterviewResultPage />
              </DashboardLayout>
            </ProtectedRoute>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
