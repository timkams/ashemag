import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  BookOpen,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  ArrowUpRight,
  ExternalLink,
  Bot,
  User,
  GraduationCap,
  Key,
  Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useBioChat } from '@/lib/bio-chat-context';
import { useTheme } from '@/lib/theme-context';

interface BioChatbotProps {
  selectedStructureName?: string;
}

export default function BioChatbot({ selectedStructureName }: BioChatbotProps) {
  const {
    messages,
    loading,
    sendQuery,
    resetChat,
    gradeFilter,
    setGradeFilter,
    apiKey,
    setApiKey
  } = useBioChat();
  const { t, language } = useTheme();

  const [input, setInput] = useState('');
  const [openCitationId, setOpenCitationId] = useState<string | null>(null);
  const [showAttribution, setShowAttribution] = useState(false);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [tempKey, setTempKey] = useState(apiKey);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    // Open the latest assistant message citation by default if citations exist
    const lastMsg = messages[messages.length - 1];
    if (lastMsg && lastMsg.sender === 'assistant' && lastMsg.citations?.length) {
      setOpenCitationId(lastMsg.id);
    }
  }, [messages]);

  const handleSend = async (queryText?: string) => {
    const q = (queryText ?? input).trim();
    if (!q || loading) return;
    if (!queryText) setInput('');
    await sendQuery(q);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  const saveKey = () => {
    setApiKey(tempKey.trim());
    setShowKeyModal(false);
  };

  return (
    <div className="bio-chatbot-container">
      {/* Top Header Bar */}
      <div className="bio-chat-header">
        <div className="bio-chat-title-group">
          <div className="eyebrow">
            <span className="status-dot animate-pulse" />
            {t.chatTitle}
          </div>
          <p className="bio-chat-sub">
            {apiKey ? t.chatSubtitleGrounded : t.chatSubtitleLocal}
          </p>
        </div>
        <div className="bio-header-actions">
          <Button
            variant="ghost"
            size="sm"
            className="bio-chat-key-btn"
            onClick={() => {
              setTempKey(apiKey);
              setShowKeyModal(!showKeyModal);
            }}
            title="Configure Gemini API Key"
            aria-label="Configure Gemini API Key"
          >
            <Key size={12} className={apiKey ? 'text-[#458a85]' : 'text-slate-400'} />
            <span>{apiKey ? 'API Key' : 'Add Key'}</span>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            className="bio-chat-reset-btn"
            onClick={resetChat}
            title="Reset conversation"
            aria-label="Reset chat"
          >
            <RotateCcw size={13} />
            <span>{t.chatClear}</span>
          </Button>
        </div>
      </div>

      {/* Gemini API Key configuration drawer */}
      {showKeyModal && (
        <div className="bio-key-config-box">
          <div className="bio-key-header">
            <span>Gemini API Key (Optional)</span>
            <button type="button" onClick={() => setShowKeyModal(false)} className="text-xs text-slate-400 hover:text-slate-600">✕</button>
          </div>
          <p className="bio-key-desc">
            Provide a Google Gemini API Key to enable generative AI synthesis over the central NCERT knowledge base. (Leave empty to use built-in textbook synthesis).
          </p>
          <div className="bio-key-input-row">
            <input
              type="password"
              className="bio-key-input"
              placeholder="AIzaSy..."
              value={tempKey}
              onChange={e => setTempKey(e.target.value)}
            />
            <Button size="sm" className="bio-key-save-btn" onClick={saveKey}>
              <Check size={13} /> Save
            </Button>
          </div>
        </div>
      )}

      {/* Grade Selector Tabs */}
      <div className="bio-grade-bar">
        <span className="bio-grade-label">
          <GraduationCap size={12} /> {t.chatClassLabel}
        </span>
        {[
          { label: t.chatAllClass, value: undefined },
          { label: '9th', value: 9 },
          { label: '10th', value: 10 },
          { label: '11th', value: 11 },
          { label: '12th', value: 12 }
        ].map(tab => (
          <button
            key={tab.label}
            type="button"
            className={`bio-grade-pill ${gradeFilter === tab.value ? 'active' : ''}`}
            onClick={() => setGradeFilter(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Contextual structure pill if active in 3D */}
      {selectedStructureName && (
        <div className="bio-context-pill-row">
          <button
            type="button"
            className="bio-context-pill"
            onClick={() => handleSend(
              language === 'hi'
                ? `मानव शरीर में ${selectedStructureName} की संरचना और कार्य समझाइए`
                : `Explain the structure and function of the ${selectedStructureName} in the human body`
            )}
          >
            <Sparkles size={12} />
            <span>{t.chatAsk3dFocus} <strong>{selectedStructureName}</strong></span>
          </button>
        </div>
      )}

      {/* Chat Messages Feed */}
      <div className="bio-messages-feed">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`bio-message-row ${msg.sender === 'user' ? 'is-user' : 'is-assistant'}`}
          >
            {msg.sender === 'assistant' && (
              <div className="bio-avatar bio-avatar-bot" aria-hidden="true">
                <Bot size={14} />
              </div>
            )}

            <div className="bio-message-body">
              <div className={`bio-bubble ${msg.sender === 'user' ? 'bio-bubble-user' : 'bio-bubble-bot'}`}>
                {msg.id === 'welcome' ? t.chatWelcome : msg.text}
              </div>

              {/* Source & Citation Cards */}
              {msg.sender === 'assistant' && msg.citations && msg.citations.length > 0 && (
                <div className="bio-citation-container">
                  <button
                    type="button"
                    className="bio-citation-toggle"
                    onClick={() =>
                      setOpenCitationId(openCitationId === msg.id ? null : msg.id)
                    }
                  >
                    <BookOpen size={12} />
                    <span>
                      {msg.citations.length} {msg.citations.length === 1 ? t.chatSingleCitation : t.chatCitations}
                    </span>
                    {openCitationId === msg.id ? (
                      <ChevronUp size={12} />
                    ) : (
                      <ChevronDown size={12} />
                    )}
                  </button>

                  {openCitationId === msg.id && (
                    <div className="bio-citations-list">
                      {msg.citations.map((c, i) => (
                        <div key={i} className="bio-citation-item">
                          <div className="bio-citation-header">
                            <span className="bio-citation-ref">{c.reference}</span>
                            <Badge variant="secondary" className="bio-citation-page">
                              {c.page}
                            </Badge>
                          </div>
                          <div className="bio-citation-section">{c.section}</div>
                          <p className="bio-citation-excerpt">"{c.excerpt}"</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {msg.sender === 'user' && (
              <div className="bio-avatar bio-avatar-user" aria-hidden="true">
                <User size={14} />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="bio-message-row is-assistant">
            <div className="bio-avatar bio-avatar-bot">
              <Bot size={14} />
            </div>
            <div className="bio-bubble bio-bubble-bot bio-loading-dots">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Starter Chips */}
      <div className="bio-starters-wrap">
        <span className="bio-starters-label">{t.chatSuggestionsLabel}</span>
        <div className="bio-starters-scroll">
          {t.quickPrompts.map((prompt, i) => (
            <button
              key={i}
              type="button"
              className="bio-starter-chip"
              onClick={() => handleSend(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Input Bar */}
      <div className="bio-input-bar">
        <input
          type="text"
          className="bio-input"
          placeholder={t.chatInputPlaceholder}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          aria-label="Ask biology question"
        />
        <Button
          type="button"
          className="bio-send-btn"
          onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          aria-label="Send message"
        >
          <Send size={15} />
        </Button>
      </div>

      {/* Dataset & Anatomy License Collapsible */}
      <div className="bio-attribution-drawer">
        <button
          type="button"
          className="bio-attribution-toggle"
          onClick={() => setShowAttribution(!showAttribution)}
        >
          <span>BodyParts3D reference & licenses</span>
          {showAttribution ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>

        {showAttribution && (
          <div className="bio-attribution-content">
            <p>
              <strong>Adult Male Reference Anatomy:</strong> 2,234 individual meshes and 3,432 named concepts from BodyParts3D, © The Database Center for Life Science (CC BY 4.0).
            </p>
            <div className="bio-attribution-links">
              <a href="https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html" target="_blank" rel="noreferrer">
                Dataset license <ArrowUpRight size={12} />
              </a>
              <a href="https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html" target="_blank" rel="noreferrer">
                Original geometry <ArrowUpRight size={12} />
              </a>
              <a href="https://academic.oup.com/nar/article/37/suppl_1/D782/1000752" target="_blank" rel="noreferrer">
                Publication <ExternalLink size={12} />
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
