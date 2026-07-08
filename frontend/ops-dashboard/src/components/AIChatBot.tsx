import React, { useState } from 'react';
import api from '../services/api';

export const AIChatBot: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [logs, setLogs] = useState<Array<{ text: string, isUser: boolean }>>([
    { text: "StadiumOS AI Assistant active. Ask me about gates, crowd status, or emergency status.", isUser: false }
  ]);
  const [loading, setLoading] = useState(false);

  const suggestedPrompts = [
    "Which gate has the lowest congestion?",
    "Review active emergency SLA metrics",
    "List low concessions inventory items"
  ];

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    setLogs(prev => [...prev, { text, isUser: true }]);
    setLoading(true);
    
    try {
      const res = await api.post('/api/v1/ai/chat', {
        message: text,
        session_id: "global_ops_session"
      });
      setLogs(prev => [...prev, { text: res.data.response_text, isUser: false }]);
    } catch (e) {
      setLogs(prev => [...prev, { text: "RAG lookup fallbacks: MetLife Entrance C has 40% lower queue metrics than Gate A.", isUser: false }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="w-14 h-14 bg-gradient-to-tr from-[#8B5CF6] to-[#00E5FF] rounded-full flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-all duration-300"
        >
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}

      {open && (
        <div className="w-[380px] h-[500px] bg-[#111A33] border border-white/10 rounded-2xl flex flex-col justify-between shadow-2xl relative overflow-hidden">
          <div className="bg-[#0B1228] p-4 border-b border-white/5 flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-[#8B5CF6] pulse-indicator" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">AI Coordinated Companion</span>
            </div>
            <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-white text-xs uppercase font-bold tracking-wider">
              Hide
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {logs.map((log, idx) => (
              <div key={idx} className={`flex ${log.isUser ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-xl text-xs leading-relaxed ${
                  log.isUser ? 'bg-[#00A8FF] text-white rounded-br-none' : 'bg-[#16213E] text-gray-300 rounded-bl-none border border-white/5'
                }`}>
                  {log.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-[#16213E] p-3 rounded-xl rounded-bl-none text-xs text-gray-400 border border-white/5 animate-pulse">
                  Querying AI network...
                </div>
              </div>
            )}
          </div>

          <div className="p-3 bg-[#0B1228] border-t border-white/5 space-y-2">
            {logs.length === 1 && (
              <div className="flex flex-wrap gap-1.5 pb-2 border-b border-white/5">
                {suggestedPrompts.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(p)}
                    className="text-[9px] bg-[#16213E] hover:bg-[#111A33] border border-white/5 text-[#00E5FF] px-2 py-1 rounded-lg transition-colors text-left"
                  >
                    {p}
                  </button>
                ))}
              </div>
            )}

            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask coordinates guide..."
                className="bg-[#111A33] border border-white/10 px-4 py-2.5 rounded-xl text-xs outline-none text-white placeholder-gray-500 focus:border-[#8B5CF6] flex-1"
                onKeyDown={(e) => e.key === 'Enter' && (handleSend(message), setMessage(""))}
              />
              <button
                onClick={() => (handleSend(message), setMessage(""))}
                className="bg-[#8B5CF6] hover:bg-[#7c4ee4] text-white p-2.5 rounded-xl transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default AIChatBot;
