import React from 'react';
import { Link2 } from 'lucide-react';

const SourceCard = ({ title, url, relevance_score }) => {
  // Extract domain name for the badge
  const getDomain = (urlStr) => {
    try {
      const hostname = new URL(urlStr).hostname;
      return hostname.replace('www.', '');
    } catch (e) {
      return 'Web Link';
    }
  };

  return (
    <div className="p-4 bg-[#12121e]/80 border border-brand-border rounded-2xl flex items-center justify-between gap-4 transition duration-300 hover:border-indigo-500/20 hover:bg-[#151525]">
      <div className="min-w-0">
        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
          <span className="px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-semibold tracking-wide uppercase">
            {getDomain(url)}
          </span>
          <span className="text-[10px] text-slate-500">
            Score: {relevance_score || 'N/A'}
          </span>
        </div>
        <h4 className="text-slate-200 font-semibold text-sm truncate" title={title}>
          {title}
        </h4>
        <p className="text-slate-500 text-xs truncate mt-0.5">{url}</p>
      </div>

      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="w-8 h-8 rounded-lg bg-white/5 border border-white/5 flex items-center justify-center text-slate-400 hover:text-indigo-400 hover:bg-indigo-500/10 hover:border-indigo-500/20 transition shrink-0"
        title="Open link"
      >
        <Link2 className="w-4.5 h-4.5" />
      </a>
    </div>
  );
};

export default SourceCard;
