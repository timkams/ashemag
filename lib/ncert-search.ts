/**
 * Client-side NCERT Biology Search and QA Client.
 * Tries the live backend API first; seamlessly falls back to cached local JSON search.
 */

export interface Citation {
  reference: string;
  section: string;
  page: string;
  excerpt: string;
}

export interface QAResult {
  query: string;
  found: boolean;
  primary_source?: string;
  answer: string;
  citations: Citation[];
}

interface RawChunk {
  id: number;
  grade: number;
  subject: string;
  chapter_num: number;
  chapter_title: string;
  section_num: string;
  section_title: string;
  page_start: number;
  page_end: number;
  content: string;
  key_terms: string;
}

let cachedChunks: RawChunk[] | null = null;

const STOP_WORDS = new Set([
  'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are',
  'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but',
  'by', 'can', 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for',
  'from', 'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself',
  'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just',
  'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once',
  'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should',
  'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then',
  'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up',
  'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why',
  'with', 'would', 'you', 'your', 'yours', 'yourself', 'yourselves', 'explain', 'describe',
  'tell', 'write', 'note', 'define'
]);

async function loadChunks(): Promise<RawChunk[]> {
  if (cachedChunks) return cachedChunks;
  try {
    const res = await fetch('/ncert-bio-knowledge.json');
    if (!res.ok) throw new Error('Failed to load local knowledge base');
    cachedChunks = (await res.json()) as RawChunk[];
    return cachedChunks;
  } catch (err) {
    console.warn('Could not load /ncert-bio-knowledge.json:', err);
    return [];
  }
}

function cleanTokens(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 2 && !STOP_WORDS.has(t));
}

export async function askBiologyQuestion(query: string, gradeFilter?: number): Promise<QAResult> {
  const cleanQ = query.trim();
  if (!cleanQ) {
    return {
      query,
      found: false,
      answer: 'Please enter a biology question.',
      citations: []
    };
  }

  // 1. Try Live API Endpoint first
  try {
    const params = new URLSearchParams({ q: cleanQ });
    if (gradeFilter) params.set('grade', gradeFilter.toString());
    const apiRes = await fetch(`/api/ask?${params.toString()}`, { signal: AbortSignal.timeout(2500) });
    if (apiRes.ok) {
      const data = (await apiRes.json()) as QAResult;
      if (data && data.found) {
        return data;
      }
    }
  } catch {
    // Fall back to client-side search
  }

  // 2. Client-Side BM25 / Keyword Scoring Fallback
  const chunks = await loadChunks();
  if (!chunks.length) {
    return {
      query,
      found: false,
      answer: 'Knowledge base is currently loading. Please try again in a moment.',
      citations: []
    };
  }

  const tokens = cleanTokens(cleanQ);
  if (!tokens.length) {
    return {
      query,
      found: false,
      answer: 'Could not extract valid search terms. Try asking about a specific organ, cell, or process.',
      citations: []
    };
  }

  const scored = chunks
    .filter(c => !gradeFilter || c.grade === gradeFilter)
    .map(chunk => {
      const contentLower = chunk.content.toLowerCase();
      const secLower = chunk.section_title.toLowerCase();
      const chLower = chunk.chapter_title.toLowerCase();
      const termsLower = chunk.key_terms.toLowerCase();

      let score = 0;
      for (const t of tokens) {
        // Boost for match in section title
        if (secLower.includes(t)) score += 15;
        // Boost for match in chapter title
        if (chLower.includes(t)) score += 8;
        // Boost for match in key terms
        if (termsLower.includes(t)) score += 6;
        // Count matches in content
        const matches = (contentLower.match(new RegExp(t, 'g')) || []).length;
        score += Math.min(matches, 5) * 2;
      }

      return { chunk, score };
    })
    .filter(x => x.score > 0)
    .sort((a, b) => b.score - a.score);

  if (!scored.length) {
    return {
      query,
      found: false,
      answer: `No direct matches found in NCERT ${gradeFilter ? `Class ${gradeFilter}` : 'Class 9-12'} textbooks for this query. Try terms like "nephron", "plasma", "mitochondria", or "cardiac cycle".`,
      citations: []
    };
  }

  const top = scored[0].chunk;
  const citations: Citation[] = scored.slice(0, 3).map(item => {
    const c = item.chunk;
    const firstPara = c.content.split('\n\n')[0] || c.content;
    const excerpt = firstPara.length > 280 ? firstPara.slice(0, 280) + '...' : firstPara;
    return {
      reference: `NCERT Class ${c.grade} ${c.subject}, Chapter ${c.chapter_num}: "${c.chapter_title}"`,
      section: `${c.section_num} ${c.section_title}`,
      page: `Page ${c.page_start}-${c.page_end}`,
      excerpt
    };
  });

  // Extract best answer sentences from top chunk
  const sentences = top.content.split(/(?<=[.!?])\s+/);
  const relevantSentences = sentences.filter(s => {
    const sLower = s.toLowerCase();
    return tokens.some(t => sLower.includes(t));
  });

  const bestSentences = relevantSentences.length > 0 ? relevantSentences.slice(0, 3) : sentences.slice(0, 2);
  const answerText = bestSentences.join(' ');

  return {
    query,
    found: true,
    primary_source: `NCERT Class ${top.grade} ${top.subject} · Ch ${top.chapter_num}: ${top.chapter_title} (${top.section_title}, p.${top.page_start}-${top.page_end})`,
    answer: answerText || top.content.slice(0, 300) + '...',
    citations
  };
}

