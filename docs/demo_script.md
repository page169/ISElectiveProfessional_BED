# Demo video script (5–8 min)
1. **Problem & source (1 min):** students struggle to find rules in a long handbook; source = TPC Handbook PDF.
2. **Architecture (1–2 min):** ingest → chunk → bge-small embeddings → NumPy cosine store → LangChain + Gemini Flash → Streamlit.
3. **Live app (3 min), from the public URL:**
   - Q1: a direct policy question (open the Sources expander).
   - Q2: a follow-up that relies on memory ("What about for transferees?").
   - Q3: a list/procedure question (e.g. enrollment steps).
   - **Q4 (out of scope):** "Who won the NBA finals?" -> show the refusal.
4. **Improvements (1 min):** OCR, hybrid search, reranker, evaluation set.
