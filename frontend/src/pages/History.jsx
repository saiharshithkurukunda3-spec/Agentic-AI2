import React, { useState, useEffect } from 'react';
import { History as HistoryIcon, Trash2, Calendar, Link2, ChevronRight, ChevronDown, Loader2, ShieldAlert } from 'lucide-react';
import api from '../services/api';

const History = () => {
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedItem, setExpandedItem] = useState(null);

  // Load history records
  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/history');
      setHistoryItems(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to retrieve search history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // Delete history item
  const handleDelete = async (itemId, e) => {
    e.stopPropagation(); // Avoid triggering expand/collapse
    if (!window.confirm('Are you sure you want to delete this research record?')) return;

    try {
      await api.delete(`/history/${itemId}`);
      setHistoryItems((prev) => prev.filter((item) => item._id !== itemId));
      if (expandedItem === itemId) {
        setExpandedItem(null);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete history item.');
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const toggleExpand = (itemId) => {
    if (expandedItem === itemId) {
      setExpandedItem(null);
    } else {
      setExpandedItem(itemId);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center border border-indigo-500/30">
            <HistoryIcon className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-100">Research History</h1>
            <p className="text-slate-400 text-sm">Your private database of synthesized queries</p>
          </div>
        </div>
        <button
          onClick={fetchHistory}
          className="px-4 py-2 bg-[#121222] hover:bg-[#1a1a32] text-slate-300 border border-slate-800 rounded-xl text-sm transition"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <p className="text-sm text-red-200">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
          <span className="text-slate-400 text-sm">Loading history...</span>
        </div>
      ) : historyItems.length === 0 ? (
        <div className="glass-panel p-12 rounded-2xl border-white/5 text-center">
          <HistoryIcon className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-300 mb-2">No history records</h3>
          <p className="text-slate-500 text-sm max-w-sm mx-auto">
            You haven't run any research queries yet. Head to the workspace to get started!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {historyItems.map((item) => {
            const isExpanded = expandedItem === item._id;
            return (
              <div
                key={item._id}
                onClick={() => toggleExpand(item._id)}
                className="glass-panel rounded-2xl border-white/5 overflow-hidden transition cursor-pointer hover:border-indigo-500/20"
              >
                
                {/* Accordion Summary */}
                <div className="p-5 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 min-w-0">
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-slate-400 shrink-0" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-slate-400 shrink-0" />
                    )}
                    <div className="min-w-0">
                      <h3 className="text-slate-200 font-semibold truncate text-base">
                        {item.query}
                      </h3>
                      <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                        <Calendar className="w-3.5 h-3.5" />
                        <span>{formatDate(item.timestamp)}</span>
                        <span>•</span>
                        <span>{item.sources?.length || 0} Sources</span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={(e) => handleDelete(item._id, e)}
                    className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition shrink-0"
                    title="Delete item"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                {/* Accordion Body */}
                {isExpanded && (
                  <div className="px-5 pb-6 pt-2 border-t border-white/5 bg-[#12121e]/30">
                    <div className="prose prose-invert max-w-none mb-6">
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                        Synthesized Answer
                      </h4>
                      <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
                        {item.response}
                      </p>
                    </div>

                    {item.sources && item.sources.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                          Verified Sources
                        </h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {item.sources.map((src, idx) => (
                            <a
                              key={idx}
                              href={src.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              onClick={(e) => e.stopPropagation()} // Stop accordion toggling
                              className="p-3 bg-[#171727]/80 hover:bg-[#1f1f35] rounded-xl border border-white/5 hover:border-indigo-500/20 transition flex items-center justify-between gap-3 text-xs"
                            >
                              <div className="min-w-0">
                                <p className="text-slate-300 font-medium truncate">{src.title}</p>
                                <p className="text-slate-500 truncate mt-0.5">{src.url}</p>
                              </div>
                              <Link2 className="w-4 h-4 text-indigo-400 shrink-0" />
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default History;
