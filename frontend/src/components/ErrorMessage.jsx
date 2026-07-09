import React from 'react';
import { ShieldAlert } from 'lucide-react';

const ErrorMessage = ({ message }) => {
  if (!message) return null;

  return (
    <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-2xl flex items-start gap-3 my-4">
      <ShieldAlert className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
      <div>
        <h4 className="text-sm font-bold text-red-200">Error Encountered</h4>
        <p className="text-xs text-red-300/90 mt-1 leading-relaxed">{message}</p>
      </div>
    </div>
  );
};

export default ErrorMessage;
