"""
FastAPI Server for NCERT Biology Question Answering and Human Atlas Integration.
Provides REST APIs and an interactive web explorer interface.
"""
from typing import Optional, List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from ncert_bio.qa_engine import NCERTBioQAEngine
from ncert_bio.catalog import NCERT_CHAPTERS

app = FastAPI(
    title="NCERT Biology QA API",
    description="Knowledge base and Question-Answering engine for NCERT Science & Biology Class 9-12",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = NCERTBioQAEngine()


class CitationModel(BaseModel):
    reference: str
    section: str
    page: str
    excerpt: str


class AnswerResponse(BaseModel):
    query: str
    found: bool
    primary_source: Optional[str] = None
    answer: str
    citations: List[CitationModel] = []
    top_excerpt: Optional[str] = None


@app.get("/api/status")
def get_status():
    with engine._get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM chunks")
            chunks_count = cursor.fetchone()[0]
        except Exception:
            chunks_count = 0

    return {
        "status": "online",
        "total_catalog_chapters": len(NCERT_CHAPTERS),
        "total_indexed_chunks": chunks_count
    }


@app.get("/api/ask", response_model=AnswerResponse)
def ask_question(
    q: str = Query(..., description="The biology question"),
    grade: Optional[int] = Query(None, ge=9, le=12, description="Optional class filter (9, 10, 11, 12)"),
    top_k: int = Query(4, ge=1, le=10, description="Number of citations to return")
):
    result = engine.answer_question(q, grade=grade, top_k=top_k)
    return result


@app.get("/api/anatomy-explain")
def explain_anatomy_organ(organ: str = Query(..., description="Organ or anatomical structure name")):
    """Special endpoint designed for Human Atlas 3D integration."""
    query = f"Explain structure and function of {organ} in human body"
    result = engine.answer_question(query, grade=None, top_k=3)
    return {
        "organ": organ,
        "explanation": result.get("answer"),
        "primary_source": result.get("primary_source"),
        "citations": result.get("citations", [])
    }


@app.post("/api/reindex")
def reindex_corpus():
    count = engine.build_index(force_rebuild=True)
    return {"status": "success", "indexed_chunks": count}


@app.get("/", response_class=HTMLResponse)
def get_web_ui():
    """Interactive dark-mode biology student assistant UI."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NCERT Biology AI Tutor & Knowledge Base</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0f1d;
            --bg-card: rgba(18, 25, 44, 0.75);
            --border-color: rgba(64, 93, 153, 0.25);
            --accent: #10b981;
            --accent-glow: rgba(16, 185, 129, 0.2);
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --cyan-glow: #06b6d4;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Outfit', sans-serif;
            background: radial-gradient(circle at 50% 0%, #172554 0%, #0a0f1d 75%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
        }
        .container {
            max-width: 900px;
            width: 100%;
        }
        .header {
            text-align: center;
            margin-bottom: 35px;
        }
        .badge {
            display: inline-block;
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent);
            border: 1px solid rgba(16, 185, 129, 0.4);
            padding: 4px 14px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 30%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        p.subtitle {
            color: var(--text-muted);
            font-size: 1.1rem;
        }
        .search-box {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            margin-bottom: 30px;
        }
        .input-row {
            display: flex;
            gap: 12px;
        }
        input[type="text"] {
            flex: 1;
            background: rgba(10, 15, 29, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #fff;
            padding: 14px 18px;
            border-radius: 10px;
            font-size: 1.05rem;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s;
        }
        input[type="text"]:focus {
            border-color: var(--cyan-glow);
            box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
        }
        select {
            background: rgba(10, 15, 29, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #fff;
            padding: 0 14px;
            border-radius: 10px;
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
        }
        button {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
            color: white;
            border: none;
            padding: 14px 24px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.1s, opacity 0.2s;
        }
        button:hover { opacity: 0.95; transform: translateY(-1px); }
        .preset-queries {
            display: flex;
            gap: 8px;
            margin-top: 14px;
            flex-wrap: wrap;
            align-items: center;
        }
        .preset-label {
            font-size: 0.85rem;
            color: var(--text-muted);
        }
        .preset-pill {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #cbd5e1;
            font-size: 0.82rem;
            padding: 4px 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .preset-pill:hover { background: rgba(56, 189, 248, 0.2); border-color: #38bdf8; }
        .result-container {
            display: none;
            margin-top: 25px;
        }
        .answer-card {
            background: var(--bg-card);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 14px;
            padding: 24px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
            margin-bottom: 24px;
        }
        .source-tag {
            color: var(--accent);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .answer-text {
            font-size: 1.15rem;
            line-height: 1.65;
            color: #f8fafc;
            margin-bottom: 14px;
        }
        .citations-section h3 {
            font-size: 1.1rem;
            color: #38bdf8;
            margin-bottom: 12px;
        }
        .citation-item {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .citation-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #cbd5e1;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .citation-page {
            color: #a855f7;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
        }
        .citation-excerpt {
            color: #94a3b8;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 30px;
            color: var(--cyan-glow);
            font-size: 1.1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="badge">NCERT CURRICULUM CLASS 9–12</div>
            <h1>Biology Knowledge & QA Engine</h1>
            <p class="subtitle">Search scraped NCERT textbooks with verified citations & chapter page references</p>
        </div>

        <div class="search-box">
            <div class="input-row">
                <input type="text" id="queryInput" placeholder="Ask a biology question (e.g. How do kidneys form urine?)..." autofocus />
                <select id="gradeSelect">
                    <option value="">All Classes (9-12)</option>
                    <option value="9">Class 9 (Science)</option>
                    <option value="10">Class 10 (Life Processes)</option>
                    <option value="11">Class 11 (Physiology & Cell)</option>
                    <option value="12">Class 12 (Genetics & Reproduction)</option>
                </select>
                <button onclick="performSearch()">Ask</button>
            </div>
            <div class="preset-queries">
                <span class="preset-label">Quick topics:</span>
                <span class="preset-pill" onclick="setQuery('Describe the components of blood and formed elements')">Blood & Plasma</span>
                <span class="preset-pill" onclick="setQuery('How does the nephron filter blood in the kidney?')">Nephron & Excretion</span>
                <span class="preset-pill" onclick="setQuery('Explain the structure of mitochondria and why it is the powerhouse of the cell')">Mitochondria</span>
                <span class="preset-pill" onclick="setQuery('What happens during the cardiac cycle in the human heart?')">Cardiac Cycle</span>
                <span class="preset-pill" onclick="setQuery('Explain double circulation in human beings')">Double Circulation</span>
                <span class="preset-pill" onclick="setQuery('Describe the structure of human sperm')">Human Sperm</span>
            </div>
        </div>

        <div class="loading" id="loadingIndicator">
            🔍 Searching verified NCERT biology corpus...
        </div>

        <div class="result-container" id="resultContainer">
            <div class="answer-card">
                <div class="source-tag" id="sourceTag">📖 NCERT SOURCE</div>
                <div class="answer-text" id="answerText"></div>
            </div>

            <div class="citations-section">
                <h3>📚 Exact Textbook Citations & Excerpts</h3>
                <div id="citationsList"></div>
            </div>
        </div>
    </div>

    <script>
        function setQuery(q) {
            document.getElementById('queryInput').value = q;
            performSearch();
        }

        document.getElementById('queryInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') performSearch();
        });

        async function performSearch() {
            const query = document.getElementById('queryInput').value.trim();
            if (!query) return;

            const grade = document.getElementById('gradeSelect').value;
            const loading = document.getElementById('loadingIndicator');
            const resultBox = document.getElementById('resultContainer');

            loading.style.display = 'block';
            resultBox.style.display = 'none';

            let url = `/api/ask?q=${encodeURIComponent(query)}`;
            if (grade) url += `&grade=${grade}`;

            try {
                const res = await fetch(url);
                const data = await res.json();
                loading.style.display = 'none';

                if (!data.found) {
                    alert('No matching sections found. Try a different biology term.');
                    return;
                }

                document.getElementById('sourceTag').innerText = '📖 ' + (data.primary_source || 'NCERT Textbook');
                document.getElementById('answerText').innerText = data.answer;

                const citList = document.getElementById('citationsList');
                citList.innerHTML = '';

                data.citations.forEach(cit => {
                    const el = document.createElement('div');
                    el.className = 'citation-item';
                    el.innerHTML = `
                        <div class="citation-header">
                            <span>${cit.reference} - <em>${cit.section}</em></span>
                            <span class="citation-page">${cit.page}</span>
                        </div>
                        <div class="citation-excerpt">"${cit.excerpt}"</div>
                    `;
                    citList.appendChild(el);
                });

                resultBox.style.display = 'block';
            } catch (err) {
                loading.style.display = 'none';
                alert('Error connecting to NCERT Biology QA API: ' + err.message);
            }
        }
    </script>
</body>
</html>
    """