/**
 * Generates an answer using Gemini API grounded in the retrieved NCERT knowledge chunks.
 */
export async function askGeminiWithNCERT(
  query: string,
  apiKey?: string,
  gradeFilter?: number
): Promise<QAResult> {
  // 1. Retrieve the ground-truth textbook chunks from central knowledge base
  const baseResult = await askBiologyQuestion(query, gradeFilter);
  if (!baseResult.found) {
    return baseResult;
  }

  const effectiveKey = apiKey || (typeof window !== 'undefined' ? localStorage.getItem('gemini_api_key') : undefined) || (import.meta as any).env?.VITE_GEMINI_API_KEY;

  // If no Gemini key is provided, return the verified textbook synthesis directly
  if (!effectiveKey) {
    return baseResult;
  }

  // 2. Call Gemini with NCERT grounding context
  try {
    const contextPassages = baseResult.citations
      .map(c => `[Source: ${c.reference} - ${c.section} (${c.page})]\n${c.excerpt}`)
      .join('\n\n');

    const prompt = `You are an expert Biology and Human Anatomy tutor grounded in India's official NCERT Class 9-12 curriculum.
Use the following verified NCERT textbook excerpts as ground truth to answer the student's question accurately, concisely, and educationally.
Explain the biological concepts, mechanisms, and structures clearly.

NCERT TEXTBOOK GROUNDING PASSAGES:
${contextPassages}

STUDENT QUESTION:
${query}

Provide a well-structured, clear explanation based on the NCERT curriculum above.`;

    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${effectiveKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            temperature: 0.3,
            maxOutputTokens: 600
          }
        }),
        signal: AbortSignal.timeout(6000)
      }
    );

    if (!res.ok) {
      // If Gemini call fails (e.g. invalid key or network), fall back to base NCERT result
      console.warn('Gemini API call returned non-OK status:', res.status);
      return baseResult;
    }

    const data = (await res.json()) as any;
    const candidateText = data?.candidates?.[0]?.content?.parts?.[0]?.text;

    if (candidateText) {
      return {
        query,
        found: true,
        primary_source: `✦ Gemini AI (Grounded in ${baseResult.primary_source})`,
        answer: candidateText.trim(),
        citations: baseResult.citations
      };
    }
  } catch (err) {
    console.warn('Gemini call failed, using local NCERT answer:', err);
  }

  return baseResult;
}

