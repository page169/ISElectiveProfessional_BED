# Final Technical Report: Campus Guide AI (TPC Handbook Assistant)
IS Professional Elective #4, Generative AI Systems · 1st Semester, A.Y. 2026-2027

## 1. Introduction
Students find it hard to locate rules in a 200-page handbook. Campus Guide AI is a RAG assistant that answers questions only from the TPC Student Handbook v.04, cites the article and page used, keeps conversational context, and refuses questions outside the handbook.

## 2. Architecture
```
Handbook text -> page/section parsing -> cleaning -> chunking (800/120)
   -> embeddings (bge-small-en-v1.5) -> FAISS index (cosine)

User question -> condense with chat memory (LangChain + Gemini)
   -> embed query -> FAISS top-5 -> relevance threshold 0.40
   -> grounded answer prompt (Gemini) -> answer + citations -> Streamlit UI
```
| Layer | Technology |
|---|---|
| Orchestration | LangChain (prompts, LCEL chains, message memory) |
| Embeddings | BAAI/bge-small-en-v1.5 via FastEmbed (384 dimensions, ONNX, CPU) |
| Vector database | FAISS `IndexFlatIP` on unit vectors (cosine); NumPy fallback |
| LLM | Google Gemini (`gemini-flash-latest`, temperature 0) |
| Interface | Streamlit: Home, Ask, History and saved, Help pages |
| Delivery | Docker multi-stage image, GitHub Actions, Streamlit Community Cloud |

## 3. Data pipeline (CILO 1)
The handbook was supplied as plain text with repeated page headers. `src/rag.py` rebuilds pages from those headers (202 pages), records the printed page number and the nearest Article/Chapter heading, removes soft hyphens, carriage returns and HTML entities, re-joins hyphenated words and collapses whitespace. Text is split into 410 chunks (mean about 630 characters). Before/after evidence is in `docs/preprocessing_report.md`; embeddings are demonstrated by `scripts/embedding_demo.py`. Embeddings are L2-normalised so inner product equals cosine similarity.

## 4. Prompt design
Three prompts (condenser, grounded answerer, follow-up suggester) plus a retrieval threshold guard. See `docs/02_prompt_engineering.md`. The answerer is restricted to numbered excerpts, must cite them, and must emit the sentinel `NOT_IN_HANDBOOK` when the excerpts are insufficient.

## 5. Retrieval and RAG implementation (CILO 2)
Retrieval embeds the standalone question with the query-side bge encoder, searches FAISS for the top 5 chunks, and drops chunks scoring under 0.40. The surviving chunks are numbered and passed to the answer prompt together with the last six turns. The Streamlit UI shows each source with section, page, relevance and the full passage. The distance-metric study (`scripts/compare_metrics.py`, `docs/distance_metric_report.md`) compares cosine, Euclidean and dot product; cosine was chosen because it measures semantic direction, is bounded, and makes the threshold interpretable. The ingestion pipeline (`python ingest.py`, or the sidebar uploader) parses, chunks, embeds and indexes new documents with no manual steps.

## 6. Model choice and customization (CILO 3)
An instruction-tuned Gemini model is used without fine-tuning because handbook policies change and answers must be traceable to sources. LoRA and QLoRA reasoning, memory estimates and a proposed experiment are in `docs/04_model_customization.md`.

## 7. Deployment (CILO 4)
The app is containerised with a multi-stage Dockerfile (dependencies and the embedding model are fetched in a builder stage; the runtime image is slim, non-root, with a health check). The API key is supplied through environment variables or platform secrets, never committed. GitHub Actions compiles, tests, builds the image and publishes it to GHCR. The public app runs on Streamlit Community Cloud. Evidence is collected in `docs/05_deployment_evidence.md`.

## 8. Evaluation
`scripts/evaluate.py` runs 6 in-scope questions with expected keywords, 2 out-of-scope questions and a multi-turn memory test, and writes `docs/evaluation_results.md`.
**Results (insert after running):** in-scope correct: __ / 6 · out-of-scope declined: __ / 2 · memory test: pass / fail · median latency: __ s.
Unit tests (`pytest`) cover cleaning, page parsing and chunking.

## 9. Limitations
- The handbook is a plain-text export: tables (grading scale, prospectus) flatten and answer poorly, and section labels are approximate.
- Retrieval is single-stage dense search; exact-number questions might benefit from hybrid BM25 search or a reranker.
- A flat FAISS index is exact and fast at this size, but would need an approximate index (HNSW/IVF) if the corpus grew 100x.
- Free-tier API quotas limit concurrent use.
- Answers are only as current as the indexed handbook version, and the assistant is not an official source.

## 10. Future work
Original PDF parsing with layout and a page viewer, hybrid search and reranking, multi-document routing, embedding fine-tuning, Filipino/Bisaya support, persistent user history, and an automated regression test set.

## 11. Lessons learned
Grounding quality depended more on clean page-aware chunking and a refusal rule than on model choice. A retrieval threshold is a cheap and effective hallucination guard. Keeping the retrieval layer simple made the system easy to test and explain.

## 12. Academic integrity and AI assistance
Parts of the code and documentation were drafted with Claude (Anthropic) and reviewed, run and adapted by the project owner. Third-party libraries: LangChain, FastEmbed, FAISS, Streamlit, pypdf, python-docx, pytest. The dataset is the school's own TPC Student Handbook.
