import React, { useState } from 'react';
import { Search, Sparkles, AlertCircle, Copy, Check, Info, ShieldAlert, Cpu } from 'lucide-react';
import api from '../services/api';
import SourceCard from '../components/SourceCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const Research = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    if (query.length > 250) {
      setError('Query exceeds the limit of 250 characters.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await api.post('/research/', { query: query.trim() });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during research synthesis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result?.answer) return;
    navigator.clipboard.writeText(result.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Color code relevance scores
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5';
    if (score >= 50) return 'text-amber-400 border-amber-500/20 bg-amber-500/5';
    return 'text-red-400 border-red-500/20 bg-red-500/5';
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      
      {/* Title */}
      <div className="flex flex-col items-center text-center mb-10">
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
          AI Research Workspace
        </h1>
        <p className="text-slate-400 text-sm mt-2 max-w-md">
          Enter a topic or research query to generate a grounded synthesis using transient RAG
        </p>
      </div>

      {/* Query Bar */}
      <form onSubmit={handleSearch} className="mb-10 max-w-3xl mx-auto">
        <div className="relative flex items-center">
          <input
            type="text"
            required
            maxLength={250}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            placeholder="E.g., What are the latest developments in ambient room-temperature superconductors?"
            className="w-full pl-5 pr-32 py-4 rounded-2xl glass-input text-slate-100 placeholder-slate-500 text-sm sm:text-base focus:ring-0 focus:outline-none"
          />
          <div className="absolute right-2 flex items-center gap-2">
            <span className="text-[10px] text-slate-600 hidden sm:inline">
              {query.length}/250
            </span>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-xl transition flex items-center gap-1.5 glow-hover btn-premium"
            >
              <Search className="w-4 h-4" />
              <span>Research</span>
            </button>
          </div>
        </div>
      </form>

      {/* Errors */}
      {error && (
        <div className="max-w-3xl mx-auto">
          <ErrorMessage message={error} />
        </div>
      )}

      {/* Loader */}
      {loading && <LoadingSpinner />}

      {/* Result Output */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-6">
          
          {/* Main Answer Area */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass-panel p-6 sm:p-8 rounded-2xl border-white/5 relative overflow-hidden">
              
              {/* Orb decorations */}
              <div className="absolute -top-12 -right-12 w-28 h-28 bg-indigo-600/5 rounded-full blur-2xl pointer-events-none" />
              
              {/* Header inside result card */}
              <div className="flex items-center justify-between pb-4 border-b border-white/5 mb-6">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  <h3 className="font-bold text-slate-200 text-lg">Synthesized Analysis</h3>
                </div>
                <button
                  onClick={handleCopy}
                  className="px-3 py-1.5 bg-[#171727] hover:bg-[#202038] border border-white/5 rounded-lg text-xs text-slate-400 hover:text-slate-200 transition flex items-center gap-1.5"
                  title="Copy to clipboard"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>

              {/* Answer Text */}
              <div className="prose prose-invert max-w-none">
                <p className="text-slate-300 text-sm sm:text-base leading-relaxed whitespace-pre-line">
                  {result.answer}
                </p>
              </div>

              {/* Grounded warning disclaimer */}
              <div className="mt-8 p-3 bg-white/5 rounded-xl flex gap-2 text-[11px] text-slate-500 border border-white/5">
                <Info className="w-4 h-4 shrink-0 text-slate-400" />
                <span>
                  This analysis is transiently generated strictly from the top web results retrieved at this moment. No claims are made beyond the referenced pages.
                </span>
              </div>

            </div>
          </div>

          {/* Sidebar (Sources & Metrics) */}
          <div className="space-y-6">
            
            {/* Relevance Score Card */}
            <div className="glass-panel p-6 rounded-2xl border-white/5 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">
                  Relevance Diagnostics
                </h3>
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-4xl font-extrabold text-white">{result.relevance_score}</span>
                  <span className="text-slate-500 text-sm">/ 100</span>
                </div>
                <div className="w-full bg-white/5 rounded-full h-2.5 mb-4">
                  <div
                    className="bg-indigo-500 h-2.5 rounded-full"
                    style={{ width: `${result.relevance_score}%` }}
                  />
                </div>
              </div>

              <div className={`p-4 rounded-xl border text-xs leading-relaxed ${getScoreColor(result.relevance_score)}`}>
                {result.relevance_score >= 80 ? (
                  <span>Excellent query alignment. The retrieved search content provided explicit, highly relevant answers.</span>
                ) : result.relevance_score >= 50 ? (
                  <span>Partial query alignment. The answer uses snippets and context, but sources may have gaps.</span>
                ) : (
                  <span>Weak query alignment. Scraped data was sparse or had low correspondence to the query.</span>
                )}
              </div>
            </div>

            {/* Sources List */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
                Verified Sources
              </h3>
              {result.sources && result.sources.length > 0 ? (
                result.sources.map((src, index) => (
                  <SourceCard
                    key={index}
                    title={src.title}
                    url={src.url}
                    relevance_score={src.relevance_score}
                  />
                ))
              ) : (
                <div className="p-4 bg-white/5 rounded-2xl border border-white/5 text-center text-xs text-slate-500">
                  No explicit sources referenced.
                </div>
              )}
            </div>

          </div>

        </div>
      )}

    </div>
  );
};

export default Research;
