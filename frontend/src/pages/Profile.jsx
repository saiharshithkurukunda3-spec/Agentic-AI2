import React from 'react';
import { User, Mail, Calendar, ShieldCheck, Database, KeyRound } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const Profile = () => {
  const { user } = useAuth();

  if (!user) return null;

  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="flex items-center gap-4 mb-8">
        <div className="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center border border-indigo-500/30">
          <User className="w-6 h-6 text-indigo-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-100">My Profile</h1>
          <p className="text-slate-400 text-sm">Manage your session and settings</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* User Card */}
        <div className="md:col-span-2 glass-panel p-8 rounded-2xl border-white/5 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-600/5 rounded-full blur-2xl pointer-events-none" />
          
          <h2 className="text-xl font-bold text-slate-200 mb-6 flex items-center gap-2">
            Account Details
          </h2>

          <div className="space-y-6">
            <div className="flex items-center justify-between py-3 border-b border-white/5">
              <div className="flex items-center gap-3 text-slate-400 text-sm">
                <User className="w-4 h-4 text-indigo-400" />
                <span>Username</span>
              </div>
              <span className="text-slate-200 font-semibold">{user.username}</span>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-white/5">
              <div className="flex items-center gap-3 text-slate-400 text-sm">
                <Mail className="w-4 h-4 text-indigo-400" />
                <span>Email Address</span>
              </div>
              <span className="text-slate-200 font-semibold">{user.email}</span>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-white/5">
              <div className="flex items-center gap-3 text-slate-400 text-sm">
                <Calendar className="w-4 h-4 text-indigo-400" />
                <span>Member Since</span>
              </div>
              <span className="text-slate-200 font-semibold">{formatDate(user.created_at || new Date())}</span>
            </div>
            
            <div className="flex items-center justify-between py-3">
              <div className="flex items-center gap-3 text-slate-400 text-sm">
                <Database className="w-4 h-4 text-indigo-400" />
                <span>Account ID</span>
              </div>
              <span className="text-slate-500 font-mono text-xs">{user._id || user.id}</span>
            </div>
          </div>
        </div>

        {/* Security / Stats Card */}
        <div className="glass-panel p-6 rounded-2xl border-white/5 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              Security Check
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Your session is secured using HttpOnly cookies to defend against cookie stealing (XSS attacks). Passwords are encrypted using modern Argon2.
            </p>
            <div className="space-y-3">
              <div className="p-3 bg-emerald-500/5 border border-emerald-500/10 rounded-xl flex items-center gap-2 text-emerald-300 text-xs">
                <ShieldCheck className="w-4 h-4" />
                <span>HttpOnly Cookies Enabled</span>
              </div>
              <div className="p-3 bg-emerald-500/5 border border-emerald-500/10 rounded-xl flex items-center gap-2 text-emerald-300 text-xs">
                <KeyRound className="w-4 h-4" />
                <span>Argon2 Hash Hashing Active</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/5 text-center text-xs text-slate-500">
            VERITAS AI Engine 2.0
          </div>
        </div>

      </div>
    </div>
  );
};

export default Profile;
