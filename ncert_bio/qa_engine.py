"""
NCERT Biology Question-Answering (QA) Engine.
Indexes scraped textbook chapters into SQLite FTS5 (Full-Text Search) with BM25 ranking,
retrieves relevant textbook sections, and synthesizes authoritative biology answers.
"""
import os
import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

DEFAULT_CORPUS_DIR = Path(__file__).parent / "data" / "scraped_corpus"
DEFAULT_DB_PATH = Path(__file__).parent / "data" / "ncert_bio_fts.db"

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "tell", "explain", "describe", "write", "note",
    "give", "mention", "define", "briefly", "short"
}


class NCERTBioQAEngine:
    def __init__(self, db_path: Optional[Path] = None, corpus_dir: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.corpus_dir = Path(corpus_dir) if corpus_dir else DEFAULT_CORPUS_DIR
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create relational and FTS5 virtual tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    grade INTEGER,
                    subject TEXT,
                    chapter_num INTEGER,
                    chapter_title TEXT,
                    unit TEXT,
                    section_num TEXT,
                    section_title TEXT,
                    page_start INTEGER,
                    page_end INTEGER,
                    content TEXT,
                    key_terms TEXT
                )
            """)

            # FTS5 full-text index
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    content,
                    section_title,
                    chapter_title,
                    key_terms,
                    content='chunks',
                    content_rowid='id'
                )
            """)

            # Trigger to maintain FTS5 on insert
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                    INSERT INTO chunks_fts(rowid, content, section_title, chapter_title, key_terms)
                    VALUES (new.id, new.content, new.section_title, new.chapter_title, new.key_terms);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                    INSERT INTO chunks_fts(chunks_fts, rowid, content, section_title, chapter_title, key_terms)
                    VALUES('delete', old.id, old.content, old.section_title, old.chapter_title, old.key_terms);
                END;
            """)
            conn.commit()

    def build_index(self, force_rebuild: bool = False) -> int:
        """Scan scraped_corpus directory and index all chapter sections."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM chunks")
            existing_count = cursor.fetchone()[0]
            if existing_count > 0 and not force_rebuild:
                return existing_count

            if force_rebuild:
                cursor.execute("DELETE FROM chunks")
                cursor.execute("DELETE FROM chunks_fts")
                conn.commit()

            inserted = 0
            # Scan all json files in scraped_corpus
            for json_file in self.corpus_dir.glob("class_*/*.json"):
                with open(json_file, "r", encoding="utf-8") as f:
                    chapter_data = json.load(f)

                grade = chapter_data["grade"]
                subject = chapter_data.get("subject", "Biology")
                ch_num = chapter_data["chapter_num"]
                ch_title = chapter_data["chapter_title"]
                unit = chapter_data.get("unit", "")

                for sec in chapter_data.get("sections", []):
                    sec_num = sec.get("section_num", "")
                    sec_title = sec.get("title", "")
                    p_start = sec.get("page_start", 1)
                    p_end = sec.get("page_end", 1)
                    paragraphs = sec.get("paragraphs", [])
                    key_terms = ", ".join(sec.get("key_terms", []))

                    if not paragraphs:
                        continue

                    full_section_text = "\n\n".join(paragraphs)
                    words = full_section_text.split()

                    # Chunk if longer than 500 words
                    if len(words) <= 500:
                        chunks_to_insert = [full_section_text]
                    else:
                        chunks_to_insert = []
                        chunk_size = 400
                        overlap = 80
                        start = 0
                        while start < len(words):
                            end = min(start + chunk_size, len(words))
                            chunks_to_insert.append(" ".join(words[start:end]))
                            if end >= len(words):
                                break
                            start += chunk_size - overlap

                    for chunk_text in chunks_to_insert:
                        cursor.execute("""
                            INSERT INTO chunks (
                                grade, subject, chapter_num, chapter_title, unit,
                                section_num, section_title, page_start, page_end,
                                content, key_terms
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            grade, subject, ch_num, ch_title, unit,
                            sec_num, sec_title, p_start, p_end,
                            chunk_text, key_terms
                        ))
                        inserted += 1

            conn.commit()
            return inserted

    def _clean_query(self, query: str) -> List[str]:
        """Tokenize and filter stop words from biology query."""
        raw_tokens = re.findall(r"[a-zA-Z0-9_-]+", query.lower())
        meaningful = [t for t in raw_tokens if t not in STOP_WORDS and len(t) > 2]
        return meaningful

    def search(self, query: str, grade: Optional[int] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search chunks using SQLite FTS5 BM25 ranking."""
        tokens = self._clean_query(query)
        if not tokens:
            return []

        # Prepare FTS5 query with prefix matching on tokens
        # e.g. "nephron* OR blood* OR filtration*"
        fts_query = " OR ".join(f'"{t}"*' for t in tokens)

        grade_filter = f"AND c.grade = {int(grade)}" if grade else ""

        sql = f"""
            SELECT 
                c.id, c.grade, c.subject, c.chapter_num, c.chapter_title, c.unit,
                c.section_num, c.section_title, c.page_start, c.page_end,
                c.content, c.key_terms,
                bm25(chunks_fts, 5.0, 10.0, 8.0, 4.0) as rank
            FROM chunks_fts f
            JOIN chunks c ON f.rowid = c.id
            WHERE chunks_fts MATCH ? {grade_filter}
            ORDER BY rank
            LIMIT ?
        """

        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (fts_query, top_k * 2))
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                # Fallback simple search if FTS syntax edge case
                escaped_tokens = " OR ".join(f'"{t}"' for t in tokens)
                cursor.execute(sql, (escaped_tokens, top_k * 2))
                rows = cursor.fetchall()

            for r in rows:
                content = r["content"]
                # Score boost if query terms appear in section title or key terms
                sec_title = r["section_title"].lower()
                ch_title = r["chapter_title"].lower()
                matches_in_title = sum(1 for t in tokens if t in sec_title or t in ch_title)
                
                # Extract most relevant snippet around query terms
                snippet = self._extract_snippet(content, tokens)

                results.append({
                    "id": r["id"],
                    "grade": r["grade"],
                    "subject": r["subject"],
                    "chapter_num": r["chapter_num"],
                    "chapter_title": r["chapter_title"],
                    "unit": r["unit"],
                    "section_num": r["section_num"],
                    "section_title": r["section_title"],
                    "page_range": f"{r['page_start']}-{r['page_end']}",
                    "content": content,
                    "snippet": snippet,
                    "key_terms": r["key_terms"],
                    "score": float(r["rank"]) - (matches_in_title * 2.0)
                })

        # Sort by adjusted score (lower is better in BM25)
        results.sort(key=lambda x: x["score"])
        return results[:top_k]

    def _extract_snippet(self, text: str, tokens: List[str], max_chars: int = 350) -> str:
        """Find the best paragraph or sentence cluster containing the query tokens."""
        paragraphs = text.split("\n\n")
        best_para = paragraphs[0]
        best_hits = 0

        for p in paragraphs:
            p_lower = p.lower()
            hits = sum(1 for t in tokens if t in p_lower)
            if hits > best_hits:
                best_hits = hits
                best_para = p

        cleaned = " ".join(best_para.split())
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[:max_chars] + "..."

    def answer_question(self, query: str, grade: Optional[int] = None, top_k: int = 4) -> Dict[str, Any]:
        """
        Answers a biology question from NCERT textbooks.
        Returns a structured response containing:
        - direct authoritative summary
        - key textbook citations (Grade, Chapter, Section, Page)
        - full excerpts and key concepts
        """
        matches = self.search(query, grade=grade, top_k=top_k)

        if not matches:
            return {
                "query": query,
                "found": False,
                "answer": "No direct matching sections found in the current NCERT index. Please check your query terms or ensure the relevant chapters have been indexed.",
                "citations": []
            }

        top_match = matches[0]

        # Extract definition sentences (sentences containing 'is', 'are', 'means', 'defined as', 'consists of')
        sentences = re.split(r"(?<=[.!?])\s+", top_match["content"])
        summary_sentences = []
        tokens = self._clean_query(query)

        for s in sentences:
            s_clean = s.strip()
            s_lower = s_clean.lower()
            if any(t in s_lower for t in tokens):
                summary_sentences.append(s_clean)
                if len(summary_sentences) >= 3:
                    break

        if not summary_sentences and sentences:
            summary_sentences = [sentences[0]]

        answer_text = " ".join(summary_sentences)

        citations = []
        for m in matches:
            citations.append({
                "reference": f"NCERT Class {m['grade']} {m['subject']}, Chapter {m['chapter_num']}: \"{m['chapter_title']}\"",
                "section": f"{m['section_num']} {m['section_title']}",
                "page": f"Page {m['page_range']}",
                "excerpt": m["snippet"]
            })

        return {
            "query": query,
            "found": True,
            "primary_source": f"NCERT Class {top_match['grade']} {top_match['subject']} - Chapter {top_match['chapter_num']}: {top_match['chapter_title']} (Section: {top_match['section_title']}, Page {top_match['page_range']})",
            "answer": answer_text,
            "citations": citations,
            "top_excerpt": top_match["content"]
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NCERT Biology Question Answering Engine")
    parser.add_argument("query", nargs="?", help="Biology question to answer")
    parser.add_argument("--rebuild-index", action="store_true", help="Rebuild the FTS5 database from scraped corpus")
    parser.add_argument("--grade", type=int, choices=[9, 10, 11, 12], help="Limit search to a specific grade")
    parser.add_argument("--top-k", type=int, default=3, help="Number of citations to retrieve")

    args = parser.parse_args()
    engine = NCERTBioQAEngine()

    if args.rebuild_index:
        print("Rebuilding NCERT Biology FTS5 Index...")
        count = engine.build_index(force_rebuild=True)
        print(f"Index built successfully! Total chunks indexed: {count}")

    if args.query:
        print(f"\nQuestion: {args.query}")
        result = engine.answer_question(args.query, grade=args.grade, top_k=args.top_k)
        if not result["found"]:
            print(result["answer"])
            return

        print(f"\n[Source]: {result['primary_source']}")
        print(f"\n[Answer]:\n{result['answer']}")
        print("\n[Textbook Citations]:")
        for i, c in enumerate(result["citations"], 1):
            print(f" {i}. {c['reference']} | {c['section']} ({c['page']})")
            print(f"    Excerpt: {c['excerpt']}\n")


if __name__ == "__main__":
    main()
