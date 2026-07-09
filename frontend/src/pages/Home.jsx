import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Shield, Cpu, Zap, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const Home = () => {
  const { user } = useAuth();

  return (
    <div className="relative overflow-hidden min-h-[90vh]">
      
      {/* Background glow orbs */}
      <div className="absolute top-20 left-1/4 w-[400px] h-[400px] bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-20 right-1/4 w-[450px] h-[450px] bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Hero Section */}
      <div className="max-w-5xl mx-auto px-4 pt-16 pb-20 text-center relative z-10">
        
        {/* Banner Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-8 animate-pulse-slow">
          <Zap className="w-3.5 h-3.5" /> Introducing Veritas AI RAG 2.0
        </div>

        {/* Main Title */}
        <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight mb-8">
          Deep Web Research,
          <span className="block mt-2 bg-gradient-to-r from-indigo-400 via-indigo-300 to-cyan-300 bg-clip-text text-transparent">
            Synthesized Instantly.
          </span>
        </h1>

        {/* Subtitle */}
        <p className="max-w-2xl mx-auto text-base sm:text-lg md:text-xl text-slate-400 mb-10 leading-relaxed">
          Veritas AI is a high-speed, secure, and production-ready RAG agent. It searches, extracts, ranks, and synthesizes answers using Gemini. Fully optimized for a 512 MB memory footprint.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
          {user ? (
            <Link
              to="/research"
              className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl text-base transition btn-premium glow-hover flex items-center gap-2"
            >
              Enter Research Workspace
              <ArrowRight className="w-5 h-5" />
            </Link>
          ) : (
            <>
              <Link
                to="/signup"
                className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl text-base transition btn-premium glow-hover flex items-center gap-2 w-full sm:w-auto justify-center"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/login"
                className="px-8 py-4 bg-[#121222] hover:bg-[#1a1a32] text-slate-200 border border-slate-800 hover:border-slate-700 font-semibold rounded-xl text-base transition w-full sm:w-auto justify-center"
              >
                Sign In
              </Link>
            </>
          )}
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          
          <div className="glass-panel p-6 rounded-2xl border-white/5 relative group hover:border-indigo-500/30 transition duration-300">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4 group-hover:scale-105 transition">
              <Search className="w-5 h-5 text-indigo-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100 mb-2">Transient BM25 Search</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              We rank scraped content segments in memory via keyword density. Zero database load, lightning fast retrieval.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl border-white/5 relative group hover:border-indigo-500/30 transition duration-300">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-4 group-hover:scale-105 transition">
              <Cpu className="w-5 h-5 text-cyan-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100 mb-2">Memory-Optimized Engine</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Engineered without heavy dependencies (PyTorch/Transformers) to easily deploy on Render's 512 MB free tier.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl border-white/5 relative group hover:border-indigo-500/30 transition duration-300">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4 group-hover:scale-105 transition">
              <Shield className="w-5 h-5 text-indigo-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100 mb-2">Military-Grade Security</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Complete cookie-based HttpOnly JWT sessions, Argon2 hashing, rate limiting, and SSRF scrapers protect your profile.
            </p>
          </div>

        </div>

      </div>
    </div>
  );
};

export default Home;
