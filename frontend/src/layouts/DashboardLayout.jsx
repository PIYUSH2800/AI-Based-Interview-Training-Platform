import React, { useContext } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { LayoutDashboard, User, PlayCircle, LogOut, FileText } from 'lucide-react';

const DashboardLayout = ({ children }) => {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();
  const [aiStatus, setAiStatus] = React.useState(null);

  React.useEffect(() => {
    api.get('/ai/status')
      .then(res => setAiStatus(res.data))
      .catch(() => setAiStatus(null));
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Practice', path: '/setup', icon: PlayCircle },
    { name: 'History', path: '/history', icon: FileText },
    { name: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col hidden md:flex">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-blue-500">AI Interviewer</h1>
        </div>
        <nav className="flex-1 px-4 space-y-2 mt-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive ? 'bg-blue-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <Icon size={20} />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-slate-800 space-y-3">
          {aiStatus && (
            <div className="flex items-center justify-between text-[11px] text-slate-400 px-2">
              <span className="font-medium">AI Engine:</span>
              <span className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                aiStatus.active_mode === 'real' 
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                  : 'bg-slate-800 text-slate-400 border border-slate-700'
              }`}>
                {aiStatus.active_mode === 'real' ? `Gemini (${aiStatus.model || 'Live'})` : 'Offline / Mock'}
              </span>
            </div>
          )}

          <div className="flex items-center space-x-3 px-2">
            <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-sm font-bold text-white shadow-sm flex-shrink-0">
              {user?.name ? user.name.trim().charAt(0).toUpperCase() : (user?.email ? user.email.trim().charAt(0).toUpperCase() : 'U')}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-semibold truncate text-white">{user?.name || 'User'}</p>
              <p className="text-xs text-slate-400 truncate">{user?.email || ''}</p>
            </div>
          </div>
          <button 
            onClick={logout}
            className="flex items-center space-x-3 text-slate-400 hover:text-red-400 px-4 py-2 w-full transition-colors rounded-lg hover:bg-slate-800"
          >
            <LogOut size={18} />
            <span className="font-medium text-sm">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile Header */}
        <header className="md:hidden bg-white border-b border-slate-200 p-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-blue-600">AI Interviewer</h1>
          <button onClick={logout} className="text-slate-500 hover:text-red-500">
            <LogOut size={24} />
          </button>
        </header>

        <div className="flex-1 overflow-auto p-6 md:p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
