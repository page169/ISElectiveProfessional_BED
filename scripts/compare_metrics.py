"""Checkpoint 2: compare cosine, Euclidean and dot-product retrieval on the handbook.
Run: python scripts/compare_metrics.py  -> writes docs/distance_metric_report.md"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import rag

QUERIES = ["How many absences are allowed before a student is dropped?", "What is the dress code?",
 "How is the general weighted average computed?", "What are the penalties for a second major offense?",
 "What documents must transferees submit?", "When can I see the college physician?",
 "How many books can I borrow from the library?", "What are the requirements for graduating with honors?"]
K = 5
chunks = rag.chunk_records(rag.load_file(rag.DATA_DIR / "TPC_Student_Handbook.txt"))
emb = rag._get_embedder()
D = np.array(list(emb.embed([c["text"] for c in chunks], batch_size=rag.EMBED_BATCH)), dtype="float32")       # raw, un-normalised
Q = np.array(list(emb.query_embed(QUERIES)), dtype="float32")
norms = np.linalg.norm(D, axis=1)
unit = lambda x: x / np.linalg.norm(x, axis=-1, keepdims=True)

def topk(q):
    return {"Cosine": np.argsort(-(unit(D) @ unit(q)))[:K],
            "Euclidean (L2)": np.argsort(np.linalg.norm(D - q, axis=1))[:K],
            "Dot product": np.argsort(-(D @ q))[:K]}
label = lambda i: f"p.{chunks[i]['page']}"
rows, agree1, overlap = [], {"Euclidean (L2)": 0, "Dot product": 0}, {"Euclidean (L2)": 0, "Dot product": 0}
for q, qv in zip(QUERIES, Q):
    r = topk(qv)
    for m in agree1:
        agree1[m] += int(r[m][0] == r["Cosine"][0])
        overlap[m] += len(set(r[m]) & set(r["Cosine"])) / K
    rows.append((q, {m: ", ".join(label(i) for i in v[:3]) for m, v in r.items()}))
n = len(QUERIES)
out = ["# Distance Metric Comparison (Checkpoint 2)", "",
 f"Dataset: TPC Student Handbook, {len(chunks)} chunks embedded with `{rag.EMBED_MODEL}` ({D.shape[1]} dimensions). "
 f"{n} test queries, top-{K} retrieval. Embeddings were compared **un-normalised** so the metrics can differ.", "",
 f"Chunk vector norms: min {norms.min():.3f}, mean {norms.mean():.3f}, max {norms.max():.3f}.", "",
 "## Agreement with cosine", "| Metric | Same top-1 as cosine | Mean top-5 overlap with cosine |", "|---|---|---|"]
out += [f"| {m} | {agree1[m]}/{n} | {overlap[m]/n:.0%} |" for m in agree1]
out += ["", "## Example results (top-3 handbook pages per query)", "| Query | Cosine | Euclidean | Dot product |", "|---|---|---|---|"]
out += [f"| {q} | {r['Cosine']} | {r['Euclidean (L2)']} | {r['Dot product']} |" for q, r in rows]
spread = norms.max() - norms.min()
out += ["", "## Recommendation",
 "**Cosine similarity**, implemented as inner product over unit-length vectors (FAISS `IndexFlatIP`).",
 "- Cosine measures direction (meaning) and ignores vector length, which is the right notion of semantic similarity for text.",
 f"- Here the norm spread is {spread:.3f}; " + ("it is tiny, so all three metrics rank almost identically." if spread < 0.05 else
   "dot product and Euclidean can favour longer vectors, so rankings diverge from cosine."),
 "- Because bge-small vectors are (near-)unit length, cosine, dot product and Euclidean distance are monotonically related; the choice matters more with models that do not normalise.",
 "- Cosine scores are also bounded and interpretable, which makes the relevance threshold (default 0.40) easy to tune and explain."]
Path("docs/distance_metric_report.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
