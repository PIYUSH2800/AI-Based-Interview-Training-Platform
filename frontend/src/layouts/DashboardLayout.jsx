import React, { useContext, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import {
  LayoutDashboard,
  User,
  PlayCircle,
  LogOut,
  FileText,
  Code2,
  BrainCircuit,
  Menu,
  X,
  Zap,
} from 'lucide-react';
import api from '../services/api';

const navItems = [
  { name: 'Dashboard',  path: '/dashboard', icon: LayoutDashboard },
  { name: 'Practice',   path: '/setup',      icon: PlayCircle },
  { name: 'Coding',     path: '/coding',     icon: Code2 },
  { name: 'History',    path: '/history',    icon: FileText },
  { name: 'Profile',    path: '/profile',    icon: User },
];

const DashboardLayout = ({ children }) => {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();
  const [aiStatus, setAiStatus] = React.useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  React.useEffect(() => {
    api.get('/ai/status')
      .then(res => setAiStatus(res.data))
      .catch(() => setAiStatus(null));
  }, []);

  const initial = user?.name?.trim().charAt(0).toUpperCase()
    || user?.email?.trim().charAt(0).toUpperCase()
    || 'U';

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Brand */}
      <div className="px-6 pt-6 pb-5 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-indigo-500/30">
          <BrainCircuit size={18} className="text-white" />
        </div>
        <div className="leading-none">
          <p className="text-sm font-bold text-white tracking-tight">AI Interviewer</p>
          <p className="text-[10px] text-indigo-400 font-medium mt-0.5">Interview Training</p>
        </div>
      </div>

      {/* AI Status pill */}
      {aiStatus && (
        <div className="mx-4 mb-4 flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/60 border border-slate-700/50">
          <Zap size={13} className={aiStatus.active_mode === 'real' ? 'text-emerald-400' : 'text-slate-400'} />
          <span className="text-[11px] font-medium text-slate-400">AI Engine</span>
          <span className={`ml-auto text-[10px] font-bold px-2 py-0.5 rounded-full ${
            aiStatus.active_mode === 'real'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'bg-slate-700 text-slate-400 border border-slate-600'
          }`}>
            {aiStatus.active_mode === 'real' ? 'Gemini Live' : 'Mock Mode'}
          </span>
        </div>
      )}

      {/* Nav section label */}
      <p className="px-6 pb-2 text-[10px] font-bold uppercase tracking-widest text-slate-500">Navigation</p>

      {/* Nav items */}
      <nav className="flex-1 px-3 space-y-0.5" aria-label="Main navigation">
        {navItems.map(({ name, path, icon: Icon }) => {
          const isActive = location.pathname === path
            || (path === '/setup' && location.pathname.startsWith('/interview'));
          return (
            <Link
              key={name}
              to={path}
              onClick={() => setMobileOpen(false)}
              aria-current={isActive ? 'page' : undefined}
              className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon size={18} aria-hidden="true" />
              <span>{name}</span>
              {isActive && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-white/60" aria-hidden="true" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer: user + logout */}
      <div className="p-4 mt-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-2 py-2 rounded-xl bg-slate-800/50 mb-2">
          <div
            className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
            aria-hidden="true"
          >
            {initial}
          </div>
          <div className="overflow-hidden flex-1 min-w-0">
            <p className="text-sm font-semibold text-white truncate leading-none">{user?.name || 'User'}</p>
            <p className="text-[11px] text-slate-400 truncate mt-0.5">{user?.email || ''}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-red-400 hover:bg-slate-800 transition-all duration-150"
          aria-label="Logout"
        >
          <LogOut size={16} aria-hidden="true" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-60 flex-col bg-slate-900 border-r border-slate-800 flex-shrink-0 overflow-y-auto">
        <SidebarContent />
      </aside>

      {/* Mobile Overlay Sidebar */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 md:hidden" role="dialog" aria-modal="true" aria-label="Navigation menu">
          <div
            className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="absolute left-0 top-0 bottom-0 w-72 bg-slate-900 border-r border-slate-800 overflow-y-auto flex flex-col z-50 shadow-2xl">
            <button
              onClick={() => setMobileOpen(false)}
              className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white rounded-lg"
              aria-label="Close menu"
            >
              <X size={20} />
            </button>
            <SidebarContent />
          </aside>
        </div>
      )}

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Mobile top bar */}
        <header className="md:hidden flex items-center justify-between px-4 py-3 bg-slate-900 border-b border-slate-800 flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
              <BrainCircuit size={16} className="text-white" />
            </div>
            <span className="font-bold text-white text-sm">AI Interviewer</span>
          </div>
          <button
            onClick={() => setMobileOpen(true)}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
            aria-label="Open menu"
          >
            <Menu size={22} />
          </button>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8 animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
