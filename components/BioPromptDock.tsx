import React, { useState } from 'react';
import { ArrowUp, Sparkles, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useBioChat } from '@/lib/bio-chat-context';
import { useTheme } from '@/lib/theme-context';

interface BioPromptDockProps {
  selectedStructureName?: string;
}

export default function BioPromptDock({ selectedStructureName }: BioPromptDockProps) {
  const { sendQuery, loading, currentQuery, setIsSidebarOpen } = useBioChat();
  const { t, language } = useTheme();
  const [input, setInput] = useState('');

  const handleSubmit = async (queryText?: string) => {
    const q = (queryText ?? input).trim();
    if (!q || loading) return;
    setInput('');
    await sendQuery(q);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  // If loading, dock reduces to a sleek, compact status pill
  if (loading) {
    return (
      <div
        className="bio-dock-loading-pill"
        onClick={() => setIsSidebarOpen(true)}
        role="status"
        title="Click to view ongoing answer in sidebar"
      >
        <Loader2 size={16} className="animate-spin text-[#458a85]" />
        <span className="bio-dock-loading-text">
          {t.dockSearching} <em>"{currentQuery || 'Query'}..."</em>
        </span>
        <span className="bio-dock-loading-badge">{t.sidebarOpenBadge}</span>
      </div>
    );
  }

  return (
    <div className="bio-dock-wrapper">
      {/* Quick suggestions or contextual prompt */}
      <div className="bio-dock-suggestions">
        {selectedStructureName ? (
          <button
            type="button"
            className="bio-dock-chip is-context"
            onClick={() => handleSubmit(
              language === 'hi'
                ? `मानव शरीर में ${selectedStructureName} की संरचना और कार्य समझाइए`
                : `Explain the structure and function of the ${selectedStructureName} in the human body`
            )}
          >
            <Sparkles size={12} className="text-[#458a85]" />
            <span>{t.chatAsk3dFocus} <strong>{selectedStructureName}</strong></span>
          </button>
        ) : null}
        {t.quickPrompts.slice(0, 3).map((prompt, i) => (
          <button
            key={i}
            type="button"
            className="bio-dock-chip"
            onClick={() => handleSubmit(prompt)}
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Main ChatGPT-style Prompt Input Bar */}
      <div className="bio-prompt-bar">
        <div className="bio-prompt-prefix" onClick={() => setIsSidebarOpen(true)} title="Open Bio AI Sidebar">
          <Sparkles size={16} className="text-[#458a85]" />
          <span className="bio-prompt-model-tag">{t.dockModelTag}</span>
        </div>

        <input
          type="text"
          className="bio-prompt-input"
          placeholder={
            selectedStructureName
              ? (language === 'hi' ? `${selectedStructureName} या जीव विज्ञान के बारे में कुछ भी पूछें...` : `Ask anything about ${selectedStructureName} or biology...`)
              : t.dockPlaceholder
          }
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          aria-label="Ask biology question"
        />

        <Button
          type="button"
          className="bio-prompt-send-btn"
          onClick={() => handleSubmit()}
          disabled={!input.trim()}
          aria-label="Send query"
        >
          <ArrowUp size={16} />
        </Button>
      </div>
    </div>
  );
}
