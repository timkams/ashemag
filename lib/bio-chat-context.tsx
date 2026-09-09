import React, { createContext, useContext, useState, useEffect } from 'react';
import { askGeminiWithNCERT, type Citation } from './ncert-search';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  primarySource?: string;
  citations?: Citation[];
  timestamp: Date;
}

interface BioChatContextType {
  messages: ChatMessage[];
  loading: boolean;
  currentQuery: string;
  isSidebarOpen: boolean;
  setIsSidebarOpen: (open: boolean) => void;
  gradeFilter?: number;
  setGradeFilter: (grade?: number) => void;
  apiKey: string;
  setApiKey: (key: string) => void;
  sendQuery: (query: string) => Promise<void>;
  resetChat: () => void;
}

const BioChatContext = createContext<BioChatContextType | undefined>(undefined);

export function BioChatProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Hello! I am your NCERT Biology Assistant. Ask me anything about human anatomy, organ systems, cellular biology, genetics, or physiology from Class 9 to 12 textbooks.',
      timestamp: new Date()
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [gradeFilter, setGradeFilter] = useState<number | undefined>(undefined);
  const [apiKey, setApiKeyState] = useState<string>('');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedKey = localStorage.getItem('gemini_api_key') || '';
      setApiKeyState(savedKey);
    }
  }, []);

  const setApiKey = (key: string) => {
    setApiKeyState(key);
    if (typeof window !== 'undefined') {
      localStorage.setItem('gemini_api_key', key);
    }
  };

  const sendQuery = async (queryText: string) => {
    const q = queryText.trim();
    if (!q || loading) return;

    setCurrentQuery(q);
    setLoading(true);

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: q,
      timestamp: new Date()
    };

    // Append user message immediately
    setMessages(prev => [...prev, userMsg]);

    // Open sidebar sheet automatically!
    setIsSidebarOpen(true);

    try {
      // Call Gemini + NCERT Central Knowledge Base
      const result = await askGeminiWithNCERT(q, apiKey || undefined, gradeFilter);

      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: result.answer,
        primarySource: result.primary_source,
        citations: result.citations,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          sender: 'assistant',
          text: 'An error occurred while querying the NCERT biology database. Please try again.',
          timestamp: new Date()
        }
      ]);
    } finally {
      setLoading(false);
      setCurrentQuery('');
    }
  };

  const resetChat = () => {
    setMessages([
      {
        id: 'welcome',
        sender: 'assistant',
        text: 'Hello! I am your NCERT Biology Assistant. Ask me anything about human anatomy, organ systems, cellular biology, genetics, or physiology from Class 9 to 12 textbooks.',
        timestamp: new Date()
      }
    ]);
  };

  return (
    <BioChatContext.Provider
      value={{
        messages,
        loading,
        currentQuery,
        isSidebarOpen,
        setIsSidebarOpen,
        gradeFilter,
        setGradeFilter,
        apiKey,
        setApiKey,
        sendQuery,
        resetChat
      }}
    >
      {children}
    </BioChatContext.Provider>
  );
}

export function useBioChat() {
  const ctx = useContext(BioChatContext);
  if (!ctx) {
    throw new Error('useBioChat must be used within a BioChatProvider');
  }
  return ctx;
}
