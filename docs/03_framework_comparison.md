# Framework Comparison Note: LangChain vs LlamaIndex (Checkpoint 3)

## Short comparison
| Aspect | LangChain | LlamaIndex |
|---|---|---|
| Core idea | Composable "chains" of prompts, models, parsers and tools (LCEL pipe syntax) | Data-centric: documents are parsed into **nodes** and organised into indexes |
| Data routing | You design the flow: retrievers, routers and agents are wired explicitly | Built-in query engines and routers choose among indexes (vector, summary, keyword) |
| Node indexing | Splitters create `Document` chunks; storage via vector-store integrations | `Node` objects carry metadata and relationships (parent/child, previous/next) and feed index types directly |
| Strengths | Flexible prompts, memory, agents, many model integrations | Fast path from documents to a query engine; strong ingestion and retrieval abstractions |
| Typical trade-off | More wiring, more control | Less wiring, opinionated structure |

## What I used and why
I used **LangChain**, in these specific places:
- `ChatPromptTemplate` for the three prompts, with `placeholder` slots for chat history.
- LCEL chains (`prompt | llm | StrOutputParser()`) for question condensing, answering and follow-ups.
- `ChatGoogleGenerativeAI` as the model wrapper.
- `RecursiveCharacterTextSplitter` for chunking.
- `HumanMessage` / `AIMessage` for conversational memory (last 6 turns).

I deliberately wrote the retrieval layer myself (FastEmbed + FAISS in `src/rag.py`) instead of LangChain's vector-store classes. This keeps the dependency list small for free-tier deployment, exposes the similarity scores needed for the relevance threshold, and makes the pipeline easier to explain and defend step by step.

## What I did not use
LlamaIndex is not in the project. If the handbook grew into many documents, I would consider LlamaIndex's node parsers and a router query engine to send questions to the right document (handbook, prospectus, policies) automatically. In LangChain the equivalent would be a retriever router chain.

## Conclusion
LangChain fit best because the main engineering problems here were prompt control, memory and refusal behaviour, which are chain-design problems. LlamaIndex would fit better for a multi-document knowledge base with automatic routing.
