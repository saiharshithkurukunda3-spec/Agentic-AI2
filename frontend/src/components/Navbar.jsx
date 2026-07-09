import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Compass, User, History, LogOut, Terminal, Sparkles } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <nav className="border-b border-brand-border bg-[#0a0a0f]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-9 h-9 rounded-lg bg-indigo-600/10 border border-indigo-500/30 flex items-center justify-center group-hover:border-indigo-500/60 transition">
            <Sparkles className="w-5 h-5 text-indigo-400 group-hover:text-indigo-300 transition" />
          </div>
          <span className="text-xl font-bold tracking-wider font-mono bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
            VERITAS AI
          </span>
        </Link>

        {/* Links */}
        <div className="flex items-center gap-2 sm:gap-4">
          {user ? (
            <>
              <Link
                to="/research"
                className="px-3.5 py-2 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition flex items-center gap-1.5"
              >
                <Compass className="w-4 h-4 text-indigo-400" />
                <span className="hidden sm:inline">Workspace</span>
              </Link>
              <Link
                to="/history"
                className="px-3.5 py-2 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition flex items-center gap-1.5"
              >
                <History className="w-4 h-4 text-indigo-400" />
                <span className="hidden sm:inline">History</span>
              </Link>
              <Link
                to="/profile"
                className="px-3.5 py-2 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition flex items-center gap-1.5"
              >
                <User className="w-4 h-4 text-indigo-400" />
                <span className="hidden sm:inline">Profile</span>
              </Link>
              
              <div className="h-4 w-px bg-white/10 mx-2" />
              
              <button
                onClick={handleLogout}
                className="px-3.5 py-2 rounded-xl text-sm font-medium text-red-400 hover:text-red-300 hover:bg-red-500/10 transition flex items-center gap-1.5"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Sign Out</span>
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="px-4 py-2 text-slate-300 hover:text-white text-sm font-medium transition"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl transition btn-premium glow-hover"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>

      </div>
    </nav>
  );
};

export default Navbar;
