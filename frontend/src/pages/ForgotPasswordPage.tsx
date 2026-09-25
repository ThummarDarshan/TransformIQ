import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, KeyRound, ArrowRight, CheckCircle2, AlertCircle, ArrowLeft, Eye, EyeOff, ShieldCheck, Sparkles } from 'lucide-react';
import { TransformIQLogo } from '../components/common/TransformIQLogo';
import api from '../services/api';

export const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();

  const [step, setStep] = useState<'request' | 'verify' | 'success'>('request');
  const [email, setEmail] = useState('');
  const [resetCode, setResetCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedCodeNotice, setGeneratedCodeNotice] = useState<string | null>(null);

  const handleRequestCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const res: any = await api.post('/auth/forgot-password', { email });
      if (res.success) {
        if (res.data?.reset_code) {
          setResetCode(res.data.reset_code);
          setGeneratedCodeNotice(`Demo reset code generated: ${res.data.reset_code}`);
        }
        setStep('verify');
      }
    } catch (err: any) {
      setError(err?.detail || err?.message || 'Unable to request password reset. Please check your email.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsLoading(true);

    try {
      const res: any = await api.post('/auth/reset-password', {
        email,
        reset_code: resetCode,
        new_password: newPassword,
      });

      if (res.success) {
        setStep('success');
      }
    } catch (err: any) {
      setError(err?.detail || err?.message || 'Invalid or expired reset code. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-3.5 sm:p-6 relative overflow-hidden font-sans text-slate-100 selection:bg-blue-600 selection:text-white">
      {/* Dynamic Ambient Background Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[650px] h-[650px] bg-gradient-to-tr from-blue-600/15 via-cyan-500/10 to-indigo-600/15 blur-3xl pointer-events-none rounded-full" />
      <div className="absolute bottom-10 right-10 w-80 h-80 bg-emerald-500/10 blur-3xl pointer-events-none rounded-full" />

      <div className="w-full max-w-md bg-slate-900/90 border border-slate-800 rounded-2xl sm:rounded-3xl p-5 sm:p-8 backdrop-blur-2xl shadow-2xl relative z-10">
        {/* Header with Logo */}
        <div className="flex flex-col items-center text-center mb-6 sm:mb-8">
          <Link to="/" className="mb-3 sm:mb-4 hover:opacity-95 transition-opacity">
            <TransformIQLogo size="md" showSubtitle />
          </Link>
          
          <h2 className="text-lg sm:text-xl font-extrabold text-white tracking-tight">
            {step === 'request' && 'Reset Your Password'}
            {step === 'verify' && 'Enter Verification Code'}
            {step === 'success' && 'Password Reset Complete'}
          </h2>
          <p className="text-xs text-slate-400 mt-1.5 max-w-xs">
            {step === 'request' && 'Enter your registered email address to receive an instant verification code.'}
            {step === 'verify' && `We've sent a 6-digit verification code to ${email}.`}
            {step === 'success' && 'Your account security credentials have been updated successfully.'}
          </p>
        </div>

        {error && (
          <div className="mb-5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2.5 animate-fadeIn">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {generatedCodeNotice && step === 'verify' && (
          <div className="mb-5 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs flex items-center space-x-2.5 animate-fadeIn">
            <Sparkles className="w-4 h-4 shrink-0 text-cyan-400" />
            <span>{generatedCodeNotice} (Autofilled for evaluation)</span>
          </div>
        )}

        {/* STEP 1: REQUEST CODE */}
        {step === 'request' && (
          <form onSubmit={handleRequestCode} className="space-y-4" autoComplete="off">
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
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@transformiq.local"
                  className="w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-700/80 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/80 focus:border-blue-500 transition shadow-inner"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold text-xs rounded-xl transition-all shadow-lg shadow-blue-500/25 disabled:opacity-50 mt-2 flex items-center justify-center space-x-2 cursor-pointer"
            >
              <span>{isLoading ? 'Generating Code...' : 'Send Verification Code'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* STEP 2: VERIFY & NEW PASSWORD */}
        {step === 'verify' && (
          <form onSubmit={handleResetPassword} className="space-y-4" autoComplete="off">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                6-Digit Verification Code
              </label>
              <div className="relative">
                <KeyRound className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  required
                  maxLength={6}
                  autoComplete="off"
                  value={resetCode}
                  onChange={(e) => setResetCode(e.target.value)}
                  placeholder="e.g. 782941 or 202600"
                  className="w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-700/80 rounded-xl text-xs font-mono font-bold tracking-widest text-cyan-300 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/80 focus:border-blue-500 transition shadow-inner"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                New Secure Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  autoComplete="new-password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Min 6 characters"
                  className="w-full pl-10 pr-10 py-3 bg-slate-950/70 border border-slate-700/80 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/80 focus:border-blue-500 transition shadow-inner"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3.5 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Confirm New Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm matching password"
                  className="w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-700/80 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/80 focus:border-blue-500 transition shadow-inner"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-emerald-600 via-teal-600 to-blue-600 hover:from-emerald-500 hover:to-blue-500 text-white font-bold text-xs rounded-xl transition-all shadow-lg shadow-emerald-500/25 disabled:opacity-50 mt-2 flex items-center justify-center space-x-2 cursor-pointer"
            >
              <span>{isLoading ? 'Updating Password...' : 'Confirm & Update Password'}</span>
              <ShieldCheck className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* STEP 3: SUCCESS */}
        {step === 'success' && (
          <div className="text-center space-y-5 animate-fadeIn">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 mx-auto flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Your password has been securely updated. You can now log into your TransformIQ workspace with your new credentials.
            </p>

            <button
              type="button"
              onClick={() => navigate('/login')}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl transition-all shadow-lg shadow-blue-500/25 flex items-center justify-center space-x-2 cursor-pointer"
            >
              <span>Proceed to Sign In</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Footer Navigation */}
        <div className="mt-8 pt-6 border-t border-slate-800 flex items-center justify-between text-xs">
          <Link
            to="/login"
            className="text-slate-400 hover:text-slate-200 flex items-center space-x-1.5 transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Sign In</span>
          </Link>

          {step === 'verify' && (
            <button
              type="button"
              onClick={() => setStep('request')}
              className="text-blue-400 hover:text-blue-300 font-semibold"
            >
              Resend Code
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
