import React, { useState, useEffect } from 'react';
import { Loader2, Search, Download, Network, Brain } from 'lucide-react';

const LoadingSpinner = () => {
  const [stage, setStage] = useState(0);

  // Cycle status stages every few seconds to show RAG pipeline steps dynamically
  useEffect(() => {
    const timer1 = setTimeout(() => setStage(1), 2500); // Scraping
    const timer2 = setTimeout(() => setStage(2), 5500); // Ranking
    const timer3 = setTimeout(() => setStage(3), 8000); // Synthesizing

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  const stages = [
    { text: "Crawling indices via DuckDuckGo...", icon: <Search className="w-4 h-4 text-indigo-400" /> },
    { text: "Downloading contents & applying SSRF checks...", icon: <Download className="w-4 h-4 text-cyan-400" /> },
    { text: "Running BM25 keyword scoring on text chunks...", icon: <Network className="w-4 h-4 text-indigo-400" /> },
    { text: "Synthesizing grounded answer using Gemini...", icon: <Brain className="w-4 h-4 text-pink-400" /> }
  ];

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      
      {/* Outer spinning element */}
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-full border-4 border-indigo-500/10 border-t-indigo-500 animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <Loader2 className="w-6 h-6 text-slate-400 animate-pulse" />
        </div>
      </div>

      <h3 className="text-lg font-bold text-slate-200 mb-2">Analyzing Request</h3>
      <p className="text-slate-400 text-sm max-w-sm mb-6 leading-relaxed">
        Our agent is executing a transient RAG pipeline to compile a grounded research synthesis.
      </p>

      {/* RAG pipeline steps display */}
      <div className="w-full max-w-xs bg-[#12121e] border border-brand-border rounded-2xl p-4 space-y-3.5 text-left">
        {stages.map((st, idx) => {
          const isActive = idx === stage;
          const isDone = idx < stage;
          
          return (
            <div
              key={idx}
              className={`flex items-center gap-3 text-xs transition duration-300 ${
                isActive ? 'text-slate-100 font-semibold' : isDone ? 'text-slate-500' : 'text-slate-600'
              }`}
            >
              <div className={`w-6 h-6 rounded-md flex items-center justify-center border transition ${
                isActive 
                  ? 'bg-indigo-500/10 border-indigo-500/30' 
                  : isDone 
                    ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400' 
                    : 'bg-white/5 border-white/5'
              }`}>
                {isDone ? '✓' : st.icon}
              </div>
              <span className="truncate">{st.text}</span>
            </div>
          );
        })}
      </div>
      
    </div>
  );
};

export default LoadingSpinner;
