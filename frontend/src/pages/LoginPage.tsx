import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  Mail, 
  Lock, 
  AlertCircle, 
  ArrowRight, 
  Eye, 
  EyeOff, 
  Crown, 
  Target, 
  BarChart3, 
  Landmark, 
  Zap,
  CheckCircle2
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { TransformIQLogo } from '../components/common/TransformIQLogo';

interface DemoAccount {
  role: string;
  badge: string;
  name: string;
  email: string;
  password: string;
  icon: React.ReactNode;
  color: string;
  capabilities: string;
}

const DEMO_ACCOUNTS: DemoAccount[] = [
  {
    role: 'ADMIN',
    badge: '👑 ADMIN',
    name: 'Sarah Connor',
    email: 'admin@transformiq.local',
    password: 'TransformIQ@2026',
    icon: <Crown className="w-4 h-4 text-amber-400" />,
    color: 'text-amber-400',
    capabilities: 'System settings, user administration, token analytics, audit logs',
  },
  {
    role: 'PROJECT OWNER',
    badge: '🎯 PROJECT OWNER',
    name: 'Elena Rostova',
    email: 'owner@transformiq.local',
    password: 'TransformIQ@2026',
    icon: <Target className="w-4 h-4 text-rose-400" />,
    color: 'text-rose-400',
    capabilities: 'Full project lifecycle, scope approval, team assignment',
  },
  {
    role: 'BUSINESS ANALYST',
    badge: '📊 BUSINESS ANALYST',
    name: 'Priya Sharma',
    email: 'analyst@transformiq.local',
    password: 'TransformIQ@2026',
    icon: <BarChart3 className="w-4 h-4 text-emerald-400" />,
    color: 'text-emerald-400',
    capabilities: 'Problem discovery, stakeholder analysis, 8-dimension gap matrix',
  },
  {
    role: 'SOLUTION ARCHITECT',
    badge: '🏛️ SOLUTION ARCHITECT',
    name: 'David Chen',
    email: 'architect@transformiq.local',
    password: 'TransformIQ@2026',
    icon: <Landmark className="w-4 h-4 text-cyan-400" />,
    color: 'text-cyan-400',
    capabilities: 'React Flow architecture, BPMN workflows, PostgreSQL DDL, OpenAPI',
  },
];

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading, user, token, role } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeQuickFill, setActiveQuickFill] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && user && token) {
      if (role?.toUpperCase() === 'ADMIN') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    }
  }, [isLoading, user, token, role, navigate]);

  const handleQuickFill = (acc: DemoAccount) => {
    setEmail(acc.email);
    setPassword(acc.password);
    setActiveQuickFill(acc.email);
    setError(null);
  };

  const handleQuickLogin = async (acc: DemoAccount) => {
    setEmail(acc.email);
    setPassword(acc.password);
    setActiveQuickFill(acc.email);
    setError(null);
    try {
      const loggedUser = await login(acc.email, acc.password);
      const from = (location.state as any)?.from?.pathname;
      if (from && from !== '/login') {
        navigate(from, { replace: true });
      } else if (loggedUser?.role?.toUpperCase() === 'ADMIN') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    } catch (err: any) {
      setError(err?.detail || err?.message || 'Invalid credentials. Please check your corporate email and password.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const loggedUser = await login(email, password);
      const from = (location.state as any)?.from?.pathname;
      if (from && from !== '/login') {
        navigate(from, { replace: true });
      } else if (loggedUser?.role?.toUpperCase() === 'ADMIN') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    } catch (err: any) {
      setError(err?.detail || err?.message || 'Invalid credentials. Please check your corporate email and password.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-3.5 sm:p-6 relative overflow-hidden font-sans text-slate-100 selection:bg-blue-600 selection:text-white">
      {/* High-Tech Ambient Glowing Backdrops */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-gradient-to-tr from-blue-600/15 via-cyan-500/10 to-indigo-600/15 blur-3xl pointer-events-none rounded-full" />
      <div className="absolute bottom-10 left-10 w-96 h-96 bg-purple-600/10 blur-3xl pointer-events-none rounded-full" />

      <div className="w-full max-w-xl bg-slate-900/90 border border-slate-800/80 rounded-2xl sm:rounded-3xl p-5 sm:p-8 backdrop-blur-2xl shadow-2xl relative z-10 my-6">
        {/* Header with Logo */}
        <div className="flex flex-col items-center text-center mb-6 sm:mb-8">
          <Link to="/" className="mb-3 sm:mb-4 hover:opacity-95 transition-opacity">
            <TransformIQLogo size="md" showSubtitle />
          </Link>
          <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">Sign In to Your Workspace</h2>
          <p className="text-xs text-slate-400 mt-1">Enterprise Business Transformation AI Platform</p>
        </div>

        {error && (
          <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2.5 animate-fadeIn">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Corporate Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="email"
                required
                autoComplete="off"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setActiveQuickFill(null);
                }}
                placeholder="you@company.com"
                className="w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-700/80 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/80 focus:border-blue-500 transition shadow-inner"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-semibold text-slate-300">Password</label>
              <Link
                to="/forgot-password"
                className="text-[11px] text-blue-400 hover:text-blue-300 transition font-medium"
              >
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                autoComplete="new-password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setActiveQuickFill(null);
                }}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-10 py-3 bg-slate-950/70 border border-slate-700/80 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/80 focus:border-blue-500 transition shadow-inner"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3.5 text-slate-500 hover:text-slate-300 cursor-pointer"
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold text-xs rounded-xl transition-all shadow-lg shadow-blue-500/25 disabled:opacity-50 mt-2 flex items-center justify-center space-x-2 cursor-pointer active:scale-[0.99]"
          >
            <span>{isLoading ? 'Authenticating...' : 'Sign In to Platform'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Accounts Quick-Fill Section */}
        <div className="mt-6 pt-5 border-t border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-1.5">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-300">
                Quick Demo Access (Click to Fill & Sign In)
              </span>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Password: TransformIQ@2026</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {DEMO_ACCOUNTS.map((acc) => {
              const isSelected = activeQuickFill === acc.email || email === acc.email;
              return (
                <div
                  key={acc.email}
                  onClick={() => handleQuickFill(acc)}
                  className={`group relative p-3 rounded-xl border text-left transition-all duration-200 cursor-pointer ${
                    isSelected
                      ? 'bg-slate-800/90 border-blue-500/70 ring-1 ring-blue-500/50 shadow-md shadow-blue-500/10'
                      : 'bg-slate-950/60 border-slate-800/80 hover:bg-slate-800/50 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="p-1 rounded-md bg-slate-900 border border-slate-800 shrink-0">
                        {acc.icon}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center space-x-1.5">
                          <span className="text-xs font-bold text-white tracking-tight">
                            {acc.role}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 font-mono truncate mt-0.5">
                          {acc.email}
                        </p>
                      </div>
                    </div>
                    {isSelected && (
                      <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0 mt-0.5 animate-fadeIn" />
                    )}
                  </div>

                  <p className="text-[10px] text-slate-400 mt-2 line-clamp-1 leading-relaxed">
                    {acc.capabilities}
                  </p>

                  <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex items-center justify-between">
                    <span className="text-[10px] text-slate-500 truncate">
                      {acc.name}
                    </span>
                    <button
                      type="button"
                      disabled={isLoading}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleQuickLogin(acc);
                      }}
                      className="text-[10px] font-semibold text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 group-hover:translate-x-0.5 transition-transform shrink-0"
                    >
                      <span>Instant Sign In</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          Need a new workspace?{' '}
          <Link to="/register" className="text-cyan-400 hover:text-cyan-300 hover:underline font-semibold">
            Register Organization
          </Link>
        </p>
      </div>
    </div>
  );
};
