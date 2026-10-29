# 📘 TPC Handbook Assistant (RAG Chatbot)

**Purpose:** A Retrieval-Augmented Generation chatbot that answers student questions about the
TPC Handbook, with page-level citations and a refusal when the handbook has no answer.

**🔗 Live app:** `<paste your Streamlit Community Cloud URL here>`
**🎥 Demo video:** `<paste your Drive/YouTube link here>`

> **Usage limit:** The app uses the Google Gemini free-tier API. Heavy use may trigger a rate-limit message;
> wait about a minute and retry.

## Tech stack
| Layer | Choice |
|---|---|
| Interface | Streamlit (Community Cloud) |
| Orchestration | LangChain (prompts, LCEL chains, chat-history messages) |
| Chunking | `RecursiveCharacterTextSplitter` (800 chars, 120 overlap) |
| Embeddings | `BAAI/bge-small-en-v1.5` via FastEmbed (ONNX, CPU) |
| Vector database | FAISS `IndexFlatIP` over unit vectors (cosine), persisted in `index/` |
| LLM | Gemini Flash (`gemini-flash-latest`) via Google AI Studio (LangChain `langchain-google-genai`) |

## How the RAG pipeline works
1. **Ingest** – `data/handbook/*` (PDF/DOCX/TXT/MD) is parsed page by page and cleaned
   (hyphenation fixes, whitespace normalisation).
2. **Chunk** – text is split into overlapping chunks that keep `source` and `page` metadata.
3. **Embed & store** – chunks are embedded and saved to `index/vectors.npy` + `index/chunks.json`.
4. **Retrieve** – the user question (rewritten into a standalone question using chat memory) is
   embedded; top-k chunks are found by cosine similarity. Chunks below the relevance threshold are dropped.
5. **Generate** – the LLM answers using only the retrieved chunks and cites them as `[1]`, `[2]`.
6. **Out-of-scope handling** – two guards: (a) no chunk passes the threshold → polite refusal;
   (b) the model replies `NOT_IN_HANDBOOK` → polite refusal.
7. **Memory** – the last 6 turns are passed to the chain for multi-turn conversations.

## Interface
Campus Guide AI has four pages: **Home** (greeting, suggested questions by category, recent chats),
**Ask the handbook** (chat with source cards, save and feedback buttons, follow-up chips),
**History & saved** (session history and bookmarked answers) and **Help & support**
(FAQ and contact office). Citations show the Article/Chapter and printed page number parsed from the handbook text.

## Checkpoint deliverables
| Checkpoint | Deliverable | Where |
|---|---|---|
| 1 | Proposal | `docs/01_project_proposal.md` |
| 1 | Dataset (about 200 pages) | `data/handbook/` |
| 1 | Preprocessing script and before/after report | `scripts/preprocess_demo.py`, `docs/preprocessing_report.md` |
| 1 | Embedding demo and model explanation | `scripts/embedding_demo.py`, `docs/embedding_demo_output.txt`, final report section 3 |
| 1 | Data reflection | end of `docs/preprocessing_report.md` |
| 2 | Prompt Engineering Document | `docs/02_prompt_engineering.md` |
| 2 | API integration | `src/rag.py` (`_llm`, `answer`) |
| 2 | Vector database + similarity search | `src/rag.py` (FAISS `VectorStore`) |
| 2 | Distance metric comparison | `scripts/compare_metrics.py`, `docs/distance_metric_report.md` |
| 3 | Ingestion pipeline | `ingest.py`, `src/rag.py` (`build_index`), sidebar uploader |
| 3 | RAG app with LangChain and memory | `app.py`, `src/rag.py` |
| 3 | Framework comparison note | `docs/03_framework_comparison.md` |
| 3 | Demo queries incl. out-of-scope | `scripts/evaluate.py`, `docs/evaluation_results.md` |
| 4 | Model customization note | `docs/04_model_customization.md` |
| 4 | Web interface | `app.py` |
| 4 | Dockerfile (multi-stage), compose, CI/CD | `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml` |
| 4 | Deployment evidence | `docs/05_deployment_evidence.md` |
| 4 | Final technical report | `docs/06_final_technical_report.md` |
| 4 | Presentation and defense prep | `docs/07_presentation_outline.md` |

### Generate the evidence files (after `python ingest.py`)
```bash
python scripts/preprocess_demo.py     # docs/preprocessing_report.md
python scripts/embedding_demo.py      # docs/embedding_demo_output.txt
python scripts/compare_metrics.py     # docs/distance_metric_report.md
python scripts/evaluate.py            # docs/evaluation_results.md (needs GEMINI_API_KEY)
pip install -r requirements-dev.txt && pytest -q
docker build -t tpc-handbook-rag . && docker run --rm -p 8501:8501 -e GEMINI_API_KEY=your_key tpc-handbook-rag
```

## Run locally
```bash
git clone <your-repo-url> && cd tpc-handbook-rag
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                    # add your GEMINI_API_KEY
# place the handbook file(s) in data/handbook/
python ingest.py
streamlit run app.py
```
Get a free key at https://aistudio.google.com/apikey.

> **Full step-by-step instructions (Windows/PowerShell, Streamlit Cloud, Docker, CI/CD, evidence, submission): [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md)**

## Deploy (Streamlit Community Cloud)
1. Push this repo to GitHub as **Public** (commit the generated `index/` folder so the app starts instantly).
2. share.streamlit.io → *New app* → select repo, branch `main`, file `app.py`.
3. *Advanced settings → Secrets*: `GEMINI_API_KEY = "your_key"`.
4. Open the URL in an incognito window to confirm no login is needed.

## Sample documents
The knowledge source is the **TPC Handbook** (source: `<state where you obtained it, e.g. the school's official student handbook PDF>`).

## Project structure
```
app.py            Streamlit UI (chat, sources, sidebar controls)
ingest.py         CLI to build the index
src/rag.py        Loading, chunking, embedding, retrieval, prompts, answer chain
data/handbook/    Handbook files (input)
index/            Generated vector index
docs/             Proposal, prompt doc, framework note, etc.
```

## Limitations / future work
Tables and scanned (image-only) PDFs extract poorly (add OCR); a hybrid BM25 + dense search
and a reranker would improve recall; a real vector DB (Chroma/Qdrant) is needed beyond ~100k chunks.
