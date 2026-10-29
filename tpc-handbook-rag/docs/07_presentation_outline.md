# Final Presentation and Defense Outline (10-15 min + Q&A)
1. **Problem and motivation (1 slide):** long handbook, repeated questions, risk of wrong policy answers.
2. **Architecture (2 slides):** data -> embeddings -> FAISS -> RAG chain -> Streamlit -> Docker -> deployment.
3. **Live demo of the deployed app:** policy question with citations, follow-up using memory, out-of-scope refusal, Saved answers. Keep a recorded backup.
4. **Key decisions and trade-offs:** prompt strategy (sentinel and threshold), LangChain vs LlamaIndex, cosine metric, FAISS, no fine-tuning.
5. **Limitations and next steps.**
6. **Q&A.**

## Defense preparation
| Likely question | Short answer |
|---|---|
| Why cosine and FAISS? | Semantic direction, bounded scores for a threshold; FAISS is exact at this size and works on CPU. See `distance_metric_report.md`. |
| What happens when a user submits a query? | Condense with memory, embed, FAISS top-5, drop under 0.40, build numbered context, Gemini answers or says NOT_IN_HANDBOOK, UI shows citations. |
| How do you reduce hallucination? | Retrieval threshold, grounded prompt with refusal sentinel, citation rule, temperature 0, injection rule. |
| What breaks first at 100x documents? | Flat FAISS latency and memory; move to HNSW/IVF, add metadata filters, hybrid search and routing. |
| What would you fine-tune with LoRA/QLoRA? | The embedding model first (retrieval), then an open LLM for tone and language; see the customization note. |
| Why not fine-tune now? | Policies change, citations are required, and Gemini weights are API-only. |
| Is the key safe? | Environment variables and secrets, `.gitignore`/`.dockerignore`, no key in the image or repo. |
Every team member must be able to explain every component.
